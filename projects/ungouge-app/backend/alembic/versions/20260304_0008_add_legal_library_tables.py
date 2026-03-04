"""add legal library tables

Revision ID: 20260304_0008
Revises: 20260303_0007
Create Date: 2026-03-04 06:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260304_0008'
down_revision = '20260303_0007'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'legal_documents',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('jurisdiction_level', sa.String(length=20), nullable=False),
        sa.Column('jurisdiction_code', sa.String(length=80), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('source_type', sa.String(length=40), nullable=False),
        sa.Column('source_url', sa.String(length=1024), nullable=True),
        sa.Column('citation_text', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('effective_at', sa.DateTime(), nullable=True),
        sa.Column('superseded_at', sa.DateTime(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('checksum', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_legal_documents_jurisdiction_level', 'legal_documents', ['jurisdiction_level'])
    op.create_index('ix_legal_documents_jurisdiction_code', 'legal_documents', ['jurisdiction_code'])
    op.create_index('ix_legal_documents_source_type', 'legal_documents', ['source_type'])
    op.create_index('ix_legal_documents_effective_at', 'legal_documents', ['effective_at'])
    op.create_index('ix_legal_documents_superseded_at', 'legal_documents', ['superseded_at'])
    op.create_index('ix_legal_documents_active', 'legal_documents', ['active'])
    op.create_index('ix_legal_documents_checksum', 'legal_documents', ['checksum'])
    op.create_index('ix_legal_documents_created_at', 'legal_documents', ['created_at'])

    op.create_table(
        'legal_rules',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('legal_documents.id'), nullable=False),
        sa.Column('rule_key', sa.String(length=120), nullable=False),
        sa.Column('artifact_types', sa.JSON(), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('action', sa.String(length=20), nullable=False, server_default='escalate'),
        sa.Column('pattern_type', sa.String(length=20), nullable=False, server_default='regex'),
        sa.Column('pattern_value', sa.Text(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('required_disclaimer', sa.Text(), nullable=True),
        sa.Column('examples', sa.JSON(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_legal_rules_document_id', 'legal_rules', ['document_id'])
    op.create_index('ix_legal_rules_rule_key', 'legal_rules', ['rule_key'])
    op.create_index('ix_legal_rules_risk_level', 'legal_rules', ['risk_level'])
    op.create_index('ix_legal_rules_action', 'legal_rules', ['action'])
    op.create_index('ix_legal_rules_active', 'legal_rules', ['active'])
    op.create_index('ix_legal_rules_created_at', 'legal_rules', ['created_at'])


def downgrade():
    op.drop_index('ix_legal_rules_created_at', table_name='legal_rules')
    op.drop_index('ix_legal_rules_active', table_name='legal_rules')
    op.drop_index('ix_legal_rules_action', table_name='legal_rules')
    op.drop_index('ix_legal_rules_risk_level', table_name='legal_rules')
    op.drop_index('ix_legal_rules_rule_key', table_name='legal_rules')
    op.drop_index('ix_legal_rules_document_id', table_name='legal_rules')
    op.drop_table('legal_rules')

    op.drop_index('ix_legal_documents_created_at', table_name='legal_documents')
    op.drop_index('ix_legal_documents_checksum', table_name='legal_documents')
    op.drop_index('ix_legal_documents_active', table_name='legal_documents')
    op.drop_index('ix_legal_documents_superseded_at', table_name='legal_documents')
    op.drop_index('ix_legal_documents_effective_at', table_name='legal_documents')
    op.drop_index('ix_legal_documents_source_type', table_name='legal_documents')
    op.drop_index('ix_legal_documents_jurisdiction_code', table_name='legal_documents')
    op.drop_index('ix_legal_documents_jurisdiction_level', table_name='legal_documents')
    op.drop_table('legal_documents')
