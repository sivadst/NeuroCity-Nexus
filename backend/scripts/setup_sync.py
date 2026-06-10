import sys
sys.path.insert(0, r"C:\Users\mrsse\Desktop\NeuroCity-Nexus\NeuroCity-Nexus\backend")

from src.db.session import engine
from src.db.base import Base
from src.models.city.district import District, DistrictScore
from src.models.city.road import Road, RoadTraffic
from src.models.city.building import Building

# Create all tables
Base.metadata.create_all(bind=engine)
print("Tables created!")

# Verify
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tables:", tables)
