import uuid

from sqlalchemy import Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


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

    district = relationship("District", back_populates="buildings")

    __table_args__ = (
        Index("idx_buildings_district", "district_id"),
        Index("idx_buildings_type", "type"),
    )
