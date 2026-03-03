"""Run one weather ingestion pass (MVP utility script)."""

import asyncio
import os
import sys

# Ensure backend root is importable when running as a script
_THIS = os.path.dirname(__file__)
_BACKEND_ROOT = os.path.dirname(_THIS)
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from models.database import async_session_maker, engine, Base
from services.weather_ingest import ingest_nws_active_alerts


async def main() -> None:
    # Ensure tables exist for local/dev script runs
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        result = await ingest_nws_active_alerts(db)
        await db.commit()
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
