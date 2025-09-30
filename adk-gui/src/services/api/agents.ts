import { apiClient } from './client'
import type { InvokeRequest, InvokeResponse } from '@/types/adk'

export const agentApi = {
  // Invoke agent with message
  invoke: async (data: InvokeRequest): Promise<InvokeResponse> => {
    const response = await apiClient.post<InvokeResponse>('/agent/invoke', data)
    return response.data
  },

  // List available agents
  listAgents: async (): Promise<{ id: string; name: string; description: string }[]> => {
    const response = await apiClient.get('/agents')
    return response.data
  },
}