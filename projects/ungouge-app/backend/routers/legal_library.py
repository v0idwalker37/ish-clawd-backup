from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db, User
from models.legal_library import LegalIngestRequest, LegalRulesQuery, LegalEvaluateRequest
from services.auth import get_current_user
from services.legal_library import (
    LEGAL_LIBRARY_DIR,
    coverage_summary,
    evaluate_text_against_rules,
    get_applicable_rules,
    ingest_directory,
)

router = APIRouter()

_ALLOWED_ROOT = "/home/ungouge/clawd/projects/ungouge-app/legal-library"


def _validate_root(path: str) -> str:
    import os

    p = os.path.abspath(path)
    if not p.startswith(_ALLOWED_ROOT):
        raise HTTPException(status_code=400, detail="root_dir outside allowed legal-library path")
    return p


@router.post("/legal-library/ingest")
async def ingest_legal_library(
    body: LegalIngestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    root = body.root_dir or LEGAL_LIBRARY_DIR
    root = _validate_root(root)

    result = await ingest_directory(db, root)
    await db.commit()
    return {"status": "ok", **result}


@router.post("/legal-library/rules")
async def query_legal_rules(
    body: LegalRulesQuery,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rules = await get_applicable_rules(
        db,
        artifact_type=body.artifact_type,
        jurisdiction_codes=body.jurisdiction_codes,
    )
    return {"count": len(rules), "rules": rules}


@router.post("/legal-library/evaluate")
async def evaluate_legal_text(
    body: LegalEvaluateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rules = await get_applicable_rules(
        db,
        artifact_type=body.artifact_type,
        jurisdiction_codes=body.jurisdiction_codes,
    )
    result = evaluate_text_against_rules(body.text, rules)
    return {"status": "ok", "rule_count": len(rules), **result}


@router.get("/legal-library/coverage")
async def get_coverage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    summary = await coverage_summary(db)
    return {"status": "ok", **summary}
