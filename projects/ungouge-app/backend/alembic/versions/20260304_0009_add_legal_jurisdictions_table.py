"""add legal jurisdictions catalog

Revision ID: 20260304_0009
Revises: 20260304_0008
Create Date: 2026-03-04 06:52:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260304_0009'
down_revision = '20260304_0008'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'legal_jurisdictions',
        sa.Column('code', sa.String(length=80), primary_key=True),
        sa.Column('level', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('parent_code', sa.String(length=80), nullable=True),
        sa.Column('state_abbr', sa.String(length=2), nullable=True),
        sa.Column('state_fp', sa.String(length=2), nullable=True),
        sa.Column('county_fp', sa.String(length=3), nullable=True),
        sa.Column('place_fp', sa.String(length=5), nullable=True),
        sa.Column('source_url', sa.String(length=1024), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_legal_jurisdictions_level', 'legal_jurisdictions', ['level'])
    op.create_index('ix_legal_jurisdictions_parent_code', 'legal_jurisdictions', ['parent_code'])
    op.create_index('ix_legal_jurisdictions_state_abbr', 'legal_jurisdictions', ['state_abbr'])
    op.create_index('ix_legal_jurisdictions_state_fp', 'legal_jurisdictions', ['state_fp'])
    op.create_index('ix_legal_jurisdictions_county_fp', 'legal_jurisdictions', ['county_fp'])
    op.create_index('ix_legal_jurisdictions_place_fp', 'legal_jurisdictions', ['place_fp'])
    op.create_index('ix_legal_jurisdictions_active', 'legal_jurisdictions', ['active'])
    op.create_index('ix_legal_jurisdictions_updated_at', 'legal_jurisdictions', ['updated_at'])


def downgrade():
    op.drop_index('ix_legal_jurisdictions_updated_at', table_name='legal_jurisdictions')
    op.drop_index('ix_legal_jurisdictions_active', table_name='legal_jurisdictions')
    op.drop_index('ix_legal_jurisdictions_place_fp', table_name='legal_jurisdictions')
    op.drop_index('ix_legal_jurisdictions_county_fp', table_name='legal_jurisdictions')
    op.drop_index('ix_legal_jurisdictions_state_fp', table_name='legal_jurisdictions')
    op.drop_index('ix_legal_jurisdictions_state_abbr', table_name='legal_jurisdictions')
    op.drop_index('ix_legal_jurisdictions_parent_code', table_name='legal_jurisdictions')
    op.drop_index('ix_legal_jurisdictions_level', table_name='legal_jurisdictions')
    op.drop_table('legal_jurisdictions')
