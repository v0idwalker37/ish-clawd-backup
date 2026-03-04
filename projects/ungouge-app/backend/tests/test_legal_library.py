import json

import pytest
from httpx import AsyncClient

from services.legal_library import ingest_directory, get_applicable_rules, evaluate_text_against_rules
from tests.conftest import _TestSessionLocal

pytestmark = pytest.mark.asyncio


async def test_legal_library_ingest_and_query(tmp_path):
    bundle = {
        "jurisdiction_level": "federal",
        "jurisdiction_code": "US",
        "title": "Test Federal Pack",
        "source_type": "policy",
        "source_url": "https://example.com/federal",
        "citation_text": "Federal baseline",
        "effective_at": "2026-03-04T00:00:00Z",
        "active": True,
        "tags": ["test"],
        "rules": [
            {
                "rule_key": "no-guarantee",
                "artifact_types": ["promo_page", "ad"],
                "risk_level": "high",
                "action": "rewrite",
                "pattern_type": "keyword",
                "pattern_value": "guaranteed",
                "rationale": "No absolute guarantee claims",
                "active": True,
            }
        ],
    }

    p = tmp_path / "bundle.json"
    p.write_text(json.dumps(bundle))

    async with _TestSessionLocal() as db:
        result = await ingest_directory(db, str(tmp_path))
        await db.commit()

        assert result["files"] == 1
        assert result["documents"] >= 1
        assert result["rules_upserted"] >= 1

        rules = await get_applicable_rules(
            db,
            artifact_type="promo_page",
            jurisdiction_codes=["US"],
        )
        assert len(rules) >= 1
        assert any(r["rule_key"] == "no-guarantee" for r in rules)


async def test_legal_library_evaluate_text(tmp_path):
    bundle = {
        "jurisdiction_level": "platform",
        "jurisdiction_code": "US",
        "title": "Platform Test",
        "source_type": "policy",
        "source_url": "https://example.com/platform",
        "citation_text": "Platform baseline",
        "effective_at": "2026-03-04T00:00:00Z",
        "active": True,
        "tags": ["test"],
        "rules": [
            {
                "rule_key": "block-causation",
                "artifact_types": ["report"],
                "risk_level": "critical",
                "action": "block",
                "pattern_type": "regex",
                "pattern_value": "\\bproves\\b.{0,80}\\bdamage\\b",
                "rationale": "No causation certainty",
                "active": True,
            }
        ],
    }

    p = tmp_path / "bundle.json"
    p.write_text(json.dumps(bundle))

    async with _TestSessionLocal() as db:
        await ingest_directory(db, str(tmp_path))
        await db.commit()

        rules = await get_applicable_rules(
            db,
            artifact_type="report",
            jurisdiction_codes=["US"],
        )
        result = evaluate_text_against_rules("Satellite proves storm damage.", rules)
        assert result["decision"] in {"block", "rewrite", "escalate"}
        assert result["hit_count"] >= 1


async def test_legal_library_api_flow(client: AsyncClient, auth_headers: dict):
    # Ingest bundled packs from repo legal-library path
    ingest = await client.post("/api/legal-library/ingest", json={}, headers=auth_headers)
    assert ingest.status_code == 200

    rules = await client.post(
        "/api/legal-library/rules",
        json={"artifact_type": "report", "jurisdiction_codes": ["US", "US-WY"]},
        headers=auth_headers,
    )
    assert rules.status_code == 200
    assert "rules" in rules.json()

    evaluate = await client.post(
        "/api/legal-library/evaluate",
        json={
            "artifact_type": "report",
            "jurisdiction_codes": ["US", "US-WY"],
            "text": "Satellite confirms this storm caused damage.",
        },
        headers=auth_headers,
    )
    assert evaluate.status_code == 200
    assert evaluate.json()["decision"] in {"block", "rewrite", "escalate", "allow"}

    coverage = await client.get("/api/legal-library/coverage", headers=auth_headers)
    assert coverage.status_code == 200
    assert "documents" in coverage.json()
