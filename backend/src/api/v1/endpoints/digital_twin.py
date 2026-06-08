from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db_session
from src.models.city import Building, District, DistrictScore, Road, RoadTraffic
from src.schemas.digital_twin import (
    BuildingResponse,
    CityDistrictSummary,
    CityStateResponse,
    DistrictDetailResponse,
    DistrictHistoryResponse,
    DistrictResponse,
    RefreshResponse,
    RoadResponse,
    RoadTrafficResponse,
    ScoreBundle,
    ScoreHistoryPoint,
)
from src.services.digital_twin.scoring import DistrictScoringEngine

router = APIRouter(prefix="/twin", tags=["Digital Twin"])
engine = DistrictScoringEngine()


def _score_bundle(score: DistrictScore) -> ScoreBundle:
    return ScoreBundle(
        traffic_score=float(score.traffic_score),
        energy_score=float(score.energy_score),
        pollution_score=float(score.pollution_score),
        carbon_score=float(score.carbon_score),
        sustainability_score=float(score.sustainability_score),
    )


async def _latest_scores(session: AsyncSession) -> dict[UUID, DistrictScore]:
    latest_sq = (
        select(DistrictScore.district_id, func.max(DistrictScore.time).label("time"))
        .group_by(DistrictScore.district_id)
        .subquery()
    )
    rows = (
        await session.execute(
            select(DistrictScore)
            .join(
                latest_sq,
                (DistrictScore.district_id == latest_sq.c.district_id)
                & (DistrictScore.time == latest_sq.c.time),
            )
        )
    ).scalars().all()
    return {row.district_id: row for row in rows}


async def _latest_road_traffic(session: AsyncSession) -> dict[UUID, RoadTraffic]:
    latest_sq = (
        select(RoadTraffic.road_id, func.max(RoadTraffic.time).label("time"))
        .group_by(RoadTraffic.road_id)
        .subquery()
    )
    rows = (
        await session.execute(
            select(RoadTraffic)
            .join(
                latest_sq,
                (RoadTraffic.road_id == latest_sq.c.road_id) & (RoadTraffic.time == latest_sq.c.time),
            )
        )
    ).scalars().all()
    return {row.road_id: row for row in rows}


async def _history_rows(session: AsyncSession, hours: int) -> dict[UUID, list[ScoreHistoryPoint]]:
    rows = (
        await session.execute(
            select(DistrictScore)
            .where(DistrictScore.time >= datetime.now(UTC) - timedelta(hours=hours))
            .order_by(DistrictScore.district_id.asc(), DistrictScore.time.asc())
        )
    ).scalars().all()
    grouped: dict[UUID, list[ScoreHistoryPoint]] = {}
    for row in rows:
        grouped.setdefault(row.district_id, []).append(
            ScoreHistoryPoint(
                time=row.time,
                value=engine.composite_score(
                    {
                        "traffic": float(row.traffic_score),
                        "energy": float(row.energy_score),
                        "pollution": float(row.pollution_score),
                        "carbon": float(row.carbon_score),
                        "sustainability": float(row.sustainability_score),
                    }
                ),
            )
        )
    return grouped


async def _get_district_or_404(session: AsyncSession, district_id: UUID) -> District:
    district = (await session.execute(select(District).where(District.id == district_id))).scalar_one_or_none()
    if district is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="District not found")
    return district


@router.get("/districts", response_model=list[DistrictResponse])
async def list_districts(
    include_history: bool = Query(default=False),
    include_buildings: bool = Query(default=False),
    include_roads: bool = Query(default=False),
    session: AsyncSession = Depends(get_db_session),
) -> list[DistrictResponse]:
    """Return all districts with their current scores.

    curl -s http://localhost:8000/api/v1/twin/districts
    """
    districts = (await session.execute(select(District).order_by(District.name))).scalars().all()
    latest_scores = await _latest_scores(session)
    latest_traffic = await _latest_road_traffic(session)
    histories = await _history_rows(session, 24) if include_history else {}
    buildings_by_district: dict[UUID, list[BuildingResponse]] = {}
    if include_buildings:
        buildings = (await session.execute(select(Building).order_by(Building.name))).scalars().all()
        for building in buildings:
            buildings_by_district.setdefault(building.district_id, []).append(
                BuildingResponse.model_validate(building, from_attributes=True)
            )
    roads_by_district: dict[UUID, list[RoadResponse]] = {}
    if include_roads:
        roads = (await session.execute(select(Road).order_by(Road.name))).scalars().all()
        for road in roads:
            traffic = latest_traffic.get(road.id)
            road_model = RoadResponse.model_validate(road, from_attributes=True)
            roads_by_district.setdefault(road.from_district_id, []).append(
                road_model.model_copy(
                    update={
                        "latest_traffic": RoadTrafficResponse.model_validate(traffic, from_attributes=True)
                        if traffic
                        else None
                    }
                )
            )
            roads_by_district.setdefault(road.to_district_id, []).append(
                road_model.model_copy(
                    update={
                        "latest_traffic": RoadTrafficResponse.model_validate(traffic, from_attributes=True)
                        if traffic
                        else None
                    }
                )
            )

    results: list[DistrictResponse] = []
    for district in districts:
        score = latest_scores.get(district.id)
        if score is None:
            continue
        payload = DistrictResponse(
            id=district.id,
            name=district.name,
            code=district.code,
            center_lat=district.center_lat,
            center_lon=district.center_lon,
            area_sqkm=district.area_sqkm,
            population=district.population,
            elevation=district.elevation,
            boundary_geojson=district.boundary_geojson,
            scores=_score_bundle(score),
            composite_score=engine.composite_score(
                {
                    "traffic": float(score.traffic_score),
                    "energy": float(score.energy_score),
                    "pollution": float(score.pollution_score),
                    "carbon": float(score.carbon_score),
                    "sustainability": float(score.sustainability_score),
                }
            ),
            last_updated=score.time,
            buildings=buildings_by_district.get(district.id) if include_buildings else None,
            roads=roads_by_district.get(district.id) if include_roads else None,
            history=histories.get(district.id) if include_history else None,
        )
        results.append(payload)
    return results


