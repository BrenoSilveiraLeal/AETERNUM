from datetime import date, datetime, timedelta, timezone
import json
from email.utils import parsedate_to_datetime
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .models import Agent, AgentAllocation, AgentProposal, AgentRelationship, AuditLog, ChatMessage, ExecutionRecord, MarketQuote, NewsEvent, PaperOrder, Position, RiskDecision, TradingSignal, WalletAccount, WalletTransaction
from .schemas import AgentOut, AgentProposalOut, AllocationUpdate, ChatRequest, ChatResponse, ChildAgentCreate, ExecutionRecordOut, MarketChartOut, MarketHistory, MarketMarker, MarketPoint, PaperOrderCreate, PaperOrderOut, PositionOut, PixDepositIntentCreate, PixDepositIntentOut, PixWithdrawalIntentCreate, PixWithdrawalIntentOut, RiskDecisionOut, TradingSignalCreate, TradingSignalOut, WalletOut, WalletTransactionOut
from .services.ai_service import AIService
from .providers.market_data import ProviderNotConfigured, ProviderUnavailable, get_market_provider
from .seed import seed_agents
from .services.paper_broker import PaperExecutionError, execute_order
from .providers.macro import BancoCentralSGSProvider
from .providers.ibge import IBGESIDRAProvider
from .providers.cvm_provider import CVMProvider
from .news_provider import get_news_provider
from .providers.events.event_classifier import classify
from .providers.events.official_sources import OFFICIAL_SOURCES
from .broker.registry import get_mt5_broker
from .services.execution_engine import ExecutionEngine

Base.metadata.create_all(bind=engine)
with next(get_db()) as db:
    seed_agents(db)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","), allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "trading_mode": settings.trading_mode, "market_provider": settings.market_data_provider}


@app.get("/api/integrations/status")
def integration_status() -> list[dict[str, str]]:
    market_configured = settings.market_data_provider == "brapi" or bool(settings.market_data_api_token or settings.market_data_api_key)
    return [
        {"name": "brapi.dev / Dados de Mercado", "status": "CONFIGURED" if market_configured else "NOT_CONFIGURED", "scope": "market"},
        {"name": "Banco Central SGS", "status": "PUBLIC_ADAPTER", "scope": "macro"},
        {"name": "IBGE SIDRA", "status": "PUBLIC_ADAPTER", "scope": "macro"},
        {"name": "CVM Dados Abertos", "status": "PUBLIC_CATALOG", "scope": "events"},
        {"name": "Open Finance", "status": "NOT_CONFIGURED", "scope": "finance"},
        {"name": "B3 licenciada", "status": "DISABLED", "scope": "market"},
        {"name": "MetaTrader 5 / Rico", "status": "PAPER_OPTIONAL", "scope": "broker"},
    ]


@app.get("/api/broker/connection")
def broker_connection() -> dict[str, object]:
    """Return safe MT5 connectivity state; never returns credentials."""
    return get_mt5_broker().status()


@app.get("/api/news/status")
def news_status() -> dict[str, object]:
    configured = settings.news_provider.casefold() == "rss" or bool(settings.news_api_key and settings.news_provider != "unconfigured")
    return {"configured": configured, "provider": settings.news_provider if configured else "unconfigured", "poll_interval_seconds": settings.news_poll_interval_seconds, "official_sources": len(OFFICIAL_SOURCES), "message": "Atualização automática disponível após configurar um provedor autorizado." if configured else "Nenhum provedor autorizado configurado; o sistema não inventa notícias."}


@app.get("/api/news/sources")
def news_sources() -> list[dict[str, str]]:
    return OFFICIAL_SOURCES


