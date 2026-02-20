"""add estimation fields to quotes

Revision ID: 0003
Revises: 0002
Create Date: 2026-02-19

Adds estimation metadata to quotes table (mirroring analysis_reports):
  - is_estimated: Boolean flag for AI-estimated breakdowns
  - estimation_confidence: Confidence level (high/medium/low)
  - estimation_methodology: How the estimation was performed
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add estimation fields to quotes
    with op.batch_alter_table("quotes", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_estimated", sa.Boolean(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("estimation_confidence", sa.String(20), nullable=True))
        batch_op.add_column(sa.Column("estimation_methodology", sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove estimation fields from quotes
    with op.batch_alter_table("quotes", schema=None) as batch_op:
        batch_op.drop_column("estimation_methodology")
        batch_op.drop_column("estimation_confidence")
        batch_op.drop_column("is_estimated")
