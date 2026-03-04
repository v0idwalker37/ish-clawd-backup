from pydantic import BaseModel, Field
from typing import List, Optional


class LegalIngestRequest(BaseModel):
    root_dir: Optional[str] = Field(default=None, description="Optional override root; defaults to configured LEGAL_LIBRARY_DIR")


class LegalRulesQuery(BaseModel):
    artifact_type: str
    jurisdiction_codes: List[str]


class LegalEvaluateRequest(BaseModel):
    artifact_type: str
    jurisdiction_codes: List[str]
    text: str


class JurisdictionSyncRequest(BaseModel):
    include_places: bool = True
