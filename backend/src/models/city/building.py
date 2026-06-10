from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class BuildingType(str, enum.Enum):
    residential = "residential"
    commercial = "commercial"
    industrial = "industrial"
    public = "public"


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    district_id: Mapped[str] = mapped_column(String(36), ForeignKey("districts.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # residential/commercial/industrial/public
    floors: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    footprint_area: Mapped[float] = mapped_column(Float, nullable=False)
    height_m: Mapped[float] = mapped_column(Float, nullable=True)
    energy_consumption_annual: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    district = relationship("District", back_populates="buildings")

    __table_args__ = (
        CheckConstraint("floors > 0", name="ck_buildings_floors_positive"),
        CheckConstraint("footprint_area > 0", name="ck_buildings_foot