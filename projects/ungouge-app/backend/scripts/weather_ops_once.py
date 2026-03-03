"""Run one full weather ops cycle (ingest + stale expiry)."""

import asyncio
import os
import sys

_THIS = os.path.dirname(__file__)
_BACKEND_ROOT = os.path.dirname(_THIS)
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from models.database import async_session_maker, engine, Base
from services.weather_maintenance import run_weather_ops_cycle


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        result = await run_weather_ops_cycle(db)
        await db.commit()
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
