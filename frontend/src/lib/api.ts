import axios from "axios";

import type { Building, CityState, District, Road } from "@/src/types/city";
import type { ScenarioCreateRequest, ScenarioResult } from "@/src/types/simulation";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
});

export async function fetchDistricts(include_history = false, include_buildings = true, include_roads = true): Promise<District[]> {
  const response = await api.get<District[]>("/api/v1/twin/districts", {
    params: { include_history, include_buildings, include_roads }
  });
  return response.data;
}

export async function fetchDistrict(id: string): Promise<District & { buildings: Building[]; roads: Road[]; history: any[] }> {
  const response = await api.get<District & { buildings: Building[]; roads: Road[]; history: any[] }>(
    `/api/v1/twin/districts/${id}`
  );
  return response.data;
}

export async function fetchCityState(): Promise<CityState> {
  const response = await api.get<CityState>("/api/v1/twin/state");
  return response.data;
}

export async function refreshScores(): Promise<{ updated_districts: number; processing_time_ms: number }> {
  const response = await api.post<{ updated_districts: number; processing_time_ms: number }>("/api/v1/twin/refresh");
  return response.data;
}

export async function runScenario(request: ScenarioCreateRequest): Promise<ScenarioResult> {
  const response = await api.post<ScenarioResult>("/api/v1/simulation/scenarios", request);
  return response.data;
}
