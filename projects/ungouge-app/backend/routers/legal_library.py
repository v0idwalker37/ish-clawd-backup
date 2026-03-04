from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import get_db, User, LegalJurisdiction
from models.legal_library import (
    LegalIngestRequest,
    LegalRulesQuery,
    LegalEvaluateRequest,
    JurisdictionSyncRequest,
)
from services.auth import get_current_user
from services.legal_library import (
    LEGAL_LIBRARY_DIR,
    coverage_summary,
    evaluate_text_against_rules,
    get_applicable_rules,
    ingest_directory,
)
from services.legal_jurisdictions import sync_us_jurisdictions, expand_jurisdiction_chain

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


@router.post("/legal-library/jurisdictions/sync")
async def sync_jurisdictions(
    body: JurisdictionSyncRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await sync_us_jurisdictions(db, include_places=body.include_places)
    await db.commit()
    return {"status": "ok", **result}


@router.get("/legal-library/jurisdictions")
async def list_jurisdictions(
    level: str | None = None,
    state_abbr: str | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    limit = max(1, min(limit, 5000))
    q = select(LegalJurisdiction).where(LegalJurisdiction.active == True)  # noqa: E712
    if level:
        q = q.where(LegalJurisdiction.level == level.lower())
    if state_abbr:
        q = q.where(LegalJurisdiction.state_abbr == state_abbr.upper())
    q = q.order_by(LegalJurisdiction.code).limit(limit)

    rows = (await db.execute(q)).scalars().all()
    return {
        "count": len(rows),
        "jurisdictions": [
            {
                "code": r.code,
                "level": r.level,
                "name": r.name,
                "parent_code": r.parent_code,
                "state_abbr": r.state_abbr,
            }
            for r in rows
        ],
    }


@router.post("/legal-library/rules")
async def query_legal_rules(
    body: LegalRulesQuery,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expanded = list(dict.fromkeys(sum([expand_jurisdiction_chain(c) for c in body.jurisdiction_codes], [])))
    rules = await get_applicable_rules(
        db,
        artifact_type=body.artifact_type,
        jurisdiction_codes=expanded,
    )
    return {"count": len(rules), "jurisdiction_chain": expanded, "rules": rules}


@router.post("/legal-library/evaluate")
async def evaluate_legal_text(
    body: LegalEvaluateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expanded = list(dict.fromkeys(sum([expand_jurisdiction_chain(c) for c in body.jurisdiction_codes], [])))
    rules = await get_applicable_rules(
        db,
        artifact_type=body.artifact_type,
        jurisdiction_codes=expanded,
    )
    result = evaluate_text_against_rules(body.text, rules)
    return {"status": "ok", "jurisdiction_chain": expanded, "rule_count": len(rules), **result}


@router.get("/legal-library/coverage")
async def get_coverage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    summary = await coverage_summary(db)
    return {"status": "ok", **summary}
