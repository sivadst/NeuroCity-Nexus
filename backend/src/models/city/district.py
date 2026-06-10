from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Numeric, String, func, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class District(Base):
    __tablename__ = "districts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(24), unique=True, nullable=False)
    boundary_geojson: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    center_lat: Mapped[float] = mapped_column(Float, nullable=False)
    center_lon: Mapped[float] = mapped_column(Float, nullable=False)
    area_sqkm: Mapped[float] = mapped_column(Float, nullable=False)
    population: Mapped[int] = mapped_column(nullable=False)
    elevation: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    scores: Mapped[list["DistrictScore"]] = relationship(
        back_populates="district",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="desc(DistrictScore.time)",
    )
    buildings: Mapped[list["Building"]] = relationship(
        back_populates="district",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    roads_from: Mapped[list["Road"]] = relationship(
        back_populates="from_district",
        foreign_keys="Road.from_district_id",
    )
    roads_to: Mapped[list["Road"]] = relationship(
        back_populates="to_district",
        foreign_keys="Road.to_district_id",
    )

    __table_args__ = (
        CheckConstraint("area_sqkm > 0", name="ck_districts_area_positive"),
        CheckConstraint("population >= 0", name="ck_districts_population_non_negative"),
    )


class DistrictScore(Base):
    __tablename__ = "district_scores"

    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True, nullable=False)
    district_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("districts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    traffic_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    energy_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    pollution_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    carbon_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    sustainability_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    district: Mapped[District] = relationship(back_populates="scores")

    __table_args__ = (
        CheckConstraint("traffic_score BETWEEN 0 AND 100", name="ck_district_scores_traffic_range"),
        CheckConstraint("energy_score BETWEEN 0 AND 100", name="ck_district_scores_energy_range"),
        CheckConstraint("pollution_score BETWEEN 0 AND 100", name="ck_district_scores_pollution_range"),
        CheckConstraint("carbon_score BETWEEN 0 AND 100", name="ck_district_scores_carbon_range"),
        CheckConstraint(
            "sustainability_score BETWEEN 0 AND 100",
            name="ck_district_scores_sustainability_range",
        ),
        Index("ix_district_scores_time_district", "time", "district_id"),
    )


from src.models.city.building import Building  # noqa: E402
from src.models.city.road import Road  # noqa: E402
