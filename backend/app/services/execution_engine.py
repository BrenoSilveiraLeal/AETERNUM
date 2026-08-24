from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..config import settings
from ..broker.base import BrokerAdapter
from ..broker.mt5 import MetaTraderBroker
from ..models import AuditLog, ExecutionRecord, MarketQuote, PaperOrder, RiskDecision, TradingSignal
from .risk_manager import RiskManager


class ExecutionEngine:
    """The only service allowed to turn an approved signal into an order."""

    def __init__(self, risk_manager: RiskManager | None = None, broker: BrokerAdapter | None = None) -> None:
        self.risk_manager = risk_manager or RiskManager()
        self.broker = broker or MetaTraderBroker()

    def execute(self, db: Session, signal: TradingSignal, request_id: str | None = None) -> ExecutionRecord:
        quote = db.query(MarketQuote).filter(MarketQuote.symbol == signal.symbol, MarketQuote.status.in_(["OK", "SUCCESS"])).order_by(MarketQuote.collected_at.desc()).first()
        if quote is None:
            signal.status = "BLOCKED_NO_QUOTE"
            record = ExecutionRecord(signal_id=signal.id, status="BLOCKED", error="No verified market quote")
            db.add(record)
            db.add(AuditLog(action="SIGNAL_BLOCKED", actor="execution_engine", request_id=request_id, result="NO_QUOTE"))
            db.flush()
            return record
        result = self.risk_manager.evaluate(db, signal, float(quote.value))
        db.add(RiskDecision(signal_id=signal.id, approved=result.approved, reason=result.reason, requested_notional=result.requested_notional, allowed_notional=result.allowed_notional))
        if not result.approved:
            signal.status = "BLOCKED_RISK"
            record = ExecutionRecord(signal_id=signal.id, status="BLOCKED", error=result.reason)
            db.add(record)
            db.add(AuditLog(action="SIGNAL_BLOCKED", actor="execution_engine", request_id=request_id, result="RISK"))
            db.flush()
            return record
        if settings.trading_mode.upper() != "PAPER":
            raise RuntimeError("Execution is locked unless TRADING_MODE=PAPER")
        self.broker.prepare_order({"symbol": signal.symbol, "side": signal.action, "volume": signal.position_size, "stop_loss": signal.stop_loss, "take_profit": signal.take_profit})
        order = PaperOrder(symbol=signal.symbol, side=signal.action, order_type="MARKET", quantity=signal.position_size, rationale=signal.reason, status="SIMULATED")
        db.add(order)
        db.flush()
        signal.status = "PAPER_ORDER_PREPARED"
        record = ExecutionRecord(signal_id=signal.id, mode="PAPER", broker="PaperBroker", status="PREPARED", paper_order_id=order.id)
        db.add(record)
        db.add(AuditLog(action="PAPER_ORDER_PREPARED", actor="execution_engine", request_id=request_id, result="PREPARED"))
        db.flush()
        return record
