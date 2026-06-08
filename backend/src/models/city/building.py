from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class BuildingType(str, enum.Enum):
    residential = "residential"
    commercial = "commercial"
    industrial = "industrial"
    public = "public"


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    district_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("districts.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    type: Mapped[BuildingType] = mapped_column(Enum(BuildingType, name="building_type"), nullable=False)
    floors: Mapped[int] = mapped_column(Integer, nullable=False)
    footprint_area: Mapped[float] = mapped_column(Float, nullable=False)
    height_m: Mapped[float] = mapped_column(Float, nullable=False)
    energy_consumption_annual: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    district: Mapped["District"] = relationship(back_populates="buildings")

    __table_args__ = (
        CheckConstraint("floors > 0", name="ck_buildings_floors_positive"),
        CheckConstraint("footprint_area > 0", name="ck_buildings_footprint_positive"),
        CheckConstraint("height_m > 0", name="ck_buildings_height_positive"),
        CheckConstraint(
            "energy_consumption_annual >= 0",
            name="ck_buildings_energy_non_negative",
        ),
    )


from src.models.city.district import District  # noqa: E402
