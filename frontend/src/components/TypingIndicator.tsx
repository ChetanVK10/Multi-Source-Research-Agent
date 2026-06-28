export function TypingIndicator() {
  return (
    <div className="flex gap-1 rounded-lg border border-white/10 bg-card px-4 py-3">
      <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300 [animation-delay:-0.2s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300 [animation-delay:-0.1s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-300" />
    </div>
  )
}
