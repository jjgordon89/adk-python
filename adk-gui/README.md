# ADK GUI

A modern, responsive web interface for interacting with the Agent Development Kit (ADK) agents. Built with React, TypeScript, and Tailwind CSS, this GUI provides an intuitive way to manage agent sessions, chat with AI agents, and visualize multi-agent workflows.

## Features

### Core Functionality

- **Session Management** - Create, view, and manage agent sessions with full CRUD operations
- **Real-time Chat Interface** - Interactive conversation with agents supporting streaming responses
- **Agent Invocation** - Send messages to agents and receive intelligent responses
- **Event History** - View complete history of agent interactions and tool invocations
- **Responsive Design** - Works seamlessly on desktop and tablet devices

### SafetyCulture Integration

Specialized components for SafetyCulture inspection workflows:

- **Asset Discovery View** - Display and filter discovered SafetyCulture assets
- **Template Match Display** - Visualize AI-powered template matching with confidence scores
- **Batch Operations** - Process multiple assets simultaneously
- **Database Browser** - View and query SQLite database contents

### Technical Highlights

- **Type-Safe Development** - Full TypeScript support for safer, more maintainable code
- **Modern State Management** - Zustand for global state, React Query for server state
- **Component Library** - shadcn/ui components built on Radix UI primitives
- **Real-time Updates** - Server-Sent Events (SSE) for streaming agent responses
- **Dark Mode Ready** - Theme support built-in (implementation pending)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** - Version 18.0 or higher
  ```bash
  node --version  # Should output v18.0.0 or higher
  ```

- **Package Manager** - npm (comes with Node) or pnpm (recommended)
  ```bash
  npm --version   # or
  pnpm --version
  ```

- **ADK Backend** - Running ADK FastAPI server (see [Backend Integration Guide](BACKEND_INTEGRATION.md))

## Installation

### 1. Clone or Navigate to the Project

```bash
cd adk-gui
```

### 2. Install Dependencies

Using npm:
```bash
npm install
```

Using pnpm (recommended):
```bash
pnpm install
```

### 3. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit [`.env`](.env) with your configuration:
```env
# Backend API URL (default: http://localhost:8000)
VITE_ADK_API_URL=http://localhost:8000

# Request timeout in milliseconds (default: 30000)
VITE_ADK_API_TIMEOUT=30000

# SSE reconnection delay in milliseconds (default: 3000)
VITE_SSE_RECONNECT_DELAY=3000

# Enable debug logging (default: false)
VITE_ENABLE_DEBUG=false
```

## Configuration

### Environment Variables

All configuration is managed through environment variables prefixed with `VITE_`:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VITE_ADK_API_URL` | Backend API base URL | `http://localhost:8000` | Yes |
| `VITE_ADK_API_TIMEOUT` | API request timeout (ms) | `30000` | No |
| `VITE_SSE_RECONNECT_DELAY` | SSE reconnection delay (ms) | `3000` | No |
| `VITE_ENABLE_DEBUG` | Enable debug logging | `false` | No |

### Backend Connection

The frontend connects to an ADK FastAPI backend. For detailed backend setup instructions, see [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md).

**Quick Backend Start:**
```bash
# In your ADK project directory
adk web path/to/your/agent.py

# Example with SafetyCulture agent
adk web safetyculture_agent/agent.py
```

Verify the backend is running:
```bash
curl http://localhost:8000/health
```

## Development

### Start Development Server

```bash
npm run dev
```

or with pnpm:
```bash
pnpm dev
```

The application will be available at **http://localhost:3000** (or the next available port).

### Development Features

- **Hot Module Replacement (HMR)** - Instant updates without losing application state
- **Fast Refresh** - Preserves component state during edits
- **TypeScript Checking** - Real-time type checking in your editor
- **React Query DevTools** - Inspect and debug server state (development only)

### Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server with HMR |
| `npm run build` | Build optimized production bundle |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint to check code quality |

## Build for Production

### Create Production Build

```bash
npm run build
```

This will:
1. Type-check the entire codebase
2. Bundle and minify JavaScript/CSS
3. Optimize assets
4. Output to the `dist/` directory

### Preview Production Build

Test the production build locally:

```bash
npm run preview
```

The preview server will start on **http://localhost:4173**.

### Production Deployment

The `dist/` directory contains static files that can be deployed to:
- **Vercel** - `vercel deploy`
- **Netlify** - Drag and drop `dist/` folder
- **AWS S3 + CloudFront** - Upload static files
- **Any static hosting service**

**Important:** Ensure your production environment variables are correctly configured for your backend API URL.

## Project Structure

