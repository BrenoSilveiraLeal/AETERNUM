from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AgentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    unique_id: str
    id: int
    name: str
    role: str
    specialization: str
    parent_agent_id: int | None
    avatar: str
    avatar_path: str
    avatar_index: int
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


class MarketMarker(BaseModel):
    kind: str
    date: str
    value: float
    label: str
    status: str


class MarketChartOut(BaseModel):
    symbol: str
    source: str
    data_status: str
    delayed: bool
    points: list[MarketPoint]
    markers: list[MarketMarker]


class MarketQuoteOut(BaseModel):
    symbol: str
    value: float | None
    source: str
    source_url: str
    source_timestamp: datetime | None
    collected_at: datetime
    status: str
    delayed: bool
    message: str | None = None


class PositionOut(BaseModel):
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    invested_value: float
    current_value: float
    unrealized_pnl: float
    mode: str


class WalletTransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    direction: str
    amount: float
    status: str
    method: str
    description: str
    created_at: datetime


class WalletOut(BaseModel):
    agent_unique_id: str
    agent_name: str
    currency: str
    balance: float
    status: str
    pix_status: str
    transactions: list[WalletTransactionOut]


class PixDepositIntentCreate(BaseModel):
    amount: float


class PixDepositIntentOut(BaseModel):
    id: int
    amount: float
    status: str
    pix_status: str
    message: str


class PixWithdrawalIntentCreate(BaseModel):
    amount: float
    pix_key: str


class PixWithdrawalIntentOut(BaseModel):
    id: int
    amount: float
    status: str
    pix_status: str
    message: str


class ChildAgentCreate(BaseModel):
    name: str
    role: str
    specialization: str
    objective: str
    reason: str
    risk_level: str = "LOW"


class AgentProposalOut(ChildAgentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    parent_agent_id: int
    status: str
    created_at: datetime
    decided_at: datetime | None = None


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
    filled_price: float | None = None
    executed_at: datetime | None = None
    mode: str = "PAPER"


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    created_at: datetime
    display_time: str
    sources: list[str]
    actions: list[str]
