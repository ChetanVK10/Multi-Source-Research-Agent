import type { LucideIcon } from 'lucide-react'

export function EmptyState({ icon: Icon, title, description }: { icon: LucideIcon; title: string; description: string }) {
  return (
    <div className="grid min-h-64 place-items-center rounded-lg border border-dashed border-white/10 bg-surface/60 p-8 text-center">
      <div>
        <Icon className="mx-auto h-10 w-10 text-cyan-300" />
        <h2 className="mt-4 text-lg font-semibold text-slate-100">{title}</h2>
        <p className="mt-2 max-w-md text-sm leading-6 text-slate-400">{description}</p>
      </div>
    </div>
  )
}
