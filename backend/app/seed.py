from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Agent


def seed_agents(db: Session) -> None:
    aurion = db.scalar(select(Agent).where(Agent.unique_id == "AURION"))
    if aurion is None:
        aurion = Agent(unique_id="AURION", name="Aurion", role="ORCHESTRATOR", avatar="✦", specialization="Market intelligence & quantitative research")
        db.add(aurion)
        db.flush()
    aurion.status = "ACTIVE"
    for old_agent in db.scalars(select(Agent).where(Agent.unique_id != "AURION")):
        old_agent.status = "ARCHIVED"
    db.commit()
