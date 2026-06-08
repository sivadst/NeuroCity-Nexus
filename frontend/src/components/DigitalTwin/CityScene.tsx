"use client";

import { memo, Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";

import { DistrictMesh } from "@/src/components/DigitalTwin/DistrictMesh";
import { Environment } from "@/src/components/DigitalTwin/Environment";
import RoadNetwork from "@/src/components/DigitalTwin/RoadNetwork";
import { ScoreOverlay } from "@/src/components/DigitalTwin/ScoreOverlay";
import { LoadingSpinner } from "@/src/components/Shared/LoadingSpinner";
import type { District, Road } from "@/src/types/city";

interface Props {
  districts: District[];
  roads: Road[];
  selectedDistrictId: string | null;
  onSelectDistrict: (district: District) => void;
  showDistricts: boolean;
  showRoads: boolean;
  showScores: boolean;
}

function CityScene({ districts, roads, selectedDistrictId, onSelectDistrict, showDistricts, showRoads, showScores }: Props) {
  return (
    <div className="h-full w-full bg-[#0a0a0a]">
      <Canvas shadows camera={{ position: [80, 80, 80], fov: 45, near: 0.1, far: 1000 }} style={{ width: "100%", height: "100%" }}>
        <Suspense fallback={<LoadingSpinner />}>
          <Environment />
          <OrbitControls enableDamping dampingFactor={0.05} maxPolarAngle={Math.PI / 2.2} />
          {showRoads && <RoadNetwork roads={roads} districts={districts} />}
          {showDistricts &&
            districts.map((district) => (
              <group key={district.id}>
                <DistrictMesh
                  district={district}
                  isSelected={selectedDistrictId === district.id}
                  onClick={() => onSelectDistrict(district)}
                />
                {showScores && <ScoreOverlay district={district} />}
              </group>
            ))}
        </Suspense>
      </Canvas>
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(59,130,246,0.06),transparent_40%)]" />
    </div>
  );
}

export default memo(CityScene);
