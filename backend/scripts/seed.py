from datetime import UTC, datetime, timedelta
from random import Random

from psycopg import connect

from app.config import get_settings

settings = get_settings()
rng = Random(42)


def main() -> None:
    now = datetime.now(UTC).replace(microsecond=0)
    districts = ["Apex", "Harbor", "Midtown"]

    with connect(settings.database_url, autocommit=True) as connection:
        with connection.cursor() as cursor:
            district_ids: dict[str, int] = {}

            for district in districts:
                cursor.execute(
                    """
                    INSERT INTO districts (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id;
                    """,
                    (district,),
                )
                district_ids[district] = cursor.fetchone()[0]

            for district, district_id in district_ids.items():
                for minutes_ago in range(12):
                    timestamp = now - timedelta(minutes=minutes_ago * 5)
                    metrics = [
                        ("traffic_flow", rng.uniform(48.0, 92.0), "vehicles_per_minute"),
                        ("air_quality_index", rng.uniform(22.0, 71.0), "aqi"),
                        ("grid_load", rng.uniform(58.0, 97.0), "percent"),
                    ]

                    for metric_name, metric_value, unit in metrics:
                        cursor.execute(
                            """
                            INSERT INTO telemetry_events (
                                time,
                                district_id,
                                metric_name,
                                metric_value,
                                unit,
                                metadata
                            )
                            VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                            ON CONFLICT (time, district_id, metric_name)
                            DO UPDATE SET
                                metric_value = EXCLUDED.metric_value,
                                unit = EXCLUDED.unit,
                                metadata = EXCLUDED.metadata;
                            """,
                            (
                                timestamp,
                                district_id,
                                metric_name,
                                round(metric_value, 2),
                                unit,
                                (
                                    '{"district":"%s","source":"phase-0-seed","confidence":0.98}'
                                    % district
                                ),
                            ),
                        )

    print("Seed completed successfully.")


if __name__ == "__main__":
    main()