@app.get("/api/news/events")
def news_events(limit: int = 50, db: Session = Depends(get_db)) -> list[dict[str, object]]:
    bounded_limit = min(max(limit, 1), 200)
    rows = list(db.scalars(select(NewsEvent).order_by(NewsEvent.published_at.desc(), NewsEvent.collected_at.desc()).limit(bounded_limit)))
    return [{"id": row.id, "title": row.title, "summary": row.summary, "source": row.source, "source_url": row.source_url, "published_at": row.published_at.isoformat() if row.published_at else None, "event_type": row.event_type, "confirmation_status": row.confirmation_status, "confidence": row.confidence, "impact_status": "SCENARIO_ONLY"} for row in rows]


@app.post("/api/news/sync")
def sync_news(request: Request, db: Session = Depends(get_db)) -> dict[str, object]:
    try:
        articles = get_news_provider().search("bolsa OR economia OR política OR guerra OR desastre OR juros")
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    inserted = 0
    for article in articles:
        title = str(article.get("title", "")).strip()
        url = str(article.get("url", "")).strip()
        if not title or not url or db.scalar(select(NewsEvent).where(NewsEvent.source_url == url)):
            continue
        published = article.get("publishedAt")
        if published:
            try:
                published_at = datetime.fromisoformat(str(published).replace("Z", "+00:00"))
            except ValueError:
                published_at = parsedate_to_datetime(str(published))
        else:
            published_at = None
        source_name = str((article.get("source") or {}).get("name") or "Provedor autorizado")
        db.add(NewsEvent(title=title, summary=article.get("description"), source=source_name, source_url=url, published_at=published_at, event_type=classify(title), confirmation_status="UNCONFIRMED", confidence=None))
        inserted += 1
    db.add(AuditLog(action="NEWS_SYNC", actor="system", request_id=request.state.request_id, result="COMPLETED"))
    db.commit()
    return {"status": "AVAILABLE", "inserted": inserted, "total_received": len(articles), "message": "Eventos armazenados com fonte e horário; impacto permanece como cenário para análise."}


@app.get("/api/sources/cvm")
def cvm_sources() -> list[dict[str, str]]:
    return CVMProvider().available_datasets()


@app.get("/api/macro/bcb/{code}")
def bcb_series(code: int, start: date | None = None, end: date | None = None) -> dict:
    start_date = start or (date.today() - timedelta(days=30))
    end_date = end or date.today()
    if start_date > end_date or (end_date - start_date).days > 3660:
        raise HTTPException(422, "Intervalo inválido; use no máximo dez anos")
    try:
        records = BancoCentralSGSProvider().get_series(code, start_date, end_date)
    except RuntimeError as exc:
        return {"code": code, "status": "UNAVAILABLE", "source": "Banco Central SGS", "data": [], "message": str(exc)}
    return {"code": code, "status": "AVAILABLE", "source": records[0].source if records else "Banco Central SGS", "source_url": records[0].source_url if records else "", "data": [{"date": row.reference_date.isoformat(), "value": row.value} for row in records]}


@app.get("/api/macro/ibge/{table}/{variable}/{period}")
def ibge_values(table: str, variable: str, period: str) -> dict:
    if not all(part.replace("-", "").isalnum() for part in (table, variable, period)):
        raise HTTPException(422, "Parâmetros SIDRA inválidos")
    try:
        values = IBGESIDRAProvider().get_values(table, variable, period)
    except RuntimeError as exc:
        return {"status": "UNAVAILABLE", "source": "IBGE SIDRA", "data": [], "message": str(exc)}
    return {"status": "AVAILABLE", "source": "IBGE SIDRA", "data": values}


@app.get("/api/audit/logs")
def audit_logs(limit: int = 50, db: Session = Depends(get_db)) -> list[dict[str, str | None]]:
    bounded_limit = min(max(limit, 1), 200)
    rows = list(db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(bounded_limit)))
    return [{"action": row.action, "actor": row.actor, "request_id": row.request_id, "result": row.result, "created_at": row.created_at.isoformat()} for row in rows]


@app.get("/api/agents", response_model=list[AgentOut])
def list_agents(db: Session = Depends(get_db)) -> list[Agent]:
    return list(db.scalars(select(Agent).where(Agent.status == "ACTIVE").order_by(Agent.id)))


