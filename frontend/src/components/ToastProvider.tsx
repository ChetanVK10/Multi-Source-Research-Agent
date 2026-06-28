import { useCallback, useMemo, useState } from 'react'
import { CheckCircle2, Info, X, XCircle } from 'lucide-react'
import clsx from 'clsx'

import { ToastContext, type Toast } from './toast-context'

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const remove = useCallback((id: string) => {
    setToasts((items) => items.filter((toast) => toast.id !== id))
  }, [])

  const notify = useCallback(
    (toast: Omit<Toast, 'id'>) => {
      const id = crypto.randomUUID()
      setToasts((items) => [...items, { ...toast, id }])
      window.setTimeout(() => remove(id), 4800)
    },
    [remove],
  )

  const value = useMemo(() => ({ notify }), [notify])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-4 top-4 z-50 flex w-[calc(100%-2rem)] max-w-sm flex-col gap-3">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={clsx(
              'rounded-lg border bg-card/95 p-4 shadow-2xl shadow-black/30 backdrop-blur',
              toast.kind === 'success' && 'border-emerald-400/30',
              toast.kind === 'error' && 'border-rose-400/30',
              toast.kind === 'info' && 'border-cyan-400/30',
            )}
          >
            <div className="flex items-start gap-3">
              {toast.kind === 'success' ? (
                <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-300" />
              ) : toast.kind === 'error' ? (
                <XCircle className="mt-0.5 h-5 w-5 text-rose-300" />
              ) : (
                <Info className="mt-0.5 h-5 w-5 text-cyan-300" />
              )}
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-slate-100">{toast.title}</p>
                {toast.message ? <p className="mt-1 text-sm text-slate-400">{toast.message}</p> : null}
              </div>
              <button className="text-slate-500 transition hover:text-slate-200" onClick={() => remove(toast.id)}>
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
