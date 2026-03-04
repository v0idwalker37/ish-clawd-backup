"""Legal knowledge library services.

Production-oriented primitives for:
- ingesting curated legal bundles
- retrieving applicable rules by jurisdiction + artifact type
- producing citation-backed decisions for legal gate workflows
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import LegalDocument, LegalRule, LegalJurisdiction


LEGAL_LIBRARY_DIR = os.getenv(
    "LEGAL_LIBRARY_DIR",
    "/home/ungouge/clawd/projects/ungouge-app/legal-library/bundles",
)


@dataclass
class RuleHit:
    rule_id: str
    rule_key: str
    action: str
    risk_level: str
    evidence: str
    document_id: str


def _now() -> datetime:
    return datetime.utcnow()


def _sha(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str).encode()
    return hashlib.sha256(raw).hexdigest()


def _norm_jur(code: str) -> str:
    return (code or "").strip().upper()


def _parse_dt(v: Optional[str]) -> Optional[datetime]:
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


async def upsert_bundle(db: AsyncSession, bundle: Dict[str, Any]) -> Dict[str, int]:
    """Insert/update one legal bundle and its rules."""
    checksum = _sha(bundle)
    jurisdiction_level = (bundle.get("jurisdiction_level") or "platform").lower()
    jurisdiction_code = _norm_jur(bundle.get("jurisdiction_code") or "US")
    title = (bundle.get("title") or "Untitled Legal Bundle").strip()

    # Try to find existing doc by checksum first, then title+jurisdiction.
    existing = await db.scalar(
        select(LegalDocument)
        .where(LegalDocument.checksum == checksum)
        .limit(1)
    )

    if not existing:
        existing = await db.scalar(
            select(LegalDocument)
            .where(LegalDocument.jurisdiction_code == jurisdiction_code)
            .where(LegalDocument.title == title)
            .limit(1)
        )

    if existing:
        doc = existing
        doc.jurisdiction_level = jurisdiction_level
        doc.jurisdiction_code = jurisdiction_code
        doc.source_type = (bundle.get("source_type") or "policy").lower()
        doc.source_url = bundle.get("source_url")
        doc.citation_text = bundle.get("citation_text")
        doc.tags = bundle.get("tags") or []
        doc.effective_at = _parse_dt(bundle.get("effective_at"))
        doc.superseded_at = _parse_dt(bundle.get("superseded_at"))
        doc.active = bool(bundle.get("active", True))
        doc.checksum = checksum
        doc.updated_at = _now()
    else:
        doc = LegalDocument(
            id=str(uuid.uuid4()),
            jurisdiction_level=jurisdiction_level,
            jurisdiction_code=jurisdiction_code,
            title=title,
            source_type=(bundle.get("source_type") or "policy").lower(),
            source_url=bundle.get("source_url"),
            citation_text=bundle.get("citation_text"),
            tags=bundle.get("tags") or [],
            effective_at=_parse_dt(bundle.get("effective_at")),
            superseded_at=_parse_dt(bundle.get("superseded_at")),
            active=bool(bundle.get("active", True)),
            checksum=checksum,
            created_at=_now(),
            updated_at=_now(),
        )
        db.add(doc)
        await db.flush()

    # Existing rules by rule_key for doc
    existing_rules = {
        r.rule_key: r
        for r in (
            await db.execute(
                select(LegalRule).where(LegalRule.document_id == doc.id)
            )
        ).scalars().all()
    }

    incoming_keys = set()
    upserted = 0
    for rb in bundle.get("rules") or []:
        key = (rb.get("rule_key") or "").strip()
        if not key:
            continue
        incoming_keys.add(key)

        row = existing_rules.get(key)
        if row:
            row.artifact_types = rb.get("artifact_types") or ["report", "promo_page", "pr", "ad"]
            row.risk_level = (rb.get("risk_level") or "medium").lower()
            row.action = (rb.get("action") or "escalate").lower()
            row.pattern_type = (rb.get("pattern_type") or "regex").lower()
            row.pattern_value = rb.get("pattern_value") or ""
            row.rationale = rb.get("rationale")
            row.required_disclaimer = rb.get("required_disclaimer")
            row.examples = rb.get("examples")
            row.active = bool(rb.get("active", True))
            row.updated_at = _now()
        else:
            row = LegalRule(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                rule_key=key,
                artifact_types=rb.get("artifact_types") or ["report", "promo_page", "pr", "ad"],
                risk_level=(rb.get("risk_level") or "medium").lower(),
                action=(rb.get("action") or "escalate").lower(),
                pattern_type=(rb.get("pattern_type") or "regex").lower(),
                pattern_value=rb.get("pattern_value") or "",
                rationale=rb.get("rationale"),
                required_disclaimer=rb.get("required_disclaimer"),
                examples=rb.get("examples"),
                active=bool(rb.get("active", True)),
                created_at=_now(),
                updated_at=_now(),
            )
            db.add(row)

        upserted += 1

    # Soft-disable doc rules missing from bundle
    for key, row in existing_rules.items():
        if key not in incoming_keys:
            row.active = False
            row.updated_at = _now()

    await db.flush()
    return {"documents": 1, "rules_upserted": upserted}


async def ingest_directory(db: AsyncSession, root_dir: str = LEGAL_LIBRARY_DIR) -> Dict[str, int]:
    root = Path(root_dir)
    if not root.exists():
        return {"documents": 0, "rules_upserted": 0, "files": 0}

    docs = 0
    rules = 0
    files = 0

    for path in sorted(root.rglob("*.json")):
        files += 1
        bundle = json.loads(path.read_text())
        res = await upsert_bundle(db, bundle)
        docs += res.get("documents", 0)
        rules += res.get("rules_upserted", 0)

    return {"documents": docs, "rules_upserted": rules, "files": files}


def _jur_match_priority(rule_jur: str, requested: Iterable[str]) -> int:
    requested = [_norm_jur(x) for x in requested if x]
    r = _norm_jur(rule_jur)
    # Higher = more specific match
    if r in requested:
        return 100 + len(r)
    # Prefix hierarchical fallback: US-VT-WASHINGTON should match request US-VT
    for q in requested:
        if r.startswith(q + "-"):
            return 80 + len(q)
    # Federal fallback
    if r == "US":
        return 10
    return 0


async def get_applicable_rules(
    db: AsyncSession,
    *,
    artifact_type: str,
    jurisdiction_codes: List[str],
    as_of: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    as_of = as_of or _now()
    artifact_type = (artifact_type or "").lower()

    # Expand to hierarchical fallback chain (city/county -> state -> US)
    from services.legal_jurisdictions import expand_jurisdiction_chain

    expanded = []
    for code in jurisdiction_codes or ["US"]:
        expanded.extend(expand_jurisdiction_chain(code))
    # stable unique
    jurisdiction_codes = list(dict.fromkeys(expanded))

    docs = (
        await db.execute(
            select(LegalDocument).where(LegalDocument.active == True)  # noqa: E712
        )
    ).scalars().all()

    # Filter docs by temporal validity + jurisdiction relevance
    doc_map = {}
    for d in docs:
        if d.effective_at and d.effective_at > as_of:
            continue
        if d.superseded_at and d.superseded_at <= as_of:
            continue
        pri = _jur_match_priority(d.jurisdiction_code, jurisdiction_codes)
        if pri <= 0:
            continue
        doc_map[d.id] = (d, pri)

    if not doc_map:
        return []

    rules = (
        await db.execute(
            select(LegalRule)
            .where(LegalRule.active == True)  # noqa: E712
            .where(LegalRule.document_id.in_(list(doc_map.keys())))
        )
    ).scalars().all()

    out = []
    for r in rules:
        types = [str(x).lower() for x in (r.artifact_types or [])]
        if artifact_type not in types and "*" not in types and "all" not in types:
            continue
        d, pri = doc_map[r.document_id]
        out.append(
            {
                "rule_id": r.id,
                "rule_key": r.rule_key,
                "action": r.action,
                "risk_level": r.risk_level,
                "pattern_type": r.pattern_type,
                "pattern_value": r.pattern_value,
                "rationale": r.rationale,
                "required_disclaimer": r.required_disclaimer,
                "document": {
                    "id": d.id,
                    "jurisdiction_code": d.jurisdiction_code,
                    "title": d.title,
                    "source_url": d.source_url,
                    "citation_text": d.citation_text,
                    "source_type": d.source_type,
                },
                "match_priority": pri,
            }
        )

    out.sort(key=lambda x: (x["match_priority"], x["risk_level"]), reverse=True)
    return out


def evaluate_text_against_rules(text: str, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    text = text or ""
    hits: List[RuleHit] = []

    for r in rules:
        ptype = (r.get("pattern_type") or "regex").lower()
        pval = r.get("pattern_value") or ""
        matched = False
        evidence = ""

        try:
            if ptype == "regex":
                m = re.search(pval, text, flags=re.IGNORECASE)
                if m:
                    matched = True
                    evidence = m.group(0)[:240]
            elif ptype == "keyword":
                kw = pval.lower()
                if kw and kw in text.lower():
                    matched = True
                    evidence = kw
            elif ptype == "manual":
                # manual rules are surfaced as advisories, not auto-matched
                matched = False
        except re.error:
            # invalid regex in a bundle should not break evaluation
            matched = False

        if matched:
            hits.append(
                RuleHit(
                    rule_id=r["rule_id"],
                    rule_key=r["rule_key"],
                    action=r["action"],
                    risk_level=r["risk_level"],
                    evidence=evidence,
                    document_id=r["document"]["id"],
                )
            )

    # Decision precedence
    priority = {"block": 4, "escalate": 3, "rewrite": 2, "allow": 1}
    decision = "allow"
    for h in hits:
        if priority.get(h.action, 0) > priority.get(decision, 0):
            decision = h.action

    citation_ids = sorted({h.document_id for h in hits})

    return {
        "decision": decision,
        "hit_count": len(hits),
        "hits": [h.__dict__ for h in hits],
        "citation_document_ids": citation_ids,
    }


async def coverage_summary(db: AsyncSession) -> Dict[str, Any]:
    docs = (await db.execute(select(LegalDocument))).scalars().all()
    rules = (await db.execute(select(LegalRule))).scalars().all()
    jurs = (await db.execute(select(LegalJurisdiction))).scalars().all()

    by_jur = {}
    for d in docs:
        by_jur[d.jurisdiction_code] = by_jur.get(d.jurisdiction_code, 0) + 1

    by_level = {}
    for j in jurs:
        by_level[j.level] = by_level.get(j.level, 0) + 1

    return {
        "documents": len(docs),
        "rules": len(rules),
        "jurisdictions": by_jur,
        "jurisdiction_catalog_count": len(jurs),
        "jurisdiction_levels": by_level,
    }
