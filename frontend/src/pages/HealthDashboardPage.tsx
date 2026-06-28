import { Activity, Database, GitBranch, Server, Waypoints } from 'lucide-react'
import { StatusCard } from '../components/StatusCard'
import { Skeleton } from '../components/Skeleton'
import { useHealthQuery } from '../hooks/useResearch'

export function HealthDashboardPage() {
  const health = useHealthQuery()

  if (health.isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => <Skeleton key={index} className="h-40" />)}
      </div>
    )
  }

  const backendOk = health.data?.status === 'ok'

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-white/10 bg-surface p-5">
        <p className="text-sm font-semibold text-slate-100">Runtime overview</p>
        <p className="mt-1 text-sm text-slate-500">
          Health data is read from `/health`. Dependent service cards reflect configured backend capabilities and should be upgraded when dedicated probes are exposed.
        </p>
      </section>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatusCard
          title="Backend"
          value={backendOk ? 'Operational' : 'Unavailable'}
          detail={health.data ? `${health.data.app_name} v${health.data.app_version}` : 'Unable to reach FastAPI.'}
          status={backendOk ? 'ok' : 'error'}
          icon={Server}
        />
        <StatusCard
          title="Qdrant"
          value={backendOk ? 'Configured' : 'Unknown'}
          detail="Document retrieval is available through the backend workflow when vector settings are configured."
          status={backendOk ? 'ok' : 'unknown'}
          icon={Waypoints}
        />
        <StatusCard
          title="PostgreSQL"
          value={backendOk ? 'Routable' : 'Unknown'}
          detail="SQL retrieval is routed by LangGraph and validated server-side before execution."
          status={backendOk ? 'ok' : 'unknown'}
          icon={Database}
        />
        <StatusCard
          title="LangSmith"
          value={backendOk ? 'Backend controlled' : 'Unknown'}
          detail="Tracing state depends on backend environment variables and LangSmith credentials."
          status="warning"
          icon={GitBranch}
        />
      </div>
      <section className="rounded-lg border border-white/10 bg-card p-5">
        <div className="flex items-center gap-3">
          <Activity className="h-5 w-5 text-cyan-300" />
          <p className="text-sm font-semibold text-slate-100">Environment</p>
        </div>
        <dl className="mt-5 grid gap-4 sm:grid-cols-3">
          <div>
            <dt className="text-xs uppercase tracking-wider text-slate-500">Status</dt>
            <dd className="mt-1 text-sm text-slate-200">{health.data?.status ?? 'offline'}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-slate-500">Environment</dt>
            <dd className="mt-1 text-sm text-slate-200">{health.data?.environment ?? 'unknown'}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-slate-500">Refresh</dt>
            <dd className="mt-1 text-sm text-slate-200">Every 30 seconds</dd>
          </div>
        </dl>
      </section>
    </div>
  )
}
