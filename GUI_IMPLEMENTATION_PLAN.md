# ADK GUI Implementation Plan

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Project Setup](#project-setup)
4. [Phase 1: MVP Implementation](#phase-1-mvp-implementation)
5. [Integration with ADK Backend](#integration-with-adk-backend)
6. [SafetyCulture Agent Integration](#safetyculture-agent-integration)
7. [Development Workflow](#development-workflow)
8. [Quick Start Guide](#quick-start-guide)
9. [Troubleshooting](#troubleshooting)
10. [Next Steps](#next-steps)

---

## Introduction

This document provides a detailed, step-by-step implementation plan for building the ADK GUI. It's designed to guide developers through the complete process of creating a functional web interface for interacting with ADK agents, with special emphasis on the SafetyCulture agent system.

### Implementation Timeline

- **Phase 1 (MVP)**: 2-3 weeks - Core functionality
- **Phase 2 (Enhanced)**: 2 weeks - Real-time features
- **Phase 3 (Advanced)**: 2-3 weeks - Multi-agent support
- **Phase 4 (SafetyCulture)**: 2-3 weeks - Specialized features

### Document Purpose

This guide provides:
- Step-by-step setup instructions
- Detailed task breakdowns for each component
- Code examples and patterns
- Integration guidelines
- Testing strategies
- Troubleshooting help

---

## Prerequisites

### Required Software

1. **Node.js**: Version 18.x or higher
   ```bash
   node --version  # Should be v18.0.0+
   ```

2. **Package Manager**: npm (comes with Node) or pnpm (recommended)
   ```bash
   npm install -g pnpm  # Optional but recommended
   ```

3. **Git**: For version control
   ```bash
   git --version
   ```

4. **Code Editor**: VS Code (recommended) with extensions:
   - ESLint
   - Prettier
   - Tailwind CSS IntelliSense
   - TypeScript Vue Plugin (Volar)

### Required Knowledge

- **TypeScript**: Intermediate level
- **React**: Hooks, Context, component patterns
- **CSS/Tailwind**: Basic styling knowledge
- **REST APIs**: HTTP methods, status codes
- **Async JavaScript**: Promises, async/await
- **Git**: Basic version control

### ADK Backend Requirements

- ADK Python package installed
- FastAPI server running (typically on port 8000)
- At least one agent configured
- SafetyCulture agent configured (for SC-specific features)

---

## Project Setup

### Step 1: Initialize React + TypeScript Project

```bash
# Navigate to your desired directory
cd ~/projects

# Create new Vite project with React + TypeScript template
pnpm create vite adk-gui --template react-ts

# Navigate into project
cd adk-gui

# Install dependencies
pnpm install
```

### Step 2: Install Core Dependencies

```bash
# State Management
pnpm add zustand
pnpm add @tanstack/react-query

# UI Components (shadcn/ui dependencies)
pnpm add class-variance-authority clsx tailwind-merge
pnpm add @radix-ui/react-dialog
pnpm add @radix-ui/react-dropdown-menu
pnpm add @radix-ui/react-select
pnpm add @radix-ui/react-tabs
pnpm add @radix-ui/react-toast
pnpm add @radix-ui/react-slot
pnpm add lucide-react

# HTTP Client
pnpm add axios

# Utilities
pnpm add date-fns
pnpm add react-markdown
pnpm add react-syntax-highlighter
pnpm add @types/react-syntax-highlighter -D
```

### Step 3: Install Development Dependencies

```bash
# TypeScript types
pnpm add -D @types/node

# Linting and Formatting
pnpm add -D eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser
pnpm add -D prettier eslint-config-prettier eslint-plugin-prettier

# Testing (optional but recommended)
pnpm add -D vitest @testing-library/react @testing-library/jest-dom
pnpm add -D @testing-library/user-event
```

### Step 4: Configure Tailwind CSS

```bash
# Install Tailwind
pnpm add -D tailwindcss postcss autoprefixer

# Initialize Tailwind
pnpx tailwindcss init -p
```

Update [`tailwind.config.js`](tailwind.config.js):

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

### Step 5: Configure TypeScript

Update [`tsconfig.json`](tsconfig.json):

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### Step 6: Configure Path Aliases

Update [`vite.config.ts`](vite.config.ts):

```typescript
import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

### Step 7: Set Up Environment Variables

Create [`.env`](.env):

```env
VITE_ADK_API_URL=http://localhost:8000
VITE_ADK_API_TIMEOUT=30000
VITE_SSE_RECONNECT_DELAY=3000
VITE_ENABLE_DEBUG=true
```

Create [`.env.example`](.env.example):

```env
VITE_ADK_API_URL=http://localhost:8000
VITE_ADK_API_TIMEOUT=30000
VITE_SSE_RECONNECT_DELAY=3000
VITE_ENABLE_DEBUG=false
```

### Step 8: Initialize Project Structure

```bash
# Create directory structure
mkdir -p src/{components,hooks,services,stores,types,utils,lib}
mkdir -p src/components/{session,chat,artifacts,agents,safetyculture,ui}
mkdir -p src/services/{api,sse,safetyculture}
mkdir -p src/hooks/{api,common}

# Create placeholder files
touch src/services/api/client.ts
touch src/services/api/sessions.ts
touch src/services/api/agents.ts
touch src/types/adk.ts
touch src/types/session.ts
touch src/lib/utils.ts
```

### Step 9: Add Utility Files

Create [`src/lib/utils.ts`](src/lib/utils.ts):

```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleString()
}

export function truncate(str: string, length: number): string {
  return str.length > length ? str.substring(0, length) + "..." : str
}
```

Create [`src/lib/constants.ts`](src/lib/constants.ts):

```typescript
export const API_BASE_URL = import.meta.env.VITE_ADK_API_URL || 'http://localhost:8000'
export const API_TIMEOUT = parseInt(import.meta.env.VITE_ADK_API_TIMEOUT || '30000')
export const SSE_RECONNECT_DELAY = parseInt(import.meta.env.VITE_SSE_RECONNECT_DELAY || '3000')
export const DEBUG_MODE = import.meta.env.VITE_ENABLE_DEBUG === 'true'

export const MESSAGE_ROLES = {
  USER: 'user',
  AGENT: 'agent',
  SYSTEM: 'system',
} as const

export const SESSION_STATUS = {
  ACTIVE: 'active',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const
```

---

## Phase 1: MVP Implementation

### Timeline: 2-3 Weeks

### Objective

Build a minimal but functional GUI that allows users to:
- Create and manage sessions
- Send messages to agents
- View agent responses
- See basic event history

### Task Breakdown

#### Week 1: Foundation & API Integration

##### Task 1.1: Set Up API Client (Day 1)

Create [`src/services/api/client.ts`](src/services/api/client.ts):

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios'
import { API_BASE_URL, API_TIMEOUT } from '@/lib/constants'

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('adk_auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - clear token and redirect to login
          localStorage.removeItem('adk_auth_token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  public getClient(): AxiosInstance {
    return this.client
  }
}

export const apiClient = new APIClient().getClient()
```

##### Task 1.2: Define TypeScript Types (Day 1)

Create [`src/types/adk.ts`](src/types/adk.ts):

```typescript
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
```

##### Task 1.3: Implement Session API (Day 2)

Create [`src/services/api/sessions.ts`](src/services/api/sessions.ts):

```typescript
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
```

##### Task 1.4: Implement Agent API (Day 2)

Create [`src/services/api/agents.ts`](src/services/api/agents.ts):

```typescript
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
```

##### Task 1.5: Set Up React Query (Day 3)

Create [`src/App.tsx`](src/App.tsx):

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { MainLayout } from './components/layouts/MainLayout'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainLayout />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

export default App
```

##### Task 1.6: Create Custom Hooks (Day 3-4)

Create [`src/hooks/api/useSessions.ts`](src/hooks/api/useSessions.ts):

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { sessionApi } from '@/services/api/sessions'
import type { CreateSessionRequest } from '@/types/adk'

const QUERY_KEYS = {
  sessions: ['sessions'] as const,
  session: (id: string) => ['sessions', id] as const,
  events: (id: string) => ['sessions', id, 'events'] as const,
}

export function useSessions() {
  return useQuery({
    queryKey: QUERY_KEYS.sessions,
    queryFn: sessionApi.list,
  })
}

export function useSession(id: string) {
  return useQuery({
    queryKey: QUERY_KEYS.session(id),
    queryFn: () => sessionApi.get(id),
    enabled: !!id,
  })
}

export function useSessionEvents(id: string) {
  return useQuery({
    queryKey: QUERY_KEYS.events(id),
    queryFn: () => sessionApi.getEvents(id),
    enabled: !!id,
    refetchInterval: 5000, // Poll every 5 seconds
  })
}

export function useCreateSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateSessionRequest) => sessionApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.sessions })
    },
  })
}

export function useDeleteSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => sessionApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.sessions })
    },
  })
}
```

Create [`src/hooks/api/useAgentInvoke.ts`](src/hooks/api/useAgentInvoke.ts):

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { agentApi } from '@/services/api/agents'
import type { InvokeRequest } from '@/types/adk'

export function useAgentInvoke() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: InvokeRequest) => agentApi.invoke(data),
    onSuccess: (_, variables) => {
      // Invalidate events for this session
      queryClient.invalidateQueries({
        queryKey: ['sessions', variables.sessionId, 'events'],
      })
    },
  })
}
```

#### Week 2: Core UI Components

##### Task 2.1: Create Session List Component (Day 5-6)

Create [`src/components/session/SessionList.tsx`](src/components/session/SessionList.tsx):

```typescript
import { useSessions, useDeleteSession } from '@/hooks/api/useSessions'
import { formatDate } from '@/lib/utils'
import { Trash2, MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface SessionListProps {
  onSelectSession: (sessionId: string) => void
  selectedSessionId?: string
}

export function SessionList({ onSelectSession, selectedSessionId }: SessionListProps) {
  const { data: sessions, isLoading, error } = useSessions()
  const deleteSession = useDeleteSession()

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('Are you sure you want to delete this session?')) {
      await deleteSession.mutateAsync(id)
    }
  }

  if (isLoading) {
    return <div className="p-4">Loading sessions...</div>
  }

  if (error) {
    return <div className="p-4 text-red-500">Error loading sessions</div>
  }

  if (!sessions?.length) {
    return <div className="p-4 text-muted-foreground">No sessions yet</div>
  }

  return (
    <div className="space-y-2">
      {sessions.map((session) => (
        <div
          key={session.id}
          onClick={() => onSelectSession(session.id)}
          className={`p-3 rounded-lg cursor-pointer transition-colors ${
            selectedSessionId === session.id
              ? 'bg-primary text-primary-foreground'
              : 'bg-card hover:bg-accent'
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              <span className="font-medium">Session {session.id.slice(0, 8)}</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => handleDelete(session.id, e)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
          <div className="text-sm text-muted-foreground mt-1">
            {formatDate(session.createdAt)}
          </div>
        </div>
      ))}
    </div>
  )
}
```

##### Task 2.2: Create Chat Interface (Day 6-7)

Create [`src/components/chat/ChatInterface.tsx`](src/components/chat/ChatInterface.tsx):

```typescript
import { useState } from 'react'
import { useSessionEvents } from '@/hooks/api/useSessions'
import { useAgentInvoke } from '@/hooks/api/useAgentInvoke'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'

interface ChatInterfaceProps {
  sessionId: string
}

export function ChatInterface({ sessionId }: ChatInterfaceProps) {
  const { data: events, isLoading } = useSessionEvents(sessionId)
  const agentInvoke = useAgentInvoke()

  const handleSendMessage = async (message: string) => {
    await agentInvoke.mutateAsync({
      sessionId,
      message,
      streaming: false,
    })
  }

  if (isLoading) {
    return <div className="p-4">Loading messages...</div>
  }

  return (
    <div className="flex flex-col h-full">
      <MessageList events={events || []} />
      <MessageInput
        onSend={handleSendMessage}
        disabled={agentInvoke.isPending}
      />
    </div>
  )
}
```

Create [`src/components/chat/MessageList.tsx`](src/components/chat/MessageList.tsx):

```typescript
import { useEffect, useRef } from 'react'
import type { Event } from '@/types/adk'
import { formatDate } from '@/lib/utils'
import { User, Bot } from 'lucide-react'

interface MessageListProps {
  events: Event[]
}

export function MessageList({ events }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events])

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {events.map((event) => (
        <div
          key={event.id}
          className={`flex gap-3 ${
            event.role === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          {event.role === 'agent' && (
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
              <Bot className="h-4 w-4 text-primary-foreground" />
            </div>
          )}
          <div
            className={`max-w-[70%] rounded-lg p-3 ${
              event.role === 'user'
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted'
            }`}
          >
            <div className="text-sm">{event.content}</div>
            <div className="text-xs mt-1 opacity-70">
              {formatDate(event.timestamp)}
            </div>
          </div>
          {event.role === 'user' && (
            <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
              <User className="h-4 w-4 text-secondary-foreground" />
            </div>
          )}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
```

Create [`src/components/chat/MessageInput.tsx`](src/components/chat/MessageInput.tsx):

```typescript
import { useState } from 'react'
import { Send } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface MessageInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSend(message)
      setMessage('')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t">
      <div className="flex gap-2">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={disabled}
          rows={3}
          className="resize-none"
        />
        <Button type="submit" disabled={disabled || !message.trim()}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </form>
  )
}
```

##### Task 2.3: Create Main Layout (Day 8)

Create [`src/components/layouts/MainLayout.tsx`](src/components/layouts/MainLayout.tsx):

```typescript
import { useState } from 'react'
import { SessionList } from '@/components/session/SessionList'
import { ChatInterface } from '@/components/chat/ChatInterface'
import { Button } from '@/components/ui/button'
import { useCreateSession } from '@/hooks/api/useSessions'
import { Plus } from 'lucide-react'

export function MainLayout() {
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null)
  const createSession = useCreateSession()

  const handleCreateSession = async () => {
    const session = await createSession.mutateAsync({
      agentId: 'default', // Replace with actual agent selection
    })
    setSelectedSessionId(session.id)
  }

  return (
    <div className="h-screen flex">
      {/* Sidebar */}
      <div className="w-80 border-r bg-card flex flex-col">
        <div className="p-4 border-b">
          <Button onClick={handleCreateSession} className="w-full">
            <Plus className="h-4 w-4 mr-2" />
            New Session
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto">
          <SessionList
            onSelectSession={setSelectedSessionId}
            selectedSessionId={selectedSessionId || undefined}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {selectedSessionId ? (
          <ChatInterface sessionId={selectedSessionId} />
        ) : (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            Select a session or create a new one to get started
          </div>
        )}
      </div>
    </div>
  )
}
```

#### Week 3: Polish & Testing

##### Task 3.1: Add Error Handling (Day 9)

Create [`src/components/common/ErrorBoundary.tsx`](src/components/common/ErrorBoundary.tsx):

```typescript
import { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 text-center">
          <h2 className="text-2xl font-bold mb-4">Something went wrong</h2>
          <p className="text-muted-foreground">{this.state.error?.message}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded"
          >
            Reload Page
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
```

##### Task 3.2: Add Loading States (Day 9-10)

Create [`src/components/ui/skeleton.tsx`](src/components/ui/skeleton.tsx):

```typescript
import { cn } from '@/lib/utils'

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-muted', className)}
      {...props}
    />
  )
}

export { Skeleton }
```

##### Task 3.3: Add Basic Tests (Day 10-11)

Create [`src/components/session/__tests__/SessionList.test.tsx`](src/components/session/__tests__/SessionList.test.tsx):

```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SessionList } from '../SessionList'

const queryClient = new QueryClient()

describe('SessionList', () => {
  it('renders loading state', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionList onSelectSession={vi.fn()} />
      </QueryClientProvider>
    )
    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })
})
```

### Acceptance Criteria

- [ ] Users can create new sessions
- [ ] Users can view list of sessions
- [ ] Users can select a session
- [ ] Users can send messages to agents
- [ ] Users can view agent responses
- [ ] Users can delete sessions
- [ ] All API errors are handled gracefully
- [ ] Loading states are displayed appropriately
- [ ] Basic responsive design works on desktop

---

## Integration with ADK Backend

### Backend Setup

#### Step 1: Start ADK FastAPI Server

```bash
# From ADK project root
cd ~/adk-python

# Ensure ADK is installed
pip install -e .

# Start the web server (default port 8000)
adk web --agent safetyculture_agent.agent
```

#### Step 2: Verify Backend is Running

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test sessions endpoint
curl http://localhost:8000/sessions
```

#### Step 3: Configure CORS (if needed)

If you encounter CORS errors, you may need to configure the ADK FastAPI server to allow requests from your frontend origin.

Create a custom FastAPI configuration or modify the ADK server to include:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Endpoint Testing

Use these curl commands to verify endpoints:

```bash
# List sessions
curl http://localhost:8000/sessions

# Create session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"agentId": "safetyculture"}'

# Get session events
curl http://localhost:8000/sessions/{SESSION_ID}/events

# Invoke agent
curl -X POST http://localhost:8000/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "{SESSION_ID}",
    "message": "Find all assets"
  }'
```

---

## SafetyCulture Agent Integration

### Specialized Components for SafetyCulture Workflows

#### Asset Discovery View

Create [`src/components/safetyculture/AssetDiscoveryView.tsx`](src/components/safetyculture/AssetDiscoveryView.tsx):

```typescript
import { useState } from 'react'
import type { Asset } from '@/types/safetyculture'
import { Table } from '@/components/ui/table'
import { Button } from '@/components/ui/button'

interface AssetDiscoveryViewProps {
  assets: Asset[]
  onSelectAsset: (asset: Asset) => void
}

export function AssetDiscoveryView({ assets, onSelectAsset }: AssetDiscoveryViewProps) {
  const [selectedAssets, setSelectedAssets] = useState<Set<string>>(new Set())

  const toggleAsset = (assetId: string) => {
    const newSelected = new Set(selectedAssets)
    if (newSelected.has(assetId)) {
      newSelected.delete(assetId)
    } else {
      newSelected.add(assetId)
    }
    setSelectedAssets(newSelected)
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">
          Discovered Assets ({assets.length})
        </h3>
        {selectedAssets.size > 0 && (
          <Button>
            Process Selected ({selectedAssets.size})
          </Button>
        )}
      </div>

      <div className="border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-muted">
            <tr>
              <th className="p-3 text-left">
                <input
                  type="checkbox"
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedAssets(new Set(assets.map(a => a.id)))
                    } else {
                      setSelectedAssets(new Set())
                    }
                  }}
                />
              </th>
              <th className="p-3 text-left">Name</th>
              <th className="p-3 text-left">Type</th>
              <th className="p-3 text-left">Location</th>
              <th className="p-3 text-left">Last Inspection</th>
            </tr>
          </thead>
          <tbody>
            {assets.map((asset) => (
              <tr
                key={asset.id}
                className="border-t hover:bg-accent cursor-pointer"
                onClick={() => onSelectAsset(asset)}
              >
                <td className="p-3">
                  <input
                    type="checkbox"
                    checked={selectedAssets.has(asset.id)}
                    onChange={(e) => {
                      e.stopPropagation()
                      toggleAsset(asset.id)
                    }}
                  />
                </td>
                <td className="p-3">{asset.name}</td>
                <td className="p-3">{asset.type}</td>
                <td className="p-3">{asset.location}</td>
                <td className="p-3">
                  {asset.lastInspectionDate || 'Never'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

#### Template Matching Display

Create [`src/components/safetyculture/TemplateMatchDisplay.tsx`](src/components/safetyculture/TemplateMatchDisplay.tsx):

```typescript
import type { TemplateMatch } from '@/types/safetyculture'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Check, AlertCircle } from 'lucide-react'

interface TemplateMatchDisplayProps {
  matches: TemplateMatch[]
  onSelectTemplate: (templateId: string) => void
}

export function TemplateMatchDisplay({
  matches,
  onSelectTemplate,
}: TemplateMatchDisplayProps) {
  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500'
    if (score >= 0.6) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return 'High'
    if (score >= 0.6) return 'Medium'
    return 'Low'
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold">Template Matches</h3>
      
      {matches.map((match) => (
        <Card
          key={match.templateId}
          className="p-4 cursor-pointer hover:bg-accent transition-colors"
          onClick={() => onSelectTemplate(match.templateId)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h4 className="font-medium">{match.templateName}</h4>
                <Badge variant="secondary">{match.assetType}</Badge>
              </div>
              
              <p className="text-sm text-muted-foreground mt-2">
                {match.reasoning}
              </p>
              
              <div className="mt-3 flex items-center gap-2">
                <span className="text-sm">Confidence:</span>
                <div className="flex-1 max-w-xs h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getConfidenceColor(match.matchScore)}`}
                    style={{ width: `${match.matchScore * 100}%` }}
                  />
                </div>
                <span className="text-sm font-medium">
                  {getConfidenceLabel(match.matchScore)}
                </span>
              </div>
            </div>
            
            {match.matchScore >= 0.8 && (
              <Check className="h-5 w-5 text-green-500" />
            )}
            {match.matchScore < 0.6 && (
              <AlertCircle className="h-5 w-5 text-yellow-500" />
            )}
          </div>
        </Card>
      ))}
    </div>
  )
}
```

### SafetyCulture Type Definitions

Create [`src/types/safetyculture.ts`](src/types/safetyculture.ts):

```typescript
export interface Asset {
  id: string
  name: string
  type: string
  location: string
  siteId: string
  siteName: string
  metadata: Record<string, any>
  lastInspectionDate?: string
}

export interface TemplateMatch {
  templateId: string
  templateName: string
  assetType: string
  matchScore: number
  reasoning: string
}

export interface InspectionTemplate {
  id: string
  name: string
  description: string
  fields: InspectionField[]
}

export interface InspectionField {
  id: string
  type: 'text' | 'number' | 'date' | 'checkbox' | 'select' | 'media'
  label: string
  required: boolean
  options?: string[]
}

export interface Inspection {
  id: string
  templateId: string
  assetId: string
  status: 'draft' | 'completed' | 'submitted'
  responses: Record<string, any>
  createdAt: string
  completedAt?: string
}
```

---

## Development Workflow

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/session-management

# Make changes and commit
git add .
git commit -m "feat: implement session management UI"

# Push to remote
git push origin feature/session-management

# Create pull request on GitHub
```

### Development Commands

```bash
# Start development server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview

# Run tests
pnpm test

# Run linter
pnpm lint

# Format code
pnpm format
```

### Code Review Checklist

- [ ] Code follows TypeScript best practices
- [ ] Components are properly typed
- [ ] Error handling is implemented
- [ ] Loading states are handled
- [ ] Responsive design considerations
- [ ] Accessibility features included
- [ ] Tests are written (if applicable)
- [ ] No console errors or warnings
- [ ] Code is properly documented

---

## Quick Start Guide

### For Developers New to the Project

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd adk-gui
   pnpm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your ADK backend URL
   ```

3. **Start Backend**
   ```bash
   # In ADK project directory
   adk web --agent safetyculture_agent.agent
   ```

4. **Start Frontend**
   ```bash
   pnpm dev
   ```

5. **Open Browser**
   - Navigate to `http://localhost:3000`
   - Create a new session
   - Start chatting with the agent

### Testing the SafetyCulture Agent

1. **Start a Session**
2. **Send Discovery Command**:
   ```
   Find all equipment assets at the Main Site
   ```

3. **View Results** in the Asset Discovery panel

4. **Request Template Matching**:
   ```
   Match inspection templates to these assets
   ```

5. **Create Inspections**:
   ```
   Create inspections for the selected assets
   ```

---

## Troubleshooting

### Common Issues

#### Issue: CORS Errors

**Symptom**: Console errors about Cross-Origin Resource Sharing

**Solution**:
1. Configure Vite proxy in [`vite.config.ts`](vite.config.ts)
2. Or configure CORS in ADK backend
3. Or use browser extension to disable CORS (development only)

#### Issue: API Connection Refused

**Symptom**: `ERR_CONNECTION_REFUSED` or timeout errors

**Solution**:
1. Verify ADK backend is running: `curl http://localhost:8000/health`
2. Check `.env` file has correct API URL
3. Ensure no firewall blocking port 8000

#### Issue: TypeScript Errors

**Symptom**: Type checking failures

**Solution**:
```bash
# Clear TypeScript cache
rm -rf node_modules/.vite
pnpm install

# Restart TypeScript server in VS Code
Cmd/Ctrl + Shift + P -> "TypeScript: Restart TS Server"
```

#### Issue: Dependencies Not Found

**Symptom**: Module not found errors

**Solution**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

#### Issue: Build Failures

**Symptom**: Production build fails

**Solution**:
1. Check for TypeScript errors: `pnpm tsc --noEmit`
2. Verify all imports are correct
3. Check for unused variables/imports

### Performance Issues

#### Slow Initial Load

**Solutions**:
- Implement code splitting
- Lazy load routes
- Optimize bundle size

#### Slow Rendering

**Solutions**:
- Use React.memo() for expensive components
- Implement virtual scrolling for large lists
- Debounce frequent operations

### Debugging Tips

1. **Enable Debug Mode**:
   ```env
   VITE_ENABLE_DEBUG=true
   ```

2. **Use React DevTools**:
   - Install React DevTools browser extension
   - Inspect component props and state

3. **Use React Query DevTools**:
   - Already included in development mode
   - View query states and cache

4. **Network Inspection**:
   - Open browser DevTools → Network tab
   - Monitor API requests/responses
   - Check for failed requests

5. **Console Logging**:
   ```typescript
   if (import.meta.env.DEV) {
     console.log('Debug info:', data)
   }
   ```

---

## Next Steps

### After MVP Completion

1. **Phase 2: Real-time Features**
   - Implement SSE streaming
   - Add WebSocket support
   - Real-time agent status updates

2. **Phase 3: Advanced Features**
   - Multi-agent workflow visualization
   - Performance metrics dashboard
   - Advanced search and filtering

3. **Phase 4: SafetyCulture Specialization**
   - Complete asset discovery UI
   - Template matching interface
   - Inspection form renderer
   - Database viewer

### Long-term Enhancements

- [ ] Mobile responsive design
- [ ] Dark mode support
- [ ] Keyboard shortcuts
- [ ] Session export/import
- [ ] Advanced analytics
- [ ] User authentication
- [ ] Multi-user collaboration
- [ ] Plugin system

### Production Readiness

Before deploying to production:

1. **Security**
   - [ ] Implement proper authentication
   - [ ] Add CSRF protection
   - [ ] Sanitize user inputs
   - [ ] Use environment variables for secrets

2. **Performance**
   - [ ] Optimize bundle size
   - [ ] Implement caching strategies
   - [ ] Add service worker for offline support
   - [ ] Configure CDN for static assets

3. **Monitoring**
   - [ ] Add error tracking (Sentry, etc.)
   - [ ] Implement analytics
   - [ ] Set up logging
   - [ ] Configure uptime monitoring

4. **Documentation**
   - [ ] User guide
   - [ ] API documentation
   - [ ] Deployment guide
   - [ ] Troubleshooting guide

---

## Additional Resources

### Documentation

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [TanStack Query Documentation](https://tanstack.com/query)
- [Zustand Documentation](https://docs.pmnd.rs/zustand)
- [shadcn/ui Components](https://ui.shadcn.com)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

### ADK Resources

- [ADK GitHub Repository](https://github.com/google/adk-python)
- [ADK Documentation](https://github.com/google/adk-python/tree/main/docs)
- [SafetyCulture Agent README](safetyculture_agent/README.md)

### Community

- Join ADK Discord/Slack (if available)
- Stack Overflow tags: `google-adk`, `react`, `typescript`
- GitHub Discussions for questions

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-30  
**Maintained By**: ADK Development Team