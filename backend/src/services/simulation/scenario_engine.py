"""Scenario execution engine for NeuroCity Nexus."""

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.city import District, DistrictScore
from src.services.simulation.causal_model import (
    predict_carbon_impact,
    predict_energy_impact,
    predict_pollution_impact,
    predict_sustainability_impact,
    predict_traffic_impact,
)


@dataclass
class ScenarioConfig:
    name: str
    scenario_type: str
    target_districts: list[str]
    changes: dict[str, Any]
    time_horizon_months: int = 12


@dataclass
class ScenarioResult:
    scenario_id: UUID
    name: str
    baseline_scores: dict[str, dict[str, float]]
    predicted_scores: dict[str, dict[str, float]]
    deltas: dict[str, dict[str, float]]
    execution_time_ms: float
    timestamp: datetime


class ScenarioEngine:
    def __init__(self):
        pass

    async def run_scenario(
        self,
        session: AsyncSession,
        config: ScenarioConfig
    ) -> ScenarioResult:
        start = time.perf_counter()
        scenario_id = uuid4()

        # Get current district scores (latest per district)
        subq = (
            select(DistrictScore.district_id, DistrictScore.time)
            .order_by(DistrictScore.time.desc())
            .distinct(DistrictScore.district_id)
            .subquery()
        )
        
        result = await session.execute(
            select(District, DistrictScore)
            .join(DistrictScore, District.id == DistrictScore.district_id)
            .join(subq, 
                (DistrictScore.district_id == subq.c.district_id) & 
                (DistrictScore.time == subq.c.time)
            )
        )
        rows = result.all()

        baseline_scores = {}
        predicted_scores = {}

        for district, latest_score in rows:
            code = district.code
            baseline = {
                "traffic": float(latest_score.traffic_score),
                "energy": float(latest_score.energy_score),
                "pollution": float(latest_score.pollution_score),
                "carbon": float(latest_score.carbon_score),
                "sustainability": float(latest_score.sustainability_score),
            }
            baseline_scores[code] = baseline
            predicted = self._apply_changes(baseline, config, district)
            predicted_scores[code] = predicted

        # Calculate deltas
        deltas = {}
        for code in baseline_scores:
            deltas[code] = {
                metric: round(predicted_scores[code][metric] - baseline_scores[code][metric], 2)
                for metric in baseline_scores[code]
            }

        execution_time = (time.perf_counter() - start) * 1000

        return ScenarioResult(
            scenario_id=scenario_id,
            name=config.name,
            baseline_scores=baseline_scores,
            predicted_scores=predicted_scores,
            deltas=deltas,
            execution_time_ms=round(execution_time, 2),
            timestamp=datetime.now(timezone.utc),
        )

    def _apply_changes(
        self,
        baseline: dict[str, float],
        config: ScenarioConfig,
        district: District
    ) -> dict[str, float]:
        """Apply scenario changes to baseline scores."""
        predicted = dict(baseline)

        if config.scenario_type == "population_change":
            pop_change = config.changes.get("population_multiplier", 1.0) - 1.0

            predicted["traffic"] = predict_traffic_impact(
                pop_change, baseline["traffic"], transit_access=0.4
            )
            predicted["energy"] = predict_energy_impact(
                pop_change, baseline["energy"], renewable_ratio=0.25
            )
            
            traffic_delta = (baseline["traffic"] - predicted["traffic"]) / 100
            energy_delta = (baseline["energy"] - predicted["energy"]) / 100
            
            predicted["pollution"] = predict_pollution_impact(
                traffic_delta, energy_delta, baseline["pollution"],
            )
            predicted["carbon"] = predict_carbon_impact(
                pop_change,
                predicted["traffic"] - baseline["traffic"],
                predicted["energy"] - baseline["energy"],
                baseline["carbon"],
            )

        elif config.scenario_type == "policy_change":
            renewable_invest = config.changes.get("renewable_investment", 0)
            transit_invest = config.changes.get("transit_investment", 0)
            green_invest = config.changes.get("green_investment", 0)

            predicted["sustainability"] = predict_sustainability_impact(
                renewable_invest, transit_invest, green_invest, baseline["sustainability"]
            )
            predicted["carbon"] = min(100, baseline["carbon"] + renewable_invest * 8)
            predicted["traffic"] = min(100, baseline["traffic"] + transit_invest * 5)

        elif config.scenario_type == "disaster":
            severity = config.changes.get("severity", 0.5)
            affected_metrics = config.changes.get("affected_metrics", ["traffic", "energy", "pollution"])

            for metric in affected_metrics:
                predicted[metric] = max(0, baseline[metric] - severity * 40)

        # Clamp all scores
        return {k: round(max(0, min(100, v)), 2) for k, v in predicted.items()}