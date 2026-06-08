"use client";

import { useEffect, useMemo } from "react";

import CityScene from "@/src/components/DigitalTwin/CityScene";
import { DetailPanel } from "@/src/components/DigitalTwin/DetailPanel";
import { Legend } from "@/src/components/DigitalTwin/Legend";
import { ErrorBoundary } from "@/src/components/Shared/ErrorBoundary";
import { Header } from "@/src/components/Layout/Header";
import { useTwinWebSocket } from "@/src/hooks/useTwinWebSocket";
import { useTwinStore } from "@/src/store/twinStore";

export function DigitalTwinShell() {
  const {
    districts,
    selectedDistrict,
    selectDistrict,
    connectionStatus,
    lastUpdate,
    showDistricts,
    showRoads,
    showBuildings,
    showScores
  } = useTwinWebSocket();
  const setConnectionStatus = useTwinStore((state) => state.setConnectionStatus);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        selectDistrict(null);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [selectDistrict]);

  useEffect(() => {
    setConnectionStatus(connectionStatus);
  }, [connectionStatus, setConnectionStatus]);

  const roads = useMemo(
    () => Array.from(new Map(districts.flatMap((district) => district.roads ?? []).map((road) => [road.id, road])).values()),
    [districts]
  );

  return (
    <div className="relative h-screen overflow-hidden bg-[#0a0a0a] text-white">
      <Header />
      <main className="relative h-[calc(100vh-57px)]">
        <ErrorBoundary>
          <CityScene
            districts={districts}
            roads={roads}
            selectedDistrictId={selectedDistrict?.id ?? null}
            onSelectDistrict={selectDistrict}
            showDistricts={showDistricts}
            showRoads={showRoads}
            showScores={showScores}
          />
        </ErrorBoundary>
      </main>
      <DetailPanel district={selectedDistrict} onClose={() => selectDistrict(null)} />
      <Legend />
      <div className="fixed right-[420px] top-16 hidden rounded-full bg-black/50 px-3 py-1 text-xs text-white/70 lg:block">
        Last update: {lastUpdate ? new Date(lastUpdate).toLocaleTimeString() : "waiting"}
      </div>
      {showBuildings ? null : null}
    </div>
  );
}