```
adk-gui/
├── public/                      # Static assets
├── src/
│   ├── components/              # React components
│   │   ├── ui/                  # Base UI components (shadcn/ui)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── textarea.tsx
│   │   │   └── ...
│   │   ├── chat/                # Chat interface components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   └── MessageInput.tsx
│   │   ├── session/             # Session management components
│   │   │   └── SessionList.tsx
│   │   ├── layouts/             # Layout components
│   │   │   └── MainLayout.tsx
│   │   └── safetyculture/       # SafetyCulture-specific components
│   │       ├── AssetDiscoveryView.tsx
│   │       └── TemplateMatchDisplay.tsx
│   ├── services/                # API services
│   │   └── api/
│   │       ├── client.ts        # Base HTTP client
│   │       ├── sessions.ts      # Session API calls
│   │       └── agents.ts        # Agent API calls
│   ├── hooks/                   # Custom React hooks
│   │   └── api/
│   │       ├── useSessions.ts   # Session management hooks
│   │       └── useAgentInvoke.ts # Agent invocation hook
│   ├── types/                   # TypeScript type definitions
│   │   ├── adk.ts               # ADK-related types
│   │   └── safetyculture.ts     # SafetyCulture types
│   ├── lib/                     # Utility functions
│   │   ├── utils.ts             # General utilities
│   │   └── constants.ts         # Application constants
│   ├── App.tsx                  # Root application component
│   └── main.tsx                 # Application entry point
├── .env                         # Environment variables (local)
├── .env.example                 # Environment variables template
├── package.json                 # Dependencies and scripts
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── BACKEND_INTEGRATION.md      # Backend setup guide
└── README.md                   # This file
```

## Technology Stack

### Core Technologies

