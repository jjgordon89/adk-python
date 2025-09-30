import { useMutation, useQueryClient } from '@tanstack/react-query'
import { agentApi } from '@/services/api/agents'
import type { InvokeRequest, InvokeResponse } from '@/types/adk'
import { QUERY_KEYS } from './useSessions'

/**
 * Hook to invoke an agent with a message
 * Invalidates session events on success to trigger refetch
 */
export function useAgentInvoke() {
  const queryClient = useQueryClient()

  return useMutation<InvokeResponse, Error, InvokeRequest>({
    mutationFn: (data: InvokeRequest) => agentApi.invoke(data),
    onSuccess: (data) => {
      // Invalidate session events to refresh the conversation
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.events(data.sessionId),
      })
    },
  })
}