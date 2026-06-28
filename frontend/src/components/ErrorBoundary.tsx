import { Component, type ErrorInfo, type ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'

export class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  state = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(error, info)
  }

  render() {
    if (!this.state.hasError) return this.props.children

    return (
      <main className="flex min-h-screen items-center justify-center bg-background p-6 text-slate-100">
        <section className="max-w-md rounded-lg border border-rose-400/30 bg-surface p-6 shadow-2xl">
          <AlertTriangle className="h-8 w-8 text-rose-300" />
          <h1 className="mt-4 text-xl font-semibold">Something broke in the interface.</h1>
          <p className="mt-2 text-sm text-slate-400">Refresh the page after checking the browser console for details.</p>
        </section>
      </main>
    )
  }
}