@router.get("/districts/{district_id}", response_model=DistrictDetailResponse)
async def get_district(
    district_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> DistrictDetailResponse:
    """Return one district with buildings, roads, and recent history.

    curl -s http://localhost:8000/api/v1/twin/districts/<district_id>
    """
    district = await _get_district_or_404(session, district_id)
    latest_scores = await _latest_scores(session)
    latest_traffic = await _latest_road_traffic(session)
    score = latest_scores.get(district.id)
    if score is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="District score not found")

    buildings = (
        await session.execute(select(Building).where(Building.district_id == district.id).order_by(Building.name))
    ).scalars().all()
    roads = (
        await session.execute(
            select(Road).where(
                (Road.from_district_id == district.id) | (Road.to_district_id == district.id)
            )
        )
    ).scalars().all()

    road_payload: list[RoadResponse] = []
    for road in roads:
        traffic = latest_traffic.get(road.id)
        road_payload.append(
            RoadResponse.model_validate(road, from_attributes=True).model_copy(
                update={
                    "latest_traffic": RoadTrafficResponse.model_validate(traffic, from_attributes=True)
                    if traffic
                    else None
                }
            )
        )

    history_rows = (
        await session.execute(
            select(DistrictScore)
            .where(
                DistrictScore.district_id == district.id,
                DistrictScore.time >= datetime.now(UTC) - timedelta(hours=24),
            )
            .order_by(DistrictScore.time.asc())
        )
    ).scalars().all()

    return DistrictDetailResponse(
        id=district.id,
        name=district.name,
        code=district.code,
        center_lat=district.center_lat,
        center_lon=district.center_lon,
        area_sqkm=district.area_sqkm,
        population=district.population,
        elevation=district.elevation,
        boundary_geojson=district.boundary_geojson,
        scores=_score_bundle(score),
        composite_score=engine.composite_score(
            {
                "traffic": float(score.traffic_score),
                "energy": float(score.energy_score),
                "pollution": float(score.pollution_score),
                "carbon": float(score.carbon_score),
                "sustainability": float(score.sustainability_score),
            }
        ),
        last_updated=score.time,
        buildings=[BuildingResponse.model_validate(item, from_attributes=True) for item in buildings],
        roads=road_payload,
        history=[
            ScoreHistoryPoint(time=item.time, value=engine.composite_score(
                {
                    "traffic": float(item.traffic_score),
                    "energy": float(item.energy_score),
                    "pollution": float(item.pollution_score),
                    "carbon": float(item.carbon_score),
                    "sustainability": float(item.sustainability_score),
                }
            ))
            for item in history_rows
        ],
    )


