import { createContext } from 'react'

export type ToastKind = 'success' | 'error' | 'info'
export type Toast = { id: string; title: string; message?: string; kind: ToastKind }

export const ToastContext = createContext<{ notify: (toast: Omit<Toast, 'id'>) => void } | null>(null)
