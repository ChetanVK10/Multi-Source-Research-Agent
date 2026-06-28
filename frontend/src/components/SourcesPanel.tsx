import { ChevronDown, Database, FileText, Globe } from 'lucide-react'
import { useMemo, useState } from 'react'
import clsx from 'clsx'
import type { Citation, Evidence, SourceType } from '../types/api'

function sourceMeta(source?: SourceType) {
  if (source === 'web') return { label: 'Web', icon: Globe, className: 'border-cyan-300/25 bg-cyan-400/10 text-cyan-200' }
  if (source === 'sql') return { label: 'SQL', icon: Database, className: 'border-amber-300/25 bg-amber-400/10 text-amber-200' }
  return { label: 'Document', icon: FileText, className: 'border-indigo-300/25 bg-indigo-400/10 text-indigo-200' }
}

export function SourcesPanel({ citations, evidence }: { citations: Citation[]; evidence: Evidence[] }) {
  const [openIds, setOpenIds] = useState<Set<string>>(new Set())

  const evidenceById = useMemo(() => {
    return new Map(evidence.map((item) => [item.evidence_id, item]))
  }, [evidence])

  if (!citations.length && !evidence.length) {
    return (
      <aside className="rounded-lg border border-white/10 bg-surface p-5">
        <p className="text-sm font-medium text-slate-200">Sources</p>
        <p className="mt-2 text-sm text-slate-500">Citations returned by the backend will appear here.</p>
      </aside>
    )
  }

  return (
    <aside className="rounded-lg border border-white/10 bg-surface">
      <div className="border-b border-white/10 p-4">
        <p className="text-sm font-semibold text-slate-100">Sources</p>
        <p className="mt-1 text-xs text-slate-500">{citations.length} citations, {evidence.length} evidence items</p>
      </div>
      <div className="max-h-[calc(100vh-12rem)] space-y-3 overflow-y-auto p-3">
        {(citations.length ? citations : evidence.map((item) => ({
          citation_id: item.evidence_id,
          source_id: item.evidence_id,
          title: item.title,
          url: item.url,
          snippet: item.content,
        }))).map((citation) => {
          const matchingEvidence = evidenceById.get(citation.source_id) ?? evidence.find((item) => item.title === citation.title)
          const meta = sourceMeta(matchingEvidence?.source)
          const Icon = meta.icon
          const isOpen = openIds.has(citation.citation_id)
          const confidence = matchingEvidence?.score ?? null

          return (
            <article key={citation.citation_id} className="rounded-lg border border-white/10 bg-card p-3">
              <button
                className="flex w-full items-start justify-between gap-3 text-left"
                onClick={() => {
                  const next = new Set(openIds)
                  if (isOpen) next.delete(citation.citation_id)
                  else next.add(citation.citation_id)
                  setOpenIds(next)
                }}
              >
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={clsx('inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium', meta.className)}>
                      <Icon className="h-3 w-3" />
                      {meta.label}
                    </span>
                    <span className="text-xs text-slate-500">{citation.citation_id}</span>
                  </div>
                  <h3 className="mt-2 line-clamp-2 text-sm font-medium text-slate-100">{citation.title ?? 'Untitled source'}</h3>
                </div>
                <ChevronDown className={clsx('mt-1 h-4 w-4 shrink-0 text-slate-500 transition', isOpen && 'rotate-180')} />
              </button>
              <div className="mt-3">
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Confidence</span>
                  <span>{confidence == null ? 'N/A' : `${Math.round(confidence * 100)}%`}</span>
                </div>
                <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/10">
                  <div className="h-full rounded-full bg-gradient-to-r from-indigo-400 to-cyan-300" style={{ width: `${Math.max(12, (confidence ?? 0.62) * 100)}%` }} />
                </div>
              </div>
              {isOpen ? (
                <div className="mt-3 border-t border-white/10 pt-3">
                  <p className="text-sm leading-6 text-slate-400">{citation.snippet ?? matchingEvidence?.content ?? 'No excerpt provided.'}</p>
                  {citation.url ? (
                    <a className="mt-3 inline-flex max-w-full truncate text-sm text-cyan-300 hover:text-cyan-200" href={citation.url} target="_blank" rel="noreferrer">
                      {citation.url}
                    </a>
                  ) : null}
                </div>
              ) : null}
            </article>
          )
        })}
      </div>
    </aside>
  )
}
