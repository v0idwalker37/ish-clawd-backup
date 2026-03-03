from pydantic import BaseModel, Field


class PublishArtifactRequest(BaseModel):
    """Internal publish-gateway request requiring legal compliance token."""

    artifact_type: str = Field(..., description="promo_page | pr | ad | report")
    artifact_id: str = Field(..., description="Stable artifact id")
    content_hash: str = Field(..., description="SHA-256 hash of artifact content")
    compliance_token: str = Field(..., description="Signed compliance token")
    channel: str = Field(..., description="publish channel, e.g. cms|ads|pr")
