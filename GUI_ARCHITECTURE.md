# ADK GUI Architecture Design

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Technology Stack](#technology-stack)
3. [System Architecture](#system-architecture)
4. [Core Components](#core-components)
5. [API Integration Patterns](#api-integration-patterns)
6. [State Management](#state-management)
7. [Real-time Communication](#real-time-communication)
8. [SafetyCulture Agent Features](#safetyculture-agent-features)
9. [Development Phases](#development-phases)
10. [Technical Specifications](#technical-specifications)

---

## Executive Summary

This document outlines the architecture for a web-based GUI to interact with Google's Agent Development Kit (ADK) agents. The GUI provides a modern, responsive interface for managing agent sessions, viewing real-time streaming responses, browsing artifacts, and visualizing multi-agent workflows - with special emphasis on the SafetyCulture agent system.

### Design Goals

- **Real-time Interaction**: Seamless streaming of agent responses via Server-Sent Events (SSE)
- **Session Management**: Full CRUD operations for agent sessions
- **Artifact Visualization**: Rich display of generated files, images, and data
- **Multi-Agent Support**: Visual representation of agent orchestration
- **SafetyCulture Integration**: Specialized UI for inspection workflows
- **Developer Experience**: Type-safe, maintainable, and extensible codebase

---

## Technology Stack

### Frontend Framework

**React 18+ with TypeScript**

- **Rationale**: Industry-standard, excellent ecosystem, strong typing
- **Benefits**: 
  - Component reusability
  - Virtual DOM performance
  - Extensive community support
  - TypeScript integration for type safety

### State Management

**Zustand + React Query (TanStack Query)**

- **Zustand**: Lightweight global state management
  - Session management
  - UI state (modals, notifications)
  - User preferences
  
- **React Query**: Server state management
  - API data fetching and caching
  - Automatic refetching
  - Optimistic updates
  - Request deduplication

**Rationale**: Simpler than Redux, more powerful than Context API, perfect for ADK's async-heavy operations.

### UI Component Library

**shadcn/ui**

- Built on Radix UI primitives
- Fully customizable Tailwind CSS components
- Copy-paste component philosophy (no package dependency)
- Accessible by default (ARIA compliant)
- Dark mode support

**Additional UI Dependencies**:
- `lucide-react` - Icon library
- `tailwindcss` - Utility-first CSS
- `class-variance-authority` - Component variant handling

### Build Tool

**Vite**

- Fast development server with Hot Module Replacement (HMR)
- Optimized production builds
- Native ESM support
- TypeScript support out of the box

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        React Frontend                        │
│  ┌─────────────┬──────────────┬──────────────────────────┐ │
│  │  Zustand    │ React Query  │    UI Components         │ │
│  │  (Global    │  (Server     │   (shadcn/ui)            │ │
│  │   State)    │   State)     │                          │ │
│  └─────────────┴──────────────┴──────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            API Client Layer                           │  │
│  │  - HTTP Client (fetch/axios)                          │  │
│  │  - SSE Client (EventSource)                           │  │
│  │  - Request/Response interceptors                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/SSE
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   ADK FastAPI Backend                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  REST API Endpoints                                   │  │
│  │  - /agent/invoke (POST)                              │  │
│  │  - /sessions (GET/POST/DELETE)                       │  │
│  │  - /sessions/{id} (GET/PATCH)                        │  │
│  │  - /sessions/{id}/events (GET)                       │  │
│  │  - /artifacts/* (GET)                                │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Streaming Endpoints                                  │  │
│  │  - /agent/stream (SSE)                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

```
src/
├── components/
│   ├── session/
│   │   ├── SessionList.tsx          # List all sessions
│   │   ├── SessionDetail.tsx        # Session details view
│   │   ├── SessionCreator.tsx       # Create new session
│   │   └── SessionManager.tsx       # Main session container
│   ├── chat/
│   │   ├── ChatInterface.tsx        # Main chat UI
│   │   ├── MessageList.tsx          # Display messages
│   │   ├── MessageInput.tsx         # User input
│   │   └── StreamingMessage.tsx     # Real-time updates
│   ├── artifacts/
│   │   ├── ArtifactBrowser.tsx      # File/data browser
│   │   ├── ArtifactViewer.tsx       # Render artifacts
│   │   ├── ImageViewer.tsx          # Image display
│   │   └── CodeViewer.tsx           # Code syntax highlighting
│   ├── agents/
│   │   ├── AgentSelector.tsx        # Choose agent
│   │   ├── AgentWorkflow.tsx        # Multi-agent visualization
│   │   └── AgentStatus.tsx          # Agent state indicators
│   └── safetyculture/
│       ├── AssetDiscoveryView.tsx   # Asset search results
│       ├── TemplateSelector.tsx     # Template picker
│       ├── InspectionForm.tsx       # Form renderer
│       └── DatabaseViewer.tsx       # SQLite DB browser
├── stores/
│   ├── sessionStore.ts              # Zustand: Session state
│   ├── uiStore.ts                   # Zustand: UI state
│   └── agentStore.ts                # Zustand: Agent state
├── hooks/
│   ├── useAgentInvoke.ts            # React Query: Invoke agent
│   ├── useSessions.ts               # React Query: Sessions
│   ├── useEvents.ts                 # React Query: Events
│   ├── useStreaming.ts              # Custom: SSE handling
│   └── useSafetyCulture.ts          # Custom: SC-specific ops
├── services/
│   ├── api/
│   │   ├── client.ts                # Base HTTP client
│   │   ├── sessions.ts              # Session API
│   │   ├── agents.ts                # Agent API
│   │   └── artifacts.ts             # Artifact API
│   ├── sse/
│   │   └── streamingClient.ts       # SSE implementation
│   └── safetyculture/
│       └── scClient.ts              # SafetyCulture operations
├── types/
│   ├── adk.ts                       # ADK API types
│   ├── session.ts                   # Session types
│   ├── event.ts                     # Event types
│   └── safetyculture.ts             # SC-specific types
└── utils/
    ├── formatters.ts                # Data formatting
    ├── validators.ts                # Input validation
    └── constants.ts                 # App constants
```

---

## Core Components

### 1. Session Manager

**Purpose**: Manage agent sessions with full CRUD operations.

**Features**:
- List all sessions with metadata
- Create new sessions with agent selection
- Resume existing sessions
- Delete sessions
- View session history and events

**Key APIs Used**:
- `POST /sessions` - Create session
- `GET /sessions` - List sessions
- `GET /sessions/{id}` - Get session details
- `DELETE /sessions/{id}` - Delete session
- `GET /sessions/{id}/events` - Get session events

**Component Structure**:
```tsx
<SessionManager>
  <SessionList 
    sessions={sessions}
    onSelect={handleSessionSelect}
    onCreate={handleSessionCreate}
  />
  <SessionDetail 
    session={selectedSession}
    events={events}
    onUpdate={handleUpdate}
  />
</SessionManager>
```

### 2. Chat Interface

**Purpose**: Interactive conversation with agents supporting streaming responses.

**Features**:
- Send user messages
- Display agent responses in real-time
- Show tool invocations and results
- Handle multi-turn conversations
- Display thinking/reasoning process

**Key APIs Used**:
- `POST /agent/invoke` - Send message
- `GET /agent/stream` - Stream responses (SSE)

**Component Structure**:
```tsx
<ChatInterface>
  <MessageList>
    {messages.map(msg => (
      <Message 
        content={msg.content}
        role={msg.role}
        streaming={msg.streaming}
      />
    ))}
  </MessageList>
  <MessageInput 
    onSubmit={handleSubmit}
    disabled={isStreaming}
  />
</ChatInterface>
```

### 3. Artifact Browser

**Purpose**: Visualize and interact with generated artifacts.

**Features**:
- Browse all session artifacts
- Preview images, PDFs, text files
- Syntax-highlighted code display
- Download artifacts
- Filter by artifact type

**Key APIs Used**:
- `GET /artifacts/{artifact_id}` - Get artifact content

**Component Structure**:
```tsx
<ArtifactBrowser>
  <ArtifactList 
    artifacts={artifacts}
    onSelect={handleSelect}
  />
  <ArtifactViewer 
    artifact={selected}
    type={artifactType}
  />
</ArtifactBrowser>
```

### 4. Agent Workflow Visualizer

**Purpose**: Show multi-agent orchestration and handoffs.

**Features**:
- Visual flow diagram
- Agent state indicators
- Transfer visualization
- Event timeline
- Performance metrics

**Component Structure**:
```tsx
<AgentWorkflow>
  <FlowDiagram 
    agents={agents}
    transfers={transfers}
  />
  <Timeline 
    events={events}
    activeAgent={current}
  />
</AgentWorkflow>
```

### 5. SafetyCulture-Specific Components

#### Asset Discovery View

**Purpose**: Display discovered SafetyCulture assets.

**Features**:
- Table view of assets
- Filter by type, location, status
- Asset detail modal
- Batch selection
- Export functionality

```tsx
<AssetDiscoveryView>
  <AssetFilters 
    onFilterChange={handleFilter}
  />
  <AssetTable 
    assets={assets}
    onSelect={handleSelect}
    selection={selected}
  />
  <AssetDetail 
    asset={selectedAsset}
    isOpen={isDetailOpen}
  />
</AssetDiscoveryView>
```

#### Template Selector

**Purpose**: Match and select inspection templates.

**Features**:
- Template search
- AI-powered matching display
- Template preview
- Match confidence scores
- Bulk assignment

```tsx
<TemplateSelector>
  <TemplateSearch 
    query={query}
    onSearch={handleSearch}
  />
  <TemplateList 
    templates={templates}
    matches={aiMatches}
    onSelect={handleSelect}
  />
  <TemplatePreview 
    template={selected}
  />
</TemplateSelector>
```

#### Inspection Form Renderer

**Purpose**: Display and fill inspection forms.

**Features**:
- Dynamic form rendering
- Field type handling (text, date, media, etc.)
- Auto-fill visualization
- Validation status
- Preview before submission

```tsx
<InspectionForm>
  <FormHeader 
    template={template}
    asset={asset}
  />
  <FormFields 
    fields={fields}
    values={formData}
    autoFilled={aiFilledFields}
    onChange={handleChange}
  />
  <FormActions 
    onSubmit={handleSubmit}
    onPreview={handlePreview}
  />
</InspectionForm>
```

#### Database Viewer

**Purpose**: Browse SQLite database contents.

**Features**:
- Table list
- Query interface
- Data grid display
- Export to CSV
- Visual statistics

```tsx
<DatabaseViewer>
  <TableList 
    tables={tables}
    onSelect={handleTableSelect}
  />
  <QueryBuilder 
    table={selectedTable}
    onQuery={handleQuery}
  />
  <DataGrid 
    data={queryResults}
    columns={columns}
  />
</DatabaseViewer>
```

---

## API Integration Patterns

### HTTP Client Configuration

```typescript
// services/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_ADK_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('adk_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors globally
    if (error.response?.status === 401) {
      // Handle unauthorized
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### React Query Integration

```typescript
// hooks/useSessions.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sessionApi } from '@/services/api/sessions';

export function useSessions() {
  return useQuery({
    queryKey: ['sessions'],
    queryFn: sessionApi.list,
    refetchInterval: 30000, // Refresh every 30s
  });
}

export function useCreateSession() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: sessionApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
  });
}

export function useSessionEvents(sessionId: string) {
  return useQuery({
    queryKey: ['sessions', sessionId, 'events'],
    queryFn: () => sessionApi.getEvents(sessionId),
    enabled: !!sessionId,
  });
}
```

### SSE Streaming Implementation

```typescript
// services/sse/streamingClient.ts
export class StreamingClient {
  private eventSource: EventSource | null = null;
  
  connect(
    sessionId: string,
    onMessage: (data: any) => void,
    onError: (error: Error) => void
  ) {
    const url = `${API_BASE_URL}/agent/stream?sessionId=${sessionId}`;
    
    this.eventSource = new EventSource(url);
    
    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        onError(error as Error);
      }
    };
    
    this.eventSource.onerror = (error) => {
      onError(new Error('SSE connection error'));
      this.disconnect();
    };
  }
  
  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}

// hooks/useStreaming.ts
export function useStreaming(sessionId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const clientRef = useRef(new StreamingClient());
  
  useEffect(() => {
    if (!sessionId) return;
    
    setIsStreaming(true);
    
    clientRef.current.connect(
      sessionId,
      (data) => {
        setMessages(prev => [...prev, data]);
      },
      (error) => {
        console.error('Streaming error:', error);
        setIsStreaming(false);
      }
    );
    
    return () => {
      clientRef.current.disconnect();
      setIsStreaming(false);
    };
  }, [sessionId]);
  
  return { messages, isStreaming };
}
```

---

## State Management

### Zustand Stores

#### Session Store

```typescript
// stores/sessionStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SessionStore {
  currentSessionId: string | null;
  recentSessions: string[];
  setCurrentSession: (id: string) => void;
  addRecentSession: (id: string) => void;
  clearCurrentSession: () => void;
}

export const useSessionStore = create<SessionStore>()(
  persist(
    (set) => ({
      currentSessionId: null,
      recentSessions: [],
      setCurrentSession: (id) => set({ currentSessionId: id }),
      addRecentSession: (id) => set((state) => ({
        recentSessions: [id, ...state.recentSessions.filter(s => s !== id)].slice(0, 10)
      })),
      clearCurrentSession: () => set({ currentSessionId: null }),
    }),
    {
      name: 'adk-session-storage',
    }
  )
);
```

#### UI Store

```typescript
// stores/uiStore.ts
import { create } from 'zustand';

interface UIStore {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  notifications: Notification[];
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  addNotification: (notification: Notification) => void;
  removeNotification: (id: string) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  theme: 'light',
  notifications: [],
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setTheme: (theme) => set({ theme }),
  addNotification: (notification) => set((state) => ({
    notifications: [...state.notifications, notification]
  })),
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter(n => n.id !== id)
  })),
}));
```

---

## Real-time Communication

### Server-Sent Events (SSE) Flow

```
User Action → POST /agent/invoke → ADK Backend
                                        │
                                        ▼
                              Agent Processing Starts
                                        │
                                        ▼
    ┌───────────────────────────────────────────────┐
    │  SSE Stream: GET /agent/stream?sessionId=xxx  │
    └───────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
   event: thinking              event: tool_call
   data: {...}                  data: {...}
        │                               │
        ▼                               ▼
   event: response              event: complete
   data: {...}                  data: {...}
```

### Event Types

```typescript
// types/event.ts
export type SSEEventType = 
  | 'thinking'      // Agent reasoning
  | 'tool_call'     // Tool invocation
  | 'tool_result'   // Tool response
  | 'response'      // Agent response chunk
  | 'complete'      // Task complete
  | 'error';        // Error occurred

export interface SSEEvent {
  type: SSEEventType;
  sessionId: string;
  timestamp: string;
  data: any;
}
```

---

## SafetyCulture Agent Features

### Multi-Agent Workflow Visualization

The SafetyCulture agent system involves multiple specialized agents:

```
┌─────────────────────────────────────────────────────┐
│         SafetyCultureCoordinator                     │
│         (Orchestrates entire workflow)               │
└──────────────────┬──────────────────────────────────┘
                   │
      ┌────────────┼────────────┬────────────┐
      │            │            │            │
      ▼            ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  Asset   │ │ Template │ │Inspection│ │   Form   │
│Discovery │ │Selection │ │ Creation │ │ Filling  │
│  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

**UI Requirements**:
1. Visual flow diagram showing agent progression
2. Real-time status indicators for each agent
3. Data passing visualization between agents
4. Results summary for each agent's work

### Asset Discovery Results Display

**Data Structure**:
```typescript
interface Asset {
  id: string;
  name: string;
  type: string;
  location: string;
  siteId: string;
  siteName: string;
  metadata: Record<string, any>;
  lastInspectionDate?: string;
}
```

**UI Features**:
- Sortable/filterable table
- Batch selection checkboxes
- Quick filters (by type, location)
- Export to CSV
- Asset detail modal

### Template Matching Display

**Data Structure**:
```typescript
interface TemplateMatch {
  templateId: string;
  templateName: string;
  assetType: string;
  matchScore: number;  // AI confidence 0-1
  reasoning: string;   // Why this template matches
}
```

**UI Features**:
- Match confidence visualization (progress bar/badge)
- AI reasoning display
- Template preview
- Override option for user selection
- Bulk template assignment

### Inspection Form Rendering

**Features**:
- Dynamic field rendering based on template schema
- Support for multiple field types:
  - Text input
  - Number input
  - Date/time picker
  - Checkboxes
  - Radio buttons
  - Dropdown select
  - Media upload
  - Signature
- Auto-filled field highlighting
- Validation status indicators
- Preview mode before submission

### Database Browser

**Features**:
- List all tables (assets, templates, inspections, etc.)
- SQL query interface with syntax highlighting
- Result grid with sorting/filtering
- Export results to CSV/JSON
- Visual statistics (row counts, data types)
- Schema viewer

---

## Development Phases

### Phase 1: MVP (2-3 weeks)

**Goal**: Basic functional GUI for core ADK operations.

**Features**:
- [ ] Session management (create, list, delete)
- [ ] Basic chat interface
- [ ] Message display (user/agent)
- [ ] Simple agent invocation
- [ ] Event history view
- [ ] Basic styling with shadcn/ui

**Deliverables**:
- Working React app with TypeScript
- API integration for basic operations
- Zustand stores for state
- React Query for API calls
- Basic responsive layout

### Phase 2: Enhanced Interactions (2 weeks)

**Goal**: Real-time streaming and improved UX.

**Features**:
- [ ] SSE streaming implementation
- [ ] Real-time message updates
- [ ] Tool invocation display
- [ ] Artifact browser
- [ ] File/image viewer
- [ ] Error handling and notifications
- [ ] Loading states and skeletons

**Deliverables**:
- Streaming client implementation
- Enhanced chat interface
- Artifact viewing capabilities
- Improved error handling

### Phase 3: Advanced Features (2-3 weeks)

**Goal**: Multi-agent support and advanced visualizations.

**Features**:
- [ ] Agent workflow visualizer
- [ ] Multi-agent orchestration display
- [ ] Performance metrics
- [ ] Session export/import
- [ ] Advanced search and filtering
- [ ] Dark mode
- [ ] User preferences

**Deliverables**:
- Workflow visualization components
- Performance dashboards
- Advanced UI features

### Phase 4: SafetyCulture Specialization (2-3 weeks)

**Goal**: Full SafetyCulture agent support.

**Features**:
- [ ] Asset discovery results viewer
- [ ] Template matching display
- [ ] Inspection form renderer
- [ ] Database browser
- [ ] Batch operations UI
- [ ] Quality assurance dashboard
- [ ] SafetyCulture-specific visualizations

**Deliverables**:
- Complete SafetyCulture agent UI
- Specialized components for inspection workflows
- Database viewing tools

---

## Technical Specifications

### TypeScript Configuration

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
  }
}
```

### Environment Variables

```env
# .env.example
VITE_ADK_API_URL=http://localhost:8000
VITE_ADK_API_TIMEOUT=30000
VITE_SSE_RECONNECT_DELAY=3000
VITE_ENABLE_DEBUG=false
```

### Performance Considerations

1. **Code Splitting**: Use React.lazy() for route-based splitting
2. **Memoization**: Use React.memo() for expensive components
3. **Virtual Scrolling**: Implement for large lists (messages, artifacts)
4. **Debouncing**: Search inputs and API calls
5. **Caching**: Leverage React Query's built-in caching
6. **Bundle Size**: Monitor with `vite-bundle-visualizer`

### Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation support
- Focus management
- Screen reader friendly
- Color contrast compliance (WCAG AA)
- Skip navigation links

### Security

- Input sanitization
- XSS prevention
- CSRF tokens for mutations
- Secure token storage (httpOnly cookies preferred)
- Content Security Policy headers
- Regular dependency updates

### Testing Strategy

1. **Unit Tests**: Jest + React Testing Library
2. **Integration Tests**: Playwright or Cypress
3. **E2E Tests**: Critical user flows
4. **Visual Regression**: Chromatic or Percy
5. **Performance**: Lighthouse CI

---

## Future Enhancements

### Potential Features

1. **Collaborative Sessions**: Multiple users in same session
2. **Voice Input**: Speech-to-text for agent interactions
3. **Mobile App**: React Native implementation
4. **Agent Marketplace**: Browse and deploy community agents
5. **Custom Dashboards**: User-configurable layouts
6. **Advanced Analytics**: Usage metrics and insights
7. **Webhook Integration**: External system notifications
8. **Plugin System**: Extensible architecture for custom features

### Scalability Considerations

1. **API Pagination**: Handle large datasets efficiently
2. **WebSocket Upgrade**: For bi-directional real-time communication
3. **CDN Integration**: Static asset delivery
4. **Service Worker**: Offline support and caching
5. **Micro-frontends**: Modular architecture for large teams

---

## References

- [ADK Documentation](https://github.com/google/adk-python)
- [React Documentation](https://react.dev)
- [Zustand Documentation](https://docs.pmnd.rs/zustand)
- [TanStack Query Documentation](https://tanstack.com/query)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [SafetyCulture API Documentation](https://developer.safetyculture.com)

---

## Appendix A: API Endpoint Reference

### Sessions

- `GET /sessions` - List all sessions
- `POST /sessions` - Create new session
- `GET /sessions/{id}` - Get session details
- `PATCH /sessions/{id}` - Update session
- `DELETE /sessions/{id}` - Delete session
- `GET /sessions/{id}/events` - Get session events

### Agent Operations

- `POST /agent/invoke` - Invoke agent with message
- `GET /agent/stream` - Stream agent responses (SSE)

### Artifacts

- `GET /artifacts/{id}` - Get artifact content
- `GET /sessions/{id}/artifacts` - List session artifacts

---

## Appendix B: Component API Examples

### SessionManager Props

```typescript
interface SessionManagerProps {
  onSessionChange?: (sessionId: string) => void;
  defaultSessionId?: string;
  showSidebar?: boolean;
}
```

### ChatInterface Props

```typescript
interface ChatInterfaceProps {
  sessionId: string;
  onMessageSend?: (message: string) => void;
  enableStreaming?: boolean;
  showToolCalls?: boolean;
}
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-30  
**Author**: ADK Documentation Team