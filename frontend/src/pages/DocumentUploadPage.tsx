import { useMemo, useState } from 'react'
import type { ChangeEvent, DragEvent } from 'react'
import { CheckCircle2, FileText, UploadCloud, XCircle } from 'lucide-react'
import clsx from 'clsx'
import { useUploadDocumentsMutation } from '../hooks/useResearch'
import { useToast } from '../hooks/useToast'

export function DocumentUploadPage() {
  const [files, setFiles] = useState<File[]>([])
  const [progress, setProgress] = useState(0)
  const [dragging, setDragging] = useState(false)
  const upload = useUploadDocumentsMutation()
  const { notify } = useToast()

  const totalSize = useMemo(() => files.reduce((sum, file) => sum + file.size, 0), [files])

  function addFiles(fileList: FileList | null) {
    if (!fileList) return
    setFiles((items) => [...items, ...Array.from(fileList)])
  }

  async function submit() {
    if (!files.length) return
    setProgress(0)
    try {
      const response = await upload.mutateAsync({ files, onProgress: setProgress })
      notify({ kind: 'success', title: 'Documents indexed', message: `${response.documents.length} file(s) processed by the backend.` })
      setFiles([])
    } catch (error) {
      notify({ kind: 'error', title: 'Upload failed', message: error instanceof Error ? error.message : 'Check upload limits and backend logs.' })
    }
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <section className="rounded-lg border border-white/10 bg-surface p-5 shadow-2xl shadow-black/20">
        <div>
          <p className="text-sm font-semibold text-slate-100">Document ingestion</p>
          <p className="mt-1 text-sm text-slate-500">Upload PDF, Markdown, or text documents to enable intelligent retrieval and grounded question answering.</p>
        </div>
        <label
          className={clsx(
            'mt-5 grid min-h-72 cursor-pointer place-items-center rounded-lg border border-dashed p-8 text-center transition',
            dragging ? 'border-cyan-300/70 bg-cyan-400/10' : 'border-white/15 bg-background/70 hover:border-cyan-300/40',
          )}
          onDragOver={(event: DragEvent<HTMLLabelElement>) => {
            event.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(event: DragEvent<HTMLLabelElement>) => {
            event.preventDefault()
            setDragging(false)
            addFiles(event.dataTransfer.files)
          }}
        >
          <input className="sr-only" type="file" multiple onChange={(event: ChangeEvent<HTMLInputElement>) => addFiles(event.target.files)} />
          <div>
            <UploadCloud className="mx-auto h-12 w-12 text-cyan-300" />
            <h1 className="mt-4 text-xl font-semibold text-slate-100">Drop files to upload</h1>
            <p className="mt-2 text-sm text-slate-500">PDF, markdown, and text files are passed directly to `/documents/upload`.</p>
          </div>
        </label>
      </section>

      <section className="rounded-lg border border-white/10 bg-surface p-5">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <p className="text-sm font-semibold text-slate-100">Selected files</p>
            <p className="mt-1 text-sm text-slate-500">{files.length} files, {(totalSize / 1024 / 1024).toFixed(2)} MB total</p>
          </div>
          <button
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-indigo-500 to-cyan-400 px-4 py-2 text-sm font-medium text-white shadow-lg shadow-cyan-950/30 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
            onClick={submit}
            disabled={!files.length || upload.isPending}
          >
            <UploadCloud className="h-4 w-4" />
            {upload.isPending ? 'Uploading' : 'Upload'}
          </button>
        </div>
        {upload.isPending ? (
          <div className="mt-5">
            <div className="flex justify-between text-xs text-slate-500">
              <span>Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/10">
              <div className="h-full rounded-full bg-gradient-to-r from-indigo-400 to-cyan-300 transition-all" style={{ width: `${progress}%` }} />
            </div>
          </div>
        ) : null}
        <div className="mt-5 divide-y divide-white/10 overflow-hidden rounded-lg border border-white/10">
          {files.length ? (
            files.map((file, index) => (
              <div key={`${file.name}-${index}`} className="flex items-center gap-3 bg-card px-4 py-3">
                <FileText className="h-5 w-5 text-indigo-300" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-slate-100">{file.name}</p>
                  <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
                {upload.isError ? <XCircle className="h-5 w-5 text-rose-300" /> : upload.isSuccess ? <CheckCircle2 className="h-5 w-5 text-emerald-300" /> : null}
              </div>
            ))
          ) : (
            <div className="bg-card px-4 py-8 text-center text-sm text-slate-500">No files selected.</div>
          )}
        </div>
      </section>
    </div>
  )
}
