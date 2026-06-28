import { useEffect, useMemo, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { Eraser, Send, Sparkles } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'
import { ChatMessage } from '../components/ChatMessage'
import { EmptyState } from '../components/EmptyState'
import { SourcesPanel } from '../components/SourcesPanel'
import { TypingIndicator } from '../components/TypingIndicator'
import { useChatMutation, useModelsQuery, useChatQuery } from '../hooks/useResearch'
import type { ChatMessage as ChatMessageType } from '../types/api'
import { useToast } from '../hooks/useToast'

export function ResearchChatPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const activeChatId = searchParams.get('id')

  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const [question, setQuestion] = useState('')
  const bottomRef = useRef<HTMLDivElement | null>(null)
  
  const chat = useChatMutation()
  const { data: activeChat, isLoading: isActiveChatLoading } = useChatQuery(activeChatId)
  const modelsQuery = useModelsQuery()
  const { notify } = useToast()

  const [selectedProvider, setSelectedProvider] = useState<string>('')
  const [selectedModel, setSelectedModel] = useState<string>('')

  const latestAssistant = useMemo(() => [...messages].reverse().find((message) => message.role === 'assistant'), [messages])

  // Sync messages with current conversation history
  useEffect(() => {
    if (activeChatId && activeChat) {
      
      // eslint-disable-next-line react-hooks/set-state-in-effect
      
      setMessages(
        activeChat.messages.map((m) => ({
          id: crypto.randomUUID(),
          role: m.role as 'user' | 'assistant',
          content: m.content,
          createdAt: m.timestamp,

          citations: m.citations ?? [],
          evidence: m.evidence ?? [],
          provider: m.provider,
          model: m.model,
        }))
      )
    } else if (!activeChatId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setMessages([])
    }
  }, [activeChatId, activeChat])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, chat.isPending])

  useEffect(() => {
    if (modelsQuery.data && modelsQuery.data.length > 0 && !selectedProvider) {
      const defaultProv = modelsQuery.data.find((p) => p.is_available) || modelsQuery.data[0]
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSelectedProvider(defaultProv.id)
      if (defaultProv.models.length > 0) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setSelectedModel(defaultProv.models[0].id)
      }
    }
  }, [modelsQuery.data, selectedProvider])

  const handleProviderChange = (providerId: string) => {
    setSelectedProvider(providerId)
    const prov = modelsQuery.data?.find((p) => p.id === providerId)
    if (prov && prov.models.length > 0) {
      setSelectedModel(prov.models[0].id)
    } else {
      setSelectedModel('')
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const trimmed = question.trim()
    if (!trimmed || chat.isPending) return

    const userMessage: ChatMessageType = {
      id: crypto.randomUUID(),
      role: 'user',
      content: trimmed,
      createdAt: new Date().toISOString(),
    }

    setMessages((items) => [...items, userMessage])
    setQuestion('')

    try {
      const response = await chat.mutateAsync({
        question: trimmed,
        top_k: 8,
        include_sources: true,
        provider: selectedProvider || undefined,
        model: selectedModel || undefined,
        conversation_id: activeChatId || undefined,
      })

      const assistantMessage: ChatMessageType = {
        id: response.query_id,
        role: 'assistant',
        content: response.answer ?? response.message ?? 'The backend returned no answer.',
        createdAt: new Date().toISOString(),
        citations: response.citations,
        evidence: response.evidence,
        provider: response.provider,
        model: response.model,
      }

      setMessages((items) => [...items, assistantMessage])

      // If this was a new conversation, update URL parameter
      if (!activeChatId && response.conversation_id) {
        setSearchParams({ id: response.conversation_id })
      }
    } catch (error) {
      notify({
        kind: 'error',
        title: 'Research request failed',
        message: error instanceof Error ? error.message : 'Check the backend connection.',
      })
      setMessages((items) => [
        ...items,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'I could not complete that research request. Please verify the backend is running and try again.',
          createdAt: new Date().toISOString(),
        },
      ])
    }
  }

  return (
    <div className="grid h-[calc(100vh-6.5rem)] min-h-[680px] gap-4 xl:grid-cols-[minmax(0,1fr)_24rem]">
      <section className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-white/10 bg-surface/82 shadow-2xl shadow-black/20">
        <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
          <div>
            <p className="text-sm font-semibold text-slate-100">Grounded answer workspace</p>
            <p className="text-xs text-slate-500">Planner, retrievers, reranker, synthesizer</p>
          </div>
          <button
            className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-sm text-slate-300 transition hover:border-cyan-300/30 hover:text-cyan-200"
            onClick={() => setSearchParams({})}
          >
            <Eraser className="h-4 w-4" />
            New chat
          </button>
        </div>
        <div className="min-h-0 flex-1 space-y-6 overflow-y-auto p-4 sm:p-6">
          {isActiveChatLoading ? (
            <div className="flex flex-col gap-6">
              <div className="h-20 w-3/4 animate-pulse rounded-lg bg-white/5" />
              <div className="h-32 w-2/3 animate-pulse rounded-lg bg-white/5 align-self-end ml-auto" />
            </div>
          ) : !messages.length ? (
            <EmptyState
              icon={Sparkles}
              title="Ask a research question"
              description="Your backend will plan source usage, retrieve evidence from documents, web, and SQL, then synthesize an answer with citations."
            />
          ) : (
            messages.map((message) => <ChatMessage key={message.id} message={message} />)
          )}
          {chat.isPending ? <TypingIndicator /> : null}
          <div ref={bottomRef} />
        </div>
        <form className="border-t border-white/10 p-4" onSubmit={submit}>
          {modelsQuery.isLoading && (
            <div className="flex items-center justify-between pb-3">
              <div className="flex gap-4">
                <div className="h-9 w-28 animate-pulse rounded bg-white/5" />
                <div className="h-9 w-36 animate-pulse rounded bg-white/5" />
              </div>
              <div className="h-4 w-48 animate-pulse rounded bg-white/5" />
            </div>
          )}

          {modelsQuery.data && modelsQuery.data.length > 0 && (
            <div className="flex flex-wrap items-center justify-between gap-4 pb-3">
              <div className="flex gap-4">
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">LLM Provider</label>
                  <select
                    value={selectedProvider}
                    onChange={(e) => handleProviderChange(e.target.value)}
                    className="rounded-md border border-white/10 bg-slate-900 px-2.5 py-1.5 text-xs text-slate-200 outline-none focus:border-cyan-300/40 cursor-pointer"
                  >
                    {modelsQuery.data.map((prov) => (
                      <option key={prov.id} value={prov.id} disabled={!prov.is_available}>
                        {prov.name} {!prov.is_available ? '(Unavailable)' : ''}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Model</label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="rounded-md border border-white/10 bg-slate-900 px-2.5 py-1.5 text-xs text-slate-200 outline-none focus:border-cyan-300/40 cursor-pointer"
                  >
                    {modelsQuery.data
                      .find((prov) => prov.id === selectedProvider)
                      ?.models.map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.name}
                        </option>
                      )) || <option value="">No models available</option>}
                  </select>
                </div>
              </div>
              <div className="text-xs text-slate-400 font-medium">
                Using:{' '}
                <span className="text-cyan-300 font-semibold">
                  {modelsQuery.data.find((p) => p.id === selectedProvider)?.name || selectedProvider}
                </span>{' '}
                /{' '}
                <span className="text-indigo-300 font-semibold">
                  {modelsQuery.data
                    .find((p) => p.id === selectedProvider)
                    ?.models.find((m) => m.id === selectedModel)?.name || selectedModel}
                </span>
              </div>
            </div>
          )}

          <div className="flex gap-3 rounded-lg border border-white/10 bg-background p-2 focus-within:border-cyan-300/40">
            <textarea
              className="max-h-36 min-h-12 flex-1 resize-none bg-transparent px-2 py-2 text-sm leading-6 text-slate-100 outline-none placeholder:text-slate-600"
              placeholder="Ask about your documents, fresh web context, or connected SQL data..."
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault()
                  event.currentTarget.form?.requestSubmit()
                }
              }}
            />
            <button
              className="grid h-12 w-12 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400 text-white shadow-lg shadow-cyan-950/40 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
              disabled={!question.trim() || chat.isPending}
              aria-label="Send message"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </form>
      </section>
      <SourcesPanel citations={latestAssistant?.citations ?? []} evidence={latestAssistant?.evidence ?? []} />
    </div>
  )
}
