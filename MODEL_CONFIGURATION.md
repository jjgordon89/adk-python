# Model Configuration Guide

A comprehensive guide to configuring and using multiple AI model providers with the SafetyCulture ADK Agent.

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration Overview](#configuration-overview)
- [Provider-Specific Setup](#provider-specific-setup)
  - [Gemini (Google AI)](#gemini-google-ai)
  - [Llama (Vertex AI MaaS)](#llama-vertex-ai-maas)
  - [Nvidia](#nvidia)
  - [Ollama (Local)](#ollama-local)
- [Model Aliases](#model-aliases)
- [Advanced Configuration](#advanced-configuration)
- [Migration Guide](#migration-guide)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

Get up and running with the model configuration system in 5 minutes.

### 1. Set Up Environment Variables

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Required for Gemini (default provider)
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_REGION=us-central1

# Required for SafetyCulture
SAFETYCULTURE_API_TOKEN=your-api-token-here
```

### 2. Use the Default Configuration

The system works out of the box with Gemini:

```python
from safetyculture_agent.config.model_factory import ModelFactory

# Create factory instance
factory = ModelFactory()

# Use default model (Gemini 2.0 Flash)
model = factory.create_model()

# Use with ADK agents
from google.adk.agents.llm_agent import LlmAgent

agent = LlmAgent(
    name="MyAgent",
    model=factory.create_model('coordinator'),  # Uses alias
    instruction="You are a helpful assistant."
)
```

### 3. Switch Models Easily

```python
# Use different models via aliases
fast_model = factory.create_model('coordinator')  # Gemini Flash
pro_model = factory.create_model('qa')            # Gemini Pro
local_model = factory.create_model('local_dev')   # Ollama (if configured)

# Or specify directly
model = factory.create_model('gemini:pro')
model = factory.create_model('ollama/llama3')
```

### 4. Override Model Parameters

```python
# Customize model behavior at runtime
model = factory.create_model(
    'coordinator',
    generation_config={
        'temperature': 0.3,
        'max_output_tokens': 4096
    }
)
```

That's it! You're now using the configurable model system. Continue reading for advanced features and provider-specific setup.

---

## Configuration Overview

The model configuration system provides a flexible, three-tier approach to managing AI model providers.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│          Application Layer (Your Code)              │
│  ┌──────────────┐  ┌──────────────┐                │
│  │  LlmAgent 1  │  │  LlmAgent 2  │  ...           │
│  └──────┬───────┘  └──────┬───────┘                │
└─────────┼──────────────────┼──────────────────────┘
          │                  │
          ▼                  ▼
┌─────────────────────────────────────────────────────┐
│        Configuration Layer (ModelFactory)           │
│  ┌──────────────────────────────────────────────┐  │
│  │  ModelConfigLoader                           │  │
│  │  • Loads models.yaml                         │  │
│  │  • Merges models.local.yaml (optional)       │  │
│  │  • Applies environment variables             │  │
│  │  • Resolves aliases                          │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│         Provider Layer (ADK Models)                 │
│  ┌──────────┐  ┌──────────────────────────────┐   │
│  │  Gemini  │  │  LiteLlm                      │   │
│  │ (Native) │  │  • Llama (Vertex AI)          │   │
│  │          │  │  • Nvidia                     │   │
│  │          │  │  • Ollama                     │   │
│  └──────────┘  └───────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Three-Tier Configuration

The system applies configuration in priority order:

1. **Runtime Arguments** (Highest Priority)
   - Parameters passed to [`create_model()`](safetyculture_agent/config/model_factory.py:69)
   - Override everything else

2. **Environment Variables**
   - Defined in `.env` file
   - Provider-specific credentials
   - Global overrides like `MODEL_PROVIDER`

3. **YAML Configuration** (Lowest Priority)
   - [`models.yaml`](safetyculture_agent/config/models.yaml) - Base configuration
   - `models.local.yaml` - Optional user overrides (gitignored)

### File Locations

```
safetyculture_agent/
├── config/
│   ├── model_config.py      # Configuration dataclasses
│   ├── model_loader.py      # YAML loading with env vars
│   ├── model_factory.py     # Model instantiation
│   ├── models.yaml          # Default configuration
│   └── models.local.yaml    # Your overrides (optional)
├── .env                      # Your credentials (gitignored)
└── .env.example             # Template
```

### Model Specification Formats

The system accepts multiple formats for specifying models:

| Format | Example | Description |
|--------|---------|-------------|
| Alias | `'coordinator'` | Uses pre-defined semantic alias |
| Provider:Model | `'gemini:fast'` | Direct provider and model |
| Provider/Model | `'ollama/llama3'` | Alternative separator |
| Provider Only | `'gemini'` | Uses provider's default model |
| None | `None` | Uses system default |

---

## Provider-Specific Setup

### Gemini (Google AI)

**Default provider** - Optimized for production use with native integration.

#### Prerequisites

- Google Cloud Project with billing enabled
- Vertex AI API enabled
- Application Default Credentials configured

#### Setup Steps

1. **Install Google Cloud SDK** (if not already installed):
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Windows
   # Download from https://cloud.google.com/sdk/docs/install
   
   # Linux
   curl https://sdk.cloud.google.com | bash
   ```

2. **Authenticate**:
   ```bash
   # Option 1: User credentials (recommended for development)
   gcloud auth application-default login
   
   # Option 2: Service account (recommended for production)
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
   ```

3. **Enable Required APIs**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

4. **Configure Environment**:
   ```bash
   # .env file
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_REGION=us-central1
   ```

#### Available Models

| Model Variant | Model ID | Best For |
|--------------|----------|----------|
| `fast` | `gemini-2.0-flash-001` | Quick responses, coordination, discovery |
| `pro` | `gemini-2.0-pro-001` | Complex reasoning, analysis, QA |

#### Usage Examples

```python
from safetyculture_agent.config.model_factory import ModelFactory

factory = ModelFactory()

# Use fast model for coordination
coordinator = factory.create_model('gemini:fast')

# Use pro model for complex tasks
analyst = factory.create_model('gemini:pro')

# Use with custom parameters
custom = factory.create_model(
    'gemini:fast',
    generation_config={
        'temperature': 0.5,
        'max_output_tokens': 4096
    }
)
```

#### Troubleshooting

**Error: "Missing required environment variables: GOOGLE_CLOUD_PROJECT"**
- Ensure `.env` file exists with `GOOGLE_CLOUD_PROJECT` set
- Verify the project ID is correct

**Error: "Permission denied" or "403 Forbidden"**
- Check that Vertex AI API is enabled
- Verify your account has the required IAM roles:
  - `roles/aiplatform.user` or
  - `roles/ml.developer`

**Error: "Quota exceeded"**
- Check quota limits in [Google Cloud Console](https://console.cloud.google.com/iam-admin/quotas)
- Request quota increase if needed

---

### Llama (Vertex AI MaaS)

Access Meta's Llama models through Vertex AI Model-as-a-Service.

#### Prerequisites

- Same as Gemini (Google Cloud Project, Vertex AI enabled)
- Llama models enabled in Vertex AI Model Garden

#### Setup Steps

1. **Enable Llama in Model Garden**:
   - Navigate to [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
   - Find "Llama 3" models
   - Click "Enable" for the models you want to use

2. **Configure Environment**:
   ```bash
   # .env file
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_REGION=us-central1
   VERTEX_AI_LOCATION=us-central1  # Optional, defaults to us-central1
   ```

3. **Enable Provider in Configuration**:
   
   Create `models.local.yaml`:
   ```yaml
   providers:
     llama:
       enabled: true
   ```

#### Available Models

| Model Variant | Model ID | Best For |
|--------------|----------|----------|
| `llama3_8b` | `llama3-8b-instruct-maas` | General tasks, development |
| `llama3_70b` | `llama3-70b-instruct-maas` | Complex reasoning, production |

#### Usage Examples

```python
factory = ModelFactory()

# Use Llama for specific tasks
model = factory.create_model('llama:llama3_70b')

# Override default provider globally
import os
os.environ['MODEL_PROVIDER'] = 'llama'
model = factory.create_model()  # Now uses Llama by default
```

#### Cost Considerations

- Llama models are billed per token through Vertex AI
- 70B model is more expensive but more capable than 8B
- Check [Vertex AI pricing](https://cloud.google.com/vertex-ai/pricing) for current rates

---

### Nvidia

Access models hosted on Nvidia's infrastructure with fast inference.

#### Prerequisites

- Nvidia API key from [build.nvidia.com](https://build.nvidia.com)

#### Setup Steps

1. **Create API Key**:
   - Visit [build.nvidia.com](https://build.nvidia.com)
   - Sign up or log in
   - Navigate to API Keys
   - Generate a new key

2. **Configure Environment**:
   ```bash
   # .env file
   NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Enable Provider**:
   
   Create `models.local.yaml`:
   ```yaml
   providers:
     nvidia:
       enabled: true
   ```

#### Available Models

| Model Variant | Model ID | Best For |
|--------------|----------|----------|
| `llama3_8b` | `meta/llama3-8b-instruct` | Fast inference, development |
| `llama3_70b` | `meta/llama3-70b-instruct` | Production workloads |
| `mixtral_8x7b` | `mistralai/mixtral-8x7b-instruct` | Complex reasoning |

#### Usage Examples

```python
factory = ModelFactory()

# Use Nvidia-hosted models
model = factory.create_model('nvidia:llama3_70b')

# Try Mixtral
mixtral = factory.create_model('nvidia:mixtral_8x7b')
```

#### Rate Limits

- Free tier: Limited requests per minute
- Paid tier: Higher rate limits
- Check API dashboard for current limits

---

### Ollama (Local)

Run models locally for development with zero API costs and full privacy.

#### Prerequisites

- [Ollama](https://ollama.ai) installed locally
- Sufficient disk space (models are 4-40GB)
- Sufficient RAM (8GB minimum, 16GB+ recommended)

#### Setup Steps

1. **Install Ollama**:
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows
   # Download from https://ollama.ai/download
   ```

2. **Start Ollama Service**:
   ```bash
   ollama serve
   ```

3. **Pull Models**:
   ```bash
   # Llama 3.2 (recommended for development)
   ollama pull llama3.2
   
   # Llama 3.1 (larger, more capable)
   ollama pull llama3.1
   
   # Mistral (efficient alternative)
   ollama pull mistral
   
   # List available models
   ollama list
   ```

4. **Configure Environment** (optional):
   ```bash
   # .env file (only if using non-default URL)
   OLLAMA_BASE_URL=http://localhost:11434
   ```

5. **Enable Provider**:
   
   Create `models.local.yaml`:
   ```yaml
   providers:
     ollama:
       enabled: true
   ```

#### Available Models

| Model Variant | Model ID | Size | Best For |
|--------------|----------|------|----------|
| `llama3` | `llama3.2` | ~4GB | Quick testing |
| `llama3_1` | `llama3.1` | ~5GB | Enhanced capabilities |
| `mistral` | `mistral` | ~4GB | Efficient general tasks |

#### Usage Examples

```python
factory = ModelFactory()

# Use local model for development
model = factory.create_model('ollama:llama3')

# Use the local_dev alias
model = factory.create_model('local_dev')

# Switch all agents to local for testing
import os
os.environ['MODEL_PROVIDER'] = 'ollama'
```

#### Performance Tips

💡 **Tip**: First inference may be slow as the model loads into memory. Subsequent requests are much faster.

💡 **Tip**: Keep Ollama running in the background to avoid startup delays.

💡 **Tip**: For M1/M2 Macs, Ollama automatically uses Metal acceleration for better performance.

#### Troubleshooting

**Error: "Connection refused"**
- Ensure Ollama is running: `ollama serve`
- Check the URL matches: `echo $OLLAMA_BASE_URL`

**Error: "Model not found"**
- Pull the model: `ollama pull llama3.2`
- Verify with: `ollama list`

**Slow Performance**
- Close other applications to free RAM
- Consider using a smaller model
- On laptops, ensure you're plugged in (power saving may throttle CPU)

---

## Model Aliases

Aliases provide semantic names for common use cases, making code more maintainable.

### Pre-configured Aliases

Defined in [`models.yaml`](safetyculture_agent/config/models.yaml:11):

| Alias | Maps To | Purpose |
|-------|---------|---------|
| `coordinator` | `gemini/fast` | Agent coordination and orchestration |
| `discovery` | `gemini/fast` | Asset discovery tasks |
| `template_selection` | `gemini/pro` | Template matching |
| `data_extraction` | `gemini/pro` | Data extraction from forms |
| `analysis` | `gemini/pro` | Quality assurance and analysis |
| `local_dev` | `ollama/llama3` | Local development and testing |

### Using Aliases

```python
factory = ModelFactory()

# Use pre-defined aliases
coordinator = factory.create_model('coordinator')
qa_agent = factory.create_model('analysis')
dev_model = factory.create_model('local_dev')

# Aliases work with agents
from google.adk.agents.llm_agent import LlmAgent

agent = LlmAgent(
    name="Coordinator",
    model=factory.create_model('coordinator'),
    instruction="..."
)
```

### Creating Custom Aliases

Add custom aliases in `models.local.yaml`:

```yaml
# models.local.yaml
model_aliases:
  # Add your custom aliases
  fast_local: ollama/mistral
  production: gemini/pro
  cost_effective: llama/llama3_8b
  
  # Override existing aliases
  coordinator: nvidia/llama3_70b
```

### When to Use Aliases

✅ **DO use aliases when**:
- Building reusable agents
- You might switch providers later
- Working in teams (semantic names are clearer)
- You want environment-specific models (dev vs prod)

❌ **DON'T use aliases when**:
- Quick prototyping or experiments
- Model choice is critical to functionality
- One-off scripts

---

## Advanced Configuration

### Local Configuration Overrides

Create `models.local.yaml` in the config directory to override defaults without modifying the base configuration:

```yaml
# safetyculture_agent/config/models.local.yaml

# Override default provider
default_provider: ollama

# Enable additional providers
providers:
  llama:
    enabled: true
  nvidia:
    enabled: true
  ollama:
    enabled: true

# Add custom model variants
providers:
  gemini:
    models:
      experimental:
        model_id: gemini-2.0-ultra-001
        display_name: Gemini 2.0 Ultra
        temperature: 0.3
        max_output_tokens: 16384

# Override model configurations
providers:
  gemini:
    models:
      fast:
        temperature: 0.5  # Lower temperature for consistency

# Add custom aliases
model_aliases:
  ultra: gemini/experimental
  cheap: ollama/mistral
```

💡 **Tip**: `models.local.yaml` is automatically gitignored, making it perfect for personal preferences and local testing.

### Runtime Parameter Overrides

Override any model parameter at instantiation:

```python
factory = ModelFactory()

# Override generation parameters
model = factory.create_model(
    'coordinator',
    generation_config={
        'temperature': 0.3,        # More deterministic
        'max_output_tokens': 4096, # Shorter responses
        'top_p': 0.9,
        'top_k': 40
    }
)

# Override retry behavior (Gemini only)
from google.genai import types

model = factory.create_model(
    'gemini:fast',
    http_options=types.HttpOptions(
        retry=types.HttpRetryOptions(
            max_retries=5,
            initial_delay=2.0,
            max_delay=120.0
        )
    )
)
```

### Switching Default Providers

Multiple ways to change the default provider:

**Method 1: Environment Variable** (Temporary)
```bash
# In terminal
export MODEL_PROVIDER=ollama
python your_script.py
```

**Method 2: .env File** (Per-project)
```bash
# .env
MODEL_PROVIDER=ollama
```

**Method 3: Local Configuration** (Persistent)
```yaml
# models.local.yaml
default_provider: ollama
```

**Method 4: Runtime** (Programmatic)
```python
import os
os.environ['MODEL_PROVIDER'] = 'ollama'

factory = ModelFactory()
model = factory.create_model()  # Uses Ollama
```

### Model-Specific Parameters

Each provider and model has specific tuning parameters:

#### Temperature

Controls randomness in responses:
- `0.0` - Deterministic, consistent
- `0.5` - Balanced (good default for most tasks)
- `1.0` - Creative, varied
- `2.0` - Very random (rarely useful)

```python
# Deterministic for data extraction
extractor = factory.create_model(
    'data_extraction',
    generation_config={'temperature': 0.2}
)

# Creative for content generation
writer = factory.create_model(
    'coordinator',
    generation_config={'temperature': 0.9}
)
```

#### Max Output Tokens

Limits response length:

```python
# Short responses for efficiency
quick = factory.create_model(
    'coordinator',
    generation_config={'max_output_tokens': 1024}
)

# Long-form responses
detailed = factory.create_model(
    'analysis',
    generation_config={'max_output_tokens': 8192}
)
```

#### Top-p (Nucleus Sampling)

Controls diversity of token selection:
- `0.9` - More focused (default)
- `0.95` - Balanced
- `1.0` - Full vocabulary

#### Top-k

Limits token choices to top k options:
- Lower = more focused
- Higher = more diverse
- `40` is a good default

### Environment-Specific Configurations

Set up different configurations for different environments:

```yaml
# models.local.yaml (development)
default_provider: ollama
providers:
  ollama:
    enabled: true
```

```yaml
# models.production.yaml (load via MODEL_CONFIG_PATH env var)
default_provider: gemini
providers:
  gemini:
    models:
      fast:
        retry:
          max_retries: 5
          initial_delay: 2.0
```

```bash
# Load production config
export MODEL_CONFIG_PATH=./config/models.production.yaml
```

### Validation and Debugging

Enable validation to catch configuration errors early:

```python
from safetyculture_agent.config.model_loader import ModelConfigLoader

# Load configuration explicitly to validate
loader = ModelConfigLoader()
try:
    config = loader.load()
    print(f"✓ Configuration loaded successfully")
    print(f"  Default provider: {config.default_provider}")
    print(f"  Available providers: {list(config.providers.keys())}")
    print(f"  Aliases: {list(config.model_aliases.keys())}")
except ValueError as e:
    print(f"✗ Configuration error: {e}")
```

---

## Migration Guide

### From Hardcoded Models

**Before** - Direct model strings:

```python
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models import Gemini

# Hardcoded model
coordinator_agent = LlmAgent(
    name="SafetyCultureCoordinator",
    model=Gemini(model="gemini-2.0-flash-001"),
    instruction="You are a coordinator..."
)

qa_agent = LlmAgent(
    name="QualityAssurance",
    model=Gemini(model="gemini-2.0-pro-001"),
    instruction="You are a QA agent..."
)
```

**After** - Configurable models:

```python
from google.adk.agents.llm_agent import LlmAgent
from safetyculture_agent.config.model_factory import ModelFactory

# Initialize factory once at module level
model_factory = ModelFactory()

# Use aliases for semantic clarity
coordinator_agent = LlmAgent(
    name="SafetyCultureCoordinator",
    model=model_factory.create_model('coordinator'),
    instruction="You are a coordinator..."
)

qa_agent = LlmAgent(
    name="QualityAssurance",
    model=model_factory.create_model('qa'),
    instruction="You are a QA agent..."
)
```

### Benefits of Migration

✅ **Flexibility**: Switch providers without code changes  
✅ **Testability**: Use local models for development  
✅ **Maintainability**: Centralized configuration  
✅ **Environment-aware**: Different models for dev/staging/prod  
✅ **Cost control**: Easy to switch to cheaper alternatives  

### Migration Checklist

- [ ] Copy `.env.example` to `.env`
- [ ] Set required environment variables
- [ ] Import [`ModelFactory`](safetyculture_agent/config/model_factory.py)
- [ ] Replace hardcoded model strings with `factory.create_model()`
- [ ] Use aliases where appropriate
- [ ] Test with default provider
- [ ] (Optional) Create `models.local.yaml` for customization
- [ ] Update documentation to reference aliases

### Backwards Compatibility

The configuration system is fully compatible with existing ADK code. You can migrate incrementally:

```python
# Mix old and new approaches
from google.adk.models import Gemini
from safetyculture_agent.config.model_factory import ModelFactory

factory = ModelFactory()

# New: Use factory
modern_agent = LlmAgent(
    name="Modern",
    model=factory.create_model('coordinator')
)

# Old: Direct instantiation still works
legacy_agent = LlmAgent(
    name="Legacy",
    model=Gemini(model="gemini-2.0-flash-001")
)
```

---

## Troubleshooting

### Common Issues

#### Configuration Not Loading

**Symptom**: Default models not working, configuration seems ignored

**Solutions**:
1. Verify file exists: `ls safetyculture_agent/config/models.yaml`
2. Check YAML syntax: `python -c "import yaml; yaml.safe_load(open('safetyculture_agent/config/models.yaml'))"`
3. Ensure you're in the correct directory
4. Try explicit loading:
   ```python
   from pathlib import Path
   from safetyculture_agent.config.model_loader import ModelConfigLoader
   
   loader = ModelConfigLoader(config_path=Path('./safetyculture_agent/config/models.yaml'))
   config = loader.load()
   ```

#### Missing Environment Variables

**Symptom**: `ValueError: Missing required environment variables`

**Solutions**:
1. Check `.env` file exists: `ls -la .env`
2. Verify variables are set:
   ```bash
   # Check specific variables
   echo $GOOGLE_CLOUD_PROJECT
   echo $NVIDIA_API_KEY
   ```
3. Load .env in your script:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```
4. Check variable names match exactly (case-sensitive)

#### Provider Not Found

**Symptom**: `ValueError: Unknown provider: xyz`

**Solutions**:
1. Check provider is defined in `models.yaml`
2. Verify provider is enabled:
   ```yaml
   providers:
     llama:
       enabled: true  # Must be true
   ```
3. Check spelling (case-sensitive)
4. List available providers:
   ```python
   loader = ModelConfigLoader()
   config = loader.load()
   print(config.providers.keys())
   ```

#### Model Not Found

**Symptom**: `ValueError: Model 'xyz' not found in provider`

**Solutions**:
1. List available models for provider:
   ```python
   loader = ModelConfigLoader()
   config = loader.load()
   provider = loader.get_provider('gemini')
   print(provider.models.keys())
   ```
2. Check spelling matches configuration
3. Verify model is defined under correct provider

#### API Authentication Errors

**Gemini/Llama**:
```bash
# Verify credentials
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

# Check active account
gcloud auth list
```

**Nvidia**:
```bash
# Verify API key is set
echo $NVIDIA_API_KEY

# Test API key
curl -H "Authorization: Bearer $NVIDIA_API_KEY" \
     https://integrate.api.nvidia.com/v1/models
```

**Ollama**:
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Start if not running
ollama serve
```

#### Alias Resolution Errors

**Symptom**: `ValueError: Unknown alias or invalid format`

**Solutions**:
1. Check alias is defined in configuration:
   ```python
   loader = ModelConfigLoader()
   config = loader.load()
   print(config.model_aliases)
   ```
2. Use correct format: `'alias'`, `'provider:model'`, or `'provider/model'`
3. Verify spelling matches configuration exactly

### Debug Mode

Enable detailed logging to diagnose issues:

```python
import logging
import os

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Enable LiteLLM logging for non-Gemini providers
os.environ['LITELLM_LOG'] = 'DEBUG'

# Now create models - you'll see detailed output
factory = ModelFactory()
model = factory.create_model('coordinator')
```

### Verification Script

Run this script to verify your configuration:

```python
#!/usr/bin/env python3
"""Verify model configuration setup."""

import os
from pathlib import Path
from safetyculture_agent.config.model_loader import ModelConfigLoader
from safetyculture_agent.config.model_factory import ModelFactory

def verify_setup():
    print("🔍 Verifying Model Configuration Setup\n")
    
    # Check files exist
    print("1. Checking configuration files...")
    config_path = Path('safetyculture_agent/config/models.yaml')
    if config_path.exists():
        print(f"   ✓ {config_path} found")
    else:
        print(f"   ✗ {config_path} NOT FOUND")
        return False
    
    env_path = Path('.env')
    if env_path.exists():
        print(f"   ✓ {env_path} found")
    else:
        print(f"   ⚠ {env_path} not found (optional)")
    
    # Load configuration
    print("\n2. Loading configuration...")
    try:
        loader = ModelConfigLoader()
        config = loader.load()
        print(f"   ✓ Configuration loaded")
        print(f"   Default provider: {config.default_provider}")
    except Exception as e:
        print(f"   ✗ Failed to load configuration: {e}")
        return False
    
    # Check providers
    print("\n3. Checking providers...")
    for name, provider in config.providers.items():
        status = "enabled" if provider.enabled else "disabled"
        print(f"   {name}: {status}")
        if provider.enabled:
            # Check environment variables
            missing = []
            for var_name, var_value in provider.environment_vars.items():
                if var_value == 'required' and not os.getenv(var_name):
                    missing.append(var_name)
            if missing:
                print(f"      ⚠ Missing env vars: {', '.join(missing)}")
    
    # Check aliases
    print("\n4. Checking aliases...")
    for alias, target in config.model_aliases.items():
        print(f"   {alias} -> {target}")
    
    # Test model creation
    print("\n5. Testing model creation...")
    try:
        factory = ModelFactory()
        model = factory.create_model()
        print(f"   ✓ Default model created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create model: {e}")
        return False
    
    print("\n✅ Configuration verified successfully!")
    return True

if __name__ == '__main__':
    verify_setup()
```

### Getting Help

If you're still experiencing issues:

1. **Check the Design Document**: See [`MODEL_PROVIDER_CONFIGURATION_DESIGN.md`](MODEL_PROVIDER_CONFIGURATION_DESIGN.md) for architectural details

2. **Review Examples**: Look at the sample code in this guide

3. **Enable Debug Logging**: Use the debug mode above to get detailed output

4. **Check Provider Status**: 
   - Gemini: [Cloud Console](https://console.cloud.google.com)
   - Nvidia: [Build Dashboard](https://build.nvidia.com)
   - Ollama: `ollama list` and `ollama serve`

5. **Verify Network**: Ensure you can reach provider APIs
   ```bash
   # Test Gemini connectivity
   curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        "https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT/locations/us-central1/publishers/google/models"
   ```

---

## Additional Resources

- **Architecture Details**: [`MODEL_PROVIDER_CONFIGURATION_DESIGN.md`](MODEL_PROVIDER_CONFIGURATION_DESIGN.md)
- **Configuration Schema**: [`models.yaml`](safetyculture_agent/config/models.yaml)
- **Implementation**: 
  - [`model_config.py`](safetyculture_agent/config/model_config.py)
  - [`model_loader.py`](safetyculture_agent/config/model_loader.py)
  - [`model_factory.py`](safetyculture_agent/config/model_factory.py)
- **ADK Documentation**: [github.com/google/adk-python](https://github.com/google/adk-python)
- **Provider Documentation**:
  - [Vertex AI](https://cloud.google.com/vertex-ai/docs)
  - [Nvidia NIM](https://docs.nvidia.com/nim/)
  - [Ollama](https://github.com/ollama/ollama)

---

**Last Updated**: 2025-01-30  
**Version**: 1.0.0