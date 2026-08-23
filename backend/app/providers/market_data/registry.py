from ...config import settings
from .base import MarketDataProvider, ProviderNotConfigured
from .dadosdemercado import DadosDeMercadoProvider


def get_market_provider() -> MarketDataProvider:
    if settings.market_data_provider == "dadosdemercado":
        return DadosDeMercadoProvider(settings.market_data_api_url, settings.market_data_api_token or settings.market_data_api_key)
    raise ProviderNotConfigured("Integração ainda não configurada.")
