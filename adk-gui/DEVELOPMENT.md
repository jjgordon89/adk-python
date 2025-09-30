# ADK GUI Development Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Code Patterns](#code-patterns)
5. [Adding New Features](#adding-new-features)
6. [Environment Variables](#environment-variables)
7. [Common Tasks](#common-tasks)
8. [Debugging](#debugging)
9. [Contributing Guidelines](#contributing-guidelines)
10. [Best Practices](#best-practices)

---

## Getting Started

### Prerequisites

Ensure you have the following installed:

- **Node.js**: Version 18.0 or higher
  ```bash
  node --version  # Should be v18.0.0+
  ```

- **npm or pnpm**: Package manager
  ```bash
  npm --version   # or
  pnpm --version  # Recommended
  ```

- **Git**: For version control
  ```bash
  git --version
  ```

- **Code Editor**: VS Code recommended with extensions:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
  - TypeScript Vue Plugin (Volar)

### Initial Setup

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd adk-python/adk-gui
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   pnpm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open browser**
   - Navigate to `http://localhost:3000`
   - The app should load successfully

### Verifying Setup

```bash
# Check TypeScript compilation
npm run build

# Run linter
npm run lint

# Preview production build
npm run preview
```

---

## Project Structure

### Directory Organization

```
adk-gui/
├── public/                     # Static assets
├── src/
│   ├── components/             # React components
│   │   ├── ui/                 # Base UI components (shadcn/ui)
│   │   │   ├── button.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── card.tsx
│   │   │   └── ...
│   │   ├── chat/               # Chat interface components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   └── MessageInput.tsx
│   │   ├── session/            # Session management
│   │   │   └── SessionList.tsx
│   │   ├── layouts/            # Layout components
│   │   │   └── MainLayout.tsx
│   │   └── safetyculture/      # SafetyCulture-specific
│   │       ├── AssetDiscoveryView.tsx
│   │       └── TemplateMatchDisplay.tsx
│   ├── hooks/                  # Custom React hooks
│   │   └── api/                # API integration hooks
│   │       ├── useSessions.ts
│   │       └── useAgentInvoke.ts
│   ├── services/               # External services
│   │   └── api/                # API client and endpoints
│   │       ├── client.ts
│   │       ├── sessions.ts
│   │       └── agents.ts
│   ├── types/                  # TypeScript type definitions
│   │   ├── adk.ts              # ADK core types
│   │   └── safetyculture.ts    # SafetyCulture types
│   ├── lib/                    # Utility functions
│   │   ├── utils.ts
│   │   └── constants.ts
│   ├── App.tsx                 # Root component
│   ├── main.tsx                # Application entry point
│   └── index.css               # Global styles
├── .env                        # Environment variables (local)
├── .env.example                # Environment template
├── package.json                # Dependencies and scripts
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
├── tailwind.config.js          # Tailwind CSS configuration
└── README.md                   # User documentation
```

### Component Organization

**By Feature**:
- Components are grouped by feature (chat, session, etc.)
- Each feature directory contains related components
- Shared UI components live in `/ui`

**File Naming**:
- Components: PascalCase (e.g., `MessageList.tsx`)
- Hooks: camelCase with 'use' prefix (e.g., `useSessions.ts`)
- Utils: camelCase (e.g., `utils.ts`)
- Types: camelCase or PascalCase (e.g., `adk.ts`)

---

## Development Workflow

### Starting Development

```bash
# Start development server (with HMR)
npm run dev

# Open in browser
# http://localhost:3000
```

**Development Server Features**:
- Hot Module Replacement (HMR) - instant updates
- Fast Refresh - preserves component state
- Type checking in editor
- React Query DevTools available

### Building for Production

```bash
# Create production build
npm run build

# Preview production build locally
npm run preview
```

**Build Output**:
```
dist/
├── index.html
├── assets/
│   ├── index-[hash].css
│   └── index-[hash].js
└── ...
```

### Running Linter

```bash
# Check for linting errors
npm run lint

# Auto-fix linting errors (if possible)
npm run lint -- --fix
```

### Type Checking

```bash
# Run TypeScript type checker
npx tsc --noEmit
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
git add .
git commit -m "feat: add your feature"

# Push to remote
git push origin feature/your-feature-name

# Create pull request on GitHub
```

---

## Code Patterns

### Component Pattern

**Functional Components with TypeScript**:

```typescript
import { useState } from 'react'

interface MyComponentProps {
  title: string
  onAction?: () => void
  optional?: boolean
}

export function MyComponent({ title, onAction, optional = false }: MyComponentProps) {
  const [state, setState] = useState<string>('')

  const handleClick = () => {
    // Handle logic
    onAction?.()
  }

  return (
    <div className="p-4">
      <h2>{title}</h2>
      {/* Component JSX */}
    </div>
  )
}
```

**Key Principles**:
- Always define prop interfaces
- Use optional parameters with default values
- Export as named function (not default)
- Group related logic together

### API Integration Pattern

**Service Function**:

```typescript
// src/services/api/myService.ts
import { apiClient } from './client'
import type { MyType } from '@/types/adk'

export const myServiceApi = {
  getAll: async (): Promise<MyType[]> => {
    const response = await apiClient.get<MyType[]>('/my-endpoint')
    return response.data
  },

  getById: async (id: string): Promise<MyType> => {
    const response = await apiClient.get<MyType>(`/my-endpoint/${id}`)
    return response.data
  },

  create: async (data: Partial<MyType>): Promise<MyType> => {
    const response = await apiClient.post<MyType>('/my-endpoint', data)
    return response.data
  },
}
```

**Custom Hook**:

```typescript
// src/hooks/api/useMyService.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { myServiceApi } from '@/services/api/myService'

const QUERY_KEYS = {
  myItems: ['my-items'] as const,
  myItem: (id: string) => ['my-items', id] as const,
}

export function useMyItems() {
  return useQuery({
    queryKey: QUERY_KEYS.myItems,
    queryFn: myServiceApi.getAll,
  })
}

export function useCreateMyItem() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: myServiceApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.myItems })
    },
  })
}
```

### Error Handling Pattern

```typescript
export function MyComponent() {
  const { data, error, isLoading } = useMyItems()

  // Handle loading state first
  if (isLoading) {
    return <div className="p-4">Loading...</div>
  }

  // Handle error state
  if (error) {
    return (
      <div className="p-4 text-red-500">
        Error: {error instanceof Error ? error.message : 'Unknown error'}
      </div>
    )
  }

  // Handle empty state
  if (!data?.length) {
    return <div className="p-4 text-muted-foreground">No items found</div>
  }

  // Render data
  return (
    <div>
      {data.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  )
}
```

### Loading State Pattern

```typescript
export function MyComponent() {
  const { mutate, isPending } = useCreateMyItem()

  const handleSubmit = () => {
    mutate({ name: 'New Item' })
  }

  return (
    <Button onClick={handleSubmit} disabled={isPending}>
      {isPending ? 'Creating...' : 'Create Item'}
    </Button>
  )
}
```

### Type Definition Pattern

```typescript
// src/types/myTypes.ts

// Base types
export interface MyEntity {
  id: string
  name: string
  createdAt: string
  metadata: Record<string, any>
}

// Request/Response types
export interface CreateMyEntityRequest {
  name: string
  metadata?: Record<string, any>
}

export interface UpdateMyEntityRequest {
  name?: string
  metadata?: Record<string, any>
}

// Union types for status
export type EntityStatus = 'active' | 'completed' | 'failed'

export interface MyEntityWithStatus extends MyEntity {
  status: EntityStatus
}
```

---

## Adding New Features

### Adding a New UI Component

1. **Determine component location**:
   - UI primitive → [`src/components/ui/`](src/components/ui/)
   - Feature-specific → `src/components/[feature]/`
   - Layout → [`src/components/layouts/`](src/components/layouts/)

2. **Create component file**:
   ```typescript
   // src/components/myFeature/MyNewComponent.tsx
   import { Button } from '@/components/ui/button'

   interface MyNewComponentProps {
     data: string
     onAction: () => void
   }

   export function MyNewComponent({ data, onAction }: MyNewComponentProps) {
     return (
       <div className="p-4 border rounded-lg">
         <p>{data}</p>
         <Button onClick={onAction}>Action</Button>
       </div>
     )
   }
   ```

3. **Add to parent component**:
   ```typescript
   import { MyNewComponent } from '@/components/myFeature/MyNewComponent'

   export function ParentComponent() {
     return (
       <div>
         <MyNewComponent 
           data="Hello" 
           onAction={() => console.log('Clicked')} 
         />
       </div>
     )
   }
   ```

### Adding a New API Endpoint

1. **Update type definitions**:
   ```typescript
   // src/types/adk.ts
   export interface NewEntity {
     id: string
     name: string
   }
   ```

2. **Create service functions**:
   ```typescript
   // src/services/api/newService.ts
   import { apiClient } from './client'
   import type { NewEntity } from '@/types/adk'

   export const newServiceApi = {
     getAll: async (): Promise<NewEntity[]> => {
       const response = await apiClient.get<NewEntity[]>('/new-endpoint')
       return response.data
     },
   }
   ```

3. **Create custom hook**:
   ```typescript
   // src/hooks/api/useNewService.ts
   import { useQuery } from '@tanstack/react-query'
   import { newServiceApi } from '@/services/api/newService'

   export function useNewEntities() {
     return useQuery({
       queryKey: ['new-entities'],
       queryFn: newServiceApi.getAll,
     })
   }
   ```

4. **Use in component**:
   ```typescript
   import { useNewEntities } from '@/hooks/api/useNewService'

   export function MyComponent() {
     const { data, isLoading, error } = useNewEntities()
     // ... render logic
   }
   ```

### Adding a New Custom Hook

1. **Create hook file**:
   ```typescript
   // src/hooks/useMyCustomHook.ts
   import { useState, useEffect } from 'react'

   export function useMyCustomHook(initialValue: string) {
     const [value, setValue] = useState(initialValue)

     useEffect(() => {
       // Custom logic
       console.log('Value changed:', value)
     }, [value])

     return { value, setValue }
   }
   ```

2. **Use in component**:
   ```typescript
   import { useMyCustomHook } from '@/hooks/useMyCustomHook'

   export function MyComponent() {
     const { value, setValue } = useMyCustomHook('initial')
     // ... component logic
   }
   ```

### Adding shadcn/ui Components

The project uses shadcn/ui components. To add a new component:

1. **Browse available components**: https://ui.shadcn.com/docs/components

2. **Copy component code** from the shadcn/ui documentation

3. **Create file in [`src/components/ui/`](src/components/ui/)**:
   ```bash
   # Example: Adding a Dialog component
   # Create src/components/ui/dialog.tsx
   # Copy code from shadcn/ui docs
   ```

4. **Use in your components**:
   ```typescript
   import { Dialog } from '@/components/ui/dialog'
   ```

---

## Environment Variables

### Available Variables

All environment variables must be prefixed with `VITE_` to be accessible in the frontend:

```env
# Backend API Configuration
VITE_ADK_API_URL=http://localhost:8000

# Timeout Configuration (milliseconds)
VITE_ADK_API_TIMEOUT=30000

# SSE Reconnection Delay (milliseconds)
VITE_SSE_RECONNECT_DELAY=3000

# Debug Mode
VITE_ENABLE_DEBUG=false
```

### Accessing Environment Variables

```typescript
// In code
const apiUrl = import.meta.env.VITE_ADK_API_URL
const timeout = parseInt(import.meta.env.VITE_ADK_API_TIMEOUT || '30000')
const isDebug = import.meta.env.VITE_ENABLE_DEBUG === 'true'

// Best practice: Use constants file
// src/lib/constants.ts
export const API_BASE_URL = import.meta.env.VITE_ADK_API_URL || 'http://localhost:8000'
export const API_TIMEOUT = parseInt(import.meta.env.VITE_ADK_API_TIMEOUT || '30000')
```

### Environment-Specific Configuration

**Development** ([`.env`](.env)):
```env
VITE_ADK_API_URL=http://localhost:8000
VITE_ENABLE_DEBUG=true
```

**Production** (`.env.production`):
```env
VITE_ADK_API_URL=https://api.production.com
VITE_ENABLE_DEBUG=false
```

**Important Notes**:
- Never commit `.env` file to Git
- Always update [`.env.example`](.env.example) when adding new variables
- Restart dev server after changing `.env`

---

## Common Tasks

### Task: Add a New Page/Route

**Note**: Current implementation is single-page. To add routing:

1. **Install React Router**:
   ```bash
   npm install react-router-dom
   npm install -D @types/react-router-dom
   ```

2. **Create route structure**:
   ```typescript
   // src/App.tsx
   import { BrowserRouter, Routes, Route } from 'react-router-dom'
   import { MainLayout } from './components/layouts/MainLayout'
   import { SettingsPage } from './pages/SettingsPage'

   function App() {
     return (
       <BrowserRouter>
         <Routes>
           <Route path="/" element={<MainLayout />} />
           <Route path="/settings" element={<SettingsPage />} />
         </Routes>
       </BrowserRouter>
     )
   }
   ```

### Task: Add a New Type Definition

```typescript
// src/types/myNewTypes.ts
export interface MyNewType {
  id: string
  name: string
  status: 'active' | 'inactive'
  metadata?: Record<string, any>
}

// Export from types index (if you create one)
// src/types/index.ts
export * from './adk'
export * from './safetyculture'
export * from './myNewTypes'
```

### Task: Add Global State (Zustand)

```typescript
// src/stores/myStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface MyStore {
  count: number
  increment: () => void
  decrement: () => void
}

export const useMyStore = create<MyStore>()(
  persist(
    (set) => ({
      count: 0,
      increment: () => set((state) => ({ count: state.count + 1 })),
      decrement: () => set((state) => ({ count: state.count - 1 })),
    }),
    {
      name: 'my-store', // localStorage key
    }
  )
)

// Use in component
import { useMyStore } from '@/stores/myStore'

export function MyComponent() {
  const { count, increment } = useMyStore()
  
  return <button onClick={increment}>{count}</button>
}
```

### Task: Style a Component with Tailwind

```typescript
export function StyledComponent() {
  return (
    <div className="flex flex-col gap-4 p-6">
      {/* Container with flexbox, gap, and padding */}
      
      <div className="bg-primary text-primary-foreground rounded-lg p-4">
        {/* Colored background, rounded corners */}
      </div>

      <button className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors">
        {/* Button with hover effect */}
      </button>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Responsive grid layout */}
      </div>
    </div>
  )
}
```

**Common Tailwind Patterns**:
- Layout: `flex`, `grid`, `space-y-4`, `gap-2`
- Sizing: `w-full`, `h-screen`, `max-w-xl`
- Spacing: `p-4`, `m-2`, `px-6`, `py-3`
- Colors: `bg-primary`, `text-red-500`, `border-gray-300`
- Typography: `text-lg`, `font-bold`, `leading-tight`
- Responsive: `md:grid-cols-2`, `lg:p-8`

### Task: Add Form Validation

```typescript
import { useState } from 'react'

export function FormComponent() {
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = (name: string, email: string): boolean => {
    const newErrors: Record<string, string> = {}

    if (!name.trim()) {
      newErrors.name = 'Name is required'
    }

    if (!email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.target as HTMLFormElement)
    const name = formData.get('name') as string
    const email = formData.get('email') as string

    if (validate(name, email)) {
      // Submit form
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <input name="name" className="border p-2" />
        {errors.name && <p className="text-red-500">{errors.name}</p>}
      </div>
      <div>
        <input name="email" type="email" className="border p-2" />
        {errors.email && <p className="text-red-500">{errors.email}</p>}
      </div>
      <button type="submit">Submit</button>
    </form>
  )
}
```

---

## Debugging

### React Query DevTools

The app includes React Query DevTools in development mode:

```typescript
// Automatically available at bottom of screen in dev mode
// Shows all queries, their status, and cached data
<ReactQueryDevtools initialIsOpen={false} />
```

**Features**:
- View all active queries
- Inspect query data and status
- Manually refetch queries
- Clear cache
- View query timeline

### Browser DevTools

**Console Logging**:
```typescript
// Only log in development
if (import.meta.env.DEV) {
  console.log('Debug info:', data)
}
```

**Network Tab**:
- Monitor API requests
- Check request/response headers
- View response bodies
- Check timing information

**React DevTools Extension**:
- Install from Chrome/Firefox extension store
- Inspect component tree
- View component props and state
- Profile component performance

### Common Debugging Scenarios

**API not responding**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Check [`.env`](.env) has correct `VITE_ADK_API_URL`
3. Check Network tab for request details
4. Check backend logs for errors

**Component not re-rendering**:
1. Check if data is actually changing
2. Verify React Query cache invalidation
3. Check if keys are unique in lists
4. Use React DevTools to inspect props

**TypeScript errors**:
1. Check type definitions match API responses
2. Run `npx tsc --noEmit` to see all errors
3. Restart TypeScript server in VS Code
4. Clear `node_modules/.vite` cache

**Styling not applying**:
1. Check Tailwind class names are correct
2. Verify [`tailwind.config.js`](tailwind.config.js) content paths
3. Restart dev server
4. Check for conflicting styles

---

## Contributing Guidelines

### Code Style

**TypeScript**:
- Use strict mode
- Avoid `any` types
- Define interfaces for all props
- Use meaningful variable names

**React**:
- Functional components only
- Use hooks for state and effects
- Keep components small and focused
- Extract logic into custom hooks

**CSS/Tailwind**:
- Use Tailwind utilities first
- Create custom CSS only when necessary
- Follow mobile-first approach
- Use semantic class names in custom CSS

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: fix bug in component
docs: update documentation
style: format code
refactor: refactor component logic
test: add tests
chore: update dependencies
```

**Examples**:
```bash
git commit -m "feat: add session deletion functionality"
git commit -m "fix: resolve message list scroll issue"
git commit -m "docs: update installation instructions"
```

### Pull Request Process

1. **Create feature branch**: `git checkout -b feature/my-feature`
2. **Make changes**: Implement your feature
3. **Test locally**: Ensure everything works
4. **Commit changes**: Use conventional commits
5. **Push to remote**: `git push origin feature/my-feature`
6. **Create PR**: On GitHub, create pull request
7. **Code review**: Address feedback
8. **Merge**: After approval, merge to main

### Code Review Checklist

- [ ] Code follows TypeScript best practices
- [ ] Components are properly typed
- [ ] Error handling is implemented
- [ ] Loading states are handled
- [ ] No console errors or warnings
- [ ] Responsive design works
- [ ] No unnecessary re-renders
- [ ] Code is self-documenting or has comments
- [ ] Follows existing patterns

---

## Best Practices

### Performance

1. **Memoization**: Use `React.memo()` for expensive components
2. **Lazy Loading**: Use `React.lazy()` for route-based splitting
3. **Optimize Images**: Compress and use appropriate formats
4. **Debounce Inputs**: For search/filter inputs
5. **Virtual Scrolling**: For very long lists

### Accessibility

1. **ARIA Labels**: Add to interactive elements
2. **Keyboard Navigation**: Ensure all features work with keyboard
3. **Focus Management**: Proper focus states
4. **Color Contrast**: Meet WCAG AA standards
5. **Screen Reader**: Test with screen readers

### Security

1. **Input Validation**: Validate all user inputs
2. **XSS Prevention**: Sanitize user-generated content
3. **HTTPS**: Use HTTPS in production
4. **Token Storage**: Use secure storage methods
5. **Dependencies**: Keep dependencies updated

### State Management

1. **Server State**: Use React Query for API data
2. **Local State**: Use useState for component state
3. **Global State**: Use Zustand only when necessary
4. **Derived State**: Calculate from existing state
5. **Form State**: Consider using React Hook Form

### Error Handling

1. **User-Friendly Messages**: Show clear error messages
2. **Error Boundaries**: Catch and handle errors gracefully
3. **Logging**: Log errors for debugging
4. **Retry Logic**: Implement retry for network failures
5. **Fallback UI**: Show fallback content on error

---

## Useful Commands

```bash
# Development
npm run dev                  # Start dev server
npm run build               # Build for production
npm run preview             # Preview production build
npm run lint                # Run ESLint

# Type Checking
npx tsc --noEmit           # Check types without building

# Package Management
npm install <package>       # Install new package
npm update                 # Update dependencies
npm audit                  # Check for vulnerabilities
npm audit fix              # Fix vulnerabilities

# Git
git status                 # Check status
git add .                  # Stage all changes
git commit -m "message"    # Commit changes
git push                   # Push to remote
git pull                   # Pull from remote

# Debugging
npm run dev -- --host      # Expose on network
npm run dev -- --port 3001 # Use different port
```

---

## Additional Resources

### Documentation

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [TanStack Query Docs](https://tanstack.com/query/latest/docs/react/overview)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com)

### Project Documentation

- [`README.md`](README.md) - User guide and quick start
- [`BACKEND_INTEGRATION.md`](BACKEND_INTEGRATION.md) - Backend setup guide
- [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) - Technical summary
- [`GUI_ARCHITECTURE.md`](../GUI_ARCHITECTURE.md) - Architecture details
- [`GUI_IMPLEMENTATION_PLAN.md`](../GUI_IMPLEMENTATION_PLAN.md) - Implementation guide

### Getting Help

- Check existing documentation first
- Search GitHub issues
- Check browser console for errors
- Use React Query DevTools for debugging
- Ask in team chat or discussions

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-30  
**Maintained By**: ADK GUI Development Team