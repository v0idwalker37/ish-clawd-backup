"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-02-13

Captures all existing tables:
  - users
  - quotes
  - quote_line_items
  - analysis_reports
  - payments
  - refresh_tokens
  - password_reset_tokens
  - email_verification_tokens
  - token_blacklist
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ──────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        # MFA fields
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("mfa_code", sa.String(128), nullable=True),
        sa.Column("mfa_code_expires", sa.DateTime(), nullable=True),
        sa.Column("mfa_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mfa_locked_until", sa.DateTime(), nullable=True),
        # GDPR fields
        sa.Column("is_restricted", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("privacy_preferences", sa.JSON(), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_is_active", "users", ["is_active"])
    op.create_index("ix_users_is_verified", "users", ["is_verified"])
    op.create_index("ix_users_created_at", "users", ["created_at"])

    # ── quotes ─────────────────────────────────────────────────────────────
    op.create_table(
        "quotes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("project_type", sa.String(100), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("contractor_name", sa.String(255), nullable=True),
        sa.Column("payment_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_quotes_user_id", "quotes", ["user_id"])
    op.create_index("ix_quotes_payment_status", "quotes", ["payment_status"])
    op.create_index("ix_quotes_created_at", "quotes", ["created_at"])

    # ── quote_line_items ───────────────────────────────────────────────────
    op.create_table(
        "quote_line_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("quote_id", sa.String(36), sa.ForeignKey("quotes.id"), nullable=False),
        sa.Column("item_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quoted_price", sa.Float(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit", sa.String(50), nullable=False, server_default="'item'"),
    )
    op.create_index("ix_quote_line_items_quote_id", "quote_line_items", ["quote_id"])

    # ── analysis_reports ───────────────────────────────────────────────────
    op.create_table(
        "analysis_reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("quote_id", sa.String(36), sa.ForeignKey("quotes.id"), unique=True, nullable=False),
        sa.Column("total_quoted", sa.Float(), nullable=False),
        sa.Column("total_fair_low", sa.Float(), nullable=False),
        sa.Column("total_fair_high", sa.Float(), nullable=False),
        sa.Column("overall_assessment", sa.Text(), nullable=False),
        sa.Column("line_items_analysis", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_analysis_reports_created_at", "analysis_reports", ["created_at"])

    # ── payments ───────────────────────────────────────────────────────────
    op.create_table(
        "payments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("quote_id", sa.String(36), sa.ForeignKey("quotes.id"), nullable=False),
        sa.Column("stripe_payment_intent_id", sa.String(255), unique=True, nullable=False),
        sa.Column("stripe_session_id", sa.String(255), unique=True, nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="'usd'"),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_payments_quote_id", "payments", ["quote_id"])
    op.create_index("ix_payments_stripe_session_id", "payments", ["stripe_session_id"], unique=True)
    op.create_index("ix_payments_status", "payments", ["status"])

    # ── refresh_tokens ─────────────────────────────────────────────────────
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)
    op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"])

    # ── password_reset_tokens ──────────────────────────────────────────────
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token", sa.String(255), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
    op.create_index("ix_password_reset_tokens_token", "password_reset_tokens", ["token"], unique=True)
    op.create_index("ix_password_reset_tokens_expires_at", "password_reset_tokens", ["expires_at"])

    # ── email_verification_tokens ──────────────────────────────────────────
    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token", sa.String(255), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_email_verification_tokens_user_id", "email_verification_tokens", ["user_id"])
    op.create_index("ix_email_verification_tokens_token", "email_verification_tokens", ["token"], unique=True)
    op.create_index("ix_email_verification_tokens_expires_at", "email_verification_tokens", ["expires_at"])

    # ── token_blacklist ────────────────────────────────────────────────────
    op.create_table(
        "token_blacklist",
        sa.Column("token", sa.String(512), primary_key=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("blacklisted_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_token_blacklist_expires_at", "token_blacklist", ["expires_at"])


def downgrade() -> None:
    op.drop_table("token_blacklist")
    op.drop_table("email_verification_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("payments")
    op.drop_table("analysis_reports")
    op.drop_table("quote_line_items")
    op.drop_table("quotes")
    op.drop_table("users")
