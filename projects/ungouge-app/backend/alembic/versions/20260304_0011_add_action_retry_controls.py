"""add retry and dead-letter controls to event actions

Revision ID: 20260304_0011
Revises: 20260304_0010
Create Date: 2026-03-04 10:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260304_0011'
down_revision = '20260304_0010'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('event_run_actions', sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('event_run_actions', sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='3'))
    op.add_column('event_run_actions', sa.Column('dead_lettered', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.create_index('ix_event_run_actions_dead_lettered', 'event_run_actions', ['dead_lettered'])


def downgrade():
    op.drop_index('ix_event_run_actions_dead_lettered', table_name='event_run_actions')
    op.drop_column('event_run_actions', 'dead_lettered')
    op.drop_column('event_run_actions', 'max_attempts')
    op.drop_column('event_run_actions', 'attempt_count')
