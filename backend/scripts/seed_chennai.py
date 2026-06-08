from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from random import Random

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import AsyncSessionLocal
from src.models.city import Building, BuildingType, District, DistrictScore, Road, RoadTraffic, RoadType

rng = Random(7)


@dataclass(frozen=True)
class DistrictSeed:
    id: str
    name: str
    code: str
    center_lat: float
    center_lon: float
    area_sqkm: float
    population: int
    elevation: float
    boundary_geojson: dict[str, object]


DISTRICT_SEEDS = [
    DistrictSeed("23de7742-6b1d-4f88-93ac-6b935c198001", "North Chennai", "NCH", 13.1466, 80.2933, 76.4, 1480000, 9.0, {"type": "Polygon", "coordinates": [[[80.245, 13.118], [80.322, 13.118], [80.332, 13.182], [80.258, 13.194], [80.245, 13.118]]]}),
    DistrictSeed("23de7742-6b1d-4f88-93ac-6b935c198002", "Central Chennai", "CCH", 13.0711, 80.2707, 54.8, 1230000, 11.0, {"type": "Polygon", "coordinates": [[[80.229, 13.041], [80.304, 13.041], [80.309, 13.097], [80.238, 13.104], [80.229, 13.041]]]}),
    DistrictSeed("23de7742-6b1d-4f88-93ac-6b935c198003", "South Chennai", "SCH", 12.9716, 80.2432, 98.7, 1710000, 14.0, {"type": "Polygon", "coordinates": [[[80.198, 12.926], [80.287, 12.926], [80.295, 13.011], [80.206, 13.018], [80.198, 12.926]]]}),
    DistrictSeed("23de7742-6b1d-4f88-93ac-6b935c198004", "West Chennai", "WCH", 13.0529, 80.1956, 84.1, 1380000, 18.0, {"type": "Polygon", "coordinates": [[[80.144, 13.015], [80.228, 13.015], [80.231, 13.086], [80.153, 13.091], [80.144, 13.015]]]}),
    DistrictSeed("23de7742-6b1d-4f88-93ac-6b935c198005", "East Chennai", "ECH", 13.0358, 80.3021, 61.9, 1160000, 6.0, {"type": "Polygon", "coordinates": [[[80.276, 13.001], [80.344, 13.001], [80.349, 13.067], [80.282, 13.072], [80.276, 13.001]]]}),
]

ROAD_SEEDS = [
    ("9c03ce88-5af2-4d7d-b285-0165bb900001", "Inner Ring North", RoadType.arterial, "NCH", "CCH", 11800.0, 8200, 4, 60, False),
    ("9c03ce88-5af2-4d7d-b285-0165bb900002", "Marina Connector", RoadType.arterial, "CCH", "ECH", 7600.0, 6400, 3, 50, True),
    ("9c03ce88-5af2-4d7d-b285-0165bb900003", "OMR Spine", RoadType.highway, "CCH", "SCH", 15600.0, 12400, 6, 80, False),
    ("9c03ce88-5af2-4d7d-b285-0165bb900004", "Western Bypass", RoadType.highway, "WCH", "SCH", 13200.0, 9800, 5, 70, False),
    ("9c03ce88-5af2-4d7d-b285-0165bb900005", "Port Link Road", RoadType.arterial, "NCH", "ECH", 9100.0, 7200, 4, 55, False),
    ("9c03ce88-5af2-4d7d-b285-0165bb900006", "Central Crossway", RoadType.arterial, "WCH", "CCH", 8800.0, 6900, 4, 50, False),
    ("9c03ce88-5af2-4d7d-b285-0165bb900007", "Coastal South Link", RoadType.residential, "ECH", "SCH", 10400.0, 4300, 2, 40, False),
    ("9c03ce88-5af2-4d7d-b285-0165bb900008", "North West Freight Route", RoadType.highway, "NCH", "WCH", 14300.0, 10100, 5, 75, True),
]

BUILDING_MIX = [
    BuildingType.residential,
    BuildingType.commercial,
    BuildingType.industrial,
    BuildingType.public,
]


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def rush_hour_factor(hour: float) -> float:
    morning = 0.95 * max(0.0, 1.0 - abs(hour - 9.0) / 2.0)
    evening = 1.1 * max(0.0, 1.0 - abs(hour - 18.5) / 2.8)
    return morning + evening


def midday_factor(hour: float) -> float:
    return max(0.0, 1.0 - abs(hour - 13.0) / 5.5)


def night_calm_factor(hour: float) -> float:
    return max(0.0, 1.0 - abs(hour - 2.0) / 4.0)


async def reset_existing_data(session: AsyncSession) -> None:
    await session.execute(delete(RoadTraffic))
    await session.execute(delete(DistrictScore))
    await session.execute(delete(Building))
    await session.execute(delete(Road))
    await session.execute(delete(District))
    await session.commit()


