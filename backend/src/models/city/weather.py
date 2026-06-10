from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, Float, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class WeatherCondition(str, enum.Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    FOG = "fog"


class WeatherReading(Base):
    __tablename__ = "weather_readings"

    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    condition: Mapped[WeatherCondition] = mapped_column(Enum(WeatherCondition), nullable=False)
    wind_speed: Mapped[float] = mapped_column(Float, nullable=False)
    precipitation: Mapped[float] = mapped_column(Float, nullable=False)
    air_quality_index: Mapped[int] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint("humidity BETWEEN 0 AND 100", name="ck_weather_humidity_range"),
        CheckConstraint("air_quality_index >= 0", name="ck_weather_aqi_positive"),
        Index("ix_weather_readings_time", "time"),
    )
