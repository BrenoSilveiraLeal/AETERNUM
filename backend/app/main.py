from datetime import date, timedelta
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .models import Agent, AgentRelationship, PaperOrder, Position
from .schemas import AgentOut, ChildAgentCreate, MarketHistory, MarketPoint, PaperOrderCreate, PaperOrderOut, PositionOut
from .seed import seed_agents

Base.metadata.create_all(bind=engine)
with next(get_db()) as db:
    seed_agents(db)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","), allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "trading_mode": settings.trading_mode}


@app.get("/api/agents", response_model=list[AgentOut])
def list_agents(db: Session = Depends(get_db)) -> list[Agent]:
    return list(db.scalars(select(Agent).order_by(Agent.id)))


@app.post("/api/agents/{parent_id}/children", response_model=AgentOut, status_code=201)
def create_child_agent(parent_id: int, payload: ChildAgentCreate, db: Session = Depends(get_db)) -> Agent:
    parent = db.get(Agent, parent_id)
    if parent is None:
        raise HTTPException(404, "Parent agent not found")
    if parent.generation >= 3:
        raise HTTPException(400, "Maximum agent generation reached")
    if not payload.reason.strip() or not payload.objective.strip():
        raise HTTPException(422, "Reason and objective are required")
    unique_id = "AGENT_" + payload.name.upper().replace(" ", "_")
    if db.scalar(select(Agent).where(Agent.unique_id == unique_id)):
        raise HTTPException(409, "Agent already exists")
    child = Agent(unique_id=unique_id, name=payload.name, role=payload.role, specialization=payload.specialization, parent_agent_id=parent.id, generation=parent.generation + 1, status="EXPERIMENTAL", risk_level=payload.risk_level)
    db.add(child)
    db.flush()
    db.add(AgentRelationship(parent_agent_id=parent.id, child_agent_id=child.id, reason=payload.reason, objective=payload.objective))
    db.commit()
    db.refresh(child)
    return child


@app.get("/api/market/history", response_model=MarketHistory)
def market_history() -> MarketHistory:
    return MarketHistory(source="", is_demo=False, data_status="Integração ainda não configurada.", points=[])


@app.get("/api/portfolio/positions", response_model=list[PositionOut])
def portfolio_positions(db: Session = Depends(get_db)) -> list[PositionOut]:
    positions = list(db.scalars(select(Position).order_by(Position.symbol)))
    return [PositionOut(symbol=p.symbol, quantity=p.quantity, average_price=p.average_price, current_price=p.current_price, invested_value=round(p.quantity * p.average_price, 2), current_value=round(p.quantity * p.current_price, 2), unrealized_pnl=round(p.quantity * (p.current_price - p.average_price), 2), mode="PAPER") for p in positions]


@app.post("/api/paper/orders", response_model=PaperOrderOut, status_code=201)
def create_paper_order(payload: PaperOrderCreate, db: Session = Depends(get_db)) -> PaperOrder:
    side = payload.side.upper()
    order_type = payload.order_type.upper()
    if settings.trading_mode != "PAPER":
        raise HTTPException(503, "Only PAPER mode is enabled")
    if side not in {"BUY", "SELL"} or order_type not in {"MARKET", "LIMIT", "STOP", "TAKE_PROFIT"}:
        raise HTTPException(422, "Unsupported PAPER order")
    if payload.quantity <= 0 or (order_type == "LIMIT" and (payload.limit_price is None or payload.limit_price <= 0)):
        raise HTTPException(422, "Quantity and price must be positive")
    order = PaperOrder(symbol=payload.symbol.upper(), side=side, order_type=order_type, quantity=payload.quantity, limit_price=payload.limit_price, rationale=payload.rationale, status="SIMULATED")
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
