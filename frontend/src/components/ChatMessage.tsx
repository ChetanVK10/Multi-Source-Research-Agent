import { Bot, User } from 'lucide-react'
import clsx from 'clsx'
import type { ChatMessage as ChatMessageType } from '../types/api'

export function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === 'user'

  return (
    <article className={clsx('flex gap-3', isUser && 'justify-end')}>
      {!isUser ? (
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400">
          <Bot className="h-5 w-5 text-white" />
        </div>
      ) : null}
      <div className={clsx('max-w-3xl rounded-lg px-4 py-3 shadow-lg', isUser ? 'bg-gradient-to-br from-indigo-500 to-blue-500 text-white' : 'border border-white/10 bg-card text-slate-200')}>
        <div className="whitespace-pre-wrap text-sm leading-7">{message.content}</div>
        <p className={clsx('mt-2 text-[11px] flex items-center justify-between gap-4', isUser ? 'text-indigo-100' : 'text-slate-500')}>
          <span>
            {new Intl.DateTimeFormat(undefined, { hour: '2-digit', minute: '2-digit' }).format(new Date(message.createdAt))}
          </span>
          {!isUser && message.provider && message.model && (
            <span className="font-semibold text-slate-400">
              via {message.provider} / {message.model}
            </span>
          )}
        </p>
      </div>
      {isUser ? (
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-white/10 bg-surface">
          <User className="h-5 w-5 text-slate-300" />
        </div>
      ) : null}
    </article>
  )
}
