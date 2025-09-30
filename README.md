# SafetyCulture ADK Agent

An AI-powered agent system built on Google's Agent Development Kit (ADK) for automating SafetyCulture inspection workflows. This project demonstrates advanced multi-agent orchestration, AI-enhanced tools, and a modern React TypeScript GUI for enterprise inspection management.

## 🌟 Overview

The SafetyCulture ADK Agent automates complex inspection workflows by coordinating multiple specialized AI agents that work together to:

- **Discover assets** from SafetyCulture with intelligent filtering
- **Match inspection templates** using AI-powered pattern recognition
- **Create inspections** with pre-filled data and business rules
- **Fill out forms** automatically based on asset information
- **Track progress** with database-backed state management
- **Review quality** through automated QA processes

Built with flexibility and extensibility in mind, the system supports multiple AI model providers (Gemini, Llama, Nvidia, Ollama) and includes a professional web GUI for monitoring and interaction.

## 🎯 Key Features

### Multi-Agent Architecture
- **5 specialized agents** working in coordinated workflows
- **Automatic agent handoff** with context preservation
- **Parallel processing** for batch operations
- **Quality assurance** built into every workflow

### AI-Enhanced Capabilities
- **Template matching** with confidence scoring
- **Image analysis** for asset inspection
- **Historical pattern recognition** for predictive insights
- **Intelligent form filling** using business rules and AI

### Model Flexibility
- **4 AI providers**: Gemini (native), Llama (Vertex AI), Nvidia, Ollama
- **6 model aliases** for semantic configuration
- **Runtime switching** between providers without code changes
- **Cost optimization** through provider selection

### Professional GUI
- **React 19** with TypeScript for type safety
- **Real-time updates** via Server-Sent Events
- **Session management** with full CRUD operations
- **SafetyCulture visualizations** for assets and templates

### Production-Ready
- **Database tracking** with SQLite for state management
- **Memory integration** with ADK MemoryService
- **Comprehensive error handling** and logging
- **Extensible architecture** for custom tools

