import asyncio
import sys
sys.path.insert(0, r"C:\Users\mrsse\Desktop\NeuroCity-Nexus\NeuroCity-Nexus\backend")

from src.db.base import Base
from src.db.session import engine
from src.models.city.district import District, DistrictScore
from src.models.city.road import Road, RoadTraffic
from src.models.city.building import Building

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created!")

asyncio.run(create_tables())
