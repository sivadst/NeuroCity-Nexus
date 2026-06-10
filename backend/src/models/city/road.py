from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, Numeric, String, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class RoadType(str, enum.Enum):
    highway = "highway"
    arterial = "arterial"
    residential = "residential"


class Road(Base):
    __tablename__ = "roads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    road_type: Mapped[str] = mapped_column(String(20), nullable=False)  # highway/arterial/residential
    from_district_id: Mapped[str] = mapped_column(String(36), ForeignKey("districts.id", ondelete="CASCADE"), nullable=False)
    to_district_id: Mapped[str] = mapped_column(String(36), ForeignKey("districts.id", ondelete="CASCADE"), nullable=False)
    geometry_geojson: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    length_m: Mapped[float] = mapped_column(Float, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    lanes: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    speed_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    one_way: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    from_district = relationship("District", foreign_keys=[from_district_id], back_populates="roads_from")
    to_district = relationship("District", foreign_keys=[to_district_id], back_populates="roads_to")
    traffic_readings = relationship("RoadTraffic", back_populates="road", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("length_m > 0", name="ck_roads_length_positive"),
        CheckConstraint("capacity > 0", name="ck_roads_capacity_positive"),
        CheckConstraint("lanes > 0", name="ck_roads_lanes_positive"),
        CheckConstraint("speed_limit > 0", name="ck_roads_speed_limit_positive"),
        Index("idx_roads_from_to", "from_district_id", "to_district_id"),
        Index("idx_roads_type", "road_type"),
    )


class RoadTraffic(Base):
    __tablename__ = "road_traffic"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    road_id: Mapped[str] = mapped_column(String(36), ForeignKey("roads.id", ondelete="CASCADE"), nullable=False)
    vehicle_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_speed: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    congestion_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    road = relationship("Road", back_populates="traffic_readings")

    __table_args__ = (
        CheckConstraint("vehicle_count >= 0", name="ck_road_traffic_vehicle_non_negative"),
        CheckConstraint("avg_speed >= 0", name="ck_road_traffic_speed_non_negative"),
        CheckConstraint("congestion_level >= 0 AND congestion_level <= 1", name="ck_congestion_0_1"),
        Index("idx_road_traffic_time_road", "time", "road_id"),
    )


from src.models.city.district import District  # noqa: E402