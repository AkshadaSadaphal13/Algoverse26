from app.services.pricing_service import calculate_usage_and_price


def test_pricing_calculation():
    result = calculate_usage_and_price(180)
    assert result["duration_seconds"] == 180
    assert result["usage_minutes"] == 3.0
    assert result["price_usdc"] == 0.06
    assert result["currency"] == "USDC"
