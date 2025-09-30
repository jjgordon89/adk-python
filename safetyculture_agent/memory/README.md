# SafetyCulture Agent Memory Integration

This directory contains memory tools that integrate with ADK's MemoryService to provide persistent storage for SafetyCulture-specific data.

## Overview

The memory tools enable persistent storage and retrieval of:
- **Asset Registry**: Cached asset information to avoid repeated API calls
- **Template Library**: Frequently used template data for quick access
- **Workflow State**: Multi-step workflow progress tracking
- **Inspection History**: Historical inspection data for learning and optimization

## ADK Memory Integration Pattern

These tools follow ADK's memory pattern by:

1. **Using ToolContext**: All memory operations require `ToolContext` which provides access to the ADK memory service via `tool_context.search_memory()`

2. **Creating MemoryEntry Objects**: Data is stored as `MemoryEntry` instances with structured text content that can be semantically searched

3. **Semantic Search**: Retrieval uses ADK's built-in semantic search rather than key-value lookups, enabling more flexible data access

4. **Session-Based Storage**: Memory is tied to the user's session and persists across agent invocations

## Tools

### store_asset_registry
```python
async def store_asset_registry(
    assets: List[Dict[str, Any]],
    registry_key: str = "asset_registry",
    tool_context: Optional[ToolContext] = None
) -> str
```

**Purpose**: Store SafetyCulture asset data in memory for later retrieval.

**Usage Example**:
```python
assets = [
    {"id": "asset_123", "name": "Building A", "asset_type": "building"},
    {"id": "asset_456", "name": "HVAC Unit 1", "asset_type": "equipment"}
]
result = await store_asset_registry(
    assets=assets,
    registry_key="site_sydney_assets",
    tool_context=tool_context
)
```

**When to Use**:
- After discovering assets via SafetyCulture API
- Before starting inspection workflows that reference assets
- When caching frequently accessed asset lists

### retrieve_asset_registry
```python
async def retrieve_asset_registry(
    registry_key: str = "asset_registry",
    asset_type_filter: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> str
```

**Purpose**: Retrieve previously stored asset data using semantic search.

**Usage Example**:
```python
result = await retrieve_asset_registry(
    registry_key="site_sydney_assets",
    asset_type_filter="equipment",
    tool_context=tool_context
)
# Returns JSON with matching assets
```

### store_template_library
```python
async def store_template_library(
    templates: List[Dict[str, Any]],
    library_key: str = "template_library",
    tool_context: Optional[ToolContext] = None
) -> str
```

**Purpose**: Cache SafetyCulture template metadata to reduce API calls.

**Usage Example**:
```python
templates = [
    {
        "template_id": "template_abc",
        "name": "Fire Safety Inspection",
        "categories": ["safety", "fire"]
    }
]
result = await store_template_library(
    templates=templates,
    library_key="safety_templates",
    tool_context=tool_context
)
```

### retrieve_template_library
```python
async def retrieve_template_library(
    library_key: str = "template_library",
    name_filter: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> str
```

**Purpose**: Search for previously cached templates.

**Usage Example**:
```python
result = await retrieve_template_library(
    library_key="safety_templates",
    name_filter="Fire Safety",
    tool_context=tool_context
)
```

### store_workflow_state
```python
async def store_workflow_state(
    workflow_data: Dict[str, Any],
    state_key: str = "workflow_state",
    tool_context: Optional[ToolContext] = None
) -> str
```

**Purpose**: Persist workflow progress for multi-step operations.

**Usage Example**:
```python
workflow_data = {
    "current_step": "form_filling",
    "completed_steps": ["asset_discovery", "template_selection"],
    "inspection_id": "insp_789",
    "context": {
        "selected_asset": "asset_123",
        "selected_template": "template_abc"
    }
}
result = await store_workflow_state(
    workflow_data=workflow_data,
    state_key="inspection_workflow_user123",
    tool_context=tool_context
)
```

### retrieve_workflow_state
```python
async def retrieve_workflow_state(
    state_key: str = "workflow_state",
    tool_context: Optional[ToolContext] = None
) -> str
```

**Purpose**: Resume or inspect workflow progress.

### store_inspection_history
```python
async def store_inspection_history(
    inspections: List[Dict[str, Any]],
    history_key: str = "inspection_history",
    tool_context: Optional[ToolContext] = None
) -> str
```

**Purpose**: Archive completed inspections for pattern analysis.

