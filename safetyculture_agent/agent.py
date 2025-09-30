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

from datetime import datetime

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.load_memory_tool import load_memory_tool
from google.adk.tools.preload_memory_tool import preload_memory_tool

from .agents.asset_discovery_agent import asset_discovery_agent
from .agents.template_selection_agent import template_selection_agent
from .agents.inspection_creation_agent import inspection_creation_agent
from .agents.form_filling_agent import form_filling_agent
from .config.model_factory import ModelFactory
from .tools.safetyculture_tools import (
    search_safetyculture_assets,
    get_safetyculture_asset_details,
    search_safetyculture_templates,
    get_safetyculture_template_details,
    create_safetyculture_inspection,
    update_safetyculture_inspection,
    get_safetyculture_inspection_details,
    share_safetyculture_inspection,
    search_safetyculture_inspections
)
from .memory.memory_tools import (
    store_asset_registry,
    retrieve_asset_registry,
    store_template_library,
    retrieve_template_library,
    store_workflow_state,
    retrieve_workflow_state,
    store_inspection_history
)
from .ai.ai_tools import (
    ai_match_templates_to_asset,
    generate_dynamic_template_for_asset,
    analyze_asset_image_for_inspection,
    parse_maintenance_logs_for_insights,
    analyze_historical_inspection_patterns,
    generate_intelligent_inspection_data
)
from .database.database_tools import (
    initialize_asset_database,
    check_asset_completion_status,
    register_asset_for_monthly_inspection,
    update_asset_inspection_status,
    mark_asset_inspection_completed,
    get_pending_assets_for_inspection,
    get_completed_assets_report,
    get_monthly_inspection_summary,
    export_comprehensive_monthly_report,
    filter_assets_to_prevent_duplicates
)


def update_current_time(callback_context: CallbackContext):
  """Update current time in agent state."""
  callback_context.state['_time'] = datetime.now().isoformat()
  callback_context.state['_workflow_started'] = True


# Initialize ModelFactory for model instantiation
_model_factory = ModelFactory()

# Quality Assurance Agent for final review
qa_agent = LlmAgent(
    name="QualityAssuranceAgent",
    model=_model_factory.create_model('fast'),
    instruction="""You are a Quality Assurance Agent that reviews completed inspection workflows.

Your responsibilities:
1. Review completed inspections for data quality and completeness
2. Validate that business rules were applied correctly
3. Identify any issues or inconsistencies in the workflow
4. Generate summary reports of batch processing results
5. Recommend improvements for future workflows

Key capabilities:
- Review inspection creation and form filling results
- Validate data consistency across inspections
- Generate quality metrics and reports
- Identify patterns and optimization opportunities
- Store lessons learned for continuous improvement

When reviewing workflows:
- Check that all required fields were populated correctly
- Validate asset-to-template matching decisions
- Review error handling and recovery actions
- Assess overall workflow efficiency and success rates
- Document lessons learned for future improvements

Provide comprehensive quality reports including:
- Success/failure statistics
- Data quality metrics
- Error analysis and recommendations
- Performance insights
- Suggested optimizations
""",
    description="Reviews and validates completed inspection workflows",
    tools=[
        search_safetyculture_assets,
        get_safetyculture_asset_details,
        search_safetyculture_templates,
        get_safetyculture_template_details,
        create_safetyculture_inspection,
        update_safetyculture_inspection,
        get_safetyculture_inspection_details,
        share_safetyculture_inspection,
        search_safetyculture_inspections,
        store_asset_registry,
        retrieve_asset_registry,
        store_template_library,
        retrieve_template_library,
        store_workflow_state,
        retrieve_workflow_state,
        store_inspection_history
    ],
    output_key="quality_report"
)


# Main Coordinator Agent
coordinator_agent = LlmAgent(
    name="SafetyCultureCoordinator",
    model=_model_factory.create_model('coordinator'),
    before_agent_callback=update_current_time,
    instruction="""You are the SafetyCulture Inspection Coordinator, orchestrating automated inspection workflows.

Current time: {_time}
Workflow status: {_workflow_started}

Your role is to coordinate a multi-agent system that:
1. Discovers assets from SafetyCulture
2. Selects appropriate inspection templates
3. Creates inspections with pre-filled data
4. Fills out inspection forms automatically
5. Reviews and validates the completed work

Available sub-agents:
- AssetDiscoveryAgent: Finds and catalogs assets
- TemplateSelectionAgent: Matches templates to assets
- InspectionCreationAgent: Creates new inspections
- FormFillingAgent: Populates inspection forms
- QualityAssuranceAgent: Reviews completed work

Workflow coordination:
1. Start by understanding the user's requirements (asset types, sites, batch size)
2. Delegate asset discovery to find relevant assets
3. Have templates selected and matched to discovered assets
4. Create inspections in batches with proper pre-filling
5. Fill out forms using business rules and asset data
6. Review and validate the completed inspections

You have access to all SafetyCulture API tools and memory management tools for direct coordination when needed.

Always provide clear status updates and coordinate the workflow efficiently to complete batch inspection processing.
""",
    description="Coordinates the entire SafetyCulture inspection automation workflow",
    sub_agents=[
        asset_discovery_agent,
        template_selection_agent,
        inspection_creation_agent,
        form_filling_agent,
        qa_agent
    ],
    tools=[
        search_safetyculture_assets,
        get_safetyculture_asset_details,
        search_safetyculture_templates,
        get_safetyculture_template_details,
        create_safetyculture_inspection,
        update_safetyculture_inspection,
        get_safetyculture_inspection_details,
        share_safetyculture_inspection,
        search_safetyculture_inspections,
        store_asset_registry,
        retrieve_asset_registry,
        store_template_library,
        retrieve_template_library,
        store_workflow_state,
        retrieve_workflow_state,
        store_inspection_history,
        load_memory_tool,
        preload_memory_tool,
        ai_match_templates_to_asset,
        generate_dynamic_template_for_asset,
        analyze_asset_image_for_inspection,
        parse_maintenance_logs_for_insights,
        analyze_historical_inspection_patterns,
        generate_intelligent_inspection_data,
        initialize_asset_database,
        check_asset_completion_status,
        register_asset_for_monthly_inspection,
        update_asset_inspection_status,
        mark_asset_inspection_completed,
        get_pending_assets_for_inspection,
        get_completed_assets_report,
        get_monthly_inspection_summary,
        export_comprehensive_monthly_report,
        filter_assets_to_prevent_duplicates
    ]
)


# For ADK compatibility, the root agent must be named `root_agent`
root_agent = coordinator_agent
