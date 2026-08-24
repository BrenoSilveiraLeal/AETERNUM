from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Agent(Base):
    __tablename__ = "agents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unique_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    role: Mapped[str] = mapped_column(String(80), default="SPECIALIST")
    specialization: Mapped[str] = mapped_column(String(160))
    parent_agent_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avatar: Mapped[str] = mapped_column(String(32), default="◈")
    avatar_path: Mapped[str] = mapped_column(String(160), default="/avatars/aurion.png")
    avatar_index: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE")
    autonomy_level: Mapped[str] = mapped_column(String(32), default="SUPERVISED")
    risk_level: Mapped[str] = mapped_column(String(32), default="LOW")
    version: Mapped[str] = mapped_column(String(16), default="1.0.0")
    is_paper_only: Mapped[bool] = mapped_column(Boolean, default=True)
    survival_state: Mapped[str] = mapped_column(String(32), default="HEALTHY")
    generation: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class AgentAllocation(Base):
    __tablename__ = "agent_allocations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    allocation_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    max_position_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=10)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Asset(Base):
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    asset_class: Mapped[str] = mapped_column(String(32), default="EQUITY")
    sector: Mapped[str] = mapped_column(String(80), default="Technology")


class Position(Base):
    __tablename__ = "positions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(24), index=True)
    quantity: Mapped[float] = mapped_column(default=0)
    average_price: Mapped[float] = mapped_column(default=0)
    current_price: Mapped[float] = mapped_column(default=0)
    mode: Mapped[str] = mapped_column(String(16), default="PAPER")


class WalletAccount(Base):
    __tablename__ = "wallet_accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    currency: Mapped[str] = mapped_column(String(8), default="BRL")
    balance: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    status: Mapped[str] = mapped_column(String(24), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wallet_id: Mapped[int] = mapped_column(Integer, index=True)
    direction: Mapped[str] = mapped_column(String(8))
    amount: Mapped[float] = mapped_column(Numeric(18, 2))
    status: Mapped[str] = mapped_column(String(32), default="PENDING")
    method: Mapped[str] = mapped_column(String(24), default="PIX")
    provider_reference: Mapped[str | None] = mapped_column(String(160), nullable=True, unique=True)
    description: Mapped[str] = mapped_column(String(240))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class AgentRelationship(Base):
    __tablename__ = "agent_relationships"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_agent_id: Mapped[int] = mapped_column(Integer, index=True)
    child_agent_id: Mapped[int] = mapped_column(Integer, index=True, unique=True)
    relationship_type: Mapped[str] = mapped_column(String(32), default="CREATED")
    reason: Mapped[str] = mapped_column(String(500))
    objective: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class AgentProposal(Base):
    __tablename__ = "agent_proposals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_agent_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(80))
    role: Mapped[str] = mapped_column(String(80))
    specialization: Mapped[str] = mapped_column(String(160))
    objective: Mapped[str] = mapped_column(String(500))
    reason: Mapped[str] = mapped_column(String(500))
    risk_level: Mapped[str] = mapped_column(String(32), default="LOW")
    status: Mapped[str] = mapped_column(String(24), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class PaperOrder(Base):
    __tablename__ = "paper_orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(24), index=True)
    side: Mapped[str] = mapped_column(String(8))
    order_type: Mapped[str] = mapped_column(String(16), default="MARKET")
    quantity: Mapped[float] = mapped_column(default=0)
    limit_price: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="SIMULATED")
    rationale: Mapped[str] = mapped_column(String(500))
    filled_price: Mapped[float | None] = mapped_column(nullable=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class TradingSignal(Base):
    __tablename__ = "trading_signals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    symbol: Mapped[str] = mapped_column(String(24), index=True)
    action: Mapped[str] = mapped_column(String(8))
    confidence: Mapped[float] = mapped_column(Numeric(5, 4))
    reason: Mapped[str] = mapped_column(String(1000))
    risk: Mapped[str] = mapped_column(String(32), default="UNASSESSED")
    entry_min: Mapped[float | None] = mapped_column(nullable=True)
    entry_max: Mapped[float | None] = mapped_column(nullable=True)
    stop_loss: Mapped[float | None] = mapped_column(nullable=True)
    take_profit: Mapped[float | None] = mapped_column(nullable=True)
    position_size: Mapped[float] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(32), default="RECEIVED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class RiskDecision(Base):
    __tablename__ = "risk_decisions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    signal_id: Mapped[int] = mapped_column(Integer, index=True)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    reason: Mapped[str] = mapped_column(String(500))
    requested_notional: Mapped[float] = mapped_column(default=0)
    allowed_notional: Mapped[float] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class ExecutionRecord(Base):
    __tablename__ = "execution_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    signal_id: Mapped[int] = mapped_column(Integer, index=True)
    mode: Mapped[str] = mapped_column(String(16), default="PAPER")
    broker: Mapped[str] = mapped_column(String(80), default="PaperBroker")
    status: Mapped[str] = mapped_column(String(32), default="PREPARED")
    paper_order_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(96), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(String(8000))
    model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class DataSource(Base):
    __tablename__ = "data_sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    identifier: Mapped[str] = mapped_column(String(240))
    source_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="NOT_CONFIGURED")
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)


class MarketQuote(Base):
    __tablename__ = "market_quotes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(80), index=True)
    symbol: Mapped[str] = mapped_column(String(24), index=True)
    value: Mapped[float] = mapped_column()
    unit: Mapped[str] = mapped_column(String(24), default="BRL")
    source_timestamp: Mapped[datetime] = mapped_column(DateTime)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(String(24))
    raw_json: Mapped[str] = mapped_column(String(12000))
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)


class NewsEvent(Base):
    __tablename__ = "news_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    source: Mapped[str] = mapped_column(String(120))
    source_url: Mapped[str] = mapped_column(String(500))
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    event_type: Mapped[str] = mapped_column(String(64), default="UNCLASSIFIED")
    confirmation_status: Mapped[str] = mapped_column(String(32), default="UNCONFIRMED")
    confidence: Mapped[float | None] = mapped_column(nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(120))
    actor: Mapped[str] = mapped_column(String(120), default="system")
    request_id: Mapped[str | None] = mapped_column(String(96), nullable=True)
    result: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
