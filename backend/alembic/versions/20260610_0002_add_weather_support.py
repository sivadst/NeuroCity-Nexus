from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260610_0002"
down_revision = "20260608_0001"
branch_labels = None
depends_on = None

weather_condition_enum = sa.Enum("clear", "cloudy", "rain", "storm", "fog", name="weather_condition")

def upgrade() -> None:
    weather_condition_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "weather_readings",
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("humidity", sa.Float(), nullable=False),
        sa.Column("condition", weather_condition_enum, nullable=False),
        sa.Column("wind_speed", sa.Float(), nullable=False),
        sa.Column("precipitation", sa.Float(), nullable=False),
        sa.Column("air_quality_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("time"),
        sa.CheckConstraint("humidity BETWEEN 0 AND 100", name="ck_weather_humidity_range"),
        sa.CheckConstraint("air_quality_index >= 0", name="ck_weather_aqi_positive"),
    )
    op.create_index("ix_weather_readings_time", "weather_readings", ["time"])
    op.execute(
        """
        SELECT create_hypertable(
            'weather_readings',
            'time',
            if_not_exists => TRUE,
            migrate_data => TRUE,
            chunk_time_interval => INTERVAL '1 day'
        );
        """
    )

def downgrade() -> None:
    op.drop_index("ix_weather_readings_time", table_name="weather_readings")
    op.drop_table("weather_readings")
    weather_condition_enum.drop(op.get_bind(), checkfirst=True)
