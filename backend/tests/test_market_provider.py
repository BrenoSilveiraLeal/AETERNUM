from datetime import date
from app.providers.market_data.base import ProviderNotConfigured
from app.providers.market_data.dadosdemercado import DadosDeMercadoProvider


def test_market_provider_requires_token():
    provider = DadosDeMercadoProvider("https://example.invalid/v1", None)
    try:
        provider.get_history("PETR4", date.today(), date.today())
    except ProviderNotConfigured:
        return
    raise AssertionError("provider without token must not call or fabricate data")
