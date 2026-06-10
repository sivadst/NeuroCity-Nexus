from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.city.weather import WeatherCondition, WeatherReading


class WeatherService:
    """Service for managing weather data."""

    def generate_mock_reading(self, timestamp: datetime | None = None) -> WeatherReading:
        """Generate a realistic mock weather reading."""
        ts = timestamp or datetime.now(UTC)
        hour = ts.hour + ts.minute / 60.0
        
        # Base temperature varies by time of day
        base_temp = 28.0 + 5.0 * random.uniform(-1, 1) # Chennai base
        temp_cycle = -6.0 * (1.0 - abs(hour - 14.0) / 10.0) # Peak at 2pm
        temperature = base_temp + temp_cycle
        
        # Condition logic
        rand = random.random()
        if rand > 0.85:
            condition = WeatherCondition.RAIN
            precipitation = random.uniform(0.5, 5.0)
            humidity = random.uniform(80, 95)
        elif rand > 0.75:
            condition = WeatherCondition.CLOUDY
            precipitation = 0.0
            humidity = random.uniform(60, 80)
        else:
            condition = WeatherCondition.CLEAR
            precipitation = 0.0
            humidity = random.uniform(40, 65)
            
        return WeatherReading(
            time=ts,
            temperature=round(temperature, 1),
            humidity=round(humidity, 1),
            condition=condition,
            wind_speed=round(random.uniform(5, 25), 1),
            precipitation=round(precipitation, 2),
            air_quality_index=random.randint(30, 150),
        )

    async def get_latest_weather(self, session: AsyncSession) -> WeatherReading | None:
        """Fetch the most recent weather reading from the database."""
        stmt = select(WeatherReading).order_by(desc(WeatherReading.time)).limit(1)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_weather(self, session: AsyncSession) -> WeatherReading:
        """Generate and persist a new weather reading."""
        reading = self.generate_mock_reading()
        session.add(reading)
        await session.commit()
        return reading

    async def seed_historical_weather(self, session: AsyncSession, hours: int = 24) -> None:
        """Seed historical weather data for the last N hours."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        for i in range(hours * 12): # 5-minute intervals
            ts = now - timedelta(minutes=5 * i)
            reading = self.generate_mock_reading(ts)
            session.add(reading)
        await session.commit()
