import { Activity, Database, GitBranch, Server, Waypoints } from 'lucide-react'
import { StatusCard } from '../components/StatusCard'
import { Skeleton } from '../components/Skeleton'
import { useHealthQuery } from '../hooks/useResearch'
import { Globe } from "lucide-react"
import { BrainCircuit } from "lucide-react"

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
        <p className="text-sm font-semibold text-slate-100">Runtime Status</p>
        <p className="mt-1 text-sm text-slate-500">
        Current runtime status of the application services.
        </p>
      </section>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        
        <StatusCard
            title="Backend"
            value={backendOk ? "Operational" : "Offline"}
            detail={
              health.data
                ? "FastAPI backend with LangGraph orchestration."
                : "Unable to connect to backend."
       }   
       status={backendOk ? "ok" : "error"}
       icon={Server}
      />      
        <StatusCard
          title="Qdrant"
          value={backendOk ? 'Configured' : 'Unknown'}
          detail="Vector database storing document embeddings for semantic retrieval."
          status={backendOk ? 'ok' : 'unknown'}
          icon={Waypoints}
        />
        <StatusCard
  title="Web Search"
  value={backendOk ? "Operational" : "Offline"}
  detail="Tavily Search API for real-time web retrieval."
  status={backendOk ? "ok" : "error"}
  icon={Globe}
/>
        <StatusCard
  title="Embeddings"
  value={backendOk ? "Ready" : "Unavailable"}
  detail="BAAI/bge-small-en-v1.5 for semantic document embeddings."
  status={backendOk ? "ok" : "error"}
  icon={BrainCircuit}
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
