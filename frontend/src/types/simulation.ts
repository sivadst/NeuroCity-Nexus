export type ScenarioType = "population_change" | "policy_change" | "infrastructure_change" | "disaster";

export interface ScenarioCreateRequest {
  name: string;
  scenario_type: ScenarioType;
  target_districts: string[];
  changes: Record<string, any>;
  time_horizon_months: number;
}

export interface ScenarioResult {
  scenario_id: string;
  name: string;
  baseline_scores: Record<string, Record<string, number>>;
  predicted_scores: Record<string, Record<string, number>>;
  deltas: Record<string, Record<string, number>>;
  execution_time_ms: number;
  timestamp: string;
}
