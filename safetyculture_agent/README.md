# SafetyCulture Agent System

A multi-agent system built with Google ADK for automating SafetyCulture inspection workflows. This system can discover assets, select appropriate templates, create inspections, and automatically fill out inspection forms in batches.

## Architecture

The system consists of several specialized agents working together:

### Core Agents

1. **SafetyCultureCoordinator** - Main orchestrator agent
2. **AssetDiscoveryAgent** - Discovers and catalogs assets from SafetyCulture
3. **TemplateSelectionAgent** - Matches inspection templates to assets
4. **InspectionCreationAgent** - Creates new inspections from templates
5. **FormFillingAgent** - Automatically fills inspection forms with asset data
6. **QualityAssuranceAgent** - Reviews and validates completed workflows

### Key Components

- **API Client** (`tools/safetyculture_api_client.py`) - Handles SafetyCulture API interactions
- **Tools** (`tools/safetyculture_tools.py`) - ADK function tools for SafetyCulture operations
- **Memory Management** (`memory/memory_tools.py`) - Persistent data storage and retrieval
- **Configuration** (`config/`) - API settings and business rules

## Features

- **Asset Discovery**: Search and catalog assets by type, location, and other criteria
- **Template Matching**: Intelligent matching of inspection templates to asset types
- **Batch Processing**: Create and fill multiple inspections efficiently
- **Memory Management**: Persistent storage of assets, templates, and workflow state
- **Business Rules**: Configurable rules for automatic form filling
- **Quality Assurance**: Automated validation and reporting

## Configuration

### API Configuration

Set your SafetyCulture API credentials in `config/api_config.py`:

```python
SAFETYCULTURE_CONFIG = SafetyCultureConfig(
    api_token="your_api_token_here",
    base_url="https://api.safetyculture.io",
    # ... other settings
)
```

### Business Rules

Configure automatic form filling rules in `config/business_rules.py`:

```python
FIELD_MAPPING_RULES = {
    "asset_id_field": "asset_id",
    "asset_type_field": "asset_type",
    "site_location_field": "site_name",
    # ... other mappings
}
```

## Usage Examples

### Basic Workflow

```python
# The coordinator agent handles the entire workflow
# Just provide your requirements:

"Create inspections for all equipment assets at the Main Site using the Equipment Inspection template, and fill out the forms automatically."
```

### Specific Asset Types

```python
"Find all vehicles and machinery assets, create safety inspections for them, and populate the forms with asset information."
```

### Batch Processing

```python
"Process 50 assets at a time, creating inspections and filling forms for all assets that haven't been inspected in the last 30 days."
```

## Workflow Steps

1. **Asset Discovery**: The system searches SafetyCulture for assets matching your criteria
2. **Template Selection**: Appropriate inspection templates are identified and matched to asset types
3. **Inspection Creation**: New inspections are created from templates with pre-filled header information
4. **Form Filling**: Business rules are applied to automatically populate inspection fields
5. **Quality Review**: The completed work is validated and a quality report is generated

## API Integration

The system integrates with SafetyCulture's REST API to:

- Search and retrieve assets
- Find and analyze inspection templates
- Create new inspections
- Update inspection responses
- Share inspections with users
- Manage sites and locations

## Memory and State Management

The system uses ADK's memory capabilities to:

- Store discovered assets for reuse
- Cache template information
- Track workflow progress
- Maintain inspection history
- Store business rule mappings

## Error Handling

The system includes comprehensive error handling:

- API rate limiting and retry logic
- Validation of data before form submission
- Graceful handling of missing or invalid data
- Detailed error reporting and logging

## Extensibility

The modular design allows for easy extension:

- Add new agents for specialized tasks
- Extend business rules for custom field mappings
- Add new API endpoints and operations
- Integrate with other systems and data sources

## Requirements

- Google ADK (Agent Development Kit)
- Python 3.8+
- SafetyCulture API access token
- Required Python packages: `aiohttp`, `asyncio`

## Getting Started

1. Configure your SafetyCulture API credentials
2. Set up business rules for your organization
3. Run the agent system through ADK
4. Provide natural language instructions for your inspection workflow

The system will handle the complex orchestration of discovering assets, selecting templates, creating inspections, and filling forms automatically.
