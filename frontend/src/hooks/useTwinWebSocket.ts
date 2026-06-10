"use client";

import { useEffect, useRef } from "react";

import { fetchCityState, fetchDistricts } from "@/src/lib/api";
import { useTwinStore } from "@/src/store/twinStore";

const MAX_BACKOFF = 30000;

export function useTwinWebSocket() {
  const { setDistricts, updateDistrictScores, setCityState, setWeather, setConnectionStatus, setLastUpdate } = useTwinStore();
  const socketRef = useRef<WebSocket | null>(null);
  const backoffRef = useRef(1000);
  const heartbeatRef = useRef<number | null>(null);
  const pongTimerRef = useRef<number | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);

  useEffect(() => {
    let stopped = false;

    const clearTimers = () => {
      if (heartbeatRef.current) window.clearInterval(heartbeatRef.current);
      if (pongTimerRef.current) window.clearTimeout(pongTimerRef.current);
      if (reconnectTimerRef.current) window.clearTimeout(reconnectTimerRef.current);
    };

    const connect = async () => {
      if (stopped) return;
      setConnectionStatus("connecting");

      try {
        const [districts, cityState] = await Promise.all([fetchDistricts(true, true, true), fetchCityState()]);
        if (stopped) return;
        setDistricts(districts);
        setCityState(cityState);
        if (cityState.weather) {
          setWeather(cityState.weather);
        }

        const socket = new WebSocket("ws://localhost:8000/ws/twin");
        socketRef.current = socket;

        socket.onopen = () => {
          setConnectionStatus("connected");
          backoffRef.current = 1000;
          heartbeatRef.current = window.setInterval(() => {
            if (socket.readyState === WebSocket.OPEN) {
              socket.send(JSON.stringify({ action: "ping" }));
              if (pongTimerRef.current) window.clearTimeout(pongTimerRef.current);
              pongTimerRef.current = window.setTimeout(() => socket.close(), 10000);
            }
          }, 30000);
        };

        socket.onmessage = (event) => {
          const payload = JSON.parse(event.data);
          if (payload.type === "score_update") {
            updateDistrictScores(payload.districts);
            if (payload.weather) {
              setWeather(payload.weather);
            }
            setLastUpdate(payload.timestamp);
          }
 else if (payload.type === "heartbeat" || payload.type === "pong") {
            if (pongTimerRef.current) window.clearTimeout(pongTimerRef.current);
          }
        };

        socket.onclose = () => {
          clearTimers();
          setConnectionStatus("disconnected");
          if (!stopped) {
            reconnectTimerRef.current = window.setTimeout(connect, backoffRef.current);
            backoffRef.current = Math.min(backoffRef.current * 2, MAX_BACKOFF);
          }
        };

        socket.onerror = () => socket.close();
      } catch {
        setConnectionStatus("disconnected");
        if (!stopped) {
          reconnectTimerRef.current = window.setTimeout(connect, backoffRef.current);
          backoffRef.current = Math.min(backoffRef.current * 2, MAX_BACKOFF);
        }
      }
    };

    void connect();

    return () => {
      stopped = true;
      clearTimers();
      socketRef.current?.close();
    };
  }, [setCityState, setConnectionStatus, setDistricts, setLastUpdate, updateDistrictScores]);

  return useTwinStore((state) => ({
    districts: state.districts,
    cityState: state.cityState,
    selectedDistrict: state.selectedDistrict,
    connectionStatus: state.connectionStatus,
    lastUpdate: state.lastUpdate,
    selectDistrict: state.selectDistrict,
    showDistricts: state.showDistricts,
    showRoads: state.showRoads,
    showBuildings: state.showBuildings,
    showScores: state.showScores,
    setLayerVisibility: state.setLayerVisibility
  }));
}
