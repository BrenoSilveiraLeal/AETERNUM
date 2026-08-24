from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import AgentAllocation, Position, TradingSignal, WalletAccount


@dataclass(frozen=True)
class RiskResult:
    approved: bool
    reason: str
    requested_notional: float
    allowed_notional: float


class RiskManager:
    """Central risk gate shared by every agent and execution path."""

    def evaluate(self, db: Session, signal: TradingSignal, market_price: float) -> RiskResult:
        requested = round(float(signal.position_size) * market_price, 2)
        if settings.trading_mode.upper() != "PAPER":
            return RiskResult(False, "Trading mode is not PAPER", requested, 0)
        if signal.action not in {"BUY", "SELL"}:
            return RiskResult(False, "Only BUY or SELL signals can be evaluated", requested, 0)
        if not 0 <= float(signal.confidence) <= 1:
            return RiskResult(False, "Confidence must be between 0 and 1", requested, 0)
        if signal.position_size <= 0 or market_price <= 0:
            return RiskResult(False, "Position size and market price must be positive", requested, 0)
        if signal.expires_at is not None and signal.expires_at <= datetime.now(timezone.utc):
            return RiskResult(False, "Signal has expired", requested, 0)
        if signal.stop_loss is None or signal.take_profit is None:
            return RiskResult(False, "Stop loss and take profit are required", requested, 0)
        if signal.action == "BUY" and not (float(signal.stop_loss) < market_price < float(signal.take_profit)):
            return RiskResult(False, "BUY requires stop loss below price and take profit above price", requested, 0)
        if signal.action == "SELL" and not (float(signal.take_profit) < market_price < float(signal.stop_loss)):
            return RiskResult(False, "SELL requires take profit below price and stop loss above price", requested, 0)
        allocation = db.scalar(select(AgentAllocation).where(AgentAllocation.agent_id == signal.agent_id))
        wallet = db.scalar(select(WalletAccount).join(AgentAllocation, AgentAllocation.agent_id == WalletAccount.agent_id).where(AgentAllocation.agent_id == signal.agent_id))
        if allocation is None or not allocation.enabled:
            return RiskResult(False, "Agent has no enabled capital allocation", requested, 0)
        capital = float(wallet.balance or 0) if wallet else 0
        allocation_cap = round(capital * float(allocation.allocation_percent) / 100, 2)
        position_cap = round(capital * float(allocation.max_position_percent) / 100, 2)
        allowed = min(allocation_cap, position_cap)
        if allowed <= 0:
            return RiskResult(False, "No verified capital is available for this allocation", requested, allowed)
        if requested > allowed:
            return RiskResult(False, "Signal exceeds the agent allocation or position limit", requested, allowed)
        if signal.action == "SELL":
            position = db.scalar(select(Position).where(Position.symbol == signal.symbol))
            if position is None or float(position.quantity) < float(signal.position_size):
                return RiskResult(False, "SELL exceeds the available PAPER position", requested, allowed)
        return RiskResult(True, "Approved by PAPER risk limits", requested, allowed)
