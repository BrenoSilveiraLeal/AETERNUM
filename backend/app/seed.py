from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Agent


def seed_agents(db: Session) -> None:
    aurion = db.scalar(select(Agent).where(Agent.unique_id == "AURION"))
    if aurion is None:
        aurion = Agent(unique_id="AURION", name="Aurion", role="ORCHESTRATOR", avatar="✦", specialization="Market intelligence & quantitative research")
        db.add(aurion)
        db.flush()
    specialists = [
        ("MACRO", "Macro", "MACRO", "Rates, inflation and economic cycles", "◌", "MEDIUM"),
        ("SENTINEL", "Sentinel", "RISK", "Exposure, liquidity and drawdown", "⬡", "LOW"),
        ("NEWSWEAVER", "Newsweaver", "INTELLIGENCE", "News, events and source confidence", "≋", "LOW"),
        ("QUANT", "Quant", "QUANTITATIVE", "Time series, volatility and backtests", "∿", "MEDIUM"),
        ("GEOPULSE", "Geopulse", "GEOPOLITICAL", "Policy, conflict and sanctions", "⊙", "MEDIUM"),
        ("PORTFOLIO", "Portfolio", "PORTFOLIO", "Diversification and allocation scenarios", "◈", "LOW"),
        ("PAPER_BROKER", "Paper Broker", "SIMULATOR", "Paper execution and reconciliation", "▣", "LOW"),
    ]
    for uid, name, role, specialization, avatar, risk in specialists:
        if db.scalar(select(Agent).where(Agent.unique_id == uid)) is None:
            db.add(Agent(unique_id=uid, name=name, role=role, specialization=specialization, avatar=avatar, parent_agent_id=aurion.id, risk_level=risk))
    db.commit()
