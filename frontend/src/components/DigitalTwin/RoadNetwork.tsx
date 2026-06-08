"use client";

import { memo, useMemo } from "react";
import { Line } from "@react-three/drei";
import * as THREE from "three";

import type { District, Road } from "@/src/types/city";

interface Props {
  roads: Road[];
  districts: District[];
}

const congestionColor = (congestion: number) => {
  if (congestion < 0.3) return "#22c55e";
  if (congestion <= 0.6) return "#eab308";
  return "#ef4444";
};

function RoadNetwork({ roads, districts }: Props) {
  const districtMap = useMemo(() => new Map(districts.map((district) => [district.id, district])), [districts]);

  return (
    <group>
      {roads.map((road) => {
        const from = districtMap.get(road.from_district_id);
        const to = districtMap.get(road.to_district_id);
        if (!from || !to) return null;
        const points = [
          new THREE.Vector3((from.center_lon - 80.25) * 1000, 0.8, -(from.center_lat - 13.05) * 1000),
          new THREE.Vector3((to.center_lon - 80.25) * 1000, 0.8, -(to.center_lat - 13.05) * 1000)
        ];
        return (
          <Line
            key={road.id}
            points={points}
            color={congestionColor(road.congestion_level)}
            lineWidth={Math.max(1, Math.min(3, (road.lanes ?? 2) * 0.6))}
            opacity={road.congestion_level > 0.7 ? 0.5 : 0.7}
            transparent
          />
        );
      })}
    </group>
  );
}

export default memo(RoadNetwork);
