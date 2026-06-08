import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[#0a0a0a] px-6 py-20 text-white">
      <div className="mx-auto max-w-4xl rounded-3xl border border-white/10 bg-[#0f0f1a] p-10 shadow-2xl">
        <p className="text-sm uppercase tracking-[0.3em] text-blue-400">NeuroCity Nexus</p>
        <h1 className="mt-4 text-5xl font-semibold">City Brain AI foundation</h1>
        <p className="mt-4 max-w-2xl text-white/70">
          FastAPI, TimescaleDB, Redis, and Next.js are wired for Phase 1 digital twin development.
        </p>
        <div className="mt-8 flex gap-3">
          <Link href="/digital-twin" className="rounded-full bg-blue-500 px-5 py-3 font-medium text-white">
            Open Digital Twin
          </Link>
        </div>
      </div>
    </main>
  );
}
