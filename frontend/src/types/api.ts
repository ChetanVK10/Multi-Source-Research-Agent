export type SourceType = 'documents' | 'web' | 'sql'

export interface Citation {
  citation_id: string
  source_id: string
  title?: string | null
  url?: string | null
  snippet?: string | null
}

export interface Evidence {
  evidence_id: string
  source: SourceType
  content: string
  title?: string | null
  url?: string | null
  metadata: Record<string, string | number | boolean | null>
  score?: number | null
}

export interface ChatRequest {
  query_id?: string
  question: string
  top_k?: number
  include_sources?: boolean
  provider?: string
  model?: string
  conversation_id?: string
}

export interface ChatResponse {
  query_id: string
  status: 'accepted' | 'completed' | 'failed'
  answer: string | null
  citations: Citation[]
  evidence: Evidence[]
  message?: string | null
  provider?: string
  model?: string
  conversation_id?: string
}

export interface DependencyHealth {
  status: 'ok' | 'degraded' | 'unconfigured'
  message: string
}

export interface HealthResponse {
  status: 'ok' | 'degraded'
  app_name: string
  app_version: string
  environment: 'local' | 'development' | 'staging' | 'production'
  services?: Record<string, DependencyHealth>
}

export interface ModelConfig {
  id: string
  name: string
}

export interface ProviderConfig {
  id: string
  name: string
  models: ModelConfig[]
  is_available: boolean
}

export type ModelsResponse = ProviderConfig[]

export interface DocumentIngestionResult {
  document_id: string
  source_name: string
  chunks_indexed: number
}

export interface DocumentUploadResponse {
  status: string
  documents: DocumentIngestionResult[]
}


export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: string
  citations?: Citation[]
  evidence?: Evidence[]
  provider?: string
  model?: string
}

export interface ChatInfo {
  conversation_id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

export interface ChatDetail {
  conversation_id: string
  title: string
  created_at: string
  updated_at: string
  messages: ChatMessage[]
}

export interface DocumentInfo {
  document_id: string
  filename: string
  upload_time: string
  chunk_count: number
}
