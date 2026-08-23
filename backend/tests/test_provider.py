from app.market_provider import DemoMarketDataProvider


def test_demo_provider_is_explicitly_demo():
    point = DemoMarketDataProvider().history("AAPL")[0]
    assert point.is_demo is True
    assert point.is_delayed is True
