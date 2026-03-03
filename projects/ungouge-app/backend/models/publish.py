from pydantic import BaseModel, Field
from typing import Optional, List


class PublishArtifactRequest(BaseModel):
    """Internal publish-gateway request requiring legal compliance token."""

    artifact_type: str = Field(..., description="promo_page | pr | ad | report")
    artifact_id: str = Field(..., description="Stable artifact id")
    content_hash: str = Field(..., description="SHA-256 hash of artifact content")
    compliance_token: str = Field(..., description="Signed compliance token")
    channel: str = Field(..., description="publish channel, e.g. cms|ads|pr")


class LegalTokenIssueRequest(BaseModel):
    """Issue a publish token only after gate decision."""

    artifact_type: str
    artifact_id: str
    content_hash: str
    decision: str = Field(..., description="PASS | PASS_WITH_EDIT | ESCALATE | REJECT")
    reasons: Optional[List[str]] = None
    policy_pack_version: str = "legal-v1"


class ActionEnqueueRequest(BaseModel):
    action_type: str
    payload: Optional[dict] = None
    idempotency_key: Optional[str] = None


class KillSwitchRequest(BaseModel):
    enabled: bool
    reason: Optional[str] = None
