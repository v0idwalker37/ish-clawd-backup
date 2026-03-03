from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid
from datetime import datetime

from models.database import (
    get_db,
    EventRun,
    EventRunAction,
    WeatherEvent,
    WeatherRawEvent,
    LegalGateAudit,
    User,
)
from models.publish import (
    PublishArtifactRequest,
    LegalTokenIssueRequest,
    ActionEnqueueRequest,
    KillSwitchRequest,
)
from services.auth import get_current_user
from services.compliance_token import (
    verify_publish_token,
    issue_publish_token,
    ComplianceTokenError,
)
from services.event_lifecycle import transition_event_run, revoke_event_run, TransitionError
from services.event_actions import enqueue_action, run_action
from services.ops_control import get_flag, set_flag, GLOBAL_AUTOMATION_PAUSE_KEY
from services.weather_intel import qualify_event
from services.weather_maintenance import run_weather_ops_cycle
from services.logger import logger

router = APIRouter()


class EventRunCreateRequest(BaseModel):
    weather_event_id: str
    geo_scope_key: str
    canonical_slug: str | None = None


class EventRunTransitionRequest(BaseModel):
    target_status: str
    reason: str | None = None


class WeatherOpsCycleRequest(BaseModel):
    run_now: bool = True


@router.get("/weather-events")
async def list_weather_events(
    status_filter: str | None = None,
    min_score: int | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    limit = max(1, min(limit, 200))
    q = select(WeatherEvent).order_by(WeatherEvent.detected_at.desc()).limit(limit)
    if status_filter:
        q = q.where(WeatherEvent.status == status_filter)
    if min_score is not None:
        q = q.where(WeatherEvent.qualification_score >= min_score)

    rows = (await db.execute(q)).scalars().all()
    return {
        "count": len(rows),
        "events": [
            {
                "id": e.id,
                "hazard_family": e.hazard_family,
                "hazard_type": e.hazard_type,
                "status": e.status,
                "qualification_score": e.qualification_score,
                "geo_confidence": e.geo_confidence,
                "detected_at": e.detected_at.isoformat() if e.detected_at else None,
                "expires_at": e.expires_at.isoformat() if e.expires_at else None,
            }
            for e in rows
        ],
    }


@router.get("/event-ops/dashboard")
async def event_ops_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    weather_total = await db.scalar(select(func.count()).select_from(WeatherEvent))
    runs_total = await db.scalar(select(func.count()).select_from(EventRun))
    actions_total = await db.scalar(select(func.count()).select_from(EventRunAction))

    status_rows = await db.execute(
        select(WeatherEvent.status, func.count())
        .group_by(WeatherEvent.status)
    )
    status_breakdown = {k: int(v) for k, v in status_rows.all()}

    run_status_rows = await db.execute(
        select(EventRun.status, func.count())
        .group_by(EventRun.status)
    )
    run_status_breakdown = {k: int(v) for k, v in run_status_rows.all()}

    paused = await get_flag(db, GLOBAL_AUTOMATION_PAUSE_KEY, default=False)

    return {
        "weather_events_total": int(weather_total or 0),
        "event_runs_total": int(runs_total or 0),
        "actions_total": int(actions_total or 0),
        "weather_status_breakdown": status_breakdown,
        "run_status_breakdown": run_status_breakdown,
        "global_kill_switch": paused,
    }


@router.post("/weather-events/{weather_event_id}/requalify")
async def requalify_weather_event(
    weather_event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    evt = await db.scalar(select(WeatherEvent).where(WeatherEvent.id == weather_event_id))
    if not evt:
        raise HTTPException(status_code=404, detail="Weather event not found")

    source_ids = evt.source_ref_ids or {}
    nws_id = source_ids.get("nws") if isinstance(source_ids, dict) else None

    props = {
        "event": evt.hazard_type,
        "severity": "moderate",
        "certainty": "possible",
        "urgency": "expected",
    }

    if nws_id:
        raw = await db.scalar(
            select(WeatherRawEvent)
            .where(WeatherRawEvent.provider == "nws")
            .where(WeatherRawEvent.external_id == nws_id)
            .order_by(WeatherRawEvent.fetched_at.desc())
            .limit(1)
        )
        if raw and isinstance(raw.payload, dict):
            props = (raw.payload.get("properties") or props)

    county_count = 1
    if isinstance(evt.county_fips, list):
        county_count = max(1, len(evt.county_fips))

    q = qualify_event(props, geo_confidence=float(evt.geo_confidence or 0.5), county_count=county_count)
    evt.qualification_score = q.score
    evt.score_breakdown = q.breakdown
    evt.hazard_family = q.hazard_family

    if q.suppressed:
        evt.status = "SUPPRESSED"
    elif q.band in {"AUTO", "REVIEW"}:
        evt.status = "QUALIFIED"
    elif q.band == "MONITOR":
        evt.status = "CANDIDATE"
    else:
        evt.status = "REJECTED"

    evt.last_seen_at = datetime.utcnow()
    await db.commit()

    return {
        "id": evt.id,
        "status": evt.status,
        "qualification_score": evt.qualification_score,
        "band": q.band,
        "suppressed": q.suppressed,
    }


@router.post("/event-ops/run-cycle")
async def run_event_ops_cycle(
    body: WeatherOpsCycleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not body.run_now:
        return {"status": "skipped"}

    result = await run_weather_ops_cycle(db)
    await db.commit()
    return {"status": "ok", **result}


@router.post("/event-runs", status_code=status.HTTP_201_CREATED)
async def create_event_run(
    body: EventRunCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    weather = await db.execute(select(WeatherEvent).where(WeatherEvent.id == body.weather_event_id))
    if not weather.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Weather event not found")

    run = EventRun(
        id=str(uuid.uuid4()),
        weather_event_id=body.weather_event_id,
        status="DETECTED",
        geo_scope_key=body.geo_scope_key,
        canonical_slug=body.canonical_slug,
        run_version=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(run)
    await db.commit()

    logger.info("event_run_created", extra={"event_run_id": run.id, "user_id": current_user.id})
    return {"id": run.id, "status": run.status}


@router.post("/event-runs/{event_run_id}/transition")
async def transition_run(
    event_run_id: str,
    body: EventRunTransitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        run = await transition_event_run(
            db,
            event_run_id=event_run_id,
            target_status=body.target_status,
            reason=body.reason,
        )
        await db.commit()
        return {"id": run.id, "status": run.status}
    except TransitionError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/event-runs/{event_run_id}/revoke")
async def revoke_run(
    event_run_id: str,
    reason: str = "manual_revoke",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        run = await revoke_event_run(db, event_run_id, reason=reason)
        await db.commit()
        return {"id": run.id, "status": run.status}
    except TransitionError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/event-runs/{event_run_id}/rollback")
async def rollback_run(
    event_run_id: str,
    reason: str = "manual_rollback",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rollback hook: transition run into ROLLED_BACK from allowed states."""
    try:
        run = await transition_event_run(
            db,
            event_run_id=event_run_id,
            target_status="ROLLED_BACK",
            reason=reason,
        )
        await db.commit()
        return {"id": run.id, "status": run.status}
    except TransitionError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/event-runs/{event_run_id}/actions", status_code=status.HTTP_201_CREATED)
async def enqueue_event_action(
    event_run_id: str,
    body: ActionEnqueueRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ensure event run exists
    run = await db.execute(select(EventRun).where(EventRun.id == event_run_id))
    if not run.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Event run not found")

    row = await enqueue_action(
        db,
        event_run_id=event_run_id,
        action_type=body.action_type,
        payload=body.payload,
        idempotency_key=body.idempotency_key,
    )
    await db.commit()
    return {"id": row.id, "status": row.status, "action_type": row.action_type}


@router.post("/event-actions/{action_id}/execute")
async def execute_event_action(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        row = await run_action(db, action_id)
        await db.commit()
        return {"id": row.id, "status": row.status}
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/event-ops/kill-switch/global")
async def get_global_kill_switch(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enabled = await get_flag(db, GLOBAL_AUTOMATION_PAUSE_KEY, default=False)
    return {"enabled": enabled}


@router.post("/event-ops/kill-switch/global")
async def set_global_kill_switch(
    body: KillSwitchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = await set_flag(
        db,
        key=GLOBAL_AUTOMATION_PAUSE_KEY,
        enabled=body.enabled,
        reason=body.reason,
        actor_id=current_user.id,
    )
    await db.commit()
    return {"enabled": bool(row.value_json.get("enabled")), "reason": row.value_json.get("reason")}


@router.post("/legal/issue-publish-token")
async def issue_legal_publish_token(
    body: LegalTokenIssueRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (body.decision or "").upper()
    if decision not in {"PASS", "PASS_WITH_EDIT"}:
        raise HTTPException(
            status_code=400,
            detail="Token can only be issued for PASS or PASS_WITH_EDIT decisions",
        )

    audit = LegalGateAudit(
        id=str(uuid.uuid4()),
        artifact_type=body.artifact_type,
        artifact_id=body.artifact_id,
        decision=decision,
        reasons={"reasons": body.reasons or []},
        policy_pack_version=body.policy_pack_version,
        content_hash_before=body.content_hash,
        content_hash_after=body.content_hash,
        created_at=datetime.utcnow(),
    )
    db.add(audit)

    token = issue_publish_token(
        artifact_type=body.artifact_type,
        artifact_id=body.artifact_id,
        content_hash=body.content_hash,
        policy_pack_version=body.policy_pack_version,
        ttl_seconds=300,
        extra={"audit_id": audit.id, "decision": decision},
    )
    await db.commit()

    return {
        "status": "issued",
        "token": token,
        "policy_pack_version": body.policy_pack_version,
        "decision": decision,
    }


@router.post("/publish-gateway")
async def publish_gateway(
    body: PublishArtifactRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paused = await get_flag(db, GLOBAL_AUTOMATION_PAUSE_KEY, default=False)
    if paused:
        raise HTTPException(status_code=503, detail="Global automation kill-switch is enabled")

    try:
        payload = verify_publish_token(
            body.compliance_token,
            artifact_type=body.artifact_type,
            artifact_id=body.artifact_id,
            content_hash=body.content_hash,
            policy_pack_version="legal-v1",
        )
    except ComplianceTokenError as e:
        raise HTTPException(status_code=403, detail=f"Compliance token rejected: {e}")

    logger.info(
        "publish_gateway_accepted",
        extra={
            "artifact_type": body.artifact_type,
            "artifact_id": body.artifact_id,
            "channel": body.channel,
            "policy_pack_version": payload.get("policy_pack_version"),
            "user_id": current_user.id,
        },
    )

    return {
        "status": "accepted",
        "artifact_type": body.artifact_type,
        "artifact_id": body.artifact_id,
        "channel": body.channel,
        "policy_pack_version": payload.get("policy_pack_version"),
    }
