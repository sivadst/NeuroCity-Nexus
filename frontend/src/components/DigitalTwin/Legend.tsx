"use client";

import { useTwinStore } from "@/src/store/twinStore";

export function Legend() {
  const { showDistricts, showRoads, showBuildings, showScores, setLayerVisibility } = useTwinStore();

  return (
    <div className="fixed bottom-4 left-4 z-20 rounded-xl border border-white/10 bg-[#0f0f1a]/80 p-4 text-white backdrop-blur">
      <p className="mb-2 text-sm font-semibold">District Scores</p>
      <div className="mb-3 grid grid-cols-4 gap-2 text-[10px]">
        <div className="rounded bg-[#22c55e] px-2 py-1">80-100</div>
        <div className="rounded bg-[#eab308] px-2 py-1">60-79</div>
        <div className="rounded bg-[#f97316] px-2 py-1">40-59</div>
        <div className="rounded bg-[#ef4444] px-2 py-1">0-39</div>
      </div>
      <div className="flex flex-wrap gap-2 text-xs">
        {[
          ["showDistricts", "Districts", showDistricts],
          ["showRoads", "Roads", showRoads],
          ["showBuildings", "Buildings", showBuildings],
          ["showScores", "Scores", showScores]
        ].map(([key, label, active]) => (
          <button
            key={key}
            onClick={() => setLayerVisibility(key as "showDistricts" | "showRoads" | "showBuildings" | "showScores", !active)}
            className={`rounded-full border px-3 py-1 ${active ? "border-blue-400 bg-blue-500/20" : "border-white/10 bg-white/5"}`}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
