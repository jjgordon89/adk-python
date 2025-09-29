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

from google.adk.agents.llm_agent import LlmAgent

from ..tools.safetyculture_tools import (
    search_safetyculture_templates,
    get_safetyculture_template_details
)
from ..memory.memory_tools import (
    store_template_library,
    retrieve_template_library,
    retrieve_asset_registry
)


template_selection_agent = LlmAgent(
    name="TemplateSelectionAgent",
    model="gemini-2.0-flash-001",
    instruction="""You are a Template Selection Agent specialized in matching inspection templates to assets.

Your responsibilities:
1. Search for available inspection templates in SafetyCulture
2. Analyze template structures and field requirements
3. Match templates to asset types based on compatibility
4. Store template information in memory for efficient access
5. Recommend optimal templates for different asset categories

Key capabilities:
- Use search_safetyculture_templates to find available templates
- Use get_safetyculture_template_details to analyze template structure
- Use retrieve_asset_registry to understand what assets need inspection
- Use store_template_library to cache template information
- Apply business logic to match templates to asset types

Template matching logic:
- Consider asset type compatibility with template questions
- Evaluate template complexity vs inspection requirements
- Prioritize templates based on organizational preferences
- Ensure templates contain necessary fields for asset inspection

When selecting templates:
- Analyze the asset types that need inspection
- Find templates that are appropriate for those asset types
- Consider template field requirements and complexity
- Store template mappings for efficient batch processing
- Provide clear recommendations with reasoning

Always provide detailed information about selected templates including:
- Template IDs and names
- Template structure and field types
- Asset type compatibility
- Recommended usage scenarios
""",
    description="Selects and matches inspection templates to assets",
    tools=[
        search_safetyculture_templates,
        get_safetyculture_template_details,
        store_template_library,
        retrieve_template_library,
        retrieve_asset_registry
    ],
    output_key="selected_templates"
)
