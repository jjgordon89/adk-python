# SafetyCulture Agent - Tools Documentation

## Overview

The SafetyCulture Agent is a sophisticated multi-agent system built on ADK v1.15.1 that automates inspection workflows through a comprehensive toolkit of 32+ specialized tools. These tools are organized into four categories to support the complete inspection lifecycle from asset discovery through quality assurance.

**Architecture**: 6 sub-agents coordinated by the SafetyCultureCoordinator agent
**Test Coverage**: 87.0% (134/154 tests passing)
**Tool Categories**: 4 (SafetyCulture API, Memory, AI, Database)

---

## Tool Categories

### 1. SafetyCulture API Tools (9 tools)
Direct integration with SafetyCulture platform for CRUD operations on assets, templates, and inspections.

### 2. Memory Tools (7 tools)
Persistent storage using ADK's memory service for caching and workflow state management.

### 3. AI Tools (6 tools)
Intelligent automation powered by Gemini for template matching, image analysis, and data generation.

### 4. Database Tools (10 tools)
SQLite-based tracking system for preventing duplicate inspections and generating reports.

---

## 1. SafetyCulture API Tools

### Overview
These tools interact directly with the SafetyCulture REST API, providing async operations with built-in rate limiting, circuit breakers, and request signing for security. All tools leverage the [`SafetyCultureAPIClient`](safetyculture_agent/tools/safetyculture_api_client.py:79) class.

**Implementation**: [`safetyculture_tools.py`](safetyculture_agent/tools/safetyculture_tools.py:1)

---

#### 1.1 `search_safetyculture_assets`

Search for assets in SafetyCulture with flexible filtering options.

**Purpose**: Discover assets across the SafetyCulture organization by type, location, or site.

**Parameters**:
- `asset_types` (Optional[List[str]]): List of asset type names (e.g., ['Car', 'Equipment'])
- `site_names` (Optional[List[str]]): List of site names to filter by
- `limit` (int): Maximum results to return (default: 50, max: 100)

**Returns**: JSON string containing asset information including IDs, types, and metadata

**Usage Example**:
```python
from safetyculture_agent.tools.safetyculture_tools import search_safetyculture_assets

# Search for vehicles at specific sites
result = await search_safetyculture_assets(
    asset_types=["Vehicle", "Car"],
    site_names=["Main Facility", "Warehouse B"],
    limit=25
)
```

**Used By**: AssetDiscoveryAgent, SafetyCultureCoordinator, QualityAssuranceAgent

**Error Handling**:
- Sanitizes authentication errors to prevent credential leakage
- Validates input parameters before API calls
- Implements exponential backoff for rate limiting

