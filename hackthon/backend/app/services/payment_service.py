from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.models.job import Job
from app.models.payment import Payment


def create_payment_record(
    db: Session,
    job: Job,
) -> Payment:

    payment = Payment(
        job_id=job.id,
        amount_usdc=job.price_usdc,
        asset_id=settings.algorand_asset_id,
        network=settings.algorand_network,
        payment_status="pending",
        receiver_wallet=settings.algorand_receiver_address,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


def verify_payment(
    db: Session,
    payment: Payment,
    transaction_id: str,
    payer_wallet: str,
    blockchain_result: dict,
) -> Payment:

    # --------------------------------------------------
    # IMPORTANT:
    # Only mark payment verified if blockchain
    # verification was successful.
    # --------------------------------------------------

    if not blockchain_result.get("verified"):
        raise ValueError(
            "Algorand transaction could not be verified."
        )

    payment.payment_status = "verified"

    payment.transaction_id = transaction_id

    payment.payer_wallet = payer_wallet

    payment.verified_at = func.now()

    payment.settled_at = func.now()

    db.commit()
    db.refresh(payment)

    return payment


def get_payment_for_job(
    db: Session,
    job: Job,
) -> Optional[Payment]:

    return (
        db.query(Payment)
        .filter(Payment.job_id == job.id)
        .order_by(Payment.created_at.desc())
        .first()
    )