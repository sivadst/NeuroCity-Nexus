"use client";

import { Html } from "@react-three/drei";

import type { District } from "@/src/types/city";

const color = (score: number) => (score >= 80 ? "#22c55e" : score >= 60 ? "#eab308" : score >= 40 ? "#f97316" : "#ef4444");

export function ScoreOverlay({ district }: { district: District }) {
  return (
    <Html position={[(district.center_lon - 80.25) * 1000, district.population / 500000 + 4, -(district.center_lat - 13.05) * 1000]} center>
      <div
        className="rounded-full px-2 py-1 text-xs font-mono text-white shadow-lg"
        style={{ backgroundColor: color(district.composite_score) }}
      >
        {district.code} {Math.round(district.composite_score)}
      </div>
    </Html>
  );
}
