from datetime import date, datetime, time, timezone

from ...broker.mt5 import MetaTraderBroker
from .base import MarketDataProvider, MarketRecord, ProviderUnavailable


class MetaTraderMarketDataProvider(MarketDataProvider):
    name = "MetaTrader 5"

    def __init__(self, broker: MetaTraderBroker | None = None) -> None:
        self.broker = broker or MetaTraderBroker()

    def get_quote(self, symbol: str) -> MarketRecord:
        now = datetime.now(timezone.utc)
        tick = self.broker.tick(symbol)
        value = float(tick.get("last") or tick.get("bid") or tick.get("ask") or 0)
        if value <= 0:
            raise ProviderUnavailable(f"MetaTrader 5 não retornou cotação para {symbol}")
        timestamp = datetime.fromtimestamp(float(tick.get("time", now.timestamp())), tz=timezone.utc)
        return MarketRecord(symbol=symbol.upper(), value=value, source=self.name, source_url="https://www.mql5.com/en/docs/python_metatrader5", source_timestamp=timestamp, collected_at=now, status="OK", delayed=False, raw=tick)

    def get_history(self, symbol: str, start_date: date, end_date: date) -> list[MarketRecord]:
        start = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        end = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        rows = self.broker.candles(symbol, getattr(self.broker.mt5, "TIMEFRAME_D1", 1), start, end)
        records: list[MarketRecord] = []
        for row in rows:
            timestamp = datetime.fromtimestamp(float(row["time"]), tz=timezone.utc)
            records.append(MarketRecord(symbol=symbol.upper(), value=float(row.get("close", 0)), source=self.name, source_url="https://www.mql5.com/en/docs/python_metatrader5", source_timestamp=timestamp, collected_at=datetime.now(timezone.utc), status="OK", delayed=False, raw=row))
        return records

    def get_company(self, symbol: str) -> dict:
        return {"symbol": symbol.upper(), "source": self.name}

    def get_indicators(self, symbol: str) -> dict:
        return {"symbol": symbol.upper(), "status": "NOT_IMPLEMENTED", "source": self.name}

    def get_market_status(self) -> dict:
        return self.broker.status()
