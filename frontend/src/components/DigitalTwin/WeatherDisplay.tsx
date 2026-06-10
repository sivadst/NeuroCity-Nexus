"use client";

import { Cloud, CloudFog, CloudRain, CloudLightning, Sun, Wind, Thermometer, Droplets } from "lucide-react";
import { useTwinStore } from "@/src/store/twinStore";

export function WeatherDisplay() {
  const weather = useTwinStore((state) => state.weather);

  if (!weather) return null;

  const Icon = {
    clear: Sun,
    cloudy: Cloud,
    rain: CloudRain,
    storm: CloudLightning,
    fog: CloudFog,
  }[weather.condition];

  return (
    <div className="flex items-center gap-4 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs text-white/90">
      <div className="flex items-center gap-2">
        <Icon className="h-4 w-4 text-blue-400" />
        <span className="capitalize">{weather.condition}</span>
      </div>
      <div className="h-4 w-[1px] bg-white/10" />
      <div className="flex items-center gap-2">
        <Thermometer className="h-3.5 w-3.5 text-orange-400" />
        <span>{weather.temperature}°C</span>
      </div>
      <div className="h-4 w-[1px] bg-white/10" />
      <div className="flex items-center gap-2">
        <Wind className="h-3.5 w-3.5 text-emerald-400" />
        <span>{weather.wind_speed} km/h</span>
      </div>
      <div className="h-4 w-[1px] bg-white/10" />
      <div className="flex items-center gap-2">
        <Droplets className="h-3.5 w-3.5 text-blue-300" />
        <span>AQI: {weather.air_quality_index}</span>
      </div>
    </div>
  );
}
