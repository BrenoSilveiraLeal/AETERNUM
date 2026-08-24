from datetime import datetime, timezone
from types import SimpleNamespace

from app.broker.mt5 import MetaTraderBroker


class FakeMT5:
    ACCOUNT_TRADE_MODE_DEMO = 0
    ACCOUNT_TRADE_MODE_CONTEST = 1
    TIMEFRAME_D1 = 16408

    def initialize(self, **kwargs):
        return True

    def terminal_info(self):
        return SimpleNamespace(connected=True, build=1)

    def account_info(self):
        return SimpleNamespace(login=12345678, trade_mode=0, server="Rico-Demo", currency="BRL")

    def last_error(self):
        return (0, "ok")

    def symbol_info_tick(self, symbol):
        return SimpleNamespace(time=1700000000, bid=10.0, ask=10.1, last=10.05)

    def symbols_get(self):
        return (SimpleNamespace(name="PETR4", visible=True),)

    def symbol_select(self, symbol, enabled):
        return symbol == "PETR4" and enabled

    def positions_get(self):
        return ()

    def orders_get(self):
        return ()

    def order_check(self, request):
        return SimpleNamespace(retcode=0, comment="checked")


def test_mt5_status_masks_account_and_allows_demo(monkeypatch):
    monkeypatch.setattr("app.broker.mt5.settings.mt5_allowed_demo_servers", "demo")
    status = MetaTraderBroker(FakeMT5()).status()
    assert status["connected"] is True
    assert status["account"]["login_masked"] == "••••5678"
    assert status["account"]["permitted_demo"] is True


def test_mt5_never_sends_orders(monkeypatch):
    monkeypatch.setattr("app.broker.mt5.settings.mt5_allowed_demo_servers", "demo")
    broker = MetaTraderBroker(FakeMT5())
    prepared = broker.prepare_order({"symbol": "PETR4", "volume": 1})
    assert prepared["status"] == "PREPARED_ONLY"
    assert not hasattr(broker.mt5, "order_send")
