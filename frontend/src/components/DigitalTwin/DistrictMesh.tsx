"use client";

import { memo, useMemo, useRef, useState } from "react";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import { useFrame } from "@react-three/fiber";

import type { District } from "@/src/types/city";

interface Props {
  district: District;
  isSelected: boolean;
  onClick: () => void;
}

const scoreColor = (score: number) => {
  if (score >= 80) return "#22c55e";
  if (score >= 60) return "#eab308";
  if (score >= 40) return "#f97316";
  return "#ef4444";
};

function DistrictMesh({ district, isSelected, onClick }: Props) {
  const ref = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const geometry = useMemo(() => {
    const points = district.boundary_geojson.coordinates[0].map(([lon, lat]) => {
      const x = (lon - 80.25) * 1000;
      const z = -(lat - 13.05) * 1000;
      return new THREE.Vector2(x, z);
    });
    const shape = new THREE.Shape(points);
    return new THREE.ExtrudeGeometry(shape, { depth: district.population / 500000, bevelEnabled: false });
  }, [district]);
  const color = scoreColor(district.composite_score);
  const baseY = district.elevation * 0.12;

  useFrame(({ clock }) => {
    if (!ref.current) return;
    const float = Math.sin(clock.elapsedTime * 0.5) * 0.2;
    ref.current.position.y = baseY + float;
    const targetScale = isSelected ? 1.05 : hovered ? 1.02 : 1;
    ref.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.12);
  });

  return (
    <group>
      <mesh
        ref={ref}
        geometry={geometry}
        castShadow
        receiveShadow
        position={[0, baseY, 0]}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <meshStandardMaterial
          color={color}
          roughness={0.7}
          metalness={0.1}
          emissive={isSelected ? "#ffffff" : "#000000"}
          emissiveIntensity={isSelected ? 0.2 : 0}
        />
      </mesh>
      <Html position={[0, baseY + district.population / 500000 + 1.5, 0]} center>
        <div className="rounded-md bg-black/80 px-2 py-1 text-xs font-mono text-white shadow-lg">
          {district.code} {Math.round(district.composite_score)}
        </div>
      </Html>
    </group>
  );
}

export default memo(DistrictMesh);
