"""Event action adapters (MVP stubs).

These adapters intentionally avoid external side effects for now.
They return deterministic payloads that can be used by orchestration and tests.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


async def promo_page_create(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "adapter": "promo_page_create",
        "result": "ok",
        "slug": payload.get("slug"),
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


async def promo_page_update(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "adapter": "promo_page_update",
        "result": "ok",
        "slug": payload.get("slug"),
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


async def promo_page_sunset(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "adapter": "promo_page_sunset",
        "result": "ok",
        "slug": payload.get("slug"),
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


async def campaign_prepare(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "adapter": "campaign_prepare",
        "result": "ok",
        "campaign_name": payload.get("campaign_name"),
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


async def execute_action_adapter(action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    table = {
        "promo_page_create": promo_page_create,
        "promo_page_update": promo_page_update,
        "promo_page_sunset": promo_page_sunset,
        "campaign_prepare": campaign_prepare,
    }
    fn = table.get(action_type)
    if not fn:
        # Unknown action types are explicitly marked skipped
        return {
            "adapter": "unknown",
            "result": "skipped",
            "action_type": action_type,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
    return await fn(payload or {})
