import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Set PYTHONPATH environment variable for child processes
import os
os.environ["PYTHONPATH"] = str(project_root)

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
    print(f"Database file: {engine.url}")

if __name__ == "__main__":
    main()
