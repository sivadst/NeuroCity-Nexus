import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


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

    from_district = relationship("District", foreign_keys=[from_district_id], back_populates="roads_from")
    to_district = relationship("District", foreign_keys=[to_district_id], back_populates="roads_to")
    traffic_readings = relationship("RoadTraffic", back_populates="road", cascade="all, delete-orphan")

    __table_args__ = (
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
        Index("idx_road_traffic_time_road", "time", "road_id"),
        CheckConstraint("congestion_level >= 0 AND congestion_level <= 1", name="ck_congestion_0_1"),
    )
