"use client";

import Link from "next/link";
import { Brain, RefreshCcw, Settings } from "lucide-react";

import { refreshScores } from "@/src/lib/api";
import { useTwinStore } from "@/src/store/twinStore";

const navItems = ["Dashboard", "Digital Twin", "Simulation", "Copilot", "Crisis", "Forecasting", "RL", "XAI"];

export function Header() {
  const connectionStatus = useTwinStore((state) => state.connectionStatus);
  const lastUpdate = useTwinStore((state) => state.lastUpdate);

  return (
    <header className="flex items-center justify-between border-b border-white/10 bg-[#0f0f1a]/90 px-4 py-3 backdrop-blur">
      <div className="flex items-center gap-3">
        <Brain className="h-6 w-6 text-blue-400" />
        <span className="font-semibold tracking-wide text-white">NeuroCity Nexus</span>
      </div>
      <nav className="hidden items-center gap-5 lg:flex">
        {navItems.map((item) => (
          <Link key={item} href="#" className="text-sm text-white/70 transition hover:text-white">
            {item}
          </Link>
        ))}
      </nav>
      <div className="flex items-center gap-3 text-sm">
        <span className="flex items-center gap-2 text-white/70">
          <span
            className={`h-2.5 w-2.5 rounded-full ${
              connectionStatus === "connected"
                ? "bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.8)]"
                : connectionStatus === "connecting"
                  ? "bg-amber-400"
                  : "bg-red-400"
            }`}
          />
          {connectionStatus}
        </span>
        <span className="hidden text-white/50 md:inline">{lastUpdate ? new Date(lastUpdate).toLocaleTimeString() : "—"}</span>
        <button
          type="button"
          onClick={() => void refreshScores()}
          className="rounded-full border border-white/10 p-2 text-white/70 transition hover:bg-white/5 hover:text-white"
        >
          <RefreshCcw className="h-4 w-4" />
        </button>
        <button type="button" className="rounded-full border border-white/10 p-2 text-white/70 transition hover:bg-white/5 hover:text-white">
          <Settings className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
