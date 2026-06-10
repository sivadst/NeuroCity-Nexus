"""Simulation API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db_session
from src.services.simulation.scenario_engine import ScenarioConfig, ScenarioEngine

router = APIRouter(prefix="/simulation", tags=["simulation"])


class ScenarioCreateRequest(BaseModel):
    name: str
    scenario_type: str = Field(..., pattern="^(population_change|policy_change|infrastructure_change|disaster)$")
    target_districts: list[str]
    changes: dict
    time_horizon_months: int = Field(default=12, ge=1, le=60)


class ScenarioResultResponse(BaseModel):
    scenario_id: str
    name: str
    baseline_scores: dict[str, dict[str, float]]
    predicted_scores: dict[str, dict[str, float]]
    deltas: dict[str, dict[str, float]]
    execution_time_ms: float
    timestamp: str


@router.post("/scenarios", response_model=ScenarioResultResponse, status_code=status.HTTP_201_CREATED)
async def create_and_run_scenario(
    request: ScenarioCreateRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Create and run a new simulation scenario."""
    engine = ScenarioEngine()

    config = ScenarioConfig(
        name=request.name,
        scenario_type=request.scenario_type,
        target_districts=request.target_districts,
        changes=request.changes,
        time_horizon_months=request.time_horizon_months,
    )

    result = await engine.run_scenario(session, config)

    return ScenarioResultResponse(
        scenario_id=str(result.scenario_id),
        name=result.name,
        baseline_scores=result.baseline_scores,
        predicted_scores=result.predicted_scores,
        deltas=result.deltas,
        execution_time_ms=result.execution_time_ms,
        timestamp=result.timestamp.isoformat(),
    )


@router.post("/scenarios/quick/population")
async def quick_population_scenario(
    population_multiplier: float = 1.15,
    target_districts: list[str] = None,
    session: AsyncSession = Depends(get_db_session),
):
    """Quick population change scenario."""
    if target_districts is None:
        target_districts = ["all"]

    request = ScenarioCreateRequest(
        name=f"Population x{population_multiplier}",
        scenario_type="population_change",
        target_districts=target_districts,
        changes={"population_multiplier": population_multiplier},
    )

    return await create_and_run_scenario(request, session)