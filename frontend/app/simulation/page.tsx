"use client";

import { useState } from "react";
import { Header } from "@/src/components/Layout/Header";
import { Play, TrendingUp, AlertTriangle, Building2, Users } from "lucide-react";
import { runScenario } from "@/src/lib/api";
import { ScenarioResult, ScenarioType } from "@/src/types/simulation";

export default function SimulationPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [scenarioType, setScenarioType] = useState<ScenarioType>("population_change");

  const executeSimulation = async () => {
    setLoading(true);
    try {
      const payload = {
        name: `Test ${scenarioType} ${new Date().toLocaleTimeString()}`,
        scenario_type: scenarioType,
        target_districts: ["all"],
        changes: scenarioType === "population_change" 
          ? { population_multiplier: 1.2 }
          : scenarioType === "policy_change"
          ? { renewable_investment: 0.8, transit_investment: 0.5, green_investment: 0.3 }
          : scenarioType === "infrastructure_change"
          ? { road_expansion_km: 15.0, new_transit_lines: 3 }
          : { severity: 0.7, affected_metrics: ["traffic", "energy"] },
        time_horizon_months: 12,
      };
      const res = await runScenario(payload as any);
      setResult(res);
    } catch (error) {
      console.error("Simulation failed", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <Header />
      <main className="container mx-auto p-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Scenario Simulation</h1>
            <p className="text-white/50">Run what-if scenarios to predict city performance impacts.</p>
          </div>
          <button
            onClick={executeSimulation}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2.5 font-semibold transition hover:bg-blue-500 disabled:opacity-50"
          >
            {loading ? "Simulating..." : <><Play className="h-4 w-4" /> Run Simulation</>}
          </button>
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-4">
          <div className="space-y-4 lg:col-span-1">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-white/40">Scenario Type</h2>
            {[
              { id: "population_change", label: "Population Growth", icon: Users },
              { id: "policy_change", label: "Policy Investment", icon: TrendingUp },
              { id: "infrastructure_change", label: "Infrastructure", icon: Building2 },
              { id: "disaster", label: "Crisis Event", icon: AlertTriangle },
            ].map((type) => (
              <button
                key={type.id}
                onClick={() => setScenarioType(type.id as ScenarioType)}
                className={`flex w-full items-center gap-3 rounded-xl border p-4 transition ${
                  scenarioType === type.id 
                    ? "border-blue-500 bg-blue-500/10 text-blue-400" 
                    : "border-white/10 bg-white/5 text-white/70 hover:bg-white/10"
                }`}
              >
                <type.icon className="h-5 w-5" />
                <span className="font-medium">{type.label}</span>
              </button>
            ))}
          </div>

          <div className="lg:col-span-3">
            {result ? (
              <div className="rounded-2xl border border-white/10 bg-white/5 p-8">
                <div className="mb-6 flex items-center justify-between">
                  <h3 className="text-xl font-bold">{result.name}</h3>
                  <span className="text-xs text-white/40">Executed in {result.execution_time_ms}ms</span>
                </div>

                <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {Object.entries(result.deltas).slice(0, 6).map(([district, metrics]) => (
                    <div key={district} className="rounded-xl bg-black/40 p-5 border border-white/5">
                      <h4 className="mb-3 font-semibold text-blue-400">{district}</h4>
                      <div className="space-y-2">
                        {Object.entries(metrics).map(([metric, delta]) => (
                          <div key={metric} className="flex items-center justify-between text-sm">
                            <span className="capitalize text-white/60">{metric}</span>
                            <span className={`font-mono ${delta >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                              {delta >= 0 ? "+" : ""}{delta}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex h-[400px] flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 text-white/30">
                <Play className="mb-4 h-12 w-12 opacity-20" />
                <p>Select a scenario type and click 'Run Simulation' to see predictions.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
