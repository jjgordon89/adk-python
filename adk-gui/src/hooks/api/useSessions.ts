import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { sessionApi } from '@/services/api/sessions'
import type { CreateSessionRequest } from '@/types/adk'

// Centralized query keys for consistency
export const QUERY_KEYS = {
  sessions: ['sessions'] as const,
  session: (id: string) => ['sessions', id] as const,
  events: (id: string) => ['sessions', id, 'events'] as const,
}

/**
 * Hook to fetch all sessions
 */
export function useSessions() {
  return useQuery({
    queryKey: QUERY_KEYS.sessions,
    queryFn: sessionApi.list,
  })
}

/**
 * Hook to fetch a single session by ID
 */
export function useSession(id: string | undefined) {
  return useQuery({
    queryKey: QUERY_KEYS.session(id!),
    queryFn: () => sessionApi.get(id!),
    enabled: !!id,
  })
}

/**
 * Hook to fetch session events with polling
 */
export function useSessionEvents(id: string | undefined) {
  return useQuery({
    queryKey: QUERY_KEYS.events(id!),
    queryFn: () => sessionApi.getEvents(id!),
    enabled: !!id,
    refetchInterval: 5000, // Poll every 5 seconds
  })
}

/**
 * Hook to create a new session
 */
export function useCreateSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateSessionRequest) => sessionApi.create(data),
    onSuccess: () => {
      // Invalidate sessions list to refresh data
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.sessions })
    },
  })
}

/**
 * Hook to delete a session
 */
export function useDeleteSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => sessionApi.delete(id),
    onSuccess: () => {
      // Invalidate sessions list to refresh data
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.sessions })
    },
  })
}