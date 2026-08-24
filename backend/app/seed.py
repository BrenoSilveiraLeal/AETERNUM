from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Agent, AgentAllocation


def seed_agents(db: Session) -> None:
    aurion = db.scalar(select(Agent).where(Agent.unique_id == "AURION"))
    if aurion is None:
        aurion = Agent(unique_id="AURION", name="Aurion", role="ORCHESTRATOR", avatar="✦", specialization="Market intelligence & quantitative research")
        db.add(aurion)
        db.flush()
    aurion.status = "ACTIVE"
    allocation = db.scalar(select(AgentAllocation).where(AgentAllocation.agent_id == aurion.id))
    if allocation is None:
        db.add(AgentAllocation(agent_id=aurion.id, allocation_percent=40, max_position_percent=10, enabled=True))
    for old_agent in db.scalars(select(Agent).where(Agent.unique_id != "AURION")):
        old_agent.status = "ARCHIVED"
    db.commit()
