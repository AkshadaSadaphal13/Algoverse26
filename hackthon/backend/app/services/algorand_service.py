from typing import Any

from algosdk import account
from algosdk.transaction import PaymentTxn, wait_for_confirmation
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from app.config import settings


# ============================================================
# ALGOD CLIENT
# ============================================================

def get_algod_client() -> AlgodClient:
    if not settings.algorand_algod_server:
        raise RuntimeError(
            "Algorand Algod server is not configured."
        )

    return AlgodClient(
        settings.algorand_algod_token or "",
        str(settings.algorand_algod_server),
    )


# ============================================================
# INDEXER CLIENT
# ============================================================

def get_indexer_client() -> IndexerClient:
    indexer_server = getattr(
        settings,
        "algorand_indexer_server",
        None,
    )

    if not indexer_server:
        raise RuntimeError(
            "Algorand Indexer server is not configured."
        )

    return IndexerClient(
        "",
        str(indexer_server),
    )


# ============================================================
# SEND ALGO PAYMENT
# ============================================================

def send_algo_payment(
    amount_algo: float,
    receiver_address: str | None = None,
) -> dict[str, Any]:

    if not settings.algorand_payer_private_key:
        raise RuntimeError(
            "Algorand payer private key is not configured."
        )

    if not settings.algorand_payer_address:
        raise RuntimeError(
            "Algorand payer address is not configured."
        )

    receiver = (
        receiver_address
        or settings.algorand_receiver_address
    )

    if not receiver:
        raise RuntimeError(
            "Algorand receiver address is not configured."
        )

    # Verify private key belongs to configured payer.
    derived_address = account.address_from_private_key(
        settings.algorand_payer_private_key
    )

    if derived_address != settings.algorand_payer_address:
        raise RuntimeError(
            "Configured payer address does not match "
            "the private key."
        )

    if amount_algo <= 0:
        raise ValueError(
            "Payment amount must be greater than zero."
        )

    algod_client = get_algod_client()

    # ALGO -> microAlgos
    amount_microalgos = int(
        round(amount_algo * 1_000_000)
    )

    # Get network parameters.
    params = algod_client.suggested_params()

    # Create payment transaction.
    txn = PaymentTxn(
        sender=settings.algorand_payer_address,
        sp=params,
        receiver=receiver,
        amt=amount_microalgos,
    )

    # Sign transaction.
    signed_txn = txn.sign(
        settings.algorand_payer_private_key
    )

    # Submit transaction.
    txid = algod_client.send_transaction(
        signed_txn
    )

    print(f"Transaction submitted: {txid}")
    print("Waiting for Algorand confirmation...")

    # Wait for confirmation.
    confirmed = wait_for_confirmation(
        algod_client,
        txid,
        10,
    )

    confirmed_round = confirmed.get(
        "confirmed-round"
    )

    if not confirmed_round:
        raise RuntimeError(
            f"Transaction {txid} was submitted but "
            "was not confirmed within the timeout."
        )

    print(
        f"Transaction confirmed in round: "
        f"{confirmed_round}"
    )

    return {
        "transaction_id": txid,
        "sender": settings.algorand_payer_address,
        "receiver": receiver,
        "amount_algo": amount_algo,
        "amount_microalgos": amount_microalgos,
        "confirmed": True,
        "confirmed_round": confirmed_round,
    }


# ============================================================
# VERIFY ALGO PAYMENT
# ============================================================

def verify_algo_payment(
    transaction_id: str,
    expected_receiver: str,
    expected_amount_algo: float,
    expected_payer: str | None = None,
) -> dict[str, Any]:
    """
    Verify an existing ALGO payment on Algorand TestNet
    using the Algorand Indexer.

    Checks:
    - transaction exists
    - transaction is confirmed
    - transaction type is pay
    - receiver matches CodeVerse wallet
    - payer matches when provided
    - amount is sufficient
    """

    if not transaction_id:
        raise ValueError("Transaction ID is required.")

    if not expected_receiver:
        raise RuntimeError(
            "Algorand receiver address is not configured."
        )

    if expected_amount_algo <= 0:
        raise ValueError(
            "Expected payment amount must be greater than zero."
        )

    indexer_client = get_indexer_client()

    # --------------------------------------------------
    # Find transaction using Algorand Indexer
    # --------------------------------------------------

    try:
        response = indexer_client.search_transactions(
            txid=transaction_id
        )
    except Exception as exc:
        raise ValueError(
            f"Unable to find Algorand transaction: {exc}"
        ) from exc

    transactions = response.get("transactions", [])

    if not transactions:
        raise ValueError(
            "Transaction was not found on Algorand TestNet."
        )

    tx = transactions[0]

    # --------------------------------------------------
    # Confirmed transaction
    # --------------------------------------------------

    confirmed_round = tx.get("confirmed-round")

    if not confirmed_round:
        raise ValueError(
            "Transaction is not confirmed on Algorand TestNet."
        )

    # --------------------------------------------------
    # Transaction type
    # --------------------------------------------------

    if tx.get("tx-type") != "pay":
        raise ValueError(
            "Transaction is not an ALGO payment transaction."
        )

    # --------------------------------------------------
    # Sender
    # --------------------------------------------------

    sender = tx.get("sender")

    if not sender:
        raise ValueError(
            "Transaction sender is missing."
        )

    # --------------------------------------------------
    # Payment information
    # --------------------------------------------------

    payment_txn = tx.get(
        "payment-transaction",
        {},
    )

    receiver = payment_txn.get("receiver")

    if not receiver:
        raise ValueError(
            "Transaction receiver is missing."
        )

    # --------------------------------------------------
    # Verify receiver
    # --------------------------------------------------

    if receiver != expected_receiver:
        raise ValueError(
            "Transaction receiver does not match "
            "the CodeVerse receiver wallet."
        )

    # --------------------------------------------------
    # Verify payer
    # --------------------------------------------------

    if expected_payer and sender != expected_payer:
        raise ValueError(
            "Transaction sender does not match "
            "the expected payer wallet."
        )

    # --------------------------------------------------
    # Verify amount
    # --------------------------------------------------

    actual_microalgos = int(
        payment_txn.get("amount", 0)
    )

    expected_microalgos = int(
        round(expected_amount_algo * 1_000_000)
    )

    if actual_microalgos < expected_microalgos:
        raise ValueError(
            "Transaction amount is less than "
            "the required payment."
        )

    actual_algo = (
        actual_microalgos / 1_000_000
    )

    return {
        "verified": True,
        "transaction_id": transaction_id,
        "sender": sender,
        "receiver": receiver,
        "amount_algo": actual_algo,
        "amount_microalgos": actual_microalgos,
        "confirmed": True,
        "confirmed_round": confirmed_round,
    }