from pathlib import Path

from pydantic import AnyHttpUrl, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=Path(__file__).resolve().parents[1] / ".env")

    app_name: str = "CodeVerse Voice-to-Slide-Deck Backend"
    app_env: str = "development"
    payment_mode: str = "mock"
    project_root: Path = Path(__file__).resolve().parents[2]
    database_url: str = f"sqlite+pysqlite:///{(Path(__file__).resolve().parents[1] / 'dev.db').as_posix()}"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    algorand_indexer_server: str = ""
    algorand_network: str = "testnet"
    algorand_asset_id: int | None = None
    algorand_receiver_address: str | None = None
    algorand_payer_address: str | None = None
    algorand_payer_private_key: str | None = None
    algorand_algod_server: str | None = None
    algorand_algod_token: str | None = None
    algorand_algod_port: int | None = None
    x402_facilitator_url: AnyHttpUrl | None = None
    price_per_minute_usdc: float = 0.02
    frontend_origin: AnyHttpUrl = "http://localhost:5173"
    uploads_dir: Path = project_root / "backend" / "uploads"
    generated_dir: Path = project_root / "backend" / "generated"


settings = Settings()
