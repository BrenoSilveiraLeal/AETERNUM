from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String
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
    status: Mapped[str] = mapped_column(String(32), default="APPROVED")
    autonomy_level: Mapped[str] = mapped_column(String(32), default="SUPERVISED")
    risk_level: Mapped[str] = mapped_column(String(32), default="LOW")
    version: Mapped[str] = mapped_column(String(16), default="1.0.0")
    is_paper_only: Mapped[bool] = mapped_column(Boolean, default=True)
    survival_state: Mapped[str] = mapped_column(String(32), default="HEALTHY")
    generation: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


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
