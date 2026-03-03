"""add project passes and quote pass linkage

Revision ID: 20260303_0005
Revises: 20260219_0004
Create Date: 2026-03-03 16:52:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260303_0005'
down_revision = '20260219_0004'
branch_labels = None
depends_on = None


def upgrade():
    """Create project pass model and quote linkage for 30-day pass flow."""
    op.create_table(
        'project_passes',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('address_normalized', sa.String(length=255), nullable=False),
        sa.Column('project_scope_normalized', sa.String(length=120), nullable=False),
        sa.Column('starts_at', sa.DateTime(), nullable=False),
        sa.Column('ends_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('source_payment_id', sa.String(length=36), nullable=True),
        sa.Column('origin_event_run_id', sa.String(length=64), nullable=True),
        sa.Column('upload_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_index('ix_project_passes_user_id', 'project_passes', ['user_id'])
    op.create_index('ix_project_passes_address_normalized', 'project_passes', ['address_normalized'])
    op.create_index('ix_project_passes_project_scope_normalized', 'project_passes', ['project_scope_normalized'])
    op.create_index('ix_project_passes_starts_at', 'project_passes', ['starts_at'])
    op.create_index('ix_project_passes_ends_at', 'project_passes', ['ends_at'])
    op.create_index('ix_project_passes_status', 'project_passes', ['status'])

    op.add_column('quotes', sa.Column('project_pass_id', sa.String(length=36), nullable=True))
    op.add_column('quotes', sa.Column('location_normalized', sa.String(length=255), nullable=True))
    op.add_column('quotes', sa.Column('project_scope_normalized', sa.String(length=120), nullable=True))

    op.create_foreign_key(
        'fk_quotes_project_pass_id',
        'quotes',
        'project_passes',
        ['project_pass_id'],
        ['id'],
        ondelete='SET NULL',
    )

    op.create_index('ix_quotes_project_pass_id', 'quotes', ['project_pass_id'])
    op.create_index('ix_quotes_location_normalized', 'quotes', ['location_normalized'])
    op.create_index('ix_quotes_project_scope_normalized', 'quotes', ['project_scope_normalized'])


def downgrade():
    """Drop project pass model and quote pass linkage."""
    op.drop_index('ix_quotes_project_scope_normalized', table_name='quotes')
    op.drop_index('ix_quotes_location_normalized', table_name='quotes')
    op.drop_index('ix_quotes_project_pass_id', table_name='quotes')
    op.drop_constraint('fk_quotes_project_pass_id', 'quotes', type_='foreignkey')

    op.drop_column('quotes', 'project_scope_normalized')
    op.drop_column('quotes', 'location_normalized')
    op.drop_column('quotes', 'project_pass_id')

    op.drop_index('ix_project_passes_status', table_name='project_passes')
    op.drop_index('ix_project_passes_ends_at', table_name='project_passes')
    op.drop_index('ix_project_passes_starts_at', table_name='project_passes')
    op.drop_index('ix_project_passes_project_scope_normalized', table_name='project_passes')
    op.drop_index('ix_project_passes_address_normalized', table_name='project_passes')
    op.drop_index('ix_project_passes_user_id', table_name='project_passes')

    op.drop_table('project_passes')
