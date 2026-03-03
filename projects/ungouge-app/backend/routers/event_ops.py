from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from models.database import get_db, EventRun, WeatherEvent
from models.publish import PublishArtifactRequest
from services.auth import get_current_user
from models.database import User
from services.compliance_token import verify_publish_token, ComplianceTokenError
from services.event_lifecycle import transition_event_run, revoke_event_run, TransitionError
from services.logger import logger

router = APIRouter()


class EventRunCreateRequest(BaseModel):
    weather_event_id: str
    geo_scope_key: str
    canonical_slug: str | None = None


class EventRunTransitionRequest(BaseModel):
    target_status: str
    reason: str | None = None


@router.post("/event-runs", status_code=status.HTTP_201_CREATED)
async def create_event_run(
    body: EventRunCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Basic existence check
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


@router.post("/publish-gateway")
async def publish_gateway(
    body: PublishArtifactRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Internal publish gateway requiring signed compliance token.

    This is the enforcement foundation: callers must present a valid token
    issued by legal/compliance gate stage.
    """
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

    # Foundation behavior: log and acknowledge.
    # Actual channel publishing adapters come next iteration.
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
