from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.city import District, DistrictScore, Road, RoadTraffic


class DistrictScoringEngine:
    """Compute district performance scores and persist recalculated snapshots."""

    def normalize(self, value: float, min_val: float, max_val: float) -> float:
        if max_val <= min_val:
            return 0.0
        normalized = (value - min_val) / (max_val - min_val) * 100.0
        return max(0.0, min(100.0, normalized))

    def compute_traffic_score(self, vehicle_count: int, capacity: int, avg_speed: float, speed_limit: int) -> float:
        if capacity <= 0 or speed_limit <= 0:
            return 0.0
        score = 100 - (vehicle_count / capacity * 50) - ((speed_limit - avg_speed) / speed_limit * 30)
        return max(0.0, min(100.0, score))

    def compute_energy_score(
        self,
        consumption_kwh: float,
        renewable_ratio: float,
        peak_demand: float,
        baseline_demand: float,
    ) -> float:
        if peak_demand <= 0 or baseline_demand <= 0:
            return 0.0
        score = renewable_ratio * 40 + (1 - consumption_kwh / peak_demand) * 35 + (1 - peak_demand / baseline_demand) * 25
        return max(0.0, min(100.0, score))

    def compute_pollution_score(
        self,
        aqi: float,
        pm25: float,
        co2_emissions_tons: float,
        area_sqkm: float,
    ) -> float:
        if area_sqkm <= 0:
            return 0.0
        score = 100 - (aqi / 500 * 40) - (pm25 / 250 * 30) - (co2_emissions_tons / area_sqkm / 100 * 30)
        return max(0.0, min(100.0, score))

    def compute_carbon_score(self, total_emissions_tons: float, area_sqkm: float, population: int) -> float:
        if population <= 0:
            return 0.0
        per_capita = total_emissions_tons / population * 1000000
        score = 100 - (per_capita / 10000 * 100)
        return max(0.0, min(100.0, score))

    def compute_sustainability_score(
        self,
        renewable_ratio: float,
        green_space_percent: float,
        transit_access_score: float,
    ) -> float:
        score = renewable_ratio * 30 + green_space_percent * 0.4 + transit_access_score * 0.3
        return max(0.0, min(100.0, score))

    def composite_score(self, scores: dict[str, float], weights: dict[str, float] | None = None) -> float:
        weights = weights or {
            "traffic": 0.25,
            "energy": 0.20,
            "pollution": 0.20,
            "carbon": 0.20,
            "sustainability": 0.15,
        }
        value = sum(scores.get(name, 0.0) * weight for name, weight in weights.items())
        return max(0.0, min(100.0, value))

    async def update_all_districts(self, session: AsyncSession) -> dict[UUID, dict[str, float]]:
        latest_scores_sq = (
            select(DistrictScore.district_id, func.max(DistrictScore.time).label("time"))
            .group_by(DistrictScore.district_id)
            .subquery()
        )
        latest_roads_sq = (
            select(RoadTraffic.road_id, func.max(RoadTraffic.time).label("time"))
            .group_by(RoadTraffic.road_id)
            .subquery()
        )

        latest_scores_stmt = (
            select(DistrictScore)
            .join(
                latest_scores_sq,
                (DistrictScore.district_id == latest_scores_sq.c.district_id)
                & (DistrictScore.time == latest_scores_sq.c.time),
            )
        )
        latest_roads_stmt = (
            select(Road, RoadTraffic)
            .join(RoadTraffic, RoadTraffic.road_id == Road.id)
            .join(
                latest_roads_sq,
                (RoadTraffic.road_id == latest_roads_sq.c.road_id)
                & (RoadTraffic.time == latest_roads_sq.c.time),
            )
        )

        latest_score_rows = (await session.execute(latest_scores_stmt)).scalars().all()
        road_rows = (await session.execute(latest_roads_stmt)).all()
        districts = (await session.execute(select(District))).scalars().all()

        district_scores: dict[UUID, DistrictScore] = {row.district_id: row for row in latest_score_rows}
        road_metrics: dict[UUID, list[tuple[Road, RoadTraffic]]] = defaultdict(list)
        for road, traffic in road_rows:
            road_metrics[road.from_district_id].append((road, traffic))
            road_metrics[road.to_district_id].append((road, traffic))

        updated: dict[UUID, dict[str, float]] = {}
        now = datetime.now(UTC)

        for district in districts:
            roads = road_metrics.get(district.id, [])
            latest = district_scores.get(district.id)

            if roads:
                vehicle_count = int(sum(traffic.vehicle_count for _, traffic in roads) / len(roads))
                capacity = max(1, int(sum(road.capacity for road, _ in roads) / len(roads)))
                avg_speed = sum(traffic.avg_speed for _, traffic in roads) / len(roads)
                speed_limit = max(1, int(sum(road.speed_limit for road, _ in roads) / len(roads)))
            else:
                vehicle_count = 0
                capacity = 1
                avg_speed = 0.0
                speed_limit = 1

            traffic_score = self.compute_traffic_score(vehicle_count, capacity, avg_speed, speed_limit)
            renewable_ratio = min(1.0, max(0.0, (latest.sustainability_score if latest else 60.0) / 100.0))
            consumption_kwh = district.population * 2.25
            peak_demand = consumption_kwh * (1.1 + (1 - renewable_ratio) * 0.2)
            baseline_demand = consumption_kwh * 1.35
            energy_score = self.compute_energy_score(consumption_kwh, renewable_ratio, peak_demand, baseline_demand)

            aqi = 80 - traffic_score * 0.4
            pm25 = 40 - traffic_score * 0.18
            co2_emissions_tons = district.population * 0.0008 + vehicle_count * 0.002
            pollution_score = self.compute_pollution_score(aqi, pm25, co2_emissions_tons, district.area_sqkm)

            total_emissions_tons = district.population * 0.00092 + co2_emissions_tons
            carbon_score = self.compute_carbon_score(total_emissions_tons, district.area_sqkm, district.population)

            green_space_percent = min(35.0, max(4.0, district.area_sqkm / 3.2))
            transit_access_score = min(100.0, (traffic_score + speed_limit / 2) / 1.5)
            sustainability_score = self.compute_sustainability_score(
                renewable_ratio,
                green_space_percent,
                transit_access_score,
            )
            composite = self.composite_score(
                {
                    "traffic": traffic_score,
                    "energy": energy_score,
                    "pollution": pollution_score,
                    "carbon": carbon_score,
                    "sustainability": sustainability_score,
                }
            )

            new_row = DistrictScore(
                time=now,
                district_id=district.id,
                traffic_score=traffic_score,
                energy_score=energy_score,
                pollution_score=pollution_score,
                carbon_score=carbon_score,
                sustainability_score=sustainability_score,
            )
            session.add(new_row)
            updated[district.id] = {
                "traffic_score": traffic_score,
                "energy_score": energy_score,
                "pollution_score": pollution_score,
                "carbon_score": carbon_score,
                "sustainability_score": sustainability_score,
                "composite_score": composite,
            }

        await session.commit()
        return updated
