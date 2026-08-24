import logging
from datetime import datetime, timezone
from typing import Any

from ..config import settings
from .base import BrokerAdapter

logger = logging.getLogger(__name__)


class MetaTraderBroker(BrokerAdapter):
    """MetaTrader 5 terminal adapter.

    The module is optional and all methods fail soft when the terminal is absent.
    No method in this first phase calls order_send().
    """

    def __init__(self, mt5_module: Any | None = None) -> None:
        if mt5_module is not None:
            self.mt5 = mt5_module
        else:
            try:
                import MetaTrader5 as mt5  # type: ignore
            except ImportError:
                self.mt5 = None
            else:
                self.mt5 = mt5
        self.connected = False
        self.last_sync: datetime | None = None

    def _error(self) -> str:
        try:
            return str(self.mt5.last_error()) if self.mt5 else "MetaTrader5 package not installed"
        except Exception:
            return "MetaTrader 5 connection error"

    def connect(self) -> bool:
        if self.mt5 is None:
            return False
        kwargs: dict[str, Any] = {"timeout": settings.mt5_timeout_ms}
        if settings.mt5_login is not None:
            kwargs["login"] = settings.mt5_login
        if settings.mt5_server:
            kwargs["server"] = settings.mt5_server
        if settings.mt5_password:
            kwargs["password"] = settings.mt5_password
        try:
            self.connected = bool(self.mt5.initialize(settings.mt5_terminal_path, **kwargs) if settings.mt5_terminal_path else self.mt5.initialize(**kwargs))
        except Exception as exc:
            logger.warning("MetaTrader 5 initialization failed: %s", type(exc).__name__)
            self.connected = False
        if self.connected:
            self.last_sync = datetime.now(timezone.utc)
        return self.connected

    def _ensure_connected(self) -> None:
        if not self.connected and not self.connect():
            raise RuntimeError(f"MetaTrader 5 unavailable: {self._error()}")

    def _tuple(self, value: Any) -> dict[str, Any] | None:
        if value is None:
            return None
        if hasattr(value, "_asdict"):
            return value._asdict()
        if hasattr(value, "__dict__"):
            return vars(value)
        return dict(value)

    def _demo_allowed(self, account: dict[str, Any]) -> bool:
        trade_mode = account.get("trade_mode")
        demo_value = getattr(self.mt5, "ACCOUNT_TRADE_MODE_DEMO", 0)
        contest_value = getattr(self.mt5, "ACCOUNT_TRADE_MODE_CONTEST", 1)
        server = str(account.get("server") or "").casefold()
        allowed = [item.strip().casefold() for item in settings.mt5_allowed_demo_servers.split(",") if item.strip()]
        return settings.trading_mode.upper() == "PAPER" and settings.mt5_demo_only and trade_mode in {demo_value, contest_value} and any(item in server for item in allowed)

    def status(self) -> dict[str, Any]:
        result: dict[str, Any] = {"provider": "MetaTrader 5", "broker": "Rico", "connected": False, "terminal": "OFFLINE", "market_data": "UNAVAILABLE", "environment": "PAPER / DEMO", "account": None, "last_sync": self.last_sync.isoformat() if self.last_sync else None, "message": "Integração ainda não configurada."}
        if self.mt5 is None:
            result["message"] = "Pacote MetaTrader5 não instalado no ambiente do backend."
            return result
        if not self.connect():
            result["message"] = "Terminal MetaTrader 5 fechado, ausente ou inacessível."
            return result
        terminal = self._tuple(self.mt5.terminal_info()) or {}
        account = self._tuple(self.mt5.account_info()) or {}
        permitted = self._demo_allowed(account)
        result.update({"connected": True, "terminal": "CONNECTED" if terminal else "OFFLINE", "market_data": "AVAILABLE" if terminal.get("connected", True) else "UNAVAILABLE", "account": {"login_masked": self._mask_login(account.get("login")), "server": account.get("server") if permitted else None, "permitted_demo": permitted}, "message": "Conectado em conta DEMO autorizada." if permitted else "Conta conectada, mas o ambiente não foi reconhecido como DEMO permitido."})
        return result

    @staticmethod
    def _mask_login(login: Any) -> str | None:
        raw = str(login) if login is not None else ""
        return f"••••{raw[-4:]}" if raw else None

    def symbols(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        return [self._tuple(row) or {} for row in (self.mt5.symbols_get() or ())]

    def select_symbol(self, symbol: str) -> bool:
        self._ensure_connected()
        return bool(self.mt5.symbol_select(symbol.upper().strip(), True))

    def tick(self, symbol: str) -> dict[str, Any]:
        self._ensure_connected()
        value = self.mt5.symbol_info_tick(symbol.upper().strip())
        if value is None:
            raise RuntimeError(f"Símbolo inexistente ou sem tick: {symbol}")
        return self._tuple(value) or {}

    def candles(self, symbol: str, timeframe: int, start: datetime, end: datetime) -> list[dict[str, Any]]:
        self._ensure_connected()
        rows = self.mt5.copy_rates_range(symbol.upper().strip(), timeframe, start, end)
        if rows is None:
            return []
        if hasattr(rows, "dtype") and rows.dtype.names:
            return [{name: row[name].item() if hasattr(row[name], "item") else row[name] for name in rows.dtype.names} for row in rows]
        return [dict(row) if not isinstance(row, tuple) else {str(index): value for index, value in enumerate(row)} for row in rows]

    def positions(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        return [self._tuple(row) or {} for row in (self.mt5.positions_get() or ())]

    def orders(self) -> list[dict[str, Any]]:
        self._ensure_connected()
        return [self._tuple(row) or {} for row in (self.mt5.orders_get() or ())]

    def history(self, start: datetime, end: datetime) -> dict[str, list[dict[str, Any]]]:
        self._ensure_connected()
        return {"orders": [self._tuple(row) or {} for row in (self.mt5.history_orders_get(start, end) or ())], "deals": [self._tuple(row) or {} for row in (self.mt5.history_deals_get(start, end) or ())]}

    def prepare_order(self, request: dict[str, Any]) -> dict[str, Any]:
        return {"status": "PREPARED_ONLY", "request": dict(request), "message": "A ordem foi apenas preparada; envio está desabilitado nesta fase."}

    def check_order(self, request: dict[str, Any]) -> dict[str, Any]:
        self._ensure_connected()
        account = self._tuple(self.mt5.account_info()) or {}
        if not self._demo_allowed(account):
            raise PermissionError("Verificação bloqueada: conta não reconhecida como DEMO permitida em modo PAPER")
        result = self.mt5.order_check(request)
        return self._tuple(result) or {"status": "UNAVAILABLE", "message": self._error()}
