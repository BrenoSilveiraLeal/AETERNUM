from datetime import date, timedelta
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .models import Agent, Position
from .schemas import AgentOut, MarketHistory, MarketPoint, PositionOut
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


@app.get("/api/market/history", response_model=MarketHistory)
def market_history() -> MarketHistory:
    # Deterministic demo contract; replace with an official server-side provider in Fase 3.
    start = date.today() - timedelta(days=13)
    values = [100.0, 101.4, 100.8, 102.3, 103.1, 102.7, 104.0, 105.6, 104.9, 106.2, 107.0, 106.5, 108.1, 109.4]
    return MarketHistory(source="Demo provider", is_demo=True, data_status="DEMO DATA — fonte de mercado ainda não configurada", points=[MarketPoint(date=(start + timedelta(days=i)).isoformat(), value=value) for i, value in enumerate(values)])


@app.get("/api/portfolio/positions", response_model=list[PositionOut])
def portfolio_positions(db: Session = Depends(get_db)) -> list[PositionOut]:
    positions = list(db.scalars(select(Position).order_by(Position.symbol)))
    if not positions:
        positions = [Position(symbol="AAPL", quantity=12, average_price=182.10, current_price=191.44), Position(symbol="NVDA", quantity=8, average_price=118.30, current_price=126.80)]
    return [PositionOut(symbol=p.symbol, quantity=p.quantity, average_price=p.average_price, current_price=p.current_price, invested_value=round(p.quantity * p.average_price, 2), current_value=round(p.quantity * p.current_price, 2), unrealized_pnl=round(p.quantity * (p.current_price - p.average_price), 2), mode="PAPER") for p in positions]
