from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AgentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    unique_id: str
    name: str
    role: str
    specialization: str
    parent_agent_id: int | None
    avatar: str
    status: str
    survival_state: str
    autonomy_level: str
    risk_level: str
    version: str
    is_paper_only: bool
    generation: int
    created_at: datetime


class MarketPoint(BaseModel):
    date: str
    value: float


class MarketHistory(BaseModel):
    source: str
    is_demo: bool
    data_status: str
    points: list[MarketPoint]


class PositionOut(BaseModel):
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    invested_value: float
    current_value: float
    unrealized_pnl: float
    mode: str


class ChildAgentCreate(BaseModel):
    name: str
    role: str
    specialization: str
    objective: str
    reason: str
    risk_level: str = "LOW"


class PaperOrderCreate(BaseModel):
    symbol: str
    side: str
    quantity: float
    order_type: str = "MARKET"
    limit_price: float | None = None
    rationale: str


class PaperOrderOut(PaperOrderCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    mode: str = "PAPER"
