from app.config import settings


def calculate_usage_and_price(duration_seconds: float) -> dict:
    minutes = duration_seconds / 60.0
    price = round(minutes * settings.price_per_minute_usdc, 6)
    return {
        "duration_seconds": duration_seconds,
        "usage_minutes": round(minutes, 2),
        "price_usdc": price,
        "currency": "USDC",
    }
