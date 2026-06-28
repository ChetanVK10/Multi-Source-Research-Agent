import type { LucideIcon } from 'lucide-react'
import clsx from 'clsx'

export function StatusCard({
  title,
  value,
  detail,
  status,
  icon: Icon,
}: {
  title: string
  value: string
  detail: string
  status: 'ok' | 'warning' | 'error' | 'unknown'
  icon: LucideIcon
}) {
  return (
    <article className="rounded-lg border border-white/10 bg-card p-5 shadow-xl shadow-black/15">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{title}</p>
          <h3 className="mt-3 text-lg font-semibold text-slate-100">{value}</h3>
        </div>
        <div
          className={clsx(
            'rounded-lg p-2',
            status === 'ok' && 'bg-emerald-400/10 text-emerald-300',
            status === 'warning' && 'bg-amber-400/10 text-amber-300',
            status === 'error' && 'bg-rose-400/10 text-rose-300',
            status === 'unknown' && 'bg-slate-500/10 text-slate-300',
          )}
        >
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <p className="mt-4 text-sm leading-6 text-slate-400">{detail}</p>
    </article>
  )
}
