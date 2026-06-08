"use client";

import { X } from "lucide-react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { District } from "@/src/types/city";

interface Props {
  district: District | null;
  onClose: () => void;
}

const scoreColor = (score: number) => (score >= 80 ? "#22c55e" : score >= 60 ? "#eab308" : score >= 40 ? "#f97316" : "#ef4444");

export function DetailPanel({ district, onClose }: Props) {
  if (!district) {
    return (
      <aside className="fixed right-0 top-0 hidden h-screen w-[400px] border-l border-[#1a1a2e] bg-[#0f0f1a] p-6 text-white lg:block">
        <p className="text-sm text-white/70">Select a district to view details</p>
      </aside>
    );
  }

  const history = district.history ?? [];

  return (
    <aside className="fixed bottom-0 right-0 z-20 h-[45vh] w-full border-t border-[#1a1a2e] bg-[#0f0f1a] p-4 text-white lg:bottom-auto lg:top-0 lg:h-screen lg:w-[400px] lg:border-l lg:border-t-0 lg:p-6">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-semibold">{district.name}</h2>
          <p className="text-sm text-white/60">
            <span className="rounded-full bg-white/10 px-2 py-1 font-mono">{district.code}</span>{" "}
            {district.population.toLocaleString()} people, {district.area_sqkm.toFixed(1)} km2
          </p>
        </div>
        <button onClick={onClose} className="rounded-full border border-white/10 p-2 text-white/70">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        {Object.entries(district.scores).map(([key, value]) => (
          <div key={key} className="rounded-xl border border-white/10 bg-white/5 p-3">
            <div className="mb-2 flex items-center justify-between text-xs uppercase text-white/60">
              <span>{key.replace("_score", "")}</span>
              <span>{value.toFixed(0)}</span>
            </div>
            <div className="h-2 rounded-full bg-white/10">
              <div className="h-2 rounded-full" style={{ width: `${value}%`, backgroundColor: scoreColor(value) }} />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 h-36 rounded-xl border border-white/10 bg-white/5 p-3">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={history}>
            <XAxis dataKey="time" hide />
            <YAxis hide domain={[0, 100]} />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 max-h-[180px] overflow-y-auto rounded-xl border border-white/10 bg-white/5 p-3">
        {(district.buildings ?? []).map((building) => (
          <div key={building.id} className="mb-2 rounded-lg bg-black/20 p-2 text-sm">
            <div className="flex items-center justify-between">
              <span>{building.name}</span>
              <span className="text-xs text-white/50">{building.type}</span>
            </div>
            <p className="text-xs text-white/60">
              {building.floors} floors, {building.energy_consumption_annual.toFixed(0)} kWh
            </p>
          </div>
        ))}
      </div>
    </aside>
  );
}
