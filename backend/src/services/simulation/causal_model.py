"""Simple causal impact models for city simulation."""


def predict_traffic_impact(
    population_change_pct: float,
    baseline_traffic_score: float,
    transit_access: float = 0.5,
    road_capacity: float = 1.0
) -> float:
    """Predict traffic score after population change."""
    demand_increase = population_change_pct * 0.85
    transit_absorption = transit_access * 0.25
    capacity_stress = max(0, (1 + demand_increase - transit_absorption) / road_capacity)
    return max(0, baseline_traffic_score - capacity_stress * 35)


def predict_energy_impact(
    population_change_pct: float,
    baseline_energy_score: float,
    industrial_growth: float = 0.0,
    renewable_ratio: float = 0.3
) -> float:
    """Predict energy score after population change."""
    base_demand = population_change_pct * 0.7
    industrial_effect = industrial_growth * 0.4
    renewable_buffer = renewable_ratio * 0.2
    stress = base_demand + industrial_effect - renewable_buffer
    return max(0, baseline_energy_score - stress * 30)


def predict_pollution_impact(
    traffic_change: float,
    energy_change: float,
    baseline_pollution_score: float,
    green_space_ratio: float = 0.15
) -> float:
    """Predict pollution score from traffic and energy changes."""
    combined_stress = traffic_change * 0.6 + energy_change * 0.4
    green_absorption = green_space_ratio * 15
    return max(0, baseline_pollution_score - combined_stress * 25 + green_absorption)


def predict_carbon_impact(
    population_change_pct: float,
    traffic_score_delta: float,
    energy_score_delta: float,
    baseline_carbon_score: float
) -> float:
    """Predict carbon score from population and infrastructure changes."""
    per_capita_increase = population_change_pct * 0.5
    infrastructure_effect = abs(traffic_score_delta + energy_score_delta) * 0.3
    return max(0, baseline_carbon_score - per_capita_increase * 20 - infrastructure_effect)


def predict_sustainability_impact(
    renewable_investment: float,
    transit_investment: float,
    green_investment: float,
    baseline_sustainability_score: float
) -> float:
    """Predict sustainability score from policy investments."""
    total_investment = renewable_investment + transit_investment + green_investment
    improvement = total_investment * 0.15
    return min(100, baseline_sustainability_score + improvement)