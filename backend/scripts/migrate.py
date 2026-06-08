from psycopg import connect

from app.config import get_settings

settings = get_settings()


def main() -> None:
    with connect(settings.database_url, autocommit=True) as connection:
        with connection.cursor() as cursor:
            # Enable TimescaleDB and create the base schema used in development.
            cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS districts (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS telemetry_events (
                    time TIMESTAMPTZ NOT NULL,
                    district_id INTEGER NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
                    metric_name TEXT NOT NULL,
                    metric_value DOUBLE PRECISION NOT NULL,
                    unit TEXT NOT NULL,
                    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                    PRIMARY KEY (time, district_id, metric_name)
                );
                """
            )
            cursor.execute(
                """
                SELECT create_hypertable(
                    'telemetry_events',
                    'time',
                    if_not_exists => TRUE,
                    migrate_data => TRUE
                );
                """
            )
    print("Migration completed successfully.")


if __name__ == "__main__":
    main()
