export interface District {
  id: string;
  name: string;
  code: string;
  center_lat: number;
  center_lon: number;
  boundary_geojson: {
    type: "Polygon";
    coordinates: number[][][];
  };
  area_sqkm: number;
  population: number;
  elevation: number;
  scores: {
    traffic_score: number;
    energy_score: number;
    pollution_score: number;
    carbon_score: number;
    sustainability_score: number;
  };
  composite_score: number;
  last_updated: string;
  buildings?: Building[];
  roads?: Road[];
  history?: ScoreHistoryPoint[];
}

export interface Road {
  id: string;
  name: string;
  from_district_id: string;
  to_district_id: string;
  geometry_geojson: {
    type: "LineString";
    coordinates: number[][];
  };
  congestion_level: number;
  vehicle_count: number;
  avg_speed: number;
  capacity: number;
  lanes?: number;
}

export interface Building {
  id: string;
  name: string;
  type: "residential" | "commercial" | "industrial" | "public";
  floors: number;
  footprint_area: number;
  height_m: number;
  energy_consumption_annual: number;
}

export interface CityState {
  avg_traffic_score: number;
  avg_energy_score: number;
  avg_pollution_score: number;
  avg_carbon_score: number;
  avg_sustainability_score: number;
  overall_composite: number;
  active_districts_count: number;
  total_population: number;
  last_update_time: string;
  top_performing_district: { id: string; name: string; composite_score: number } | null;
  worst_performing_district: { id: string; name: string; composite_score: number } | null;
}

export interface ScoreHistoryPoint {
  time: string;
  value: number;
  traffic?: number;
  energy?: number;
  pollution?: number;
  carbon?: number;
  sustainability?: number;
}

export interface ScoreUpdate {
  type: "score_update";
  timestamp: string;
  districts: Array<{
    id: string;
    name: string;
    scores: District["scores"];
    composite_score: number;
    changed: boolean;
  }>;
}
