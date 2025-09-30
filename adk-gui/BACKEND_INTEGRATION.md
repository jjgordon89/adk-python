# ADK Backend Integration Guide

## Overview

The ADK GUI is a React-based web interface that connects to the Agent Development Kit (ADK) FastAPI backend server. This guide covers everything you need to know about setting up, configuring, and troubleshooting the backend integration.

The backend provides a RESTful API that enables:
- Session management (create, read, update, delete)
- Agent invocation and interaction
- Real-time streaming responses via Server-Sent Events (SSE)
- Artifact storage and retrieval
- Event tracking and history

## Prerequisites

Before connecting the frontend to the ADK backend, ensure you have:

- **Python 3.10 or higher** installed
- **ADK Python package** installed (`pip install google-adk`)
- **At least one agent configured** (e.g., SafetyCulture agent)
- **Environment variables** properly configured
- **Network access** to localhost port 8000 (or your configured port)

### Verify Python Installation

```bash
python --version  # Should be 3.10+
```

### Verify ADK Installation

```bash
pip show google-adk
# or
python -c "import google.adk; print(google.adk.__version__)"
```

## Starting the ADK Backend

### Basic Startup

The ADK backend is started using the [`adk web`](adk:1) command, which launches a FastAPI server that exposes your agents via HTTP endpoints.

```bash
# Navigate to your ADK project directory
cd /path/to/adk-python

# Start the server with a specific agent
adk web path/to/your/agent.py

# Example: Start with SafetyCulture agent
adk web safetyculture_agent/agent.py
```

### Server Configuration

By default, the server starts on **port 8000**. You can customize this:

```bash
# Start on a different port
adk web --port 8080 path/to/agent.py

# Start with specific host
adk web --host 0.0.0.0 --port 8000 path/to/agent.py
```

### Expected Output

When the server starts successfully, you should see output similar to:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Verification Steps

### 1. Health Check

Verify the backend is running and responsive:

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. List Sessions

Check that the sessions endpoint is accessible:

```bash
curl http://localhost:8000/sessions
```

**Expected Response:**
```json
[]
```
or a list of existing sessions.

### 3. Create a Test Session

Create a session to verify write operations:

```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"agentId": "default"}'
```

**Expected Response:**
```json
{
  "id": "session_abc123",
  "agentId": "default",
  "createdAt": "2025-01-30T10:00:00Z",
  "status": "active"
}
```

### 4. Test Agent Invocation

Invoke the agent with a simple message:

```bash
curl -X POST http://localhost:8000/agents/default/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session_abc123",
    "message": "Hello, agent!"
  }'
```

**Expected Response:**
```json
{
  "sessionId": "session_abc123",
  "response": "Hello! How can I help you?",
  "events": [...]
}
```

## CORS Configuration

If you encounter CORS (Cross-Origin Resource Sharing) errors when connecting the frontend to the backend, you'll need to configure CORS settings.

### Understanding CORS Errors

CORS errors occur when:
- The frontend (http://localhost:3000) tries to access the backend (http://localhost:8000)
- The backend doesn't explicitly allow cross-origin requests
- Browser security blocks the request

**Common CORS Error:**
```
Access to fetch at 'http://localhost:8000/sessions' from origin 'http://localhost:3000' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present 
on the requested resource.
```

### Solution 1: Using Vite Proxy (Recommended for Development)

The ADK GUI project includes a Vite proxy configuration in [`vite.config.ts`](vite.config.ts:12-20) that automatically proxies API requests:

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
}
```

With this configuration, the frontend makes requests to `/api/sessions` which are automatically proxied to `http://localhost:8000/sessions`.

### Solution 2: Configure Backend CORS

If you need to configure CORS on the backend, you can modify the ADK FastAPI server. Create a custom server configuration:

```python
# custom_server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... rest of your ADK configuration
```

### Solution 3: Development Browser Extension

For development only, you can use a browser extension to disable CORS:
- **Chrome**: "Allow CORS: Access-Control-Allow-Origin"
- **Firefox**: "CORS Everywhere"

**⚠️ Warning:** Only use browser extensions in development. Never deploy to production with CORS disabled.

## Environment Variables

The frontend uses environment variables to configure the backend connection. These are defined in the [`.env`](adk-gui/.env) file.

### Required Variables

```env
# Backend API URL
VITE_ADK_API_URL=http://localhost:8000

# Request timeout in milliseconds
VITE_ADK_API_TIMEOUT=30000

# SSE reconnection delay in milliseconds
VITE_SSE_RECONNECT_DELAY=3000

# Enable debug logging
VITE_ENABLE_DEBUG=false
```

### Configuration for Different Environments

**Local Development:**
```env
VITE_ADK_API_URL=http://localhost:8000
VITE_ENABLE_DEBUG=true
```

**Production:**
```env
VITE_ADK_API_URL=https://api.yourdomain.com
VITE_ENABLE_DEBUG=false
```

**Custom Port:**
```env
VITE_ADK_API_URL=http://localhost:8080
```

## API Endpoints Reference

### Sessions

#### List All Sessions
```http
GET /sessions
```

**Response:**
```json
[
  {
    "id": "string",
    "agentId": "string",
    "metadata": {},
    "createdAt": "string",
    "updatedAt": "string",
    "status": "active"
  }
]
```

#### Create Session
```http
POST /sessions
Content-Type: application/json

{
  "agentId": "string",
  "metadata": {}
}
```

#### Get Session Details
```http
GET /sessions/{sessionId}
```

#### Update Session
```http
PATCH /sessions/{sessionId}
Content-Type: application/json

{
  "metadata": {},
  "status": "completed"
}
```

#### Delete Session
```http
DELETE /sessions/{sessionId}
```

#### Get Session Events
```http
GET /sessions/{sessionId}/events
```

### Agent Operations

#### Invoke Agent
```http
POST /agents/{agentName}/invoke
Content-Type: application/json

{
  "sessionId": "string",
  "message": "string",
  "streaming": false
}
```

#### Stream Agent Responses (SSE)
```http
GET /agents/stream?sessionId={sessionId}
```

This endpoint uses Server-Sent Events for real-time streaming.

### Artifacts

#### Get Artifact Content
```http
GET /artifacts/{artifactId}
```

#### List Session Artifacts
```http
GET /sessions/{sessionId}/artifacts
```

## Troubleshooting

### Common Connection Issues

#### Issue: Connection Refused

**Symptoms:**
- `ERR_CONNECTION_REFUSED` error in browser console
- Frontend cannot reach backend
- API requests timeout

**Solutions:**

1. **Verify backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check the port:**
   - Ensure backend is running on port 8000 (or your configured port)
   - Verify no other service is using the port:
     ```bash
     # Windows
     netstat -ano | findstr :8000
     
     # Linux/Mac
     lsof -i :8000
     ```

3. **Check firewall settings:**
   - Ensure localhost connections are allowed
   - Temporarily disable firewall to test

4. **Verify environment variables:**
   - Check [`.env`](adk-gui/.env) file has correct `VITE_ADK_API_URL`
   - Restart frontend after changing `.env`

#### Issue: CORS Errors

**Symptoms:**
- "blocked by CORS policy" messages in console
- Requests fail with network error
- OPTIONS preflight requests failing

**Solutions:**

1. **Use Vite proxy** (easiest for development)
   - Already configured in [`vite.config.ts`](vite.config.ts:12-20)
   - No backend changes needed

2. **Configure backend CORS** (see CORS Configuration section above)

3. **Verify proxy configuration:**
   ```bash
   # Requests should go to /api/* not http://localhost:8000/*
   # Example: /api/sessions instead of http://localhost:8000/sessions
   ```

#### Issue: Backend Not Responding

**Symptoms:**
- Backend starts but requests timeout
- No response from health check
- Server logs show errors

**Solutions:**

1. **Check backend logs:**
   - Look for Python exceptions or stack traces
   - Verify agent loaded successfully

2. **Verify Python dependencies:**
   ```bash
   pip list | grep google-adk
   pip check
   ```

3. **Test with curl:**
   ```bash
   curl -v http://localhost:8000/health
   ```

4. **Restart backend:**
   ```bash
   # Stop server (Ctrl+C)
   # Start again
   adk web path/to/agent.py
   ```

#### Issue: 404 Not Found

**Symptoms:**
- Specific endpoints return 404
- Some routes work, others don't

**Solutions:**

1. **Verify endpoint paths:**
   - Check API documentation for correct paths
   - Ensure you're using the right HTTP method (GET, POST, etc.)

2. **Check ADK version:**
   - API endpoints may differ between versions
   - Update ADK if needed: `pip install --upgrade google-adk`

3. **Verify agent configuration:**
   - Some endpoints may be agent-specific
   - Check agent is properly loaded

#### Issue: Authentication Errors

**Symptoms:**
- 401 Unauthorized responses
- "Invalid token" errors

**Solutions:**

1. **Check if authentication is required:**
   - Development mode may not require auth
   - Production environments typically do

2. **Verify token storage:**
   - Check localStorage for `adk_auth_token`
   - Ensure token is included in request headers

3. **Token expiration:**
   - Tokens may expire after a period
   - Re-authenticate if needed

### Performance Issues

#### Slow Response Times

**Possible Causes:**
- Large session history
- Complex agent operations
- Network latency
- Backend resource constraints

**Solutions:**

1. **Increase timeout:**
   ```env
   VITE_ADK_API_TIMEOUT=60000  # 60 seconds
   ```

2. **Monitor backend resources:**
   - Check CPU and memory usage
   - Scale backend if needed

3. **Optimize queries:**
   - Use pagination for large datasets
   - Limit event history retrieval

#### Connection Timeouts

**Solutions:**

1. **Check network connectivity:**
   ```bash
   ping localhost
   ```

2. **Increase timeout values:**
   - In [`.env`](adk-gui/.env)
   - In API client configuration

3. **Verify backend is not overloaded:**
   - Check server logs for performance issues
   - Monitor resource usage

## Testing the Full Stack

### Step-by-Step Testing

1. **Start the Backend:**
   ```bash
   cd /path/to/adk-python
   adk web safetyculture_agent/agent.py
   ```
   Wait for "Application startup complete" message.

2. **Verify Backend Health:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Start the Frontend:**
   ```bash
   cd adk-gui
   npm run dev
   ```

4. **Open Browser:**
   - Navigate to `http://localhost:3000`
   - Open browser DevTools (F12)
   - Check Console and Network tabs

5. **Test Session Creation:**
   - Click "New Session" button
   - Verify request in Network tab
   - Check for any errors in Console

6. **Test Agent Interaction:**
   - Send a message to the agent
   - Verify message appears in chat
   - Wait for agent response
   - Check streaming if enabled

7. **Monitor Backend Logs:**
   - Watch terminal running `adk web`
   - Look for request logs
   - Check for any errors or warnings

### Using Browser DevTools

**Network Tab:**
- View all API requests
- Check request/response headers
- Inspect response bodies
- Monitor timing information

**Console Tab:**
- Check for JavaScript errors
- View debug logs (if `VITE_ENABLE_DEBUG=true`)
- Monitor state changes

**Application Tab:**
- Inspect localStorage
- Check session storage
- View cookies (if used)

## Advanced Configuration

### Custom Backend URL

For production or custom deployments:

```env
# Remote backend
VITE_ADK_API_URL=https://adk-backend.example.com

# Custom port
VITE_ADK_API_URL=http://localhost:8080

# Different host
VITE_ADK_API_URL=http://192.168.1.100:8000
```

### Request Interceptors

The API client in [`src/services/api/client.ts`](adk-gui/src/services/api/client.ts) includes interceptors for:
- Adding authentication tokens
- Handling global errors
- Logging requests (in debug mode)
- Retry logic

### Timeout Configuration

Adjust timeouts based on your needs:

```env
# Short timeout for quick operations
VITE_ADK_API_TIMEOUT=10000  # 10 seconds

# Long timeout for complex agent operations
VITE_ADK_API_TIMEOUT=120000  # 2 minutes
```

## Security Considerations

### Development vs Production

**Development:**
- CORS can be permissive
- Debug logging enabled
- No authentication required (typically)
- HTTP acceptable

**Production:**
- Strict CORS configuration
- Debug logging disabled
- Authentication required
- HTTPS mandatory

### Best Practices

1. **Use HTTPS in production:**
   ```env
   VITE_ADK_API_URL=https://api.yourdomain.com
   ```

2. **Secure token storage:**
   - Use httpOnly cookies when possible
   - Avoid localStorage for sensitive tokens in production

3. **Implement authentication:**
   - Add API keys or JWT tokens
   - Configure in API client interceptors

4. **Rate limiting:**
   - Implement on backend
   - Handle 429 responses in frontend

## Getting Help

If you encounter issues not covered in this guide:

1. **Check backend logs:**
   - Look for detailed error messages
   - Python stack traces provide valuable debugging information

2. **Enable debug mode:**
   ```env
   VITE_ENABLE_DEBUG=true
   ```

3. **Check browser console:**
   - JavaScript errors
   - Network failures
   - State management issues

4. **Review ADK documentation:**
   - [ADK GitHub Repository](https://github.com/google/adk-python)
   - [ADK Documentation](https://github.com/google/adk-python/tree/main/docs)

5. **Community resources:**
   - GitHub Issues
   - Stack Overflow
   - ADK community forums

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-30  
**Maintained By:** ADK GUI Team