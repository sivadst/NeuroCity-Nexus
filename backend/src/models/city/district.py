import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class District(Base):
    __tablename__ = "districts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(24), unique=True, nullable=False)
    boundary_geojson: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    center_lat: Mapped[float] = mapped_column(Float, nullable=False)
    center_lon: Mapped[float] = mapped_column(Float, nullable=False)
    area_sqkm: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    population: Mapped[int] = mapped_column(Numeric, nullable=False, default=0)
    elevation: Mapped[float] = mapped_column(Float, nullable=True)

    scores = relationship("DistrictScore", back_populates="district", cascade="all, delete-orphan")
    buildings = relationship("Building", back_populates="district", cascade="all, delete-orphan")
    roads_from = relationship("Road", foreign_keys="Road.from_district_id", back_populates="from_district")
    roads_to = relationship("Road", foreign_keys="Road.to_district_id", back_populates="to_district")

    __table_args__ = (
        Index("idx_districts_code", "code"),
        Index("idx_districts_center", "center_lat", "center_lon"),
    )


class DistrictScore(Base):
    __tablename__ = "district_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    district_id: Mapped[str] = mapped_column(String(36), ForeignKey("districts.id", ondelete="CASCADE"), nullable=False)
    traffic_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    energy_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pollution_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    carbon_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sustainability_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    district = relationship("District", back_populates="scores")

    __table_args__ = (
        Index("idx_district_scores_time_district", "time", "district_id"),
    )
