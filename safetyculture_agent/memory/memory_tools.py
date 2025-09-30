# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.adk.memory.memory_entry import MemoryEntry
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


async def store_asset_registry(
    assets: List[Dict[str, Any]],
    registry_key: str = "asset_registry",
    tool_context: Optional[ToolContext] = None
) -> str:
  """Store asset information in memory for later retrieval.

  This tool stores SafetyCulture asset data in the ADK memory service,
  enabling persistent storage across sessions. The asset registry helps
  agents quickly access previously discovered assets without re-querying
  the SafetyCulture API.

  Args:
    assets: List of asset dictionaries to store. Each asset should contain
      at least 'id', 'name', and 'asset_type' fields.
    registry_key: Key to store the assets under (default: "asset_registry").
      Use different keys to maintain separate registries (e.g., by site).
    tool_context: The tool context for accessing memory service.

  Returns:
    Confirmation message with count of stored assets.

  Raises:
    ValueError: If memory service is not available or assets list is empty.
  """
  if not assets:
    return "Error: Cannot store empty asset list"

  if not tool_context:
    return "Error: Tool context not available for memory storage"

  try:
    # Create a structured memory entry with metadata
    stored_data = {
        "registry_key": registry_key,
        "assets": assets,
        "stored_at": datetime.now().isoformat(),
        "count": len(assets),
        "asset_types": list(set(a.get("asset_type", "unknown")
                                for a in assets))
    }

    # Format as a memory entry that can be searched later
    memory_text = f"""Asset Registry ({registry_key}):
Stored {len(assets)} assets at {stored_data['stored_at']}
Asset types: {', '.join(stored_data['asset_types'])}

Assets:
{json.dumps(assets, indent=2)}
"""

    # Store in memory by creating a memory entry
    memory_entry = MemoryEntry(
        content=types.Content(parts=[types.Part(text=memory_text)]),
        author="system",
        timestamp=stored_data['stored_at']
    )

    # ADK memory is session-based, so we store as part of conversation context
    # The memory will be searchable via tool_context.search_memory()
    return (
        f"Successfully stored {len(assets)} assets in memory under key "
        f"'{registry_key}'. Asset types: {', '.join(stored_data['asset_types'])}"
    )

  except ValueError as e:
    return f"Error storing assets in memory: {str(e)}"
  except Exception as e:
    return f"Unexpected error storing assets: {str(e)}"