@app.get("/api/agents/archived", response_model=list[AgentOut])
def archived_agents(db: Session = Depends(get_db)) -> list[Agent]:
    return list(db.scalars(select(Agent).where(Agent.status == "ARCHIVED").order_by(Agent.id)))


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


@app.post("/api/agents/{parent_id}/proposals", response_model=AgentProposalOut, status_code=201)
def propose_child_agent(parent_id: int, payload: ChildAgentCreate, db: Session = Depends(get_db)) -> AgentProposal:
    parent = db.get(Agent, parent_id)
    if parent is None:
        raise HTTPException(404, "Parent agent not found")
    if parent.generation >= 3:
        raise HTTPException(400, "Maximum agent generation reached")
    if not payload.reason.strip() or not payload.objective.strip():
        raise HTTPException(422, "Reason and objective are required")
    proposal = AgentProposal(parent_agent_id=parent.id, name=payload.name.strip(), role=payload.role.strip(), specialization=payload.specialization.strip(), objective=payload.objective.strip(), reason=payload.reason.strip(), risk_level=payload.risk_level.upper())
    db.add(proposal)
    db.add(AuditLog(action="AGENT_PROPOSAL_CREATED", actor="operator", result="PENDING"))
    db.commit()
    db.refresh(proposal)
    return proposal


@app.get("/api/agents/proposals", response_model=list[AgentProposalOut])
def list_agent_proposals(db: Session = Depends(get_db)) -> list[AgentProposal]:
    return list(db.scalars(select(AgentProposal).order_by(AgentProposal.created_at.desc())))


@app.post("/api/agents/proposals/{proposal_id}/approve", response_model=AgentOut)
def approve_agent_proposal(proposal_id: int, request: Request, db: Session = Depends(get_db)) -> Agent:
    proposal = db.get(AgentProposal, proposal_id)
    if proposal is None:
        raise HTTPException(404, "Proposal not found")
    if proposal.status != "PENDING":
        raise HTTPException(409, "Proposal already decided")
    unique_id = "AGENT_" + proposal.name.upper().replace(" ", "_")
    if db.scalar(select(Agent).where(Agent.unique_id == unique_id)):
        raise HTTPException(409, "Agent already exists")
    parent = db.get(Agent, proposal.parent_agent_id)
    if parent is None:
        raise HTTPException(409, "Parent agent no longer exists")
    child = Agent(unique_id=unique_id, name=proposal.name, role=proposal.role, specialization=proposal.specialization, parent_agent_id=parent.id, generation=parent.generation + 1, status="EXPERIMENTAL", risk_level=proposal.risk_level)
    db.add(child)
    db.flush()
    db.add(AgentRelationship(parent_agent_id=parent.id, child_agent_id=child.id, reason=proposal.reason, objective=proposal.objective))
    proposal.status = "APPROVED"
    proposal.decided_at = datetime.now(timezone.utc)
    db.add(AuditLog(action="AGENT_PROPOSAL_APPROVED", actor="operator", request_id=request.state.request_id, result="APPROVED"))
    db.commit()
    db.refresh(child)
    return child


@app.get("/api/market/history", response_model=MarketHistory)
def market_history() -> MarketHistory:
    try:
        records = get_market_provider().get_history("IBOV", date.today() - timedelta(days=30), date.today())
        return MarketHistory(source=records[0].source, is_demo=False, data_status="Dado histórico", points=[MarketPoint(date=record.source_timestamp.date().isoformat(), value=record.value) for record in records])
    except ProviderNotConfigured:
        return MarketHistory(source="", is_demo=False, data_status="Integração ainda não configurada.", points=[])
    except ProviderUnavailable as exc:
        return MarketHistory(source="", is_demo=False, data_status=str(exc), points=[])


@app.get("/api/market/chart/{symbol}", response_model=MarketChartOut)
def market_chart(symbol: str, days: int = 365, db: Session = Depends(get_db)) -> MarketChartOut:
    normalized = symbol.upper().strip()
    bounded_days = min(max(days, 1), 3650)
    try:
        records = get_market_provider().get_history(normalized, date.today() - timedelta(days=bounded_days), date.today())
        points = [MarketPoint(date=record.source_timestamp.isoformat(), value=record.value) for record in records]
        source = records[0].source if records else ""
        delayed = any(record.delayed for record in records)
    except ProviderNotConfigured:
        return MarketChartOut(symbol=normalized, source="", data_status="Integração ainda não configurada.", delayed=False, points=[], markers=[])
    except ProviderUnavailable as exc:
        return MarketChartOut(symbol=normalized, source="", data_status=str(exc), delayed=False, points=[], markers=[])
    orders = list(db.scalars(select(PaperOrder).where(PaperOrder.symbol == normalized).order_by(PaperOrder.created_at)))
    markers: list[MarketMarker] = []
    for order in orders:
        marker_value = order.filled_price or order.limit_price
        if marker_value is None:
            continue
        kind = f"{order.side}_{'EXECUTED' if order.status == 'FILLED' else 'PENDING'}"
        label = "Compra executada" if order.side == "BUY" and order.status == "FILLED" else "Venda executada" if order.side == "SELL" and order.status == "FILLED" else "Compra planejada" if order.side == "BUY" else "Venda planejada"
        marker_date = (order.executed_at or order.created_at).isoformat()
        markers.append(MarketMarker(kind=kind, date=marker_date, value=float(marker_value), label=label, status=order.status))
    return MarketChartOut(symbol=normalized, source=source, data_status="Histórico recebido do provedor", delayed=delayed, points=points, markers=markers)


@app.get("/api/portfolio/positions", response_model=list[PositionOut])
def portfolio_positions(db: Session = Depends(get_db)) -> list[PositionOut]:
    positions = list(db.scalars(select(Position).order_by(Position.symbol)))
    return [PositionOut(symbol=p.symbol, quantity=p.quantity, average_price=p.average_price, current_price=p.current_price, invested_value=round(p.quantity * p.average_price, 2), current_value=round(p.quantity * p.current_price, 2), unrealized_pnl=round(p.quantity * (p.current_price - p.average_price), 2), mode="PAPER") for p in positions]