@router.get("/state", response_model=CityStateResponse)
async def get_state(session: AsyncSession = Depends(get_db_session)) -> CityStateResponse:
    """Return the current city-wide digital twin state.

    curl -s http://localhost:8000/api/v1/twin/state
    """
    districts = (await session.execute(select(District))).scalars().all()
    latest_scores = await _latest_scores(session)
    if not latest_scores:
        return CityStateResponse(
            avg_traffic_score=0,
            avg_energy_score=0,
            avg_pollution_score=0,
            avg_carbon_score=0,
            avg_sustainability_score=0,
            overall_composite=0,
            active_districts_count=0,
            total_population=0,
            last_update_time=None,
        )

    score_rows = list(latest_scores.values())
    top = max(districts, key=lambda d: engine.composite_score(
        {
            "traffic": float(latest_scores[d.id].traffic_score),
            "energy": float(latest_scores[d.id].energy_score),
            "pollution": float(latest_scores[d.id].pollution_score),
            "carbon": float(latest_scores[d.id].carbon_score),
            "sustainability": float(latest_scores[d.id].sustainability_score),
        }
    ))
    worst = min(districts, key=lambda d: engine.composite_score(
        {
            "traffic": float(latest_scores[d.id].traffic_score),
            "energy": float(latest_scores[d.id].energy_score),
            "pollution": float(latest_scores[d.id].pollution_score),
            "carbon": float(latest_scores[d.id].carbon_score),
            "sustainability": float(latest_scores[d.id].sustainability_score),
        }
    ))
    now = max(item.time for item in score_rows)
    return CityStateResponse(
        avg_traffic_score=sum(float(item.traffic_score) for item in score_rows) / len(score_rows),
        avg_energy_score=sum(float(item.energy_score) for item in score_rows) / len(score_rows),
        avg_pollution_score=sum(float(item.pollution_score) for item in score_rows) / len(score_rows),
        avg_carbon_score=sum(float(item.carbon_score) for item in score_rows) / len(score_rows),
        avg_sustainability_score=sum(float(item.sustainability_score) for item in score_rows) / len(score_rows),
        overall_composite=sum(
            engine.composite_score(
                {
                    "traffic": float(item.traffic_score),
                    "energy": float(item.energy_score),
                    "pollution": float(item.pollution_score),
                    "carbon": float(item.carbon_score),
                    "sustainability": float(item.sustainability_score),
                }
            )
            for item in score_rows
        )
        / len(score_rows),
        active_districts_count=len(districts),
        total_population=sum(d.population for d in districts),
        last_update_time=now,
        top_performing_district=CityDistrictSummary(
            id=top.id,
            name=top.name,
            code=top.code,
            composite_score=engine.composite_score(
                {
                    "traffic": float(latest_scores[top.id].traffic_score),
                    "energy": float(latest_scores[top.id].energy_score),
                    "pollution": float(latest_scores[top.id].pollution_score),
                    "carbon": float(latest_scores[top.id].carbon_score),
                    "sustainability": float(latest_scores[top.id].sustainability_score),
                }
            ),
        ),
        worst_performing_district=CityDistrictSummary(
            id=worst.id,
            name=worst.name,
            code=worst.code,
            composite_score=engine.composite_score(
                {
                    "traffic": float(latest_scores[worst.id].traffic_score),
                    "energy": float(latest_scores[worst.id].energy_score),
                    "pollution": float(latest_scores[worst.id].pollution_score),
                    "carbon": float(latest_scores[worst.id].carbon_score),
                    "sustainability": float(latest_scores[worst.id].sustainability_score),
                }
            ),
        ),
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(session: AsyncSession = Depends(get_db_session)) -> RefreshResponse:
    """Recalculate all district scores and persist a fresh snapshot.

    curl -X POST http://localhost:8000/api/v1/twin/refresh
    """
    start = datetime.now(UTC)
    updated = await engine.update_all_districts(session)
    elapsed = (datetime.now(UTC) - start).total_seconds() * 1000.0
    return RefreshResponse(
        updated_count=len(updated),
        processing_time_ms=elapsed,
        timestamp=datetime.now(UTC),
    )


@router.get("/districts/{district_id}/history", response_model=DistrictHistoryResponse)
async def district_history(
    district_id: UUID,
    hours: int = Query(default=24, ge=1, le=168),
    metric: Literal["traffic", "energy", "pollution", "carbon", "sustainability", "all"] = Query(default="all"),
    session: AsyncSession = Depends(get_db_session),
) -> DistrictHistoryResponse:
    """Return historical district score data for charts.

    curl -s "http://localhost:8000/api/v1/twin/districts/<id>/history?hours=24&metric=traffic"
    """
    await _get_district_or_404(session, district_id)
    rows = (
        await session.execute(
            select(DistrictScore)
            .where(
                DistrictScore.district_id == district_id,
                DistrictScore.time >= datetime.now(UTC) - timedelta(hours=hours),
            )
            .order_by(DistrictScore.time.asc())
        )
    ).scalars().all()
    metric_map = {
        "traffic": "traffic_score",
        "energy": "energy_score",
        "pollution": "pollution_score",
        "carbon": "carbon_score",
        "sustainability": "sustainability_score",
    }
    data: list[dict[str, Any]] = []
    for row in rows:
        if metric == "all":
            data.append(
                {
                    "time": row.time,
                    "traffic": float(row.traffic_score),
                    "energy": float(row.energy_score),
                    "pollution": float(row.pollution_score),
                    "carbon": float(row.carbon_score),
                    "sustainability": float(row.sustainability_score),
                }
            )
        else:
            data.append({"time": row.time, "value": float(getattr(row, metric_map[metric]))})
    return DistrictHistoryResponse(district_id=district_id, metric=metric, hours=hours, data=data)
