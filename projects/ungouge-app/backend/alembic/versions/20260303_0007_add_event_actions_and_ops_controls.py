"""add event action queue and ops controls

Revision ID: 20260303_0007
Revises: 20260303_0006
Create Date: 2026-03-03 17:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260303_0007'
down_revision = '20260303_0006'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'event_run_actions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('event_run_id', sa.String(length=36), sa.ForeignKey('event_runs.id'), nullable=False),
        sa.Column('action_type', sa.String(length=40), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='queued'),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('idempotency_key', sa.String(length=128), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_event_run_actions_event_run_id', 'event_run_actions', ['event_run_id'])
    op.create_index('ix_event_run_actions_action_type', 'event_run_actions', ['action_type'])
    op.create_index('ix_event_run_actions_status', 'event_run_actions', ['status'])
    op.create_index('ix_event_run_actions_created_at', 'event_run_actions', ['created_at'])
    op.create_index('ix_event_run_actions_idempotency_key', 'event_run_actions', ['idempotency_key'])

    op.create_table(
        'ops_controls',
        sa.Column('key', sa.String(length=80), primary_key=True),
        sa.Column('value_json', sa.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table('ops_controls')

    op.drop_index('ix_event_run_actions_idempotency_key', table_name='event_run_actions')
    op.drop_index('ix_event_run_actions_created_at', table_name='event_run_actions')
    op.drop_index('ix_event_run_actions_status', table_name='event_run_actions')
    op.drop_index('ix_event_run_actions_action_type', table_name='event_run_actions')
    op.drop_index('ix_event_run_actions_event_run_id', table_name='event_run_actions')
    op.drop_table('event_run_actions')
