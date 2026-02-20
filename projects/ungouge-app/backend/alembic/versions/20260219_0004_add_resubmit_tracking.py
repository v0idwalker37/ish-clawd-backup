"""add resubmit tracking fields

Revision ID: 20260219_0004
Revises: 20260219_0003
Create Date: 2026-02-19 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '20260219_0004'
down_revision = '20260219_0003'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add fields to track free resubmit eligibility for total-only quotes.
    
    Free Resubmit Policy:
    - If a user gets a total-only quote analyzed, they can resubmit
      for free within 90 days if they get an itemized version
    - Tracks: original_quote_id (what was this a resubmit of?) and
      resubmit_eligible_until (when does the free resubmit window close?)
    """
    # Add original_quote_id to track resubmits
    op.add_column('quotes', sa.Column(
        'original_quote_id',
        sa.String(length=36),
        nullable=True,
        comment='ID of original quote if this is a free resubmit'
    ))
    
    # Add resubmit_eligible_until to track eligibility window
    op.add_column('quotes', sa.Column(
        'resubmit_eligible_until',
        sa.DateTime,
        nullable=True,
        comment='End date for free resubmit eligibility (90 days from original)'
    ))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_quotes_original_quote',
        'quotes',
        'quotes',
        ['original_quote_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Create index for efficient resubmit lookups
    op.create_index(
        'idx_quotes_original_quote_id',
        'quotes',
        ['original_quote_id']
    )


def downgrade():
    """Remove resubmit tracking fields."""
    op.drop_index('idx_quotes_original_quote_id', table_name='quotes')
    op.drop_constraint('fk_quotes_original_quote', 'quotes', type_='foreignkey')
    op.drop_column('quotes', 'resubmit_eligible_until')
    op.drop_column('quotes', 'original_quote_id')
