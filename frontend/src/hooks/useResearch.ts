import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { researchApi } from '../services/api'
import type { ChatRequest } from '../types/api'

export function useChatMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: ChatRequest) => researchApi.chat(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chats'] })
    },
  })
}

export function useChatsQuery() {
  return useQuery({
    queryKey: ['chats'],
    queryFn: researchApi.getChats,
  })
}

export function useChatQuery(conversationId: string | null) {
  return useQuery({
    queryKey: ['chat', conversationId],
    queryFn: () => (conversationId ? researchApi.getChat(conversationId) : null),
    enabled: !!conversationId,
  })
}

export function useRenameChatMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ conversationId, title }: { conversationId: string; title: string }) =>
      researchApi.renameChat(conversationId, title),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['chats'] })
      queryClient.invalidateQueries({ queryKey: ['chat', data.conversation_id] })
    },
  })
}

export function useDeleteChatMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (conversationId: string) => researchApi.deleteChat(conversationId),
    onSuccess: (_, conversationId) => {
      queryClient.invalidateQueries({ queryKey: ['chats'] })
      queryClient.removeQueries({ queryKey: ['chat', conversationId] })
    },
  })
}

export function useDeleteAllChatsMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: researchApi.deleteAllChats,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chats'] })
    },
  })
}

export function useDocumentsQuery() {
  return useQuery({
    queryKey: ['documents'],
    queryFn: researchApi.getDocuments,
  })
}

export function useDeleteDocumentMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (documentId: string) => researchApi.deleteDocument(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })
}

export function useDeleteAllDocumentsMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: researchApi.deleteAllDocuments,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })
}

export function useHealthQuery() {
  return useQuery({
    queryKey: ['health'],
    queryFn: researchApi.health,
    refetchInterval: 30000,
  })
}

export function useUploadDocumentsMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ files, onProgress }: { files: File[]; onProgress?: (progress: number) => void }) =>
      researchApi.uploadDocuments(files, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })
}

export function useModelsQuery() {
  return useQuery({
    queryKey: ['models'],
    queryFn: researchApi.models,
  })
}
