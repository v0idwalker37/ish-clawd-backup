"""add weather intelligence core tables

Revision ID: 20260303_0006
Revises: 20260303_0005
Create Date: 2026-03-03 17:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260303_0006'
down_revision = '20260303_0005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'weather_raw_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('provider', sa.String(length=40), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('event_name', sa.String(length=255), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('fetched_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_weather_raw_events_provider', 'weather_raw_events', ['provider'])
    op.create_index('ix_weather_raw_events_external_id', 'weather_raw_events', ['external_id'])
    op.create_index('ix_weather_raw_events_fetched_at', 'weather_raw_events', ['fetched_at'])

    op.create_table(
        'weather_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('hazard_family', sa.String(length=40), nullable=False),
        sa.Column('hazard_type', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=24), nullable=False, server_default='CANDIDATE'),
        sa.Column('qualification_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('score_breakdown', sa.JSON(), nullable=True),
        sa.Column('county_fips', sa.JSON(), nullable=True),
        sa.Column('geo_confidence', sa.Float(), nullable=True),
        sa.Column('source_ref_ids', sa.JSON(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('effective_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_weather_events_hazard_family', 'weather_events', ['hazard_family'])
    op.create_index('ix_weather_events_status', 'weather_events', ['status'])
    op.create_index('ix_weather_events_qualification_score', 'weather_events', ['qualification_score'])
    op.create_index('ix_weather_events_detected_at', 'weather_events', ['detected_at'])
    op.create_index('ix_weather_events_expires_at', 'weather_events', ['expires_at'])

    op.create_table(
        'event_runs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('weather_event_id', sa.String(length=36), sa.ForeignKey('weather_events.id'), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='DETECTED'),
        sa.Column('geo_scope_key', sa.String(length=120), nullable=False),
        sa.Column('canonical_slug', sa.String(length=255), nullable=True),
        sa.Column('run_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_event_runs_weather_event_id', 'event_runs', ['weather_event_id'])
    op.create_index('ix_event_runs_status', 'event_runs', ['status'])
    op.create_index('ix_event_runs_geo_scope_key', 'event_runs', ['geo_scope_key'])
    op.create_index('ix_event_runs_canonical_slug', 'event_runs', ['canonical_slug'])
    op.create_index('ix_event_runs_created_at', 'event_runs', ['created_at'])

    op.create_table(
        'legal_gate_audits',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('artifact_type', sa.String(length=40), nullable=False),
        sa.Column('artifact_id', sa.String(length=64), nullable=False),
        sa.Column('decision', sa.String(length=24), nullable=False),
        sa.Column('reasons', sa.JSON(), nullable=True),
        sa.Column('policy_pack_version', sa.String(length=40), nullable=False, server_default='legal-v1'),
        sa.Column('content_hash_before', sa.String(length=128), nullable=True),
        sa.Column('content_hash_after', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_legal_gate_audits_artifact_type', 'legal_gate_audits', ['artifact_type'])
    op.create_index('ix_legal_gate_audits_artifact_id', 'legal_gate_audits', ['artifact_id'])
    op.create_index('ix_legal_gate_audits_decision', 'legal_gate_audits', ['decision'])
    op.create_index('ix_legal_gate_audits_created_at', 'legal_gate_audits', ['created_at'])


def downgrade():
    op.drop_index('ix_legal_gate_audits_created_at', table_name='legal_gate_audits')
    op.drop_index('ix_legal_gate_audits_decision', table_name='legal_gate_audits')
    op.drop_index('ix_legal_gate_audits_artifact_id', table_name='legal_gate_audits')
    op.drop_index('ix_legal_gate_audits_artifact_type', table_name='legal_gate_audits')
    op.drop_table('legal_gate_audits')

    op.drop_index('ix_event_runs_created_at', table_name='event_runs')
    op.drop_index('ix_event_runs_canonical_slug', table_name='event_runs')
    op.drop_index('ix_event_runs_geo_scope_key', table_name='event_runs')
    op.drop_index('ix_event_runs_status', table_name='event_runs')
    op.drop_index('ix_event_runs_weather_event_id', table_name='event_runs')
    op.drop_table('event_runs')

    op.drop_index('ix_weather_events_expires_at', table_name='weather_events')
    op.drop_index('ix_weather_events_detected_at', table_name='weather_events')
    op.drop_index('ix_weather_events_qualification_score', table_name='weather_events')
    op.drop_index('ix_weather_events_status', table_name='weather_events')
    op.drop_index('ix_weather_events_hazard_family', table_name='weather_events')
    op.drop_table('weather_events')

    op.drop_index('ix_weather_raw_events_fetched_at', table_name='weather_raw_events')
    op.drop_index('ix_weather_raw_events_external_id', table_name='weather_raw_events')
    op.drop_index('ix_weather_raw_events_provider', table_name='weather_raw_events')
    op.drop_table('weather_raw_events')
