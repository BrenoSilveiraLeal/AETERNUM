from dataclasses import dataclass
from datetime import date, datetime


class ProviderNotConfigured(Exception):
    pass


class ProviderUnavailable(Exception):
    pass


@dataclass(frozen=True)
class MarketRecord:
    symbol: str
    value: float
    source: str
    source_url: str
    source_timestamp: datetime
    collected_at: datetime
    status: str
    delayed: bool
    raw: dict


class MarketDataProvider:
    name = "unconfigured"

    def get_quote(self, symbol: str) -> MarketRecord:
        raise NotImplementedError

    def get_history(self, symbol: str, start_date: date, end_date: date) -> list[MarketRecord]:
        raise NotImplementedError

    def get_company(self, symbol: str) -> dict:
        raise NotImplementedError

    def get_indicators(self, symbol: str) -> dict:
        raise NotImplementedError

    def get_market_status(self) -> dict:
        raise NotImplementedError
