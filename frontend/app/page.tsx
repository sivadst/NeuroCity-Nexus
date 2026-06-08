const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">Phase 0 Foundation</p>
        <h1>NeuroCity Nexus</h1>
        <p className="lede">
          A containerized city-brain development stack with TimescaleDB, Redis,
          FastAPI, and Next.js ready for the next phase of the platform.
        </p>
        <div className="card-row">
          <article className="card">
            <span className="label">Backend</span>
            <strong>FastAPI</strong>
            <p>{apiBaseUrl}</p>
          </article>
          <article className="card">
            <span className="label">Database</span>
            <strong>PostgreSQL 15 + TimescaleDB</strong>
            <p>High-ingest telemetry storage</p>
          </article>
          <article className="card">
            <span className="label">Realtime</span>
            <strong>Redis 7</strong>
            <p>Caching, messaging, and coordination</p>
          </article>
        </div>
      </section>
    </main>
  );
}
