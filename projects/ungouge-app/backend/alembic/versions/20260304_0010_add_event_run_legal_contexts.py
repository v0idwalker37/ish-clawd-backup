"""add event run legal context snapshots

Revision ID: 20260304_0010
Revises: 20260304_0009
Create Date: 2026-03-04 08:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260304_0010'
down_revision = '20260304_0009'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'event_run_legal_contexts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('event_run_id', sa.String(length=36), sa.ForeignKey('event_runs.id'), nullable=False),
        sa.Column('jurisdiction_codes', sa.JSON(), nullable=True),
        sa.Column('rule_counts', sa.JSON(), nullable=True),
        sa.Column('citation_document_ids', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_event_run_legal_contexts_event_run_id', 'event_run_legal_contexts', ['event_run_id'])
    op.create_index('ix_event_run_legal_contexts_created_at', 'event_run_legal_contexts', ['created_at'])


def downgrade():
    op.drop_index('ix_event_run_legal_contexts_created_at', table_name='event_run_legal_contexts')
    op.drop_index('ix_event_run_legal_contexts_event_run_id', table_name='event_run_legal_contexts')
    op.drop_table('event_run_legal_contexts')
