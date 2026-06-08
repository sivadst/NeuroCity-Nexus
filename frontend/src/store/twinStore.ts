import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { CityState, District, ScoreUpdate } from "@/src/types/city";

interface TwinState {
  districts: District[];
  selectedDistrict: District | null;
  cityState: CityState | null;
  connectionStatus: "connected" | "disconnected" | "connecting";
  lastUpdate: string | null;
  showDistricts: boolean;
  showRoads: boolean;
  showBuildings: boolean;
  showScores: boolean;
  setDistricts: (districts: District[]) => void;
  updateDistrictScores: (updates: ScoreUpdate["districts"]) => void;
  selectDistrict: (district: District | null) => void;
  setCityState: (state: CityState) => void;
  setConnectionStatus: (status: TwinState["connectionStatus"]) => void;
  setLastUpdate: (time: string) => void;
  setLayerVisibility: (layer: "showDistricts" | "showRoads" | "showBuildings" | "showScores", value: boolean) => void;
}

export const useTwinStore = create<TwinState>()(
  persist(
    (set) => ({
      districts: [],
      selectedDistrict: null,
      cityState: null,
      connectionStatus: "disconnected",
      lastUpdate: null,
      showDistricts: true,
      showRoads: true,
      showBuildings: false,
      showScores: true,
      setDistricts: (districts) => set({ districts }),
      updateDistrictScores: (updates) =>
        set((state) => {
          const nextDistricts = state.districts.map((district) => {
            const update = updates.find((item) => item.id === district.id);
            return update
              ? {
                  ...district,
                  scores: update.scores,
                  composite_score: update.composite_score,
                  last_updated: new Date().toISOString()
                }
              : district;
          });
          const selectedUpdate = state.selectedDistrict
            ? updates.find((item) => item.id === state.selectedDistrict.id)
            : null;
          return {
            districts: nextDistricts,
            selectedDistrict: state.selectedDistrict && selectedUpdate
              ? {
                  ...state.selectedDistrict,
                  scores: selectedUpdate.scores,
                  composite_score: selectedUpdate.composite_score,
                  last_updated: new Date().toISOString()
                }
              : state.selectedDistrict,
            lastUpdate: new Date().toISOString()
          };
        }),
      selectDistrict: (district) => set({ selectedDistrict: district }),
      setCityState: (state) => set({ cityState: state }),
      setConnectionStatus: (status) => set({ connectionStatus: status }),
      setLastUpdate: (time) => set({ lastUpdate: time }),
      setLayerVisibility: (layer, value) => set({ [layer]: value } as Partial<TwinState>)
    }),
    {
      name: "neurocity-twin-store",
      partialize: (state) => ({
        selectedDistrict: state.selectedDistrict,
        showDistricts: state.showDistricts,
        showRoads: state.showRoads,
        showBuildings: state.showBuildings,
        showScores: state.showScores
      })
    }
  )
);
