from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ScoreBundle(BaseModel):
    traffic_score: float = Field(ge=0, le=100)
    energy_score: float = Field(ge=0, le=100)
    pollution_score: float = Field(ge=0, le=100)
    carbon_score: float = Field(ge=0, le=100)
    sustainability_score: float = Field(ge=0, le=100)


class RoadTrafficResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    time: datetime
    vehicle_count: int
    avg_speed: float
    congestion_level: float


class RoadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    road_type: str
    from_district_id: UUID
    to_district_id: UUID
    geometry_geojson: dict[str, Any]
    length_m: float
    capacity: int
    lanes: int
    speed_limit: int
    one_way: bool
    latest_traffic: RoadTrafficResponse | None = None


class BuildingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    district_id: UUID
    name: str
    type: str
    floors: int
    footprint_area: float
    height_m: float
    energy_consumption_annual: float


class ScoreHistoryPoint(BaseModel):
    time: datetime
    value: float


class DistrictResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    center_lat: float
    center_lon: float
    area_sqkm: float
    population: int
    elevation: float
    boundary_geojson: dict[str, Any]
    scores: ScoreBundle
    composite_score: float
    last_updated: datetime | None = None
    buildings: list[BuildingResponse] | None = None
    roads: list[RoadResponse] | None = None
    history: list[ScoreHistoryPoint] | None = None


class DistrictDetailResponse(DistrictResponse):
    buildings: list[BuildingResponse] = Field(default_factory=list)
    roads: list[RoadResponse] = Field(default_factory=list)
    history: list[ScoreHistoryPoint] = Field(default_factory=list)


class DistrictHistoryResponse(BaseModel):
    district_id: UUID
    metric: Literal["traffic", "energy", "pollution", "carbon", "sustainability", "all"]
    hours: int
    data: list[dict[str, Any]]


class CityDistrictSummary(BaseModel):
    id: UUID
    name: str
    code: str
    composite_score: float


class WeatherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    time: datetime
    temperature: float
    humidity: float
    condition: str
    wind_speed: float
    precipitation: float
    air_quality_index: int


class CityStateResponse(BaseModel):
    avg_traffic_score: float
    avg_energy_score: float
    avg_pollution_score: float
    avg_carbon_score: float
    avg_sustainability_score: float
    overall_composite: float
    active_districts_count: int
    total_population: int
    last_update_time: datetime | None
    top_performing_district: CityDistrictSummary | None = None
    worst_performing_district: CityDistrictSummary | None = None
    weather: WeatherResponse | None = None


class RefreshResponse(BaseModel):
    updated_count: int
    processing_time_ms: float
    timestamp: datetime