**Related Tools**: [`get_safetyculture_asset_details()`](#12-get_safetyculture_asset_details), [`filter_assets_to_prevent_duplicates()`](#410-filter_assets_to_prevent_duplicates)

---

#### 1.2 `get_safetyculture_asset_details`

Retrieve detailed information about a specific asset.

**Purpose**: Fetch complete asset metadata including custom fields, location data, and relationships.

**Parameters**:
- `asset_id` (str): The unique ID of the asset (validated UUID format)

**Returns**: JSON string containing detailed asset information

**Usage Example**:
```python
# Get full details for an asset
asset_details = await get_safetyculture_asset_details(
    asset_id="asset_abc123def456"
)
# Returns: {"id": "asset_abc123def456", "name": "Forklift-42", ...}
```

**Used By**: AssetDiscoveryAgent, InspectionCreationAgent, QualityAssuranceAgent

**Related Tools**: [`search_safetyculture_assets()`](#11-search_safetyculture_assets)

---

#### 1.3 `search_safetyculture_templates`

Search for inspection templates in SafetyCulture.

**Purpose**: Discover available templates for creating inspections, with optional name filtering.

**Parameters**:
- `template_name_filter` (Optional[str]): Substring to match in template names (case-insensitive)
- `include_archived` (bool): Whether to include archived templates (default: False)

**Returns**: JSON string containing template list with IDs, names, and timestamps

**Usage Example**:
```python
# Find all vehicle inspection templates
templates = await search_safetyculture_templates(
    template_name_filter="vehicle",
    include_archived=False
)
```

**Used By**: TemplateSelectionAgent, SafetyCultureCoordinator, QualityAssuranceAgent

**Related Tools**: [`get_safetyculture_template_details()`](#14-get_safetyculture_template_details), [`ai_match_templates_to_asset()`](#31-ai_match_templates_to_asset)

---

#### 1.4 `get_safetyculture_template_details`

Get detailed structure of an inspection template.

**Purpose**: Retrieve complete template schema including all sections, questions, and field types.

**Parameters**:
- `template_id` (str): The unique ID of the template (validated)

**Returns**: JSON string containing template structure with all fields and metadata

**Usage Example**:
```python
# Get template structure for form filling
template = await get_safetyculture_template_details(
    template_id="template_789xyz"
)
# Use to understand required fields and structure
```

**Used By**: TemplateSelectionAgent, InspectionCreationAgent, FormFillingAgent

**Related Tools**: [`search_safetyculture_templates()`](#13-search_safetyculture_templates)

---

#### 1.5 `create_safetyculture_inspection`

Create a new inspection from a template with optional pre-filled header data.

**Purpose**: Initiate inspections with header information like title, conductor, and location.

**Parameters**:
- `template_id` (str): The template ID to create inspection from (required)
- `inspection_title` (Optional[str]): Custom title for the inspection
- `conducted_by` (Optional[str]): Name of the inspector
- `site_location` (Optional[str]): Site/location name
- `asset_id` (Optional[str]): Asset ID being inspected

**Returns**: JSON string with created inspection details including `audit_id`

**Usage Example**:
```python
# Create pre-filled inspection
inspection = await create_safetyculture_inspection(
    template_id="template_789xyz",
    inspection_title="Monthly Vehicle Check - Forklift 42",
    conducted_by="SafetyCulture Agent",
    asset_id="asset_abc123"
)
# Extract audit_id for subsequent updates
```

**Used By**: InspectionCreationAgent, SafetyCultureCoordinator

**Field Mapping**: Uses [`FieldMappingLoader`](safetyculture_agent/config/field_mapping_loader.py:1) to map standard fields to template-specific IDs.

**Related Tools**: [`update_safetyculture_inspection()`](#16-update_safetyculture_inspection), [`register_asset_for_monthly_inspection()`](#43-register_asset_for_monthly_inspection)

---

#### 1.6 `update_safetyculture_inspection`

Update inspection responses with field values.

**Purpose**: Populate or modify inspection form fields with structured data.

**Parameters**:
- `audit_id` (str): The inspection ID to update (required)
- `field_updates` (List[Dict[str, Any]]): List of field updates, each containing:
  - `item_id` (str): The field ID to update
  - `field_type` (str): Field type ('textsingle', 'datetime', 'checkbox', etc.)
  - `value` (Any): The value to set

**Returns**: JSON string containing update response

**Usage Example**:
```python
# Update multiple fields in an inspection
updates = [
    {
        "item_id": "field_123",
        "field_type": "textsingle",
        "value": "Excellent condition"
    },
    {
        "item_id": "field_456",
        "field_type": "datetime",
        "value": "2025-10-03T10:30:00Z"
    }
]
result = await update_safetyculture_inspection(
    audit_id="audit_abc123",
    field_updates=updates
)
```

**Used By**: FormFillingAgent, SafetyCultureCoordinator

**Related Tools**: [`create_safetyculture_inspection()`](#15-create_safetyculture_inspection), [`generate_intelligent_inspection_data()`](#36-generate_intelligent_inspection_data)

---

#### 1.7 `get_safetyculture_inspection_details`

Get detailed information about a specific inspection.

**Purpose**: Retrieve complete inspection data including all responses and status.

**Parameters**:
- `audit_id` (str): The unique ID of the inspection (validated)

**Returns**: JSON string containing detailed inspection information

**Usage Example**:
```python
# Retrieve inspection for review
inspection = await get_safetyculture_inspection_details(
    audit_id="audit_abc123"
)
# Review responses before sharing
```

**Used By**: FormFillingAgent, QualityAssuranceAgent, SafetyCultureCoordinator

**Related Tools**: [`search_safetyculture_inspections()`](#19-search_safetyculture_inspections)

---

#### 1.8 `share_safetyculture_inspection`

Share an inspection with users via email.

**Purpose**: Grant access permissions to inspections for collaboration or review.

**Parameters**:
- `audit_id` (str): The inspection ID to share (required)
- `user_emails` (List[str]): List of email addresses to share with
- `permission` (str): Permission level - 'view', 'edit', or 'delete' (default: 'edit')

**Returns**: JSON string containing sharing response

**Usage Example**:
```python
# Share completed inspection with supervisors
result = await share_safetyculture_inspection(
    audit_id="audit_abc123",
    user_emails=["supervisor@example.com", "manager@example.com"],
    permission="view"
)
```

**Used By**: QualityAssuranceAgent, SafetyCultureCoordinator

**Note**: Automatically looks up user IDs from email addresses before sharing.

**Related Tools**: [`get_safetyculture_inspection_details()`](#17-get_safetyculture_inspection_details)

---

#### 1.9 `search_safetyculture_inspections`

Search for existing inspections with flexible filtering.

**Purpose**: Find inspections by template, date range, or other criteria.

**Parameters**:
- `template_id` (Optional[str]): Filter by template ID
- `modified_after` (Optional[str]): ISO datetime to filter inspections modified after date
- `limit` (int): Maximum results to return (default: 100, max: 1000)

**Returns**: JSON string containing inspection search results

**Usage Example**:
```python
# Find recent inspections from specific template
inspections = await search_safetyculture_inspections(
    template_id="template_789xyz",
    modified_after="2025-10-01T00:00:00Z",
    limit=50
)
```

**Used By**: QualityAssuranceAgent, SafetyCultureCoordinator

**Related Tools**: [`get_safetyculture_inspection_details()`](#17-get_safetyculture_inspection_details), [`analyze_historical_inspection_patterns()`](#35-analyze_historical_inspection_patterns)

---

## 2. Memory Tools

### Overview
These tools leverage ADK's memory service to provide persistent, searchable storage across agent sessions. Memory is stored as structured text that can be semantically searched using the [`ToolContext`](https://github.com/google/adk-python/blob/main/src/google/adk/tools/tool_context.py) API.

**Implementation**: [`memory_tools.py`](safetyculture_agent/memory/memory_tools.py:1)

**Key Features**:
- Semantic search using ADK's memory service
- Session-based persistence
- Structured metadata for efficient retrieval
- Automatic timestamping

---

#### 2.1 `store_asset_registry`

Store discovered asset information in memory for quick access.

**Purpose**: Cache asset data to avoid repeated API calls and enable fast lookups across workflow steps.

**Parameters**:
- `assets` (List[Dict[str, Any]]): List of asset dictionaries to store (must contain 'id', 'name', 'asset_type')
- `registry_key` (str): Storage key (default: "asset_registry") - use different keys for different registries
- `tool_context` (Optional[ToolContext]): Tool context for memory access (auto-injected by ADK)

**Returns**: Confirmation message with count of stored assets

**Usage Example**:
```python
# Store discovered assets for later retrieval
assets = [
    {"id": "asset_1", "name": "Forklift-42", "asset_type": "Vehicle"},
    {"id": "asset_2", "name": "Crane-7", "asset_type": "Equipment"}
]
result = await store_asset_registry(
    assets=assets,
    registry_key="facility_a_assets"
)
# Returns: "Successfully stored 2 assets in memory under key 'facility_a_assets'"
```

**Used By**: AssetDiscoveryAgent, SafetyCultureCoordinator

**Memory Format**:
```
Asset Registry (facility_a_assets):
Stored 2 assets at 2025-10-03T13:45:00
Asset types: Vehicle, Equipment

Assets:
[{...asset data...}]
```

**Related Tools**: [`retrieve_asset_registry()`](#22-retrieve_asset_registry)

---

#### 2.2 `retrieve_asset_registry`

Retrieve stored asset information from memory using semantic search.

**Purpose**: Fetch previously cached assets without re-querying the SafetyCulture API.

**Parameters**:
- `registry_key` (str): Storage key to retrieve from (default: "asset_registry")
- `asset_type_filter` (Optional[str]): Filter results by asset type
- `tool_context` (Optional[ToolContext]): Tool context for memory access

**Returns**: JSON string containing stored asset information or error message

**Usage Example**:
```python
# Retrieve vehicles from cached registry
vehicles = await retrieve_asset_registry(
    registry_key="facility_a_assets",
    asset_type_filter="Vehicle"
)
```

**Used By**: TemplateSelectionAgent, InspectionCreationAgent, SafetyCultureCoordinator

**Related Tools**: [`store_asset_registry()`](#21-store_asset_registry)

---

#### 2.3 `store_template_library`

Cache template information in memory for efficient access.

**Purpose**: Store frequently used templates to reduce API latency during template selection.

**Parameters**:
- `templates` (List[Dict[str, Any]]): Template dictionaries (must contain 'template_id', 'name')
- `library_key` (str): Storage key (default: "template_library")
- `tool_context` (Optional[ToolContext]): Tool context for memory access

**Returns**: Confirmation message with count of stored templates

**Usage Example**:
```python
# Cache vehicle templates
templates = [
    {"template_id": "tpl_1", "name": "Vehicle Safety Check"},
    {"template_id": "tpl_2", "name": "Vehicle Maintenance"}
]
await store_template_library(templates, library_key="vehicle_templates")
```

**Used By**: TemplateSelectionAgent, SafetyCultureCoordinator

**Related Tools**: [`retrieve_template_library()`](#24-retrieve_template_library)

---

#### 2.4 `retrieve_template_library`

Retrieve cached template information from memory.

**Purpose**: Quick access to template data without API calls.

**Parameters**:
- `library_key` (str): Storage key to retrieve from (default: "template_library")
- `name_filter` (Optional[str]): Filter by template name substring
- `tool_context` (Optional[ToolContext]): Tool context for memory access

**Returns**: JSON string containing stored template information

**Usage Example**:
```python
# Get all vehicle-related templates
templates = await retrieve_template_library(
    library_key="vehicle_templates",
    name_filter="safety"
)
```

**Used By**: TemplateSelectionAgent, InspectionCreationAgent

**Related Tools**: [`store_template_library()`](#23-store_template_library)

---

#### 2.5 `store_workflow_state`

Persist workflow state for resumption and coordination.

**Purpose**: Enable workflow resumption after interruption and maintain state across multi-step processes.

**Parameters**:
- `workflow_data` (Dict[str, Any]): Workflow state dictionary (should include 'current_step', 'completed_steps')
- `state_key` (str): Storage key (default: "workflow_state")
- `tool_context` (Optional[ToolContext]): Tool context for memory access

**Returns**: Confirmation message

**Usage Example**:
```python
# Store current workflow progress
workflow_state = {
    "current_step": "inspection_creation",
    "completed_steps": ["asset_discovery", "template_selection"],
    "assets_processed": 15,
    "total_assets": 50,
    "batch_id": "batch_20251003"
}
await store_workflow_state(workflow_state, state_key="batch_workflow")
```

**Used By**: SafetyCultureCoordinator, all sub-agents

**Related Tools**: [`retrieve_workflow_state()`](#26-retrieve_workflow_state)

---

#### 2.6 `retrieve_workflow_state`

Fetch workflow state for resumption or inspection.

**Purpose**: Resume interrupted workflows or check current progress.

**Parameters**:
- `state_key` (str): Storage key to retrieve from (default: "workflow_state")
- `tool_context` (Optional[ToolContext]): Tool context for memory access

**Returns**: JSON string containing workflow state information

**Usage Example**:
```python
# Check workflow progress
state = await retrieve_workflow_state(state_key="batch_workflow")
# Use to resume from last successful step
```

**Used By**: SafetyCultureCoordinator, QualityAssuranceAgent

**Related Tools**: [`store_workflow_state()`](#25-store_workflow_state)

---

#### 2.7 `store_inspection_history`

Archive completed inspections for pattern analysis and learning.

**Purpose**: Build historical dataset for AI-powered optimization and trend analysis.

**Parameters**:
- `inspections` (List[Dict[str, Any]]): Completed inspection data (must include 'inspection_id', 'template_id', 'completion_date')
- `history_key` (str): Storage key (default: "inspection_history")
- `tool_context` (Optional[ToolContext]): Tool context for memory access

**Returns**: Confirmation message with count of stored inspections

**Usage Example**:
```python
# Archive completed inspections for analysis
completed = [
    {
        "inspection_id": "audit_123",
        "template_id": "tpl_1",
        "completion_date": "2025-10-03",
        "asset_id": "asset_1",
        "results": {"score": 95}
    }
]
await store_inspection_history(completed)
```

**Used By**: QualityAssuranceAgent, FormFillingAgent

**Related Tools**: [`analyze_historical_inspection_patterns()`](#35-analyze_historical_inspection_patterns)

---

## 3. AI Tools

### Overview
AI-powered tools leveraging Google's Gemini models for intelligent automation. These tools provide semantic understanding, pattern recognition, and intelligent data generation capabilities.

**Implementation**: [`ai_tools.py`](safetyculture_agent/ai/ai_tools.py:1)

**Supporting Modules**:
- [`template_matcher.py`](safetyculture_agent/ai/template_matcher.py:1) - AI template matching
- [`form_intelligence.py`](safetyculture_agent/ai/form_intelligence.py:1) - Form field intelligence
- [`image_analyzer.py`](safetyculture_agent/ai/image_analyzer.py:1) - Computer vision
- [`pattern_detector.py`](safetyculture_agent/ai/pattern_detector.py:1) - Trend analysis

---

#### 3.1 `ai_match_templates_to_asset`

Use AI to match inspection templates to assets based on semantic similarity.

**Purpose**: Intelligently select the most appropriate template for an asset using compliance requirements, asset characteristics, and historical data.

**Parameters**:
- `asset_data` (Dict[str, Any]): Asset information including type, location, criticality, compliance requirements
- `available_templates` (List[Dict[str, Any]]): List of available templates to match against

**Returns**: JSON string with ranked template matches, confidence scores, and reasoning

**Usage Example**:
```python
# Find best templates for a high-criticality asset
asset = {
    "id": "asset_123",
    "type": "Pressure Vessel",
    "name": "Boiler-A",
    "criticality": "high",
    "compliance_requirements": ["OSHA", "ASME"],
    "location": "Plant Floor 2"
}
templates = [
    {"template_id": "tpl_1", "name": "Pressure Vessel Inspection"},
    {"template_id": "tpl_2", "name": "General Equipment Check"}
]
matches = await ai_match_templates_to_asset(asset, templates)
# Returns ranked list with confidence scores
```

**Output Format**:
```json
{
  "asset_id": "asset_123",
  "matches": [
    {
      "template_id": "tpl_1",
      "template_name": "Pressure Vessel Inspection",
      "confidence_score": 0.95,
      "match_reasons": ["Matches asset type", "Covers OSHA requirements"],
      "compliance_requirements": ["OSHA", "ASME"]
    }
  ],
  "best_match": {"template_id": "tpl_1", "confidence": 0.95}
}
```

**Used By**: TemplateSelectionAgent

**AI Model**: Uses Gemini for semantic similarity and compliance matching

**Related Tools**: [`generate_dynamic_template_for_asset()`](#32-generate_dynamic_template_for_asset)

---

#### 3.2 `generate_dynamic_template_for_asset`

Generate a custom inspection template dynamically based on asset characteristics.

**Purpose**: Create tailored templates when no suitable pre-existing template is found.

**Parameters**:
- `asset_data` (Dict[str, Any]): Asset information including type, criticality, compliance needs

**Returns**: JSON string containing generated template structure

**Usage Example**:
```python
# Generate custom template for specialized equipment
asset = {
    "id": "asset_456",
    "type": "CNC Machine",
    "name": "CNC-Router-5",
    "criticality": "high",
    "compliance_requirements": ["ISO 9001"],
    "custom_attributes": {"manufacturer": "ACME", "model": "XR-2000"}
}
template = await generate_dynamic_template_for_asset(asset)
# Returns template with auto-generated sections and questions
```

**Used By**: TemplateSelectionAgent (fallback when no matches found)

**AI Model**: Uses Gemini to generate contextually appropriate inspection questions

**Related Tools**: [`ai_match_templates_to_asset()`](#31-ai_match_templates_to_asset)

---

#### 3.3 `analyze_asset_image_for_inspection`

Analyze asset images to extract condition information for inspection forms.

**Purpose**: Use computer vision to assess asset condition and identify visible issues.

**Parameters**:
- `image_base64` (str): Base64 encoded image data
- `asset_type` (str): Type of asset being analyzed (helps context)

**Returns**: JSON string with condition assessment, damage reports, and safety concerns

**Usage Example**:
```python
# Analyze photo of equipment
import base64

with open("forklift_photo.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

analysis = await analyze_asset_image_for_inspection(
    image_base64=image_data,
    asset_type="Forklift"
)
# Returns condition assessment and visible issues
```

**Output Format**:
```json
{
  "asset_condition": "Fair - minor wear visible",
  "visible_damage": ["Tire tread wear", "Paint scratches on left side"],
  "safety_concerns": ["Tire pressure appears low"],
  "maintenance_indicators": ["Needs tire replacement soon"],
  "confidence_score": 0.87,
  "extracted_text": ["Model: FL-42", "Last Service: 2025-09"]
}
```

**Used By**: FormFillingAgent, InspectionCreationAgent

**AI Model**: Uses Gemini Vision for multimodal analysis

**Related Tools**: [`generate_intelligent_inspection_data()`](#36-generate_intelligent_inspection_data)

---

#### 3.4 `parse_maintenance_logs_for_insights`

Parse unstructured maintenance logs to extract structured information.

**Purpose**: Convert free-text maintenance records into structured data for inspection forms.

**Parameters**:
- `maintenance_log_text` (str): Raw maintenance log text (can be multi-entry)

**Returns**: JSON string with parsed maintenance entries

**Usage Example**:
```python
# Parse maintenance history
log_text = """
2025-09-15: Replaced hydraulic fluid. Tech: John Smith
Issues: Minor leak detected in pump seal
Recommendation: Monitor seal, may need replacement in 3 months

2025-08-10: Routine inspection. Tech: Jane Doe
All systems normal. No issues found.
"""
parsed = await parse_maintenance_logs_for_insights(log_text)
```

**Output Format**:
```json
{
  "total_entries": 2,
  "entries": [
    {
      "date": "2025-09-15",
      "action": "Replaced hydraulic fluid",
      "technician": "John Smith",
      "parts_replaced": ["hydraulic fluid"],
      "issues_found": ["Minor leak detected in pump seal"],
      "recommendations": ["Monitor seal, may need replacement in 3 months"]
    }
  ]
}
```

**Used By**: FormFillingAgent

**AI Model**: Uses Gemini for NLP and entity extraction

**Related Tools**: [`generate_intelligent_inspection_data()`](#36-generate_intelligent_inspection_data)

---

#### 3.5 `analyze_historical_inspection_patterns`

Analyze past inspections to identify patterns and predict future values.

**Purpose**: Learn from historical data to improve inspection accuracy and predict typical values.

**Parameters**:
- `asset_id` (str): ID of asset to analyze
- `inspection_history` (List[Dict[str, Any]]): Historical inspection data

**Returns**: JSON string with identified patterns and trends

**Usage Example**:
```python
# Analyze inspection trends
history = [
    {"date": "2025-09", "temperature": 185, "pressure": 120},
    {"date": "2025-08", "temperature": 182, "pressure": 118},
    {"date": "2025-07", "temperature": 180, "pressure": 115}
]
patterns = await analyze_historical_inspection_patterns(
    asset_id="asset_123",
    inspection_history=history
)
```

**Output Format**:
```json
{
  "asset_id": "asset_123",
  "patterns_found": 2,
  "patterns": [
    {
      "pattern_type": "temperature",
      "frequency": "monthly",
      "typical_values": [180, 185],
      "trend_direction": "increasing",
      "confidence": 0.92
    }
  ]
}
```

**Used By**: FormFillingAgent, QualityAssuranceAgent

**AI Model**: Uses statistical analysis and Gemini for trend interpretation

**Related Tools**: [`generate_intelligent_inspection_data()`](#36-generate_intelligent_inspection_data)

---

#### 3.6 `generate_intelligent_inspection_data`

Generate comprehensive form data using multiple AI capabilities.

**Purpose**: Create intelligent, contextually appropriate inspection data by combining image analysis, maintenance logs, and historical patterns.

**Parameters**:
- `asset_data` (Dict[str, Any]): Asset information
- `template_data` (Dict[str, Any]): Template structure
- `image_base64` (Optional[str]): Asset image (optional)
- `maintenance_log_text` (Optional[str]): Maintenance logs (optional)
- `inspection_history` (Optional[List[Dict[str, Any]]]): Historical data (optional)

**Returns**: JSON string with intelligent form data for all fields

**Usage Example**:
```python
# Generate complete inspection data
form_data = await generate_intelligent_inspection_data(
    asset_data={"id": "asset_123", "type": "Forklift", "name": "FL-42"},
    template_data={"template_id": "tpl_1", "fields": [...]},
    image_base64=image_data,  # Optional
    maintenance_log_text=log_text,  # Optional
    inspection_history=history  # Optional
)
# Returns complete field mappings ready for update_safetyculture_inspection()
```

**Output Format**:
```json
{
  "asset_id": "asset_123",
  "template_id": "tpl_1",
  "generated_at": "2025-10-03T13:45:00Z",
  "data_sources_used": {
    "image_analysis": true,
    "maintenance_logs": true,
    "historical_patterns": true
  },
  "form_data": {
    "field_123": {"value": "Good", "confidence": 0.89},
    "field_456": {"value": "185°F", "confidence": 0.95}
  },
  "confidence_assessment": "High confidence - multiple data sources"
}
```

**Used By**: FormFillingAgent

**Integration**: Combines all AI tools (#3.3, #3.4, #3.5) for comprehensive analysis

**Related Tools**: All other AI tools feed into this orchestration tool

---

## 4. Database Tools

### Overview
SQLite-based tracking system for preventing duplicate monthly inspections and generating compliance reports. Uses [`AssetTracker`](safetyculture_agent/database/asset_tracker.py:1) class for all database operations.

**Implementation**: [`database_tools.py`](safetyculture_agent/database/database_tools.py:1)

**Key Features**:
- Monthly inspection tracking
- Duplicate prevention
- Status management (pending/in_progress/completed/failed)
- Comprehensive reporting
- Thread-safe async operations

---

#### 4.1 `initialize_asset_database`

Initialize the asset tracking database with required tables and indexes.

**Purpose**: Set up database schema for first-time use.

**Parameters**: None

**Returns**: Status message indicating success or failure

**Usage Example**:
```python
# Initialize database on first run
result = await initialize_asset_database()
# Returns: "Asset tracking database initialized successfully"
```

**Used By**: SafetyCultureCoordinator (startup), AssetDiscoveryAgent

**Schema**: Creates tables for assets, inspections, and monthly summaries

**Related Tools**: All other database tools require initialization first

---

#### 4.2 `check_asset_completion_status`

Check if an asset has already been inspected this month.

**Purpose**: Prevent duplicate inspections and verify current status.

**Parameters**:
- `asset_id` (str): ID of asset to check
- `month_year` (Optional[str]): Month-year string (YYYY-MM), defaults to current month

**Returns**: JSON string with completion status and action recommendations

**Usage Example**:
```python
# Check before creating inspection
status = await check_asset_completion_status(
    asset_id="asset_123",
    month_year="2025-10"
)
```

**Output Format**:
```json
{
  "asset_id": "asset_123",
  "month_year": "2025-10",
  "is_completed": false,
  "current_status": "pending",
  "can_create_inspection": true
}
```

**Used By**: AssetDiscoveryAgent, InspectionCreationAgent

**Related Tools**: [`register_asset_for_monthly_inspection()`](#43-register_asset_for_monthly_inspection)

---

#### 4.3 `register_asset_for_monthly_inspection`

Register an asset for inspection in the tracking database.

**Purpose**: Record intent to inspect asset and prevent duplicate registrations.

**Parameters**:
- `asset_id` (str): Unique asset identifier
- `asset_name` (str): Human-readable asset name
- `asset_type` (str): Type/category of asset
- `location` (str): Physical location
- `template_id` (str): Template ID to use
- `template_name` (str): Template name
- `inspector` (str): Inspector name (default: "SafetyCulture Agent")
- `month_year` (Optional[str]): Month-year string (default: current month)

**Returns**: JSON string indicating success or failure

**Usage Example**:
```python
# Register asset before creating inspection
result = await register_asset_for_monthly_inspection(
    asset_id="asset_123",
    asset_name="Forklift-42",
    asset_type="Vehicle",
    location="Warehouse A",
    template_id="tpl_1",
    template_name="Vehicle Safety Check",
    inspector="SafetyCulture Agent"
)
```

**Used By**: InspectionCreationAgent

**Duplicate Prevention**: Returns false if asset already completed or in progress for the month

**Related Tools**: [`update_asset_inspection_status()`](#44-update_asset_inspection_status)

---

#### 4.4 `update_asset_inspection_status`

Update the inspection status for an asset.

**Purpose**: Track progress through inspection lifecycle.

**Parameters**:
- `asset_id` (str): Asset ID
- `status` (str): New status ('pending', 'in_progress', 'completed', 'failed')
- `inspection_id` (Optional[str]): SafetyCulture inspection ID
- `month_year` (Optional[str]): Month-year string (default: current month)

**Returns**: JSON string indicating success or failure

**Usage Example**:
```python
# Mark inspection as in progress
await update_asset_inspection_status(
    asset_id="asset_123",
    status="in_progress",
    inspection_id="audit_abc123"
)
```

**Used By**: InspectionCreationAgent, FormFillingAgent

**Status Values**:
- `pending`: Registered but not started
- `in_progress`: Inspection created, being filled
- `completed`: Finished successfully
- `failed`: Error occurred

**Related Tools**: [`mark_asset_inspection_completed()`](#45-mark_asset_inspection_completed)

---

#### 4.5 `mark_asset_inspection_completed`

Mark an asset inspection as completed.

**Purpose**: Finalize inspection record and prevent re-inspection this month.

**Parameters**:
- `asset_id` (str): Asset ID
- `inspection_id` (str): SafetyCulture inspection ID
- `inspector` (str): Inspector name (default: "SafetyCulture Agent")
- `month_year` (Optional[str]): Month-year string (default: current month)

**Returns**: JSON string indicating success or failure

**Usage Example**:
```python
# Mark inspection complete after form filling
result = await mark_asset_inspection_completed(
    asset_id="asset_123",
    inspection_id="audit_abc123",
    inspector="SafetyCulture Agent"
)
```

**Used By**: FormFillingAgent, QualityAssuranceAgent

**Side Effects**: Sets completion timestamp and marks asset as done for the month

**Related Tools**: [`get_completed_assets_report()`](#47-get_completed_assets_report)

---

#### 4.6 `get_pending_assets_for_inspection`

Get all pending asset inspections for a month.

**Purpose**: Retrieve assets waiting for inspection to prioritize workflow.

**Parameters**:
- `month_year` (Optional[str]): Month-year string (default: current month)
- `limit` (Optional[int]): Maximum assets to return

**Returns**: JSON string with list of pending assets

**Usage Example**:
```python
# Get next batch of assets to inspect
pending = await get_pending_assets_for_inspection(
    month_year="2025-10",
    limit=25
)
```

**Output Format**:
```json
{
  "month_year": "2025-10",
  "total_pending": 15,
  "limit_applied": 25,
  "assets": [
    {
      "asset_id": "asset_123",
      "asset_name": "Forklift-42",
      "asset_type": "Vehicle",
      "location": "Warehouse A",
      "template_id": "tpl_1",
      "template_name": "Vehicle Safety Check",
      "created_at": "2025-10-01T08:00:00Z"
    }
  ]
}
```

**Used By**: SafetyCultureCoordinator, QualityAssuranceAgent

**Related Tools**: [`get_completed_assets_report()`](#47-get_completed_assets_report)

---

#### 4.7 `get_completed_assets_report`

Get all completed asset inspections for a month.

**Purpose**: Generate completion reports for compliance and audit purposes.

**Parameters**:
- `month_year` (Optional[str]): Month-year string (default: current month)

**Returns**: JSON string with list of completed assets

**Usage Example**:
```python
# Generate monthly completion report
completed = await get_completed_assets_report(month_year="2025-10")
```

**Output Format**:
```json
{
  "month_year": "2025-10",
  "total_completed": 42,
  "assets": [
    {
      "asset_id": "asset_123",
      "asset_name": "Forklift-42",
      "asset_type": "Vehicle",
      "location": "Warehouse A",
      "inspection_id": "audit_abc123",
      "completion_date": "2025-10-03T14:30:00Z",
      "inspector": "SafetyCulture Agent"
    }
  ]
}
```

**Used By**: QualityAssuranceAgent, SafetyCultureCoordinator

**Related Tools**: [`get_monthly_inspection_summary()`](#48-get_monthly_inspection_summary)

---

#### 4.8 `get_monthly_inspection_summary`

Get monthly inspection summary with statistics and completion rates.

**Purpose**: Generate executive summary with KPIs and completion metrics.

**Parameters**:
- `month_year` (Optional[str]): Month-year string (default: current month)

**Returns**: JSON string with comprehensive statistics

**Usage Example**:
```python
# Generate monthly KPI report
summary = await get_monthly_inspection_summary(month_year="2025-10")
```

**Output Format**:
```json
{
  "month_year": "2025-10",
  "total_registered": 50,
  "total_completed": 42,
  "total_pending": 5,
  "total_in_progress": 3,
  "completion_rate": 0.84,
  "by_asset_type": {
    "Vehicle": {"completed": 20, "total": 25},
    "Equipment": {"completed": 22, "total": 25}
  },
  "by_location": {
    "Warehouse A": {"completed": 30, "total": 35}
  }
}
```

**Used By**: QualityAssuranceAgent, SafetyCultureCoordinator

**Related Tools**: [`export_comprehensive_monthly_report()`](#49-export_comprehensive_monthly_report)

---

#### 4.9 `export_comprehensive_monthly_report`

Export a comprehensive monthly report with all details.

**Purpose**: Generate complete audit trail with all asset details and statistics.

**Parameters**:
- `month_year` (Optional[str]): Month-year string (default: current month)

**Returns**: JSON string with comprehensive monthly report

**Usage Example**:
```python
# Export full monthly report
report = await export_comprehensive_monthly_report(month_year="2025-10")
# Can be saved to file or sent to stakeholders
```

**Used By**: QualityAssuranceAgent

**Contents**: Includes summary statistics + full asset lists + timeline data

**Related Tools**: [`get_monthly_inspection_summary()`](#48-get_monthly_inspection_summary)

---

#### 4.10 `filter_assets_to_prevent_duplicates`

Filter discovered assets to remove those already completed this month.

**Purpose**: Prevent duplicate inspections by checking database before processing.

**Parameters**:
- `discovered_assets` (List[Dict[str, Any]]): Assets from SafetyCulture API
- `month_year` (Optional[str]): Month-year string (default: current month)

**Returns**: JSON string with filtered assets needing inspection

**Usage Example**:
```python
# Filter assets after discovery
discovered = [
    {"id": "asset_1", "name": "Forklift-42"},
    {"id": "asset_2", "name": "Crane-7"}
]
filtered = await filter_assets_to_prevent_duplicates(
    discovered_assets=discovered,
    month_year="2025-10"
)
```

**Output Format**:
```json
{
  "month_year": "2025-10",
  "total_discovered": 2,
  "already_completed": 1,
  "needs_inspection": 1,
  "completed_asset_ids": ["asset_1"],
  "assets_needing_inspection": [{"id": "asset_2", "name": "Crane-7"}]
}
```

**Used By**: AssetDiscoveryAgent, SafetyCultureCoordinator

**Related Tools**: [`check_asset_completion_status()`](#42-check_asset_completion_status)

---

## Tool Usage Patterns

### Common Workflows

#### Workflow 1: Asset Discovery → Template Selection

```python
# 1. Search for assets
assets_json = await search_safetyculture_assets(
    asset_types=["Vehicle"],
    site_names=["Main Facility"],
    limit=50
)

# 2. Filter out already-completed assets
filtered_json = await filter_assets_to_prevent_duplicates(
    discovered_assets=json.loads(assets_json)["assets"]
)

# 3. Store in memory for later retrieval
await store_asset_registry(
    assets=json.loads(filtered_json)["assets_needing_inspection"],
    registry_key="october_vehicles"
)

# 4. Search for templates
templates_json = await search_safetyculture_templates(
    template_name_filter="vehicle"
)

# 5. AI-match templates to each asset
for asset in assets:
    matches = await ai_match_templates_to_asset(
        asset_data=asset,
        available_templates=json.loads(templates_json)["templates"]
    )
```

#### Workflow 2: Inspection Creation → Form Filling

```python
# 1. Register asset in tracking database
await register_asset_for_monthly_inspection(
    asset_id="asset_123",
    asset_name="Forklift-42",
    asset_type="Vehicle",
    location="Warehouse A",
    template_id="tpl_1",
    template_name="Vehicle Safety Check"
)

# 2. Create inspection with pre-filled header
inspection = await create_safetyculture_inspection(
    template_id="tpl_1",
    inspection_title="Monthly Check - Forklift-42",
    conducted_by="SafetyCulture Agent",
    asset_id="asset_123"
)
audit_id = json.loads(inspection)["audit_id"]

# 3. Update status to in_progress
await update_asset_inspection_status(
    asset_id="asset_123",
    status="in_progress",
    inspection_id=audit_id
)

# 4. Generate intelligent form data (using AI + images + logs)
form_data = await generate_intelligent_inspection_data(
    asset_data=asset,
    template_data=template,
    image_base64=image,
    maintenance_log_text=logs
)

# 5. Update inspection with generated data
field_updates = []  # Convert form_data to field updates
await update_safetyculture_inspection(
    audit_id=audit_id,
    field_updates=field_updates
)

# 6. Mark as completed
await mark_asset_inspection_completed(
    asset_id="asset_123",
    inspection_id=audit_id
)
```

#### Workflow 3: Quality Assurance → Final Submission

```python
# 1. Get completed inspections for review
completed = await get_completed_assets_report(month_year="2025-10")

# 2. Review each inspection
for asset in json.loads(completed)["assets"]:
    inspection = await get_safetyculture_inspection_details(
        audit_id=asset["inspection_id"]
    )
    # Validate responses...

# 3. Generate monthly summary
summary = await get_monthly_inspection_summary(month_year="2025-10")

# 4. Export comprehensive report
report = await export_comprehensive_monthly_report(month_year="2025-10")

# 5. Share inspections with stakeholders
for asset in completed_assets:
    await share_safetyculture_inspection(
        audit_id=asset["inspection_id"],
        user_emails=["supervisor@example.com"],
        permission="view"
    )
```

---

## Error Handling

### Security-First Error Handling

All tools implement security-conscious error handling using [`SecureHeaderManager`](safetyculture_agent/utils/secure_header_manager.py:1):

1. **Credential Sanitization**: API tokens and authentication headers are never included in error messages
2. **Error Classification**: Distinguishes between validation errors (safe) and system errors (sanitized)
3. **Logging**: Detailed errors logged securely, sanitized errors returned to users

**Example**:
```python
try:
    result = await search_safetyculture_assets(...)
except SafetyCultureAPIError as e:
    # Error message has been sanitized - no credentials exposed
    logger.error(f"Safe error message: {e}")
except SafetyCultureValidationError as e:
    # Validation errors are safe to show users
    logger.warning(f"Invalid input: {e}")
```

### Rate Limiting & Circuit Breakers

**Rate Limiting**: [`ExponentialBackoffRateLimiter`](safetyculture_agent/utils/rate_limiter.py:1)
- Token bucket algorithm with burst capacity
- Exponential backoff on rate limit hits
- Configurable via [`SafetyCultureConfig`](safetyculture_agent/config/api_config.py:1)

**Circuit Breaker**: [`CircuitBreaker`](safetyculture_agent/utils/circuit_breaker.py:1)
- Opens after 5 consecutive failures
- Half-open state for testing recovery
- Exponential timeout increase (60s → 600s max)

**Request Signing**: [`RequestSigner`](safetyculture_agent/utils/request_signer.py:1)
- HMAC-SHA256 signatures for API requests
- 5-minute timestamp window
- Optional - enable with `SAFETYCULTURE_SIGNING_KEY` env var

---

## Quick Reference

### Tool Matrix

| Tool | Category | Sub-Agents Using It | Primary Use Case |
|------|----------|---------------------|------------------|
| `search_safetyculture_assets` | API | AssetDiscovery, Coordinator, QA | Find assets to inspect |
| `get_safetyculture_asset_details` | API | AssetDiscovery, InspectionCreation, QA | Get asset metadata |
| `search_safetyculture_templates` | API | TemplateSelection, Coordinator, QA | Find templates |
| `get_safetyculture_template_details` | API | TemplateSelection, InspectionCreation, FormFilling | Get template structure |
| `create_safetyculture_inspection` | API | InspectionCreation, Coordinator | Create new inspections |
| `update_safetyculture_inspection` | API | FormFilling, Coordinator | Update inspection fields |
| `get_safetyculture_inspection_details` | API | FormFilling, QA, Coordinator | Review inspections |
| `share_safetyculture_inspection` | API | QA, Coordinator | Share with stakeholders |
| `search_safetyculture_inspections` | API | QA, Coordinator | Find existing inspections |
| `store_asset_registry` | Memory | AssetDiscovery, Coordinator | Cache discovered assets |
| `retrieve_asset_registry` | Memory | TemplateSelection, InspectionCreation, Coordinator | Retrieve cached assets |
| `store_template_library` | Memory | TemplateSelection, Coordinator | Cache templates |
| `retrieve_template_library` | Memory | TemplateSelection, InspectionCreation | Retrieve cached templates |
| `store_workflow_state` | Memory | Coordinator, all sub-agents | Save workflow progress |
| `retrieve_workflow_state` | Memory | Coordinator, QA | Resume workflows |
| `store_inspection_history` | Memory | QA, FormFilling | Archive for learning |
| `ai_match_templates_to_asset` | AI | TemplateSelection | Smart template matching |
| `generate_dynamic_template_for_asset` | AI | TemplateSelection | Create custom templates |
| `analyze_asset_image_for_inspection` | AI | FormFilling, InspectionCreation | Extract from images |
| `parse_maintenance_logs_for_insights` | AI | FormFilling | Parse logs |
| `analyze_historical_inspection_patterns` | AI | FormFilling, QA | Learn from history |
| `generate_intelligent_inspection_data` | AI | FormFilling | Generate form data |
| `initialize_asset_database` | Database | Coordinator, AssetDiscovery | Setup database |
| `check_asset_completion_status` | Database | AssetDiscovery, InspectionCreation | Check duplicates |
| `register_asset_for_monthly_inspection` | Database | InspectionCreation | Register asset |
| `update_asset_inspection_status` | Database | InspectionCreation, FormFilling | Track progress |
| `mark_asset_inspection_completed` | Database | FormFilling, QA | Mark complete |
| `get_pending_assets_for_inspection` | Database | Coordinator, QA | Get work queue |
| `get_completed_assets_report` | Database | QA, Coordinator | Generate reports |
| `get_monthly_inspection_summary` | Database | QA, Coordinator | Get KPIs |
| `export_comprehensive_monthly_report` | Database | QA | Export audit trail |
| `filter_assets_to_prevent_duplicates` | Database | AssetDiscovery, Coordinator | Prevent duplicates |

### Tool Dependencies

```
Asset Discovery Flow:
search_safetyculture_assets → filter_assets_to_prevent_duplicates → store_asset_registry

Template Selection Flow:
search_safetyculture_templates → ai_match_templates_to_asset → store_template_library

Inspection Creation Flow:
register_asset_for_monthly_inspection → create_safetyculture_inspection → update_asset_inspection_status

Form Filling Flow:
generate_intelligent_inspection_data → update_safetyculture_inspection → mark_asset_inspection_completed

Quality Assurance Flow:
get_completed_assets_report → get_safetyculture_inspection_details → get_monthly_inspection_summary
```

### ADK Integration Points

- **Memory Service**: Tools use [`ToolContext.search_memory()`](https://github.com/google/adk-python/blob/main/src/google/adk/tools/tool_context.py) for semantic search
- **Function Tools**: All tools wrapped as [`FunctionTool`](https://github.com/google/adk-python/blob/main/src/google/adk/tools/function_tool.py) instances
- **Agent Tools**: Registered in [`agent.py`](safetyculture_agent/agent.py:164) for each sub-agent
- **Telemetry**: API tools instrumented with [`@trace_async`](safetyculture_agent/telemetry/decorators.py:1) decorator

---

## Configuration

### Environment Variables

Required for SafetyCulture API tools:
```bash
SAFETYCULTURE_API_TOKEN=your_api_token_here
SAFETYCULTURE_BASE_URL=https://api.safetyculture.io
```

Optional for enhanced security:
```bash
SAFETYCULTURE_SIGNING_KEY=your_hmac_signing_key  # Enable request signing
```

Database configuration (optional):
```bash
ASSET_TRACKER_DB_PATH=./data/asset_tracker.db  # SQLite database path
```

### Rate Limiting Configuration

Configured in [`SafetyCultureConfig`](safetyculture_agent/config/api_config.py:1):
```python
config = SafetyCultureConfig(
    requests_per_second=10,  # Base rate limit
    request_timeout=30,      # Timeout in seconds
    max_retries=3,           # Retry attempts
    retry_delay=1            # Base delay between retries
)
```

---

## Best Practices

### 1. Always Check Completion Status
Before creating inspections, use [`check_asset_completion_status()`](#42-check_asset_completion_status) to prevent duplicates.

### 2. Use Memory for Caching
Cache frequently accessed data (assets, templates) in memory to reduce API calls.

### 3. Leverage AI Tools
Use [`generate_intelligent_inspection_data()`](#36-generate_intelligent_inspection_data) with all available data sources for best results.

### 4. Track Workflow State
Use [`store_workflow_state()`](#25-store_workflow_state) for long-running batch processes to enable resumption.

### 5. Generate Reports Regularly
Use database reporting tools for compliance tracking and KPI monitoring.

### 6. Handle Errors Gracefully
Always wrap tool calls in try-except blocks to handle API failures and validation errors.

---

## Additional Resources

- **Architecture Overview**: [`AGENT_STARTUP_REPORT.md`](AGENT_STARTUP_REPORT.md:1)
- **Provider Abstraction**: [`PROVIDER_ABSTRACTION_ARCHITECTURE.md`](PROVIDER_ABSTRACTION_ARCHITECTURE.md:1)
- **Telemetry Guide**: [`safetyculture_agent/telemetry/README.md`](safetyculture_agent/telemetry/README.md:1)
- **ADK Documentation**: [github.com/google/adk-python](https://github.com/google/adk-python)
- **SafetyCulture API**: [developer.safetyculture.com](https://developer.safetyculture.com)

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-03  
**Maintained By**: SafetyCulture Agent Development Team