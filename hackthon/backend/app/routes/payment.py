from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.job import Job
from app.routes.audio import get_db

from app.schemas.job import JobResultResponse
from app.schemas.payment import (
    PaymentCreateResponse,
    PaymentVerifyRequest,
)

from app.services.payment_service import (
    create_payment_record,
    get_payment_for_job,
    verify_payment as verify_payment_record,
)

from app.services.algorand_service import (
    send_algo_payment,
    verify_algo_payment,
)


router = APIRouter(prefix="/api/jobs")


# ============================================================
# PAYMENT DETAILS
# ============================================================

@router.get(
    "/{job_id}/payment",
    response_model=PaymentCreateResponse,
)
def get_payment(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = (
        db.query(Job)
        .filter(Job.job_id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    payment = get_payment_for_job(
        db,
        job,
    )

    if not payment:
        payment = create_payment_record(
            db,
            job,
        )

    return PaymentCreateResponse.from_orm(
        payment
    )


# ============================================================
# TEMPORARY REAL ALGORAND PAYMENT TEST
# ============================================================

@router.post("/test-algorand-payment")
def test_algorand_payment():
    """
    Temporary endpoint used to test a real
    ALGO TestNet transaction.

    This endpoint is only for backend testing.
    """

    try:
        result = send_algo_payment(
            amount_algo=0.02,
        )

        return {
            "success": True,
            **result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Algorand payment failed: {exc}",
        ) from exc


# ============================================================
# REAL ALGORAND PAYMENT VERIFICATION
# ============================================================

@router.post(
    "/{job_id}/payment/verify",
    response_model=PaymentCreateResponse,
)
def verify_payment(
    job_id: str,
    payload: PaymentVerifyRequest,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # 1. Find job
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(Job.job_id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # --------------------------------------------------------
    # 2. Check Algorand receiver wallet
    # --------------------------------------------------------

    if not settings.algorand_receiver_address:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Algorand receiver wallet is not configured.",
        )

    # --------------------------------------------------------
    # 3. Get or create payment record
    # --------------------------------------------------------

    payment = get_payment_for_job(
        db,
        job,
    )

    if not payment:
        payment = create_payment_record(
            db,
            job,
        )

    # --------------------------------------------------------
    # 4. Already verified
    # --------------------------------------------------------

    if payment.payment_status == "verified":
        return PaymentCreateResponse.from_orm(
            payment
        )

    # --------------------------------------------------------
    # 5. Validate transaction ID
    # --------------------------------------------------------

    transaction_id = (
        payload.transaction_id or ""
    ).strip()

    if not transaction_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction ID is required.",
        )

    # --------------------------------------------------------
    # 6. Validate payer wallet
    # --------------------------------------------------------

    payer_wallet = (
        payload.payer_wallet or ""
    ).strip()

    if not payer_wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payer wallet is required.",
        )

    # --------------------------------------------------------
    # 7. Determine required ALGO amount
    #
    # Your current database column is named price_usdc,
    # but the actual blockchain payment is Native ALGO.
    #
    # We keep the existing database field for now so we
    # don't break your current database/schema.
    # --------------------------------------------------------

    required_amount_algo = float(
        job.price_usdc or 0
    )

    if required_amount_algo <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment amount for this job.",
        )

    # --------------------------------------------------------
    # 8. REAL BLOCKCHAIN VERIFICATION
    #
    # This checks the Algorand Indexer:
    #
    # - transaction exists
    # - transaction is confirmed
    # - transaction type is pay
    # - receiver is CodeVerse wallet
    # - payer matches submitted wallet
    # - amount is sufficient
    # --------------------------------------------------------

    try:
        blockchain_result = verify_algo_payment(
            transaction_id=transaction_id,
            expected_receiver=(
                settings.algorand_receiver_address
            ),
            expected_amount_algo=required_amount_algo,
            expected_payer=payer_wallet,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Algorand verification failed: {exc}",
        ) from exc

    # --------------------------------------------------------
    # 9. Make sure blockchain verification succeeded
    # --------------------------------------------------------

    if not blockchain_result.get("verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Algorand transaction could not be verified.",
        )

    # --------------------------------------------------------
    # 10. Store verified payment in database
    # --------------------------------------------------------

    payment = verify_payment_record(
        db=db,
        payment=payment,
        transaction_id=(
            blockchain_result["transaction_id"]
        ),
        payer_wallet=(
            blockchain_result["sender"]
        ),
        blockchain_result=blockchain_result,
    )

    # --------------------------------------------------------
    # 11. Mark job as paid
    # --------------------------------------------------------

    job.payment_status = "verified"

    db.commit()
    db.refresh(job)

    # --------------------------------------------------------
    # 12. Return payment information
    # --------------------------------------------------------

    return PaymentCreateResponse.from_orm(
        payment
    )


# ============================================================
# RESULT
# ============================================================

@router.get(
    "/{job_id}/result",
    response_model=JobResultResponse,
)
def get_result(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = (
        db.query(Job)
        .filter(Job.job_id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if (
        job.processing_status != "completed"
        or not job.result_summary
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not available yet",
        )

    return JobResultResponse.from_orm(
        job
    )


# ============================================================
# PROCESS JOB
# ============================================================

@router.post(
    "/{job_id}/process",
    response_model=JobResultResponse,
)
def process_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # 1. Find job
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(Job.job_id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # --------------------------------------------------------
    # 2. Check payment
    # --------------------------------------------------------

    payment = get_payment_for_job(
        db,
        job,
    )

    if (
        not payment
        or payment.payment_status != "verified"
    ):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": "Payment required",
                "amount_algo": job.price_usdc,
                "asset_id": settings.algorand_asset_id,
                "network": settings.algorand_network,
                "receiver_wallet": (
                    settings.algorand_receiver_address
                ),
                "payment_status": "pending",
            },
        )

    # --------------------------------------------------------
    # 3. Process job
    # --------------------------------------------------------

    if job.processing_status != "completed":

        job.processing_status = "completed"

        job.payment_status = "verified"

        job.result_summary = (
            f"Generated a "
            f"{max(3, int(round(job.usage_minutes or 0)))}-slide "
            f"outline from "
            f"{job.original_filename}."
        )

        db.commit()
        db.refresh(job)

    # --------------------------------------------------------
    # 4. Return result
    # --------------------------------------------------------

    return JobResultResponse.from_orm(
        job
    )