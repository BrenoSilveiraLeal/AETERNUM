from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class BrokerAdapter(ABC):
    """Read-only broker contract; execution is intentionally not exposed yet."""

    @abstractmethod
    def status(self) -> dict[str, Any]: ...

    @abstractmethod
    def symbols(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def tick(self, symbol: str) -> dict[str, Any]: ...

    @abstractmethod
    def candles(self, symbol: str, timeframe: int, start: datetime, end: datetime) -> list[dict[str, Any]]: ...

    @abstractmethod
    def positions(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def orders(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def prepare_order(self, request: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def check_order(self, request: dict[str, Any]) -> dict[str, Any]: ...
