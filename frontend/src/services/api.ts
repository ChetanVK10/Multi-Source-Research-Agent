import axios from 'axios'
import type {
  ChatRequest,
  ChatResponse,
  DocumentUploadResponse,
  HealthResponse,
  ModelsResponse,
  ChatInfo,
  ChatDetail,
  DocumentInfo,
} from '../types/api'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  timeout: 120000,
})

export const researchApi = {
  chat: async (payload: ChatRequest) => {
    const response = await apiClient.post<ChatResponse>('/chat', payload)
    return response.data
  },
  getChats: async () => {
    const response = await apiClient.get<ChatInfo[]>('/chats')
    return response.data
  },
  getChat: async (conversationId: string) => {
    const response = await apiClient.get<ChatDetail>(`/chats/${conversationId}`)
    return response.data
  },
  renameChat: async (conversationId: string, title: string) => {
    const response = await apiClient.put<ChatInfo>(`/chats/${conversationId}`, { title })
    return response.data
  },
  deleteChat: async (conversationId: string) => {
    await apiClient.delete(`/chats/${conversationId}`)
  },
  deleteAllChats: async () => {
    await apiClient.delete('/chats')
  },
  getDocuments: async () => {
    const response = await apiClient.get<DocumentInfo[]>('/documents')
    return response.data
  },
  deleteDocument: async (documentId: string) => {
    await apiClient.delete(`/documents/${documentId}`)
  },
  deleteAllDocuments: async () => {
    await apiClient.delete('/documents')
  },
  uploadDocuments: async (files: File[], onUploadProgress?: (progress: number) => void) => {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))

    const response = await apiClient.post<DocumentUploadResponse>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (!event.total) return
        onUploadProgress?.(Math.round((event.loaded * 100) / event.total))
      },
    })

    return response.data
  },
  health: async () => {
    const response = await apiClient.get<HealthResponse>('/health')
    return response.data
  },
  models: async () => {
    const response = await apiClient.get<ModelsResponse>('/models')
    return response.data
  },
}

