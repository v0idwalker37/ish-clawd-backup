import pytest

from services.legal_jurisdictions import sync_us_jurisdictions, expand_jurisdiction_chain
from tests.conftest import _TestSessionLocal
from models.database import LegalJurisdiction
from sqlalchemy import select, func

pytestmark = pytest.mark.asyncio


STATE_TEXT = """STATE|STUSAB|STATE_NAME|STATENS
50|VT|Vermont|01779803
56|WY|Wyoming|01779807
"""

COUNTY_TEXT = """STATE|STATEFP|COUNTYFP|COUNTYNS|COUNTYNAME|CLASSFP|FUNCSTAT
VT|50|023|01477900|Washington County|H1|A
WY|56|001|01605058|Albany County|H1|A
"""

PLACE_TEXT = """STATE|STATEFP|PLACEFP|PLACENS|PLACENAME|TYPE|CLASSFP|FUNCSTAT|COUNTIES
VT|50|55000|02412345|Northfield village|INCORPORATED PLACE|C1|A|Washington County
WY|56|12345|02456789|Some City|INCORPORATED PLACE|C1|A|Albany County
"""


async def test_sync_us_jurisdictions_with_sample_data():
    async with _TestSessionLocal() as db:
        result = await sync_us_jurisdictions(
            db,
            include_places=True,
            state_text=STATE_TEXT,
            county_text=COUNTY_TEXT,
            place_text=PLACE_TEXT,
        )
        await db.commit()

        assert result["states"] == 2
        assert result["counties"] == 2
        assert result["cities"] == 2

        total = await db.scalar(select(func.count()).select_from(LegalJurisdiction))
        # 1 federal + 2 states + 2 counties + 2 cities
        assert total == 7

        vt = await db.scalar(select(LegalJurisdiction).where(LegalJurisdiction.code == "US-VT"))
        assert vt is not None
        assert vt.level == "state"

        county = await db.scalar(
            select(LegalJurisdiction).where(LegalJurisdiction.code == "US-VT-COUNTY-023")
        )
        assert county is not None
        assert county.parent_code == "US-VT"


@pytest.mark.parametrize(
    "code,expected",
    [
        ("US", ["US"]),
        ("US-VT", ["US-VT", "US"]),
        ("US-VT-COUNTY-023", ["US-VT-COUNTY-023", "US-VT", "US"]),
        ("US-VT-CITY-55000", ["US-VT-CITY-55000", "US-VT", "US"]),
    ],
)
def test_expand_jurisdiction_chain(code, expected):
    assert expand_jurisdiction_chain(code) == expected
