import {
  Activity,
  Bot,
  ChevronLeft,
  ChevronRight,
  FileUp,
  HeartPulse,
  Sparkles,
  X,
  FileText,
  Plus,
  Edit2,
  Trash2,
  Check,
} from 'lucide-react'
import { NavLink, useNavigate, useSearchParams } from 'react-router-dom'
import clsx from 'clsx'
import { useState } from 'react'
import {
  useChatsQuery,
  useRenameChatMutation,
  useDeleteChatMutation,
  useDeleteAllChatsMutation,
} from '../hooks/useResearch'

const navItems = [
  { to: '/chat', label: 'Research', icon: Bot },
  { to: '/upload', label: 'Upload', icon: FileUp },
  { to: '/documents', label: 'Documents', icon: FileText },
  { to: '/health', label: 'Health', icon: HeartPulse },
]

export function Sidebar({
  collapsed,
  mobileOpen,
  status,
  onCloseMobile,
  onToggleCollapsed,
}: {
  collapsed: boolean
  mobileOpen: boolean
  status: 'online' | 'offline' | 'checking'
  onCloseMobile: () => void
  onToggleCollapsed: () => void
}) {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const activeChatId = searchParams.get('id')

  const { data: chats } = useChatsQuery()
  const renameChat = useRenameChatMutation()
  const deleteChat = useDeleteChatMutation()
  const deleteAllChats = useDeleteAllChatsMutation()

  const [editingChatId, setEditingChatId] = useState<string | null>(null)
  const [editingTitle, setEditingTitle] = useState('')

  const handleStartRename = (id: string, currentTitle: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingChatId(id)
    setEditingTitle(currentTitle)
  }

  const handleSaveRename = (id: string, e: React.MouseEvent | React.FormEvent) => {
    e.stopPropagation()
    e.preventDefault()
    if (editingTitle.trim()) {
      renameChat.mutate({ conversationId: id, title: editingTitle.trim() })
    }
    setEditingChatId(null)
  }

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('Are you sure you want to delete this chat?')) {
      deleteChat.mutate(id)
      if (activeChatId === id) {
        navigate('/chat')
      }
    }
  }

  const handleDeleteAll = () => {
    if (confirm('Are you sure you want to delete all chats? This cannot be undone.')) {
      deleteAllChats.mutate()
      navigate('/chat')
    }
  }

  return (
    <>
      <div
        className={clsx('fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden', mobileOpen ? 'block' : 'hidden')}
        onClick={onCloseMobile}
      />
      <aside
        className={clsx(
          'fixed inset-y-0 left-0 z-40 flex flex-col border-r border-white/10 bg-surface/95 shadow-2xl shadow-black/40 backdrop-blur-xl transition-all',
          collapsed ? 'w-20' : 'w-72',
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        )}
      >
        {/* Header */}
        <div className="flex h-16 items-center justify-between border-b border-white/10 px-4">
          <div className="flex min-w-0 items-center gap-3">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400 shadow-lg shadow-cyan-950/40">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            {!collapsed ? (
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-white">Research Agent</p>
                <p className="truncate text-xs text-slate-500">Multi-source synthesis</p>
              </div>
            ) : null}
          </div>
          <button className="rounded-md p-1.5 text-slate-400 hover:bg-white/5 hover:text-white lg:hidden" onClick={onCloseMobile}>
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* New Chat Button */}
        <div className="px-3 pt-4 pb-2">
          <button
            onClick={() => {
              navigate('/chat')
              onCloseMobile()
            }}
            className={clsx(
              'flex items-center gap-2 rounded-lg border border-white/10 bg-slate-900/60 py-2.5 text-sm font-medium text-slate-300 transition hover:border-cyan-300/40 hover:text-cyan-200 w-full justify-center',
              collapsed ? 'px-2' : 'px-4',
            )}
            title="New Chat"
          >
            <Plus className="h-4 w-4 shrink-0" />
            {!collapsed && <span>New Chat</span>}
          </button>
        </div>

        {/* Chats History (Middle Section) */}
        {!collapsed && chats && chats.length > 0 && (
          <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1 min-h-0 border-t border-white/5">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-2 px-2.5">Recent Chats</p>
            {chats.map((chat) => {
              const isActive = activeChatId === chat.conversation_id
              const isEditing = editingChatId === chat.conversation_id

              return (
                <div
                  key={chat.conversation_id}
                  onClick={() => {
                    navigate(`/chat?id=${chat.conversation_id}`)
                    onCloseMobile()
                  }}
                  className={clsx(
                    'group relative flex items-center justify-between rounded-lg px-2.5 py-2 text-xs font-medium transition cursor-pointer',
                    isActive
                      ? 'bg-gradient-to-r from-indigo-500/22 to-cyan-400/12 text-cyan-100 ring-1 ring-cyan-300/20'
                      : 'text-slate-400 hover:bg-white/5 hover:text-slate-100',
                  )}
                >
                  {isEditing ? (
                    <form
                      onSubmit={(e) => handleSaveRename(chat.conversation_id, e)}
                      className="flex flex-1 items-center gap-1.5 min-w-0"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <input
                        autoFocus
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        className="flex-1 bg-slate-950 border border-white/10 rounded px-1.5 py-0.5 text-xs text-slate-200 outline-none focus:border-cyan-300/40"
                      />
                      <button
                        type="submit"
                        className="text-emerald-400 hover:text-emerald-300 p-0.5"
                      >
                        <Check className="h-3 w-3" />
                      </button>
                    </form>
                  ) : (
                    <>
                      <span className="truncate pr-10">{chat.title}</span>
                      <span className={clsx(
                        'absolute right-2 items-center gap-1.5 hidden group-hover:flex pl-2 bg-gradient-to-l',
                        isActive ? 'from-indigo-950/90' : 'from-slate-900/90'
                      )}>
                        <button
                          onClick={(e) => handleStartRename(chat.conversation_id, chat.title, e)}
                          className="text-slate-500 hover:text-slate-200 p-0.5 transition"
                          title="Rename"
                        >
                          <Edit2 className="h-3 w-3" />
                        </button>
                        <button
                          onClick={(e) => handleDelete(chat.conversation_id, e)}
                          className="text-slate-500 hover:text-rose-400 p-0.5 transition"
                          title="Delete"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </span>
                    </>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* Clear History button */}
        {!collapsed && chats && chats.length > 0 && (
          <div className="px-3 pb-2 pt-1 border-t border-white/5">
            <button
              onClick={handleDeleteAll}
              className="flex items-center justify-center gap-1.5 w-full rounded-md py-1.5 text-[11px] font-semibold text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20 transition"
            >
              <Trash2 className="h-3 w-3" />
              Clear History
            </button>
          </div>
        )}

        {/* Navigation Section */}
        <nav className="space-y-1.5 px-3 py-4 border-t border-white/10">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onCloseMobile}
              className={({ isActive }) =>
                clsx(
                  'group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition',
                  isActive ? 'bg-gradient-to-r from-indigo-500/22 to-cyan-400/12 text-cyan-100 ring-1 ring-cyan-300/20' : 'text-slate-400 hover:bg-white/5 hover:text-slate-100',
                  collapsed && 'justify-center',
                )
              }
            >
              <item.icon className="h-4.5 w-4.5 shrink-0" />
              {!collapsed ? <span>{item.label}</span> : null}
            </NavLink>
          ))}
        </nav>

        {/* Bottom Section */}
        <div className="border-t border-white/10 p-3">
          <div className={clsx('rounded-lg border border-white/10 bg-card p-3', collapsed && 'grid place-items-center')}>
            <div className="flex items-center gap-3">
              <span
                className={clsx(
                  'h-2.5 w-2.5 rounded-full',
                  status === 'online' && 'bg-emerald-400',
                  status === 'offline' && 'bg-rose-400',
                  status === 'checking' && 'bg-amber-400',
                )}
              />
              {!collapsed ? (
                <div className="min-w-0">
                  <p className="text-[9px] font-medium uppercase tracking-wider text-slate-500">System status</p>
                  <p className="text-xs capitalize text-slate-200">{status}</p>
                </div>
              ) : null}
              {!collapsed ? <Activity className="ml-auto h-4 w-4 text-cyan-300" /> : null}
            </div>
          </div>
          <button
            className="mt-3 hidden w-full items-center justify-center gap-2 rounded-lg border border-white/10 py-2 text-sm text-slate-400 transition hover:border-cyan-300/30 hover:text-cyan-200 lg:flex"
            onClick={onToggleCollapsed}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            {!collapsed ? 'Collapse' : null}
          </button>
        </div>
      </aside>
    </>
  )
}
