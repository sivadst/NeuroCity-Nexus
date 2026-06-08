"use client";

import { Grid, Stars } from "@react-three/drei";

export function Environment() {
  return (
    <>
      <fog attach="fog" args={["#0a0a0a", 50, 300]} />
      <ambientLight intensity={0.4} />
      <directionalLight position={[50, 100, 50]} intensity={1} castShadow />
      <Stars radius={300} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[200, 200]} />
        <meshStandardMaterial color="#1a1a2e" />
      </mesh>
      <Grid args={[200, 200]} sectionSize={5} sectionColor="#2a2a3e" cellColor="#1e1e2f" fadeDistance={140} fadeStrength={1} />
    </>
  );
}