async def seed_districts(session: AsyncSession) -> dict[str, District]:
    districts: dict[str, District] = {}
    for seed in DISTRICT_SEEDS:
        district = District(
            id=uuid.UUID(seed.id),
            name=seed.name,
            code=seed.code,
            boundary_geojson=seed.boundary_geojson,
            center_lat=seed.center_lat,
            center_lon=seed.center_lon,
            area_sqkm=seed.area_sqkm,
            population=seed.population,
            elevation=seed.elevation,
        )
        session.add(district)
        districts[seed.code] = district

    await session.flush()
    return districts


async def seed_roads(session: AsyncSession, districts: dict[str, District]) -> list[Road]:
    roads: list[Road] = []
    for road_id, name, road_type, from_code, to_code, length_m, capacity, lanes, speed_limit, one_way in ROAD_SEEDS:
        from_district = districts[from_code]
        to_district = districts[to_code]
        road = Road(
            id=uuid.UUID(road_id),
            name=name,
            road_type=road_type,
            from_district_id=from_district.id,
            to_district_id=to_district.id,
            geometry_geojson={
                "type": "LineString",
                "coordinates": [
                    [from_district.center_lon, from_district.center_lat],
                    [to_district.center_lon, to_district.center_lat],
                ],
            },
            length_m=length_m,
            capacity=capacity,
            lanes=lanes,
            speed_limit=speed_limit,
            one_way=one_way,
        )
        roads.append(road)
        session.add(road)

    await session.flush()
    return roads


async def seed_buildings(session: AsyncSession, districts: dict[str, District]) -> None:
    district_list = list(districts.values())
    for index in range(20):
        district = district_list[index % len(district_list)]
        building_type = BUILDING_MIX[index % len(BUILDING_MIX)]
        footprint = 900.0 + (index % 5) * 240.0 + rng.uniform(0.0, 120.0)
        floors = 3 + (index % 9)
        height = floors * rng.uniform(3.1, 3.8)
        energy = footprint * floors * rng.uniform(18.0, 29.0)

        session.add(
            Building(
                id=uuid.uuid4(),
                district_id=district.id,
                name=f"{district.code}-{building_type.value.title()}-{index + 1:02d}",
                type=building_type,
                floors=floors,
                footprint_area=round(footprint, 2),
                height_m=round(height, 2),
                energy_consumption_annual=round(energy, 2),
            )
        )


async def seed_historical_scores(
    session: AsyncSession,
    districts: dict[str, District],
    roads: list[Road],
) -> None:
    now = datetime.now(UTC).replace(second=0, microsecond=0)

    for step in range(288):
        timestamp = now - timedelta(minutes=5 * (287 - step))
        hour = timestamp.hour + (timestamp.minute / 60.0)
        rush = rush_hour_factor(hour)
        midday = midday_factor(hour)
        night = night_calm_factor(hour)

        for road in roads:
            baseline = road.capacity * (0.28 + 0.14 * rng.random())
            vehicles = baseline + road.capacity * rush * (0.42 + 0.12 * rng.random())
            if road.road_type is RoadType.highway:
                vehicles *= 1.12
            congestion = clamp(vehicles / max(road.capacity, 1), 0.08, 0.98)
            avg_speed = clamp(
                road.speed_limit * (1.02 - congestion * 0.62 + 0.04 * rng.random() + night * 0.12),
                12.0,
                float(road.speed_limit),
            )
            session.add(
                RoadTraffic(
                    time=timestamp,
                    road_id=road.id,
                    vehicle_count=int(vehicles),
                    avg_speed=round(avg_speed, 2),
                    congestion_level=round(congestion, 3),
                )
            )

        for district in districts.values():
            density = district.population / district.area_sqkm
            traffic = clamp(82 - rush * 38 - (density / 50000.0) * 18 + rng.uniform(-4, 4), 18, 96)
            energy = clamp(86 - midday * 21 - night * 9 + rng.uniform(-3, 3), 28, 97)
            pollution = clamp(81 - rush * 34 - midday * 7 + rng.uniform(-5, 5), 20, 95)
            industrial_spike = 8 if district.code == "NCH" and 11 <= hour <= 16 else 0
            carbon = clamp(78 - industrial_spike - (density / 60000.0) * 12 + rng.uniform(-4, 4), 22, 93)
            sustainability_trend = (step / 287.0) * 7.5
            sustainability = clamp(58 + sustainability_trend - rush * 6 + rng.uniform(-2.5, 2.5), 35, 88)

            session.add(
                DistrictScore(
                    time=timestamp,
                    district_id=district.id,
                    traffic_score=round(traffic, 2),
                    energy_score=round(energy, 2),
                    pollution_score=round(pollution, 2),
                    carbon_score=round(carbon, 2),
                    sustainability_score=round(sustainability, 2),
                )
            )


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await reset_existing_data(session)
        districts = await seed_districts(session)
        roads = await seed_roads(session, districts)
        await seed_buildings(session, districts)
        await seed_historical_scores(session, districts, roads)
        await session.commit()

    print("Chennai digital twin seed completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