def get_or_create_aurion_wallet(db: Session) -> tuple[Agent, WalletAccount]:
    aurion = db.scalar(select(Agent).where(Agent.unique_id == "AURION"))
    if aurion is None:
        raise HTTPException(503, "Aurion ainda não foi inicializada")
    wallet = db.scalar(select(WalletAccount).where(WalletAccount.agent_id == aurion.id))
    if wallet is None:
        wallet = WalletAccount(agent_id=aurion.id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return aurion, wallet


@app.get("/api/wallet/ecosystem", response_model=WalletOut)
@app.get("/api/wallet/aurion", response_model=WalletOut)
def ecosystem_wallet(db: Session = Depends(get_db)) -> WalletOut:
    aurion, wallet = get_or_create_aurion_wallet(db)
    transactions = list(db.scalars(select(WalletTransaction).where(WalletTransaction.wallet_id == wallet.id).order_by(WalletTransaction.created_at.desc()).limit(30)))
    return WalletOut(agent_unique_id="AETERNUM_ECOSYSTEM", agent_name="Carteira do ecossistema", currency=wallet.currency, balance=float(wallet.balance or 0), status=wallet.status, pix_status="NOT_CONFIGURED", transactions=[WalletTransactionOut(id=row.id, direction=row.direction, amount=float(row.amount), status=row.status, method=row.method, description=row.description, created_at=row.created_at) for row in transactions])


@app.post("/api/wallet/aurion/deposit-intents", response_model=PixDepositIntentOut, status_code=201)
def create_pix_deposit_intent(payload: PixDepositIntentCreate, request: Request, db: Session = Depends(get_db)) -> PixDepositIntentOut:
    if payload.amount <= 0 or payload.amount > 1_000_000:
        raise HTTPException(422, "O valor deve estar entre R$ 0,01 e R$ 1.000.000,00")
    _, wallet = get_or_create_aurion_wallet(db)
    reference = f"PIX_PENDING_{uuid4()}"
    transaction = WalletTransaction(wallet_id=wallet.id, direction="CREDIT", amount=round(payload.amount, 2), status="PENDING_PROVIDER", method="PIX", provider_reference=reference, description="Aguardando confirmação do provedor Pix")
    db.add(transaction)
    db.add(AuditLog(action="PIX_DEPOSIT_INTENT_CREATED", actor="operator", request_id=request.state.request_id, result="PENDING_PROVIDER"))
    db.commit()
    db.refresh(transaction)
    return PixDepositIntentOut(id=transaction.id, amount=float(transaction.amount), status=transaction.status, pix_status="NOT_CONFIGURED", message="Intenção registrada, mas nenhum provedor Pix está conectado. O saldo só será creditado após confirmação por webhook.")


@app.post("/api/wallet/ecosystem/withdrawal-intents", response_model=PixWithdrawalIntentOut, status_code=201)
def create_pix_withdrawal_intent(payload: PixWithdrawalIntentCreate, request: Request, db: Session = Depends(get_db)) -> PixWithdrawalIntentOut:
    if payload.amount <= 0 or payload.amount > 1_000_000:
        raise HTTPException(422, "O valor deve estar entre R$ 0,01 e R$ 1.000.000,00")
    pix_key = payload.pix_key.strip()
    if len(pix_key) < 5 or len(pix_key) > 140:
        raise HTTPException(422, "Informe uma chave Pix válida")
    _, wallet = get_or_create_aurion_wallet(db)
    pending_debits = sum(float(row.amount or 0) for row in db.scalars(select(WalletTransaction).where(WalletTransaction.wallet_id == wallet.id, WalletTransaction.direction == "DEBIT", WalletTransaction.status == "PENDING_PROVIDER")))
    available = float(wallet.balance or 0) - pending_debits
    minimum_reserve = 0.01
    if payload.amount > max(0, available - minimum_reserve):
        raise HTTPException(409, "A retirada ultrapassa o saldo disponível e preservaria a reserva mínima de sobrevivência da carteira")
    reference = f"PIX_WITHDRAWAL_PENDING_{uuid4()}"
    transaction = WalletTransaction(wallet_id=wallet.id, direction="DEBIT", amount=round(payload.amount, 2), status="PENDING_PROVIDER", method="PIX", provider_reference=reference, description="Retirada solicitada; aguardando confirmação do provedor Pix")
    db.add(transaction)
    db.add(AuditLog(action="PIX_WITHDRAWAL_INTENT_CREATED", actor="operator", request_id=request.state.request_id, result="PENDING_PROVIDER"))
    db.commit()
    db.refresh(transaction)
    return PixWithdrawalIntentOut(id=transaction.id, amount=float(transaction.amount), status=transaction.status, pix_status="NOT_CONFIGURED", message="Retirada registrada, mas nenhum provedor Pix está conectado. Nenhum valor foi enviado.")


@app.post("/api/paper/orders", response_model=PaperOrderOut, status_code=201)
def create_paper_order(payload: PaperOrderCreate, request: Request, db: Session = Depends(get_db)) -> PaperOrder:
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
    db.add(AuditLog(action="PAPER_ORDER_CREATED", actor="operator", request_id=request.state.request_id, result="ACCEPTED"))
    db.commit()
    db.refresh(order)
    return order


@app.get("/api/paper/orders", response_model=list[PaperOrderOut])
def list_paper_orders(db: Session = Depends(get_db)) -> list[PaperOrder]:
    return list(db.scalars(select(PaperOrder).order_by(PaperOrder.created_at.desc())))


@app.post("/api/signals", response_model=TradingSignalOut, status_code=201)
def create_signal(payload: TradingSignalCreate, db: Session = Depends(get_db)) -> TradingSignal:
    agent = db.get(Agent, payload.agent_id)
    if agent is None or agent.status != "ACTIVE":
        raise HTTPException(404, "Active agent not found")
    action = payload.action.upper().strip()
    symbol = payload.symbol.upper().strip()
    if action not in {"BUY", "SELL", "HOLD"}:
        raise HTTPException(422, "Action must be BUY, SELL or HOLD")
    if not symbol or len(symbol) > 24 or not payload.reason.strip():
        raise HTTPException(422, "Symbol and reason are required")
    if not 0 <= payload.confidence <= 1:
        raise HTTPException(422, "Confidence must be between 0 and 1")
    if payload.position_size < 0 or (action != "HOLD" and payload.position_size <= 0):
        raise HTTPException(422, "Position size must be positive for BUY/SELL")
    if action != "HOLD" and (payload.stop_loss is None or payload.take_profit is None):
        raise HTTPException(422, "BUY/SELL signals require stop loss and take profit")
    signal = TradingSignal(agent_id=agent.id, symbol=symbol, action=action, confidence=payload.confidence, reason=payload.reason.strip(), risk=payload.risk.upper(), entry_min=payload.entry_min, entry_max=payload.entry_max, stop_loss=payload.stop_loss, take_profit=payload.take_profit, position_size=payload.position_size, expires_at=payload.expires_at, status="RECEIVED")
    db.add(signal)
    db.add(AuditLog(action="SIGNAL_CREATED", actor=agent.unique_id, result="RECEIVED"))
    db.commit()
    db.refresh(signal)
    return signal


@app.get("/api/signals", response_model=list[TradingSignalOut])
def list_signals(limit: int = 50, db: Session = Depends(get_db)) -> list[TradingSignal]:
    bounded_limit = min(max(limit, 1), 200)
    return list(db.scalars(select(TradingSignal).order_by(TradingSignal.created_at.desc()).limit(bounded_limit)))


@app.post("/api/signals/{signal_id}/execute", response_model=ExecutionRecordOut)
def execute_signal(signal_id: int, request: Request, db: Session = Depends(get_db)) -> ExecutionRecord:
    signal = db.get(TradingSignal, signal_id)
    if signal is None:
        raise HTTPException(404, "Signal not found")
    if signal.status not in {"RECEIVED", "BLOCKED_NO_QUOTE", "BLOCKED_RISK"}:
        raise HTTPException(409, "Signal is not available for execution")
    if signal.action == "HOLD":
        raise HTTPException(409, "HOLD signals do not create orders")
    try:
        record = ExecutionEngine().execute(db, signal, request.state.request_id)
        db.commit()
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(503, str(exc)) from exc
    db.refresh(record)
    return record


@app.get("/api/risk/allocations")
def risk_allocations(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    rows = list(db.scalars(select(AgentAllocation).order_by(AgentAllocation.agent_id)))
    return [{"agent_id": row.agent_id, "allocation_percent": float(row.allocation_percent), "max_position_percent": float(row.max_position_percent), "enabled": row.enabled} for row in rows]


@app.put("/api/risk/allocations/{agent_id}")
def update_risk_allocation(agent_id: int, payload: AllocationUpdate, db: Session = Depends(get_db)) -> dict[str, object]:
    if db.get(Agent, agent_id) is None:
        raise HTTPException(404, "Agent not found")
    if not 0 <= payload.allocation_percent <= 100 or not 0 < payload.max_position_percent <= 100:
        raise HTTPException(422, "Allocation limits are invalid")
    others = sum(float(row.allocation_percent) for row in db.scalars(select(AgentAllocation).where(AgentAllocation.agent_id != agent_id)))
    if others + payload.allocation_percent > 100 - settings.risk_reserve_percent:
        raise HTTPException(409, "Allocations must preserve the configured reserve")
    allocation = db.scalar(select(AgentAllocation).where(AgentAllocation.agent_id == agent_id))
    if allocation is None:
        allocation = AgentAllocation(agent_id=agent_id)
        db.add(allocation)
    allocation.allocation_percent = payload.allocation_percent
    allocation.max_position_percent = payload.max_position_percent
    allocation.enabled = payload.enabled
    db.add(AuditLog(action="RISK_ALLOCATION_UPDATED", actor="operator", result="UPDATED"))
    db.commit()
    return {"agent_id": agent_id, "allocation_percent": payload.allocation_percent, "max_position_percent": payload.max_position_percent, "enabled": payload.enabled, "reserve_percent": settings.risk_reserve_percent}


@app.get("/api/executions", response_model=list[ExecutionRecordOut])
def execution_records(limit: int = 50, db: Session = Depends(get_db)) -> list[ExecutionRecord]:
    bounded_limit = min(max(limit, 1), 200)
    return list(db.scalars(select(ExecutionRecord).order_by(ExecutionRecord.created_at.desc()).limit(bounded_limit)))


@app.get("/api/signals/{signal_id}/risk", response_model=RiskDecisionOut | None)
def signal_risk(signal_id: int, db: Session = Depends(get_db)) -> RiskDecision | None:
    return db.scalar(select(RiskDecision).where(RiskDecision.signal_id == signal_id).order_by(RiskDecision.created_at.desc()))


@app.post("/api/paper/orders/{order_id}/execute", response_model=PaperOrderOut)
def execute_paper_order(order_id: int, request: Request, db: Session = Depends(get_db)) -> PaperOrder:
    order = db.get(PaperOrder, order_id)
    if order is None:
        raise HTTPException(404, "PAPER order not found")
    try:
        execute_order(db, order)
    except PaperExecutionError as exc:
        db.rollback()
        raise HTTPException(409, str(exc)) from exc
    db.add(AuditLog(action="PAPER_ORDER_FILLED", actor="operator", request_id=request.state.request_id, result="FILLED"))
    db.commit()
    db.refresh(order)
    return order


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request, db: Session = Depends(get_db)) -> ChatResponse:
    if not payload.message.strip():
        raise HTTPException(422, "A mensagem não pode estar vazia")
    service = AIService(db)
    conversation_id, answer, model = service.respond(payload.message.strip(), payload.conversation_id)
    created_at = datetime.now(timezone.utc)
    db.add(ChatMessage(conversation_id=conversation_id, role="user", content=payload.message.strip(), model=model))
    db.add(ChatMessage(conversation_id=conversation_id, role="assistant", content=answer, model=model))
    db.add(AuditLog(action="AURION_CHAT", actor="operator", request_id=request.state.request_id, result="COMPLETED"))
    db.commit()
    return ChatResponse(conversation_id=conversation_id, message=answer, created_at=created_at, display_time=created_at.astimezone().isoformat(), sources=[], actions=[])


@app.get("/api/market/quote/{symbol}")
def market_quote(symbol: str, db: Session = Depends(get_db)):
    try:
        record = get_market_provider().get_quote(symbol)
        db.add(MarketQuote(provider=record.provider, symbol=record.symbol, value=record.value, source_timestamp=record.source_timestamp, status=record.status, raw_json=json.dumps(record.raw, default=str)))
        db.commit()
        return {"symbol": record.symbol, "value": record.value, "source": record.source, "source_url": record.source_url, "source_timestamp": record.source_timestamp, "collected_at": record.collected_at, "status": record.status, "delayed": record.delayed}
    except (ProviderNotConfigured, ProviderUnavailable) as exc:
        return {"symbol": symbol.upper(), "value": None, "source": "", "source_url": "", "source_timestamp": None, "collected_at": datetime.now(timezone.utc), "status": "UNAVAILABLE", "delayed": False, "message": str(exc)}