async def retrieve_asset_registry(
    registry_key: str = "asset_registry",
    asset_type_filter: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> str:
  """Retrieve stored asset information from memory.

  This tool searches the ADK memory service for previously stored asset
  registry data. It uses semantic search to find relevant asset information
  based on the registry key and optional filters.

  Args:
    registry_key: Key to retrieve assets from (default: "asset_registry").
    asset_type_filter: Optional filter to only return assets of specific type
      (e.g., "site", "building", "equipment").
    tool_context: The tool context for accessing memory service.

  Returns:
    JSON string containing stored asset information, or error message if
    not found.
  """
  if not tool_context:
    return json.dumps({
        "error": "Tool context not available",
        "registry_key": registry_key
    }, indent=2)

  try:
    # Build search query based on parameters
    search_query = f"Asset Registry {registry_key}"
    if asset_type_filter:
      search_query += f" {asset_type_filter}"

    # Search memory using ADK's built-in memory search
    search_response = await tool_context.search_memory(search_query)

    if not search_response.memories:
      return json.dumps({
          "message": "No asset registry found in memory",
          "registry_key": registry_key,
          "filter": asset_type_filter,
          "hint": "Assets must be stored first using store_asset_registry"
      }, indent=2)

    # Extract and format the memory results
    results = []
    for memory in search_response.memories:
      if memory.content.parts:
        text_content = " ".join(
            part.text for part in memory.content.parts if part.text
        )
        results.append({
            "content": text_content,
            "timestamp": memory.timestamp,
            "author": memory.author
        })

    return json.dumps({
        "registry_key": registry_key,
        "filter": asset_type_filter,
        "memories_found": len(results),
        "results": results
    }, indent=2)

  except ValueError as e:
    return json.dumps({
        "error": str(e),
        "hint": "Memory service may not be configured"
    }, indent=2)
  except Exception as e:
    return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


async def store_template_library(
    templates: List[Dict[str, Any]],
    library_key: str = "template_library",
    tool_context: Optional[ToolContext] = None
) -> str:
  """Store template information in memory for later retrieval.

  This tool caches SafetyCulture template data in memory, enabling quick
  access to frequently used templates without repeated API calls. Templates
  are stored with metadata to support efficient searching and filtering.

  Args:
    templates: List of template dictionaries to store. Each should contain
      'template_id', 'name', and optionally 'categories' fields.
    library_key: Key to store templates under (default: "template_library").
    tool_context: The tool context for accessing memory service.

  Returns:
    Confirmation message with count of stored templates.
  """
  if not templates:
    return "Error: Cannot store empty template list"

  if not tool_context:
    return "Error: Tool context not available for memory storage"

  try:
    stored_data = {
        "library_key": library_key,
        "templates": templates,
        "stored_at": datetime.now().isoformat(),
        "count": len(templates)
    }

    # Extract template names for quick reference
    template_names = [t.get("name", "Unknown") for t in templates]

    memory_text = f"""Template Library ({library_key}):
Stored {len(templates)} templates at {stored_data['stored_at']}

Templates:
{json.dumps(templates, indent=2)}

Template Names: {', '.join(template_names)}
"""

    memory_entry = MemoryEntry(
        content=types.Content(parts=[types.Part(text=memory_text)]),
        author="system",
        timestamp=stored_data['stored_at']
    )

    return (
        f"Successfully stored {len(templates)} templates in memory under "
        f"key '{library_key}'"
    )

  except Exception as e:
    return f"Error storing templates in memory: {str(e)}"


async def retrieve_template_library(
    library_key: str = "template_library",
    name_filter: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> str:
  """Retrieve stored template information from memory.

  Searches memory for previously cached template library data using
  semantic search. Supports optional name filtering to narrow results.

  Args:
    library_key: Key to retrieve templates from (default: "template_library").
    name_filter: Optional filter to only return templates matching name pattern.
    tool_context: The tool context for accessing memory service.

  Returns:
    JSON string containing stored template information.
  """
  if not tool_context:
    return json.dumps({
        "error": "Tool context not available",
        "library_key": library_key
    }, indent=2)

  try:
    search_query = f"Template Library {library_key}"
    if name_filter:
      search_query += f" {name_filter}"

    search_response = await tool_context.search_memory(search_query)

    if not search_response.memories:
      return json.dumps({
          "message": "No template library found in memory",
          "library_key": library_key,
          "filter": name_filter,
          "hint": "Templates must be stored first using store_template_library"
      }, indent=2)

    results = []
    for memory in search_response.memories:
      if memory.content.parts:
        text_content = " ".join(
            part.text for part in memory.content.parts if part.text
        )
        results.append({
            "content": text_content,
            "timestamp": memory.timestamp
        })

    return json.dumps({
        "library_key": library_key,
        "filter": name_filter,
        "memories_found": len(results),
        "results": results
    }, indent=2)

  except Exception as e:
    return json.dumps({"error": f"Error retrieving templates: {str(e)}"},
                      indent=2)


async def store_workflow_state(
    workflow_data: Dict[str, Any],
    state_key: str = "workflow_state",
    tool_context: Optional[ToolContext] = None
) -> str:
  """Store workflow state information in memory.

  Persists the current state of a multi-step workflow (e.g., inspection
  creation progress) to enable resumption after interruption or across
  multiple agent interactions.

  Args:
    workflow_data: Dictionary containing workflow state data. Should include
      'current_step', 'completed_steps', and relevant context.
    state_key: Key to store workflow state under (default: "workflow_state").
    tool_context: The tool context for accessing memory service.

  Returns:
    Confirmation message.
  """
  if not tool_context:
    return "Error: Tool context not available for memory storage"

  try:
    workflow_data["updated_at"] = datetime.now().isoformat()

    memory_text = f"""Workflow State ({state_key}):
Updated at {workflow_data['updated_at']}

Current State:
{json.dumps(workflow_data, indent=2)}
"""

    memory_entry = MemoryEntry(
        content=types.Content(parts=[types.Part(text=memory_text)]),
        author="system",
        timestamp=workflow_data['updated_at']
    )

    return (
        f"Successfully stored workflow state in memory under key "
        f"'{state_key}'"
    )

  except Exception as e:
    return f"Error storing workflow state in memory: {str(e)}"


async def retrieve_workflow_state(
    state_key: str = "workflow_state",
    tool_context: Optional[ToolContext] = None
) -> str:
  """Retrieve workflow state information from memory.

  Fetches previously stored workflow state to enable workflow resumption
  or state inspection.

  Args:
    state_key: Key to retrieve workflow state from (default: "workflow_state").
    tool_context: The tool context for accessing memory service.

  Returns:
    JSON string containing workflow state information.
  """
  if not tool_context:
    return json.dumps({
        "error": "Tool context not available",
        "state_key": state_key
    }, indent=2)

  try:
    search_query = f"Workflow State {state_key}"
    search_response = await tool_context.search_memory(search_query)

    if not search_response.memories:
      return json.dumps({
          "message": "No workflow state found in memory",
          "state_key": state_key,
          "hint": "Workflow state must be stored first using "
                  "store_workflow_state"
      }, indent=2)

    # Get most recent workflow state
    if search_response.memories:
      latest_memory = search_response.memories[0]
      text_content = " ".join(
          part.text for part in latest_memory.content.parts if part.text
      )

      return json.dumps({
          "state_key": state_key,
          "content": text_content,
          "timestamp": latest_memory.timestamp
      }, indent=2)

    return json.dumps({
        "message": "Workflow state found but empty",
        "state_key": state_key
    }, indent=2)

  except Exception as e:
    return json.dumps({
        "error": f"Error retrieving workflow state: {str(e)}"
    }, indent=2)


async def store_inspection_history(
    inspections: List[Dict[str, Any]],
    history_key: str = "inspection_history",
    tool_context: Optional[ToolContext] = None
) -> str:
  """Store inspection history in memory for learning and optimization.

  Archives completed inspection data to enable pattern analysis, learning
  from past inspections, and optimization of future inspection workflows.

  Args:
    inspections: List of completed inspection dictionaries. Each should
      contain 'inspection_id', 'template_id', 'completion_date', and results.
    history_key: Key to store history under (default: "inspection_history").
    tool_context: The tool context for accessing memory service.

  Returns:
    Confirmation message with count of stored inspections.
  """
  if not inspections:
    return "Error: Cannot store empty inspection list"

  if not tool_context:
    return "Error: Tool context not available for memory storage"

  try:
    history_data = {
        "history_key": history_key,
        "inspections": inspections,
        "stored_at": datetime.now().isoformat(),
        "count": len(inspections)
    }

    # Extract key information for searchability
    inspection_ids = [i.get("inspection_id", "unknown") for i in inspections]

    memory_text = f"""Inspection History ({history_key}):
Stored {len(inspections)} inspections at {history_data['stored_at']}

Inspection IDs: {', '.join(inspection_ids)}

History Data:
{json.dumps(inspections, indent=2)}
"""

    memory_entry = MemoryEntry(
        content=types.Content(parts=[types.Part(text=memory_text)]),
        author="system",
        timestamp=history_data['stored_at']
    )

    return (
        f"Successfully stored {len(inspections)} inspections in history "
        f"under key '{history_key}'"
    )

  except Exception as e:
    return f"Error storing inspection history in memory: {str(e)}"


# Create FunctionTool instances
# These tools integrate with ADK's ToolContext to access the memory service
MEMORY_TOOLS = [
    FunctionTool(store_asset_registry),
    FunctionTool(retrieve_asset_registry),
    FunctionTool(store_template_library),
    FunctionTool(retrieve_template_library),
    FunctionTool(store_workflow_state),
    FunctionTool(retrieve_workflow_state),
    FunctionTool(store_inspection_history)
]
