import { Outlet, useLocation } from 'react-router-dom'
import { Activity, Menu } from 'lucide-react'
import { useState } from 'react'
import clsx from 'clsx'
import { Sidebar } from '../components/Sidebar'
import { useHealthQuery } from '../hooks/useResearch'

const pageTitles: Record<string, string> = {
  '/chat': 'Research Chat',
  '/upload': 'Document Upload',
  '/documents': 'Document Management',
  '/health': 'System Health',
}

export function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()
  const health = useHealthQuery()
  const isOnline = health.data?.status === 'ok'

  return (
    <div className="min-h-screen bg-background text-slate-100">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_30%_-10%,rgba(79,70,229,0.22),transparent_32%),radial-gradient(circle_at_90%_10%,rgba(34,211,238,0.12),transparent_28%)]" />
      <div className="relative flex min-h-screen">
        <Sidebar
          collapsed={collapsed}
          mobileOpen={mobileOpen}
          onCloseMobile={() => setMobileOpen(false)}
          onToggleCollapsed={() => setCollapsed((value) => !value)}
          status={isOnline ? 'online' : health.isError ? 'offline' : 'checking'}
        />
        <div className={clsx('flex min-w-0 flex-1 flex-col transition-all', collapsed ? 'lg:pl-20' : 'lg:pl-72')}>
          <header className="sticky top-0 z-20 border-b border-white/10 bg-background/82 backdrop-blur-xl">
            <div className="flex h-16 items-center justify-between gap-4 px-4 sm:px-6">
              <div className="flex min-w-0 items-center gap-3">
                <button
                  className="rounded-md border border-white/10 bg-surface p-2 text-slate-300 transition hover:border-cyan-300/40 hover:text-cyan-200 lg:hidden"
                  onClick={() => setMobileOpen(true)}
                  aria-label="Open navigation"
                >
                  <Menu className="h-5 w-5" />
                </button>
                <div className="min-w-0">
                  <h1 className="truncate text-base font-semibold sm:text-lg">{pageTitles[location.pathname] ?? 'Research Agent'}</h1>
                </div>
              </div>
              <div className="flex items-center gap-3 rounded-full border border-white/10 bg-surface px-3 py-1.5 text-xs text-slate-300">
                <span className={clsx('h-2 w-2 rounded-full', isOnline ? 'bg-emerald-400' : health.isError ? 'bg-rose-400' : 'bg-amber-400')} />
                <Activity className="h-4 w-4 text-cyan-300" />
                <span className="hidden sm:inline">{health.data?.environment ?? 'checking'}</span>
              </div>
            </div>
          </header>
          <main className="min-h-0 flex-1 p-4 sm:p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