- **[React 19](https://react.dev)** - UI library for building component-based interfaces
- **[TypeScript 5.8](https://www.typescriptlang.org/)** - Type-safe JavaScript with enhanced developer experience
- **[Vite](https://vitejs.dev/)** - Next-generation frontend build tool with fast HMR
- **[Tailwind CSS 4](https://tailwindcss.com/)** - Utility-first CSS framework

### State Management

- **[Zustand](https://docs.pmnd.rs/zustand)** - Lightweight global state management
- **[TanStack Query (React Query)](https://tanstack.com/query)** - Powerful async state management for server data

### UI Components

- **[shadcn/ui](https://ui.shadcn.com)** - Re-usable components built with Radix UI and Tailwind CSS
- **[Radix UI](https://www.radix-ui.com/)** - Unstyled, accessible component primitives
- **[Lucide React](https://lucide.dev/)** - Beautiful, consistent icon set

### HTTP & Data Fetching

- **[Axios](https://axios-http.com/)** - Promise-based HTTP client
- **EventSource** - Native browser API for Server-Sent Events (SSE)

### Utilities

- **[date-fns](https://date-fns.org/)** - Modern date utility library
- **[clsx](https://github.com/lukeed/clsx)** - Utility for constructing className strings
- **[class-variance-authority](https://cva.style/)** - Component variant management

## Usage

### Starting a Session

1. **Start the backend server** (see [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md))
2. **Open the application** in your browser (http://localhost:3000)
3. **Click "New Session"** button in the sidebar
4. **Wait for session creation** - The new session will appear in the list

### Chatting with Agents

1. **Select a session** from the sidebar
2. **Type your message** in the input field at the bottom
3. **Press Enter** or click the send button
4. **View agent response** in the chat area
5. **Continue conversation** - The full context is maintained

### Using SafetyCulture Features

#### Asset Discovery

1. **Send a discovery command** to the agent:
   ```
   Find all equipment assets at the Main Site
   ```
2. **View results** in the Asset Discovery View
3. **Filter assets** by type, location, or status
4. **Select assets** for batch operations
5. **Export data** if needed

#### Template Matching

1. **Request template matching**:
   ```
   Match inspection templates to these assets
   ```
2. **Review AI-powered matches** with confidence scores
3. **Read AI reasoning** for each template recommendation
4. **Select appropriate templates** for your assets
5. **Override selections** if needed

#### Viewing Asset Details

- **Click on any asset** in the table to view details
- **Review metadata** including location, type, and history
- **Check last inspection date** to prioritize work
- **Navigate to related templates** for inspection creation

## SafetyCulture Features

The ADK GUI includes specialized components for SafetyCulture inspection workflows:

### Asset Discovery View

The [`AssetDiscoveryView`](src/components/safetyculture/AssetDiscoveryView.tsx) component provides:

- **Tabular Display** - Organized view of all discovered assets
- **Multi-select** - Batch selection with checkboxes
- **Filtering** - Filter by asset type, location, or status
- **Sorting** - Sort by any column
- **Asset Details** - Click to view full asset information
- **Export Options** - Export selected assets to CSV

### Template Match Display

The [`TemplateMatchDisplay`](src/components/safetyculture/TemplateMatchDisplay.tsx) component shows:

- **AI Confidence Scores** - Visual confidence indicators for each match
- **Match Reasoning** - AI-generated explanation for template selection
- **Template Preview** - Quick preview of template details
- **Confidence Levels** - High (>80%), Medium (60-80%), Low (<60%)
- **Color Coding** - Visual indicators for match quality
- **Override Options** - Manual template selection if needed

### Workflow Example

A typical SafetyCulture workflow:

1. **Discover Assets** → Agent finds all assets at a location
2. **View Results** → AssetDiscoveryView displays assets in table
3. **Match Templates** → Agent suggests inspection templates
4. **Review Matches** → TemplateMatchDisplay shows AI recommendations
5. **Create Inspections** → Generate inspections for selected assets
6. **Track Progress** → Monitor inspection completion status

## Development Guidelines

### Code Style

- **TypeScript** - Use strict typing, avoid `any`
- **Components** - Functional components with hooks
- **Naming** - PascalCase for components, camelCase for functions
- **File Structure** - One component per file, co-locate related files

### Component Patterns

```typescript
// Example component structure
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useSessions } from '@/hooks/api/useSessions'

interface MyComponentProps {
  sessionId: string
  onUpdate?: () => void
}

export function MyComponent({ sessionId, onUpdate }: MyComponentProps) {
  const [state, setState] = useState<string>('')
  const { data, isLoading } = useSessions()

  // Component logic here

  return (
    <div className="p-4">
      {/* JSX here */}
    </div>
  )
}
```

### API Integration

Use React Query hooks for all API calls:

```typescript
// Good - Using React Query
const { data, isLoading, error } = useSessions()

// Avoid - Direct API calls in components
useEffect(() => {
  fetch('/api/sessions').then(...)  // Don't do this
}, [])
```

### State Management

- **React Query** - For server state (API data)
- **Zustand** - For global client state (UI state, user preferences)
- **useState** - For local component state
- **useRef** - For values that don't trigger re-renders

## Troubleshooting

### Common Issues

#### Issue: Application Won't Start

**Solution:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# or with pnpm
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

#### Issue: Backend Connection Errors

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `.env` file has correct `VITE_ADK_API_URL`
3. Restart frontend: Stop server (Ctrl+C) and run `npm run dev` again
4. See [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) for detailed troubleshooting

#### Issue: CORS Errors in Console

**Solution:**
The project includes Vite proxy configuration that handles CORS automatically. If you still see errors:
1. Ensure backend is running on port 8000
2. Check [`vite.config.ts`](vite.config.ts) proxy configuration
3. See [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md#cors-configuration)

#### Issue: TypeScript Errors

**Solution:**
```bash
# Restart TypeScript server in VS Code
# Press Ctrl+Shift+P (Cmd+Shift+P on Mac)
# Type: "TypeScript: Restart TS Server"

# Or clear TypeScript cache
rm -rf node_modules/.vite
npm install
```

#### Issue: Styling Not Applied

**Solution:**
1. Ensure Tailwind CSS is properly configured
2. Check [`tailwind.config.js`](tailwind.config.js) includes correct paths
3. Verify `globals.css` is imported in `main.tsx`
4. Restart development server

### Getting Help

If you encounter issues:

1. **Check the logs** - Browser console and terminal output
2. **Enable debug mode** - Set `VITE_ENABLE_DEBUG=true` in `.env`
3. **Review documentation**:
   - [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) - Backend setup guide
   - [GUI_ARCHITECTURE.md](../GUI_ARCHITECTURE.md) - Architecture details
   - [GUI_IMPLEMENTATION_PLAN.md](../GUI_IMPLEMENTATION_PLAN.md) - Implementation guide

4. **Check dependencies** - Ensure all packages are installed correctly
5. **Search GitHub issues** - See if others have encountered similar problems

## Contributing

We welcome contributions! Here's how you can help:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run linting: `npm run lint`
5. Test thoroughly
6. Commit with conventional commits: `git commit -m "feat: add new feature"`
7. Push to your fork: `git push origin feature/my-feature`
8. Open a Pull Request

### Code Quality

- Follow TypeScript best practices
- Use ESLint and fix all warnings
- Write meaningful commit messages
- Add comments for complex logic
- Ensure responsive design
- Test on multiple browsers

### Areas for Contribution

- **New Features** - Additional SafetyCulture components, dashboard views
- **Performance** - Optimize rendering, reduce bundle size
- **Accessibility** - Improve ARIA labels, keyboard navigation
- **Testing** - Add unit and integration tests
- **Documentation** - Improve guides, add examples
- **Bug Fixes** - Fix reported issues

## License

This project is part of the ADK (Agent Development Kit) project and follows the same license.

See [LICENSE](../LICENSE) in the repository root for details.

## Related Documentation

- **[BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md)** - Complete guide for backend setup and integration
- **[GUI_ARCHITECTURE.md](../GUI_ARCHITECTURE.md)** - Detailed architecture and design decisions
- **[GUI_IMPLEMENTATION_PLAN.md](../GUI_IMPLEMENTATION_PLAN.md)** - Step-by-step implementation guide
- **[ADK Documentation](https://github.com/google/adk-python)** - Main ADK repository

## Resources

### Documentation

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [TanStack Query Docs](https://tanstack.com/query/latest/docs/react/overview)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com)

### ADK Resources

- [ADK GitHub Repository](https://github.com/google/adk-python)
- [ADK Documentation](https://github.com/google/adk-python/tree/main/docs)
- [SafetyCulture API](https://developer.safetyculture.com)

## Support

For questions, issues, or contributions:

- **GitHub Issues** - Report bugs or request features
- **Discussions** - Ask questions, share ideas
- **Pull Requests** - Contribute code improvements

---

**Built with ❤️ for the ADK community**

**Version:** 0.0.0  
**Last Updated:** 2025-01-30  
**Maintained By:** ADK GUI Team
