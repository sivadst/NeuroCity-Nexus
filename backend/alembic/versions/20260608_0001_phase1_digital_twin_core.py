from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260608_0001"
down_revision = None
branch_labels = None
depends_on = None

road_type_enum = sa.Enum("highway", "arterial", "residential", name="road_type")
building_type_enum = sa.Enum("residential", "commercial", "industrial", "public", name="building_type")


DISTRICTS = [
    {
        "id": "23de7742-6b1d-4f88-93ac-6b935c198001",
        "name": "North Chennai",
        "code": "NCH",
        "center_lat": 13.1466,
        "center_lon": 80.2933,
        "area_sqkm": 76.4,
        "population": 1480000,
        "elevation": 9.0,
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[[80.245, 13.118], [80.322, 13.118], [80.332, 13.182], [80.258, 13.194], [80.245, 13.118]]],
        },
    },
    {
        "id": "23de7742-6b1d-4f88-93ac-6b935c198002",
        "name": "Central Chennai",
        "code": "CCH",
        "center_lat": 13.0711,
        "center_lon": 80.2707,
        "area_sqkm": 54.8,
        "population": 1230000,
        "elevation": 11.0,
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[[80.229, 13.041], [80.304, 13.041], [80.309, 13.097], [80.238, 13.104], [80.229, 13.041]]],
        },
    },
    {
        "id": "23de7742-6b1d-4f88-93ac-6b935c198003",
        "name": "South Chennai",
        "code": "SCH",
        "center_lat": 12.9716,
        "center_lon": 80.2432,
        "area_sqkm": 98.7,
        "population": 1710000,
        "elevation": 14.0,
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[[80.198, 12.926], [80.287, 12.926], [80.295, 13.011], [80.206, 13.018], [80.198, 12.926]]],
        },
    },
    {
        "id": "23de7742-6b1d-4f88-93ac-6b935c198004",
        "name": "West Chennai",
        "code": "WCH",
        "center_lat": 13.0529,
        "center_lon": 80.1956,
        "area_sqkm": 84.1,
        "population": 1380000,
        "elevation": 18.0,
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[[80.144, 13.015], [80.228, 13.015], [80.231, 13.086], [80.153, 13.091], [80.144, 13.015]]],
        },
    },
    {
        "id": "23de7742-6b1d-4f88-93ac-6b935c198005",
        "name": "East Chennai",
        "code": "ECH",
        "center_lat": 13.0358,
        "center_lon": 80.3021,
        "area_sqkm": 61.9,
        "population": 1160000,
        "elevation": 6.0,
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[[80.276, 13.001], [80.344, 13.001], [80.349, 13.067], [80.282, 13.072], [80.276, 13.001]]],
        },
    },
]

ROADS = [
    ("9c03ce88-5af2-4d7d-b285-0165bb900001", "Inner Ring North", "arterial", "23de7742-6b1d-4f88-93ac-6b935c198001", "23de7742-6b1d-4f88-93ac-6b935c198002", 11800.0, 8200, 4, 60, False),
    ("9c03ce88-5af2-4d7d-b285-0165bb900002", "Marina Connector", "arterial", "23de7742-6b1d-4f88-93ac-6b935c198002", "23de7742-6b1d-4f88-93ac-6b935c198005", 7600.0, 6400, 3, 50, True),
    ("9c03ce88-5af2-4d7d-b285-0165bb900003", "OMR Spine", "highway", "23de7742-6b1d-4f88-93ac-6b935c198002", "23de7742-6b1d-4f88-93ac-6b935c198003", 15600.0, 12400, 6, 80, False),
    ("9c03ce88-5af2-4d7d-b285-0165bb900004", "Western Bypass", "highway", "23de7742-6b1d-4f88-93ac-6b935c198004", "23de7742-6b1d-4f88-93ac-6b935c198003", 13200.0, 9800, 5, 70, False),
    ("9c03ce88-5af2-4d7d-b285-0165bb900005", "Port Link Road", "arterial", "23de7742-6b1d-4f88-93ac-6b935c198001", "23de7742-6b1d-4f88-93ac-6b935c198005", 9100.0, 7200, 4, 55, False),
    ("9c03ce88-5af2-4d7d-b285-0165bb900006", "Central Crossway", "arterial", "23de7742-6b1d-4f88-93ac-6b935c198004", "23de7742-6b1d-4f88-93ac-6b935c198002", 8800.0, 6900, 4, 50, False),
    ("9c03ce88-5af2-4d7d-b285-0165bb900007", "Coastal South Link", "residential", "23de7742-6b1d-4f88-93ac-6b935c198005", "23de7742-6b1d-4f88-93ac-6b935c198003", 10400.0, 4300, 2, 40, False),
    ("9c03ce88-5af2-4d7d-b285-0165bb900008", "North West Freight Route", "highway", "23de7742-6b1d-4f88-93ac-6b935c198001", "23de7742-6b1d-4f88-93ac-6b935c198004", 14300.0, 10100, 5, 75, True),
]


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    road_type_enum.create(op.get_bind(), checkfirst=True)
    building_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "districts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("code", sa.String(length=24), nullable=False, unique=True),
        sa.Column("boundary_geojson", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("center_lat", sa.Float(), nullable=False),
        sa.Column("center_lon", sa.Float(), nullable=False),
        sa.Column("area_sqkm", sa.Float(), nullable=False),
        sa.Column("population", sa.Integer(), nullable=False),
        sa.Column("elevation", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("area_sqkm > 0", name="ck_districts_area_positive"),
        sa.CheckConstraint("population >= 0", name="ck_districts_population_non_negative"),
    )
    op.execute(
        "CREATE INDEX ix_districts_center_point ON districts USING spgist ((point(center_lon, center_lat)));"
    )

    op.create_table(
        "district_scores",
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("traffic_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("energy_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("pollution_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("carbon_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("sustainability_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["district_id"], ["districts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("time", "district_id"),
        sa.CheckConstraint("traffic_score BETWEEN 0 AND 100", name="ck_district_scores_traffic_range"),
        sa.CheckConstraint("energy_score BETWEEN 0 AND 100", name="ck_district_scores_energy_range"),
        sa.CheckConstraint("pollution_score BETWEEN 0 AND 100", name="ck_district_scores_pollution_range"),
        sa.CheckConstraint("carbon_score BETWEEN 0 AND 100", name="ck_district_scores_carbon_range"),
        sa.CheckConstraint(
            "sustainability_score BETWEEN 0 AND 100",
            name="ck_district_scores_sustainability_range",
        ),
    )
    op.create_index("ix_district_scores_time_district", "district_scores", ["time", "district_id"])
    op.execute(
        """
        SELECT create_hypertable(
            'district_scores',
            'time',
            if_not_exists => TRUE,
            migrate_data => TRUE,
            chunk_time_interval => INTERVAL '1 day'
        );
        """
    )

    op.create_table(
        "roads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("road_type", road_type_enum, nullable=False),
        sa.Column("from_district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("to_district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("geometry_geojson", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("length_m", sa.Float(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("lanes", sa.Integer(), nullable=False),
        sa.Column("speed_limit", sa.Integer(), nullable=False),
        sa.Column("one_way", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["from_district_id"], ["districts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_district_id"], ["districts.id"], ondelete="CASCADE"),
        sa.CheckConstraint("length_m > 0", name="ck_roads_length_positive"),
        sa.CheckConstraint("capacity > 0", name="ck_roads_capacity_positive"),
        sa.CheckConstraint("lanes > 0", name="ck_roads_lanes_positive"),
        sa.CheckConstraint("speed_limit > 0", name="ck_roads_speed_limit_positive"),
    )

    op.create_table(
        "road_traffic",
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("road_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vehicle_count", sa.Integer(), nullable=False),
        sa.Column("avg_speed", sa.Float(), nullable=False),
        sa.Column("congestion_level", sa.Numeric(4, 3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["road_id"], ["roads.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("time", "road_id"),
        sa.CheckConstraint("vehicle_count >= 0", name="ck_road_traffic_vehicle_non_negative"),
        sa.CheckConstraint("avg_speed >= 0", name="ck_road_traffic_speed_non_negative"),
        sa.CheckConstraint("congestion_level BETWEEN 0 AND 1", name="ck_road_traffic_congestion_range"),
    )
    op.create_index("ix_road_traffic_time_road", "road_traffic", ["time", "road_id"])
    op.execute(
        """
        SELECT create_hypertable(
            'road_traffic',
            'time',
            if_not_exists => TRUE,
            migrate_data => TRUE,
            chunk_time_interval => INTERVAL '1 day'
        );
        """
    )

    op.create_table(
        "buildings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("type", building_type_enum, nullable=False),
        sa.Column("floors", sa.Integer(), nullable=False),
        sa.Column("footprint_area", sa.Float(), nullable=False),
        sa.Column("height_m", sa.Float(), nullable=False),
        sa.Column("energy_consumption_annual", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["district_id"], ["districts.id"], ondelete="CASCADE"),
        sa.CheckConstraint("floors > 0", name="ck_buildings_floors_positive"),
        sa.CheckConstraint("footprint_area > 0", name="ck_buildings_footprint_positive"),
        sa.CheckConstraint("height_m > 0", name="ck_buildings_height_positive"),
        sa.CheckConstraint("energy_consumption_annual >= 0", name="ck_buildings_energy_non_negative"),
    )

    districts_table = sa.table(
        "districts",
        sa.column("id", postgresql.UUID(as_uuid=False)),
        sa.column("name", sa.String()),
        sa.column("code", sa.String()),
        sa.column("boundary_geojson", postgresql.JSONB()),
        sa.column("center_lat", sa.Float()),
        sa.column("center_lon", sa.Float()),
        sa.column("area_sqkm", sa.Float()),
        sa.column("population", sa.Integer()),
        sa.column("elevation", sa.Float()),
    )
    op.bulk_insert(districts_table, DISTRICTS)

    roads_table = sa.table(
        "roads",
        sa.column("id", postgresql.UUID(as_uuid=False)),
        sa.column("name", sa.String()),
        sa.column("road_type", sa.String()),
        sa.column("from_district_id", postgresql.UUID(as_uuid=False)),
        sa.column("to_district_id", postgresql.UUID(as_uuid=False)),
        sa.column("geometry_geojson", postgresql.JSONB()),
        sa.column("length_m", sa.Float()),
        sa.column("capacity", sa.Integer()),
        sa.column("lanes", sa.Integer()),
        sa.column("speed_limit", sa.Integer()),
        sa.column("one_way", sa.Boolean()),
    )
    op.bulk_insert(
        roads_table,
        [
            {
                "id": road_id,
                "name": name,
                "road_type": road_type,
                "from_district_id": from_id,
                "to_district_id": to_id,
                "geometry_geojson": {
                    "type": "LineString",
                    "coordinates": [
                        [next(item["center_lon"] for item in DISTRICTS if item["id"] == from_id), next(item["center_lat"] for item in DISTRICTS if item["id"] == from_id)],
                        [next(item["center_lon"] for item in DISTRICTS if item["id"] == to_id), next(item["center_lat"] for item in DISTRICTS if item["id"] == to_id)],
                    ],
                },
                "length_m": length_m,
                "capacity": capacity,
                "lanes": lanes,
                "speed_limit": speed_limit,
                "one_way": one_way,
            }
            for road_id, name, road_type, from_id, to_id, length_m, capacity, lanes, speed_limit, one_way in ROADS
        ],
    )


def downgrade() -> None:
    op.drop_table("buildings")
    op.drop_index("ix_road_traffic_time_road", table_name="road_traffic")
    op.drop_table("road_traffic")
    op.drop_table("roads")
    op.drop_index("ix_district_scores_time_district", table_name="district_scores")
    op.drop_table("district_scores")
    op.execute("DROP INDEX IF EXISTS ix_districts_center_point;")
    op.drop_table("districts")

    building_type_enum.drop(op.get_bind(), checkfirst=True)
    road_type_enum.drop(op.get_bind(), checkfirst=True)
