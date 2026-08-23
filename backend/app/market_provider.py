from dataclasses import dataclass
from datetime import datetime, timezone


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

    def history(self, symbol: str) -> list[MarketDataPoint]:
        raise NotImplementedError


class DemoMarketDataProvider(MarketDataProvider):
    name = "Demo provider"

    def history(self, symbol: str) -> list[MarketDataPoint]:
        return [MarketDataPoint(symbol, value, self.name, datetime.now(timezone.utc), True, True) for value in (100.0, 101.4, 100.8, 102.3)]
