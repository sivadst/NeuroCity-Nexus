from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, Float, ForeignKey, Index, Integer, Numeric, String, func, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class RoadType(str, enum.Enum):
    highway = "highway"
    arterial = "arterial"
    residential = "residential"


class Road(Base):
    __tablename__ = "roads"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    road_type: Mapped[RoadType] = mapped_column(Enum(RoadType, name="road_type"), nullable=False)
    from_district_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("districts.id", ondelete="CASCADE"),
        nullable=False,
    )
    to_district_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("districts.id", ondelete="CASCADE"),
        nullable=False,
    )
    geometry_geojson: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    length_m: Mapped[float] = mapped_column(Float, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    lanes: Mapped[int] = mapped_column(Integer, nullable=False)
    speed_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    one_way: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    from_district: Mapped["District"] = relationship(
        back_populates="roads_from",
        foreign_keys=[from_district_id],
    )
    to_district: Mapped["District"] = relationship(
        back_populates="roads_to",
        foreign_keys=[to_district_id],
    )
    traffic_points: Mapped[list["RoadTraffic"]] = relationship(
        back_populates="road",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="desc(RoadTraffic.time)",
    )

    __table_args__ = (
        CheckConstraint("length_m > 0", name="ck_roads_length_positive"),
        CheckConstraint("capacity > 0", name="ck_roads_capacity_positive"),
        CheckConstraint("lanes > 0", name="ck_roads_lanes_positive"),
        CheckConstraint("speed_limit > 0", name="ck_roads_speed_limit_positive"),
    )


class RoadTraffic(Base):
    __tablename__ = "road_traffic"

    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True, nullable=False)
    road_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("roads.id", ondelete="CASCADE"),
        primary_key=True,
    )
    vehicle_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_speed: Mapped[float] = mapped_column(Float, nullable=False)
    congestion_level: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    road: Mapped[Road] = relationship(back_populates="traffic_points")

    __table_args__ = (
        CheckConstraint("vehicle_count >= 0", name="ck_road_traffic_vehicle_non_negative"),
        CheckConstraint("avg_speed >= 0", name="ck_road_traffic_speed_non_negative"),
        CheckConstraint("congestion_level BETWEEN 0 AND 1", name="ck_road_traffic_congestion_range"),
        Index("ix_road_traffic_time_road", "time", "road_id"),
    )


from src.models.city.district import District  # noqa: E402