## 📋 Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Multi-Agent System](#multi-agent-system)
- [Model Configuration](#model-configuration)
- [GUI Application](#gui-application)
- [Development](#development)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   React TypeScript GUI                       │
│              (Real-time monitoring & control)                │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/SSE
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   ADK FastAPI Backend                        │
│              (/agent/invoke, /sessions/*)                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              SafetyCulture Coordinator Agent                 │
│         (Orchestrates multi-agent workflows)                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬────────────┐
        │               │               │            │
        ▼               ▼               ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌─────────┐ ┌─────────┐
│   Asset      │ │  Template    │ │Inspection│ │  Form   │
│  Discovery   │ │  Selection   │ │ Creation │ │ Filling │
│    Agent     │ │    Agent     │ │  Agent   │ │  Agent  │
└──────────────┘ └──────────────┘ └─────────┘ └─────────┘
        │               │               │            │
        └───────────────┴───────────────┴────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌─────────────┐
│SafetyCulture │ │  AI Tools    │ │  Database   │
│     API      │ │  (Gemini)    │ │  (SQLite)   │
└──────────────┘ └──────────────┘ └─────────────┘
```

## 📦 Prerequisites

### Required
- **Python 3.10+** - Agent runtime environment
- **Node.js 18+** - For GUI development (optional)
- **Google Cloud Project** - For Gemini API access
- **SafetyCulture Account** - With API access enabled

### Optional
- **Ollama** - For local model development
- **Nvidia API Key** - For Nvidia-hosted models
- **Docker** - For containerized deployment

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/adk-python.git
cd adk-python

# Install Python dependencies
pip install -r safetyculture_agent/requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Minimum required configuration:**
```env
# SafetyCulture API
SAFETYCULTURE_API_TOKEN=your_api_token_here

# Google Cloud (for Gemini)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1
```

### 3. Authenticate with Google Cloud

```bash
# Option 1: User credentials (development)
gcloud auth application-default login

# Option 2: Service account (production)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### 4. Start the Agent Server

```bash
# Start ADK web server with SafetyCulture agent
adk web safetyculture_agent/agent.py

# Server will start on http://localhost:8000
```

### 5. Run the GUI (Optional)

```bash
# Navigate to GUI directory
cd adk-gui

# Install dependencies
npm install

# Start development server
npm run dev

# GUI will open at http://localhost:3000
```

### 6. Test the Agent

```bash
# Create a test session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"agentId": "default"}'

# Invoke the agent
curl -X POST http://localhost:8000/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session_xxx",
    "message": "Find all equipment assets at Main Site"
  }'
```

## 📥 Installation

### Python Agent Setup

1. **Install ADK and dependencies:**
   ```bash
   pip install google-adk>=1.0.0
   pip install -r safetyculture_agent/requirements.txt
   ```

2. **Verify installation:**
   ```bash
   python -c "import google.adk; print(google.adk.__version__)"
   ```

3. **Set up Google Cloud authentication:**
   ```bash
   # Install gcloud CLI
   # See: https://cloud.google.com/sdk/docs/install

   # Authenticate
   gcloud auth application-default login
   
   # Set project
   gcloud config set project YOUR_PROJECT_ID
   
   # Enable required APIs
   gcloud services enable aiplatform.googleapis.com
   ```

4. **Get SafetyCulture API token:**
   - Visit https://app.safetyculture.com/account/api-tokens
   - Generate a new API token
   - Add to `.env` file

### GUI Setup (Optional)

1. **Install Node.js dependencies:**
   ```bash
   cd adk-gui
   npm install
   ```

2. **Configure GUI environment:**
   ```bash
   cp .env.example .env
   # Edit .env with backend URL (default: http://localhost:8000)
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

## ⚙️ Configuration

### Environment Variables

The project uses environment variables for all configuration. See [`.env.example`](.env.example) for the complete template.

**Core Configuration:**
```env
# SafetyCulture API (Required)
SAFETYCULTURE_API_TOKEN=your_token_here

# Google Cloud (Required for Gemini)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1

# Optional: Other model providers
# NVIDIA_API_KEY=your_nvidia_key
# OLLAMA_BASE_URL=http://localhost:11434
```

### Model Configuration

The agent supports multiple AI model providers through a flexible configuration system. See [`MODEL_CONFIGURATION.md`](MODEL_CONFIGURATION.md) for detailed setup instructions.

**Quick model switching:**
```bash
# Use default (Gemini Flash)
adk web safetyculture_agent/agent.py

# Use Ollama for local development
export MODEL_PROVIDER=ollama
adk web safetyculture_agent/agent.py

# Use specific model via alias
# Edit safetyculture_agent/config/models.yaml
```

**Supported providers:**
- **Gemini** (default) - Native Google AI with best integration
- **Llama** - Via Vertex AI Model-as-a-Service
- **Nvidia** - High-performance cloud inference
- **Ollama** - Local development with zero API costs

### Custom Configuration

Create `safetyculture_agent/config/models.local.yaml` for personal overrides:

```yaml
# Override default provider
default_provider: ollama

# Enable additional providers
providers:
  ollama:
    enabled: true
  
# Add custom aliases
model_aliases:
  my_dev: ollama/llama3
```

## 💻 Usage

### Basic Agent Invocation

```python
from google.adk.runners import Runner
from safetyculture_agent.agent import root_agent

# Create runner
runner = Runner(agent=root_agent)

# Run agent with a message
result = await runner.run(
    user_id="user123",
    session_id="session456",
    message="Find all fire extinguishers that need inspection this month"
)

print(result.response)
```

### Common Workflows

#### 1. Asset Discovery
```python
# Find assets by type
message = "Search for all equipment assets at the Sydney office"
result = await runner.run(user_id="user123", message=message)
```

#### 2. Batch Inspection Creation
```python
# Create inspections for multiple assets
message = """
Create monthly safety inspections for all fire extinguishers 
at Main Building using the Fire Safety template
"""
result = await runner.run(user_id="user123", message=message)
```

#### 3. Template Matching
```python
# Let AI match templates to asset types
message = "Match appropriate inspection templates to all HVAC equipment"
result = await runner.run(user_id="user123", message=message)
```

#### 4. Form Auto-Fill
```python
# Fill inspection forms automatically
message = """
Fill out the monthly inspection form for asset HVAC-001 
using the standard maintenance checklist
"""
result = await runner.run(user_id="user123", message=message)
```

### Using the GUI

1. **Start a new session** - Click "New Session" in sidebar
2. **Send a message** - Type your request in the chat input
3. **Monitor progress** - Watch agent workflow in real-time
4. **View results** - See asset discovery and template matching results
5. **Export data** - Download reports and inspection summaries

For detailed GUI usage, see [`adk-gui/README.md`](adk-gui/README.md).

## 📁 Project Structure

```
adk-python/
├── safetyculture_agent/          # Main agent implementation
│   ├── agent.py                  # Root agent and coordinator
│   ├── agents/                   # Specialized sub-agents
│   │   ├── asset_discovery_agent.py
│   │   ├── template_selection_agent.py
│   │   ├── inspection_creation_agent.py
│   │   └── form_filling_agent.py
│   ├── tools/                    # SafetyCulture API tools
│   │   └── safetyculture_tools.py
│   ├── ai/                       # AI-enhanced capabilities
│   │   └── ai_tools.py
│   ├── database/                 # SQLite tracking tools
│   │   └── database_tools.py
│   ├── memory/                   # ADK memory integration
│   │   ├── memory_tools.py
│   │   └── README.md
│   ├── config/                   # Model configuration system
│   │   ├── models.yaml           # Base model definitions
│   │   ├── model_config.py       # Configuration classes
│   │   ├── model_loader.py       # YAML loader
│   │   └── model_factory.py      # Model instantiation
│   └── requirements.txt          # Python dependencies
│
├── adk-gui/                      # React TypeScript GUI
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/             # API clients
│   │   ├── hooks/                # Custom React hooks
│   │   └── types/                # TypeScript definitions
│   ├── package.json
│   └── README.md
│
├── .env.example                  # Environment template
├── README.md                     # This file
├── MODEL_CONFIGURATION.md        # Model setup guide
├── MODEL_PROVIDER_CONFIGURATION_DESIGN.md  # Architecture docs
└── GUI_ARCHITECTURE.md           # GUI design document
```

## 🤖 Multi-Agent System

The SafetyCulture agent uses a coordinated multi-agent architecture with 5 specialized agents:

### 1. SafetyCulture Coordinator
**Role:** Orchestrates the entire workflow  
**Capabilities:**
- Understands user requirements
- Delegates to appropriate sub-agents
- Manages workflow state
- Provides status updates

### 2. Asset Discovery Agent
**Role:** Finds and catalogs SafetyCulture assets  
**Tools:**
- [`search_safetyculture_assets()`](safetyculture_agent/tools/safetyculture_tools.py)
- [`get_safetyculture_asset_details()`](safetyculture_agent/tools/safetyculture_tools.py)
- Database tracking tools

### 3. Template Selection Agent
**Role:** Matches inspection templates to assets  
**Capabilities:**
- AI-powered template matching
- Confidence scoring
- Asset type pattern recognition
- Historical analysis

### 4. Inspection Creation Agent
**Role:** Creates new inspections with pre-filled data  
**Tools:**
- [`create_safetyculture_inspection()`](safetyculture_agent/tools/safetyculture_tools.py)
- Template application
- Business rule enforcement

### 5. Form Filling Agent
**Role:** Automatically fills inspection forms  
**Capabilities:**
- Intelligent data extraction
- Field mapping
- Validation logic
- Multi-section forms

### 6. Quality Assurance Agent
**Role:** Reviews and validates completed work  
**Capabilities:**
- Data quality checks
- Consistency validation
- Success rate tracking
- Improvement recommendations

## 🎛️ Model Configuration

The project includes a sophisticated model configuration system supporting multiple providers. This allows you to:

- **Switch providers** without code changes
- **Test locally** with Ollama (zero API costs)
- **Optimize costs** by choosing appropriate models
- **Customize per environment** (dev/staging/prod)

### Quick Configuration

**Use default Gemini:**
```bash
# No configuration needed - works out of the box
adk web safetyculture_agent/agent.py
```

**Switch to local Ollama:**
```bash
# Install Ollama: https://ollama.ai
ollama pull llama3
export MODEL_PROVIDER=ollama
adk web safetyculture_agent/agent.py
```

**Use different model for specific agent:**
```python
from safetyculture_agent.config.model_factory import ModelFactory

factory = ModelFactory()

# Use fast model for coordination
coordinator = factory.create_model('coordinator')

# Use pro model for complex analysis
analyst = factory.create_model('analysis')
```

For complete model configuration documentation, see [`MODEL_CONFIGURATION.md`](MODEL_CONFIGURATION.md).

## 🖥️ GUI Application

The project includes a professional React TypeScript GUI for monitoring and interacting with the agent system.

### Features

- **Session Management** - Create, view, and manage agent sessions
- **Real-time Chat** - Interactive conversation with streaming responses
- **Asset Visualization** - Table view of discovered assets with filtering
- **Template Matching** - AI confidence scores and reasoning display
- **Progress Tracking** - Visual workflow status indicators
- **Responsive Design** - Works on desktop and tablet devices

### Technology Stack

- **React 19** with TypeScript 5.8
- **Vite** for fast development and optimized builds
- **TanStack Query** for server state management
- **Tailwind CSS** for styling
- **shadcn/ui** for accessible components

### GUI Setup

```bash
cd adk-gui
npm install
cp .env.example .env
# Edit .env with backend URL
npm run dev
```

For complete GUI documentation, see [`adk-gui/README.md`](adk-gui/README.md).

## 🛠️ Development

### Setting Up Development Environment

1. **Clone repository:**
   ```bash
   git clone https://github.com/yourusername/adk-python.git
   cd adk-python
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r safetyculture_agent/requirements.txt
   ```

4. **Set up Ollama for local development:**
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3
   export MODEL_PROVIDER=ollama
   ```

### Running Tests

```bash
# Run ADK unit tests
pytest tests/unittests

# Run integration tests
pytest tests/integration
```

### Code Style

The project follows Google Python Style Guide:
- 2-space indentation
- 80-character line length
- Snake_case for functions/variables
- CamelCase for classes
- Comprehensive docstrings

### Adding New Tools

1. Create tool function in appropriate module
2. Add to agent's tools list in [`agent.py`](safetyculture_agent/agent.py)
3. Update documentation
4. Add tests

Example:
```python
def my_custom_tool(param: str) -> str:
    """Tool description for AI model.
    
    Args:
        param: Parameter description
        
    Returns:
        Result description
    """
    # Implementation
    return result
```

## 🚀 Deployment

### Local Deployment

```bash
# Start the agent server
adk web safetyculture_agent/agent.py

# In another terminal, start the GUI (optional)
cd adk-gui
npm run build
npm run preview
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY safetyculture_agent/ ./safetyculture_agent/
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["adk", "web", "safetyculture_agent/agent.py", "--host", "0.0.0.0"]
```

Build and run:
```bash
docker build -t safetyculture-agent .
docker run -p 8000:8000 \
  -e SAFETYCULTURE_API_TOKEN=$SAFETYCULTURE_API_TOKEN \
  -e GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
  safetyculture-agent
```

### Cloud Deployment

**Google Cloud Run:**
```bash
# Build and deploy
gcloud run deploy safetyculture-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

**AWS ECS/Fargate:**
- Use provided Dockerfile
- Configure environment variables via ECS task definition
- Set up Application Load Balancer
- Enable CloudWatch logging

## 📚 Documentation

### Core Documentation
- **[README.md](README.md)** - This file (project overview)
- **[MODEL_CONFIGURATION.md](MODEL_CONFIGURATION.md)** - Model provider setup (1,141 lines)
- **[MODEL_PROVIDER_CONFIGURATION_DESIGN.md](MODEL_PROVIDER_CONFIGURATION_DESIGN.md)** - Architecture design (919 lines)
- **[GUI_ARCHITECTURE.md](GUI_ARCHITECTURE.md)** - GUI design and architecture (1,040 lines)

### Component Documentation
- **[safetyculture_agent/memory/README.md](safetyculture_agent/memory/README.md)** - Memory service integration (351 lines)
- **[adk-gui/README.md](adk-gui/README.md)** - GUI user guide (555 lines)
- **[adk-gui/BACKEND_INTEGRATION.md](adk-gui/BACKEND_INTEGRATION.md)** - Backend setup guide (687 lines)
- **[adk-gui/IMPLEMENTATION_SUMMARY.md](adk-gui/IMPLEMENTATION_SUMMARY.md)** - Implementation details (978 lines)

### External Resources
- **[ADK Documentation](https://github.com/google/adk-python)** - Official ADK guide
- **[SafetyCulture API](https://developer.safetyculture.com)** - API reference
- **[Gemini API](https://ai.google.dev/docs)** - Model documentation

## 🔧 Troubleshooting

### Common Issues

#### Agent Won't Start

**Problem:** `ModuleNotFoundError` or import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r safetyculture_agent/requirements.txt --upgrade

# Verify ADK installation
python -c "import google.adk; print('ADK OK')"
```

#### Authentication Failures

**Problem:** `401 Unauthorized` or `Permission denied`

**Solution:**
```bash
# Re-authenticate with Google Cloud
gcloud auth application-default login

# Verify credentials
gcloud auth list

# Check environment variables
echo $SAFETYCULTURE_API_TOKEN
echo $GOOGLE_CLOUD_PROJECT
```

#### Model Provider Errors

**Problem:** `Unknown provider` or `Model not found`

**Solution:**
1. Check [`models.yaml`](safetyculture_agent/config/models.yaml) configuration
2. Verify provider is enabled
3. Ensure required environment variables are set
4. See [`MODEL_CONFIGURATION.md`](MODEL_CONFIGURATION.md#troubleshooting)

#### GUI Connection Issues

**Problem:** Backend connection refused or CORS errors

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `.env` file in `adk-gui/` directory
3. Restart both backend and frontend
4. See [`adk-gui/BACKEND_INTEGRATION.md`](adk-gui/BACKEND_INTEGRATION.md#troubleshooting)

### Getting Help

If you encounter issues not covered here:

1. **Check logs** - Backend terminal and browser console
2. **Enable debug mode** - Set `DEBUG=true` in `.env`
3. **Review documentation** - Comprehensive guides available
4. **Search issues** - Check GitHub issues for similar problems
5. **Ask for help** - Open a new issue with details

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Process

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/my-feature`
3. **Make your changes** with clear commit messages
4. **Run tests** to ensure nothing breaks
5. **Update documentation** if needed
6. **Submit a pull request**

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add new asset filtering capability
fix: Resolve template matching timeout issue
docs: Update model configuration guide
test: Add integration tests for form filling
```

### Code Standards

- Follow Google Python Style Guide
- Add type hints to all functions
- Write comprehensive docstrings
- Include tests for new features
- Update documentation

### Areas for Contribution

- 🆕 **New Features** - Additional SafetyCulture integrations
- 🐛 **Bug Fixes** - Fix reported issues
- 📖 **Documentation** - Improve guides and examples
- 🧪 **Testing** - Increase test coverage
- 🎨 **GUI** - Enhance user interface
- ⚡ **Performance** - Optimize agent workflows

## 📄 License

Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this project except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## 🙏 Acknowledgments

Built on the [Agent Development Kit (ADK)](https://github.com/google/adk-python) by Google.

Special thanks to:
- **Google ADK Team** - For the excellent agent framework
- **SafetyCulture** - For the comprehensive API
- **ADK Community** - For feedback and contributions

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-30  
**Status:** Production Ready ✅

For questions, issues, or contributions, please visit our [GitHub repository](https://github.com/yourusername/adk-python).
