import { Trash2, FileText, Loader2 } from 'lucide-react'
import {
  useDocumentsQuery,
  useDeleteDocumentMutation,
  useDeleteAllDocumentsMutation,
} from '../hooks/useResearch'
import { useToast } from '../hooks/useToast'

export function DocumentsPage() {
  const { data: documents, isLoading, isError, error } = useDocumentsQuery()
  const deleteDoc = useDeleteDocumentMutation()
  const deleteAllDocs = useDeleteAllDocumentsMutation()
  const { notify } = useToast()

  const handleDelete = async (id: string, name: string) => {
    if (confirm(`Are you sure you want to delete "${name}"? This will remove all chunks and vectors.`)) {
      try {
        await deleteDoc.mutateAsync(id)
        notify({ kind: 'info', title: 'Document deleted', message: `Successfully deleted "${name}"` })
      } catch (err) {
        notify({
          kind: 'error',
          title: 'Deletion failed',
          message: err instanceof Error ? err.message : 'Could not delete document.',
        })
      }
    }
  }

  const handleDeleteAll = async () => {
    if (confirm('Are you sure you want to delete ALL uploaded documents? This will clear all Qdrant vectors.')) {
      try {
        await deleteAllDocs.mutateAsync()
        notify({ kind: 'info', title: 'All documents deleted', message: 'Successfully deleted all vector indices.' })
      } catch (err) {
        notify({
          kind: 'error',
          title: 'Deletion failed',
          message: err instanceof Error ? err.message : 'Could not delete all documents.',
        })
      }
    }
  }

  const formatDate = (isoString: string) => {
    if (!isoString || isoString === 'Unknown') return 'N/A'
    try {
      return new Intl.DateTimeFormat(undefined, {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      }).format(new Date(isoString))
    } catch {
      return isoString
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white">Indexed Documents</h2>
          <p className="text-sm text-slate-400">View and manage uploaded documents.</p>
        </div>
        {documents && documents.length > 0 && (
          <button
            onClick={handleDeleteAll}
            disabled={deleteAllDocs.isPending}
            className="inline-flex items-center gap-2 rounded-lg border border-rose-500/20 bg-rose-500/10 px-4 py-2 text-sm font-semibold text-rose-300 transition hover:bg-rose-500/20 disabled:opacity-50"
          >
            <Trash2 className="h-4 w-4" />
            Delete All
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="flex h-64 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-cyan-400" />
        </div>
      ) : isError ? (
        <div className="rounded-lg border border-rose-500/20 bg-rose-950/20 p-6 text-center">
          <p className="text-sm font-semibold text-rose-300">Failed to load documents</p>
          <p className="mt-1 text-xs text-rose-400">{error instanceof Error ? error.message : 'Unknown error'}</p>
        </div>
      ) : !documents || documents.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-white/10 p-12 text-center bg-surface/50">
          <div className="grid h-12 w-12 place-items-center rounded-full bg-white/5 text-slate-500 mb-4">
            <FileText className="h-6 w-6" />
          </div>
          <h3 className="text-sm font-semibold text-slate-200">No documents found</h3>
          <p className="mt-1 text-xs text-slate-500 max-w-sm">
            Upload document files (.txt, .md, or .pdf) on the Upload page to index them in the Qdrant vector database.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-white/10 bg-surface/82 shadow-xl shadow-black/20">
          <table className="w-full border-collapse text-left text-sm text-slate-300">
            <thead>
              <tr className="border-b border-white/10 bg-slate-900/60 font-semibold text-slate-200">
                <th className="px-6 py-4">Filename</th>
                <th className="px-6 py-4">Upload Time</th>
                <th className="px-6 py-4">Chunks</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {documents.map((doc) => (
                <tr key={doc.document_id} className="hover:bg-white/5 transition">
                  <td className="px-6 py-4 font-medium text-slate-100 flex items-center gap-3">
                    <FileText className="h-4 w-4 shrink-0 text-cyan-400" />
                    <span className="truncate max-w-xs sm:max-w-md" title={doc.filename}>{doc.filename}</span>
                  </td>
                  <td className="px-6 py-4 text-slate-400">{formatDate(doc.upload_time)}</td>
                  <td className="px-6 py-4 text-slate-400 font-mono text-xs">{doc.chunk_count}</td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDelete(doc.document_id, doc.filename)}
                      disabled={deleteDoc.isPending}
                      className="inline-flex items-center justify-center h-8 w-8 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition"
                      title="Delete document"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
