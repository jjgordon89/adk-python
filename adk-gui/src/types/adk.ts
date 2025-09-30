export interface Session {
  id: string
  agentId: string
  metadata: Record<string, any>
  createdAt: string
  updatedAt: string
  status: 'active' | 'completed' | 'failed'
}

export interface CreateSessionRequest {
  agentId: string
  metadata?: Record<string, any>
}

export interface Event {
  id: string
  sessionId: string
  type: 'message' | 'tool_call' | 'tool_result' | 'thinking' | 'error'
  role: 'user' | 'agent' | 'system'
  content: string
  timestamp: string
  metadata?: Record<string, any>
}

export interface InvokeRequest {
  sessionId: string
  message: string
  streaming?: boolean
}

export interface InvokeResponse {
  sessionId: string
  response: string
  events: Event[]
}

export interface Artifact {
  id: string
  sessionId: string
  name: string
  type: string
  size: number
  createdAt: string
  url: string
}