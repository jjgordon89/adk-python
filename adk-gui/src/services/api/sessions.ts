import { apiClient } from './client'
import type { Session, CreateSessionRequest, Event } from '@/types/adk'

export const sessionApi = {
  // List all sessions
  list: async (): Promise<Session[]> => {
    const response = await apiClient.get<Session[]>('/sessions')
    return response.data
  },

  // Get single session
  get: async (id: string): Promise<Session> => {
    const response = await apiClient.get<Session>(`/sessions/${id}`)
    return response.data
  },

  // Create new session
  create: async (data: CreateSessionRequest): Promise<Session> => {
    const response = await apiClient.post<Session>('/sessions', data)
    return response.data
  },

  // Update session
  update: async (id: string, data: Partial<Session>): Promise<Session> => {
    const response = await apiClient.patch<Session>(`/sessions/${id}`, data)
    return response.data
  },

  // Delete session
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/sessions/${id}`)
  },

  // Get session events
  getEvents: async (id: string): Promise<Event[]> => {
    const response = await apiClient.get<Event[]>(`/sessions/${id}/events`)
    return response.data
  },
}