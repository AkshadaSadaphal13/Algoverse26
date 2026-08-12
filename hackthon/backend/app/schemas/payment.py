from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaymentCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: int
    payment_status: str
    amount_usdc: float | None = None
    asset_id: int | None = None
    network: str
    transaction_id: str | None = None
    payer_wallet: str | None = None
    receiver_wallet: str | None = None
    verified_at: datetime | None = None
    settled_at: datetime | None = None


class PaymentVerifyRequest(BaseModel):
    transaction_id: str
    payer_wallet: str
