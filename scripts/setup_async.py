import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db.base import Base
from src.db.session import engine

# Import all models so they register with Base metadata
from src.models.city.district import District, DistrictScore
from src.models.city.road import Road, RoadTraffic
from src.models.city.building import Building

def main():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done! All tables created successfully.")

if __name__ == "__main__":
    main()