**Usage Example**:
```python
inspections = [
    {
        "inspection_id": "insp_789",
        "template_id": "template_abc",
        "completion_date": "2025-01-15T10:30:00Z",
        "findings": [...]
    }
]
result = await store_inspection_history(
    inspections=inspections,
    history_key="monthly_inspections_jan",
    tool_context=tool_context
)
```

## Integration with Agents

### Adding Memory Tools to an Agent

```python
from google.adk.agents.llm_agent import LlmAgent
from safetyculture_agent.memory.memory_tools import MEMORY_TOOLS

agent = LlmAgent(
    name="asset_discovery_agent",
    tools=MEMORY_TOOLS + other_tools,
    # ... other config
)
```

### Configuring Memory Service

The MemoryService must be configured at the runner level:

```python
from google.adk.runners import Runner
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService

runner = Runner(
    agent=my_agent,
    memory_service=InMemoryMemoryService()  # or VertexAIMemoryBankService
)
```

## Memory Service Options

### InMemoryMemoryService
- **Use Case**: Development, testing, single-session scenarios
- **Persistence**: In-process only, lost on restart
- **Performance**: Fast, no external dependencies

### VertexAIMemoryBankService
- **Use Case**: Production deployments, multi-user applications
- **Persistence**: Cloud-based, survives restarts
- **Performance**: Requires GCP setup, supports vector search
- **Configuration**: Requires Vertex AI Memory Bank setup

## Migration Considerations

### From Placeholder Implementation

The previous placeholder implementation did not actually persist data. When migrating:

1. **No Data to Migrate**: Since placeholders didn't store data, there's no migration needed
2. **Update Agent Initialization**: Ensure `memory_service` is configured on the runner
3. **Test Memory Operations**: Verify store/retrieve operations work in your environment

### Memory Service Initialization Example

```python
from google.adk.runners import Runner
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from safetyculture_agent.agent import create_safetyculture_agent

agent = create_safetyculture_agent()
runner = Runner(
    agent=agent,
    memory_service=InMemoryMemoryService()
)

# Now memory tools will work properly
result = await runner.run(
    user_id="user123",
    session_id="session456",
    message="Store the asset registry"
)
```

## Error Handling

All memory tools include comprehensive error handling:

- **ValueError**: Raised when memory service is not configured
- **Empty Data**: Returns error message for empty input lists
- **Missing Context**: Returns JSON error response when ToolContext unavailable
- **Search Failures**: Returns helpful hints for debugging

Example error response:
```json
{
  "error": "Tool context not available",
  "registry_key": "asset_registry",
  "hint": "Ensure memory_service is configured on the runner"
}
```

## Best Practices

1. **Use Descriptive Keys**: Include context in registry/library keys (e.g., "site_sydney_assets" vs "assets")

2. **Regular Updates**: Update workflow state after each major step to enable resumption

3. **Batch Storage**: Store multiple assets/templates together rather than individually

4. **Filter on Retrieval**: Use filters to narrow search results and improve relevance

5. **Error Checking**: Always check for error messages in tool responses

6. **Memory Service Selection**:
   - Development: Use `InMemoryMemoryService`
   - Production: Use `VertexAIMemoryBankService` for persistence

## Testing

To test memory tools:

```python
import pytest
from google.adk.tools.tool_context import ToolContext
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from safetyculture_agent.memory.memory_tools import (
    store_asset_registry,
    retrieve_asset_registry
)

@pytest.mark.asyncio
async def test_asset_storage():
    # Setup
    memory_service = InMemoryMemoryService()
    tool_context = create_mock_tool_context(memory_service)
    
    # Store
    assets = [{"id": "test_123", "name": "Test Asset"}]
    store_result = await store_asset_registry(
        assets=assets,
        tool_context=tool_context
    )
    assert "Successfully stored" in store_result
    
    # Retrieve
    retrieve_result = await retrieve_asset_registry(
        tool_context=tool_context
    )
    assert "test_123" in retrieve_result
```

## Troubleshooting

### "Tool context not available"
- Ensure tools are called with `tool_context` parameter
- Verify agent is using FunctionTool instances correctly

### "Memory service is not available"
- Check that `memory_service` is configured on the Runner
- Verify the service is properly initialized

### "No memories found"
- Data must be stored before retrieval
- Check that registry/library keys match between store and retrieve
- Semantic search may not find exact matches - try broader queries

## Related Documentation

- [ADK Memory Documentation](../../src/google/adk/memory/)
- [ADK Tools Documentation](../../src/google/adk/tools/)
- [SafetyCulture Agent Architecture](../README.md)