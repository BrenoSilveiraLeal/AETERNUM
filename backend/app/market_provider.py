from dataclasses import dataclass
from datetime import date, datetime, timezone


@dataclass(frozen=True)
class MarketDataPoint:
    symbol: str
    value: float
    source: str
    collected_at: datetime
    is_delayed: bool
    is_demo: bool


class MarketDataProvider:
    """Provider boundary; production adapters must use authorized APIs only."""

    name = "unconfigured"

    def get_quote(self, symbol: str) -> MarketDataPoint:
        raise NotImplementedError

    def get_history(self, symbol: str, start: date, end: date) -> list[MarketDataPoint]:
        raise NotImplementedError

    def get_fundamentals(self, symbol: str) -> dict[str, str | float]:
        raise NotImplementedError


class DemoMarketDataProvider(MarketDataProvider):
    """Legacy test provider; never selected by the production API."""
    name = "Demo provider"

    def get_quote(self, symbol: str) -> MarketDataPoint:
        return self.get_history(symbol, date.today(), date.today())[-1]

    def history(self, symbol: str) -> list[MarketDataPoint]:
        return self.get_history(symbol, date.today(), date.today())

    def get_history(self, symbol: str, start: date, end: date) -> list[MarketDataPoint]:
        return [MarketDataPoint(symbol, value, self.name, datetime.now(timezone.utc), True, True) for value in (100.0, 101.4, 100.8, 102.3)]

    def get_fundamentals(self, symbol: str) -> dict[str, str | float]:
        return {"symbol": symbol, "status": "DEMO DATA — fonte oficial ainda não configurada"}
