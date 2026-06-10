import asyncio
import sys
sys.path.insert(0, r"C:\Users\mrsse\Desktop\NeuroCity-Nexus\NeuroCity-Nexus\backend")

from src.db.base import Base
from src.db.session import engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created successfully!")

asyncio.run(create_tables())
