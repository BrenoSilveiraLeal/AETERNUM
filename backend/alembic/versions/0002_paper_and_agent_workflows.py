"""Add paper execution and agent proposal workflow."""
from alembic import op
import sqlalchemy as sa

revision = "0002_paper_and_agent_workflows"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("paper_orders", sa.Column("filled_price", sa.Float(), nullable=True))
    op.add_column("paper_orders", sa.Column("executed_at", sa.DateTime(), nullable=True))
    op.create_table(
        "agent_proposals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("parent_agent_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("role", sa.String(length=80), nullable=False),
        sa.Column("specialization", sa.String(length=160), nullable=False),
        sa.Column("objective", sa.String(length=500), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=False, server_default="LOW"),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("decided_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_agent_proposals_parent_agent_id", "agent_proposals", ["parent_agent_id"])


def downgrade():
    op.drop_index("ix_agent_proposals_parent_agent_id", table_name="agent_proposals")
    op.drop_table("agent_proposals")
    op.drop_column("paper_orders", "executed_at")
    op.drop_column("paper_orders", "filled_price")
