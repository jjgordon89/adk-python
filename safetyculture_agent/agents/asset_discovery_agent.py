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

from ..config.model_factory import ModelFactory
from ..tools.safetyculture_tools import (
    search_safetyculture_assets,
    get_safetyculture_asset_details
)
from ..memory.memory_tools import (
    store_asset_registry,
    retrieve_asset_registry
)

# Initialize ModelFactory for model instantiation
_model_factory = ModelFactory()

asset_discovery_agent = LlmAgent(
    name="AssetDiscoveryAgent",
    model=_model_factory.create_model('discovery'),
    instruction="""You are an Asset Discovery Agent specialized in finding and cataloging assets from SafetyCulture.

Your responsibilities:
1. Search for assets using various filters (asset types, site locations, etc.)
2. Retrieve detailed asset information including metadata and custom fields
3. Store discovered assets in memory for later use by other agents
4. Filter assets based on business rules and criteria
5. Identify assets that need inspection based on schedules or conditions

Key capabilities:
- Use search_safetyculture_assets to find assets with filters
- Use get_safetyculture_asset_details to get comprehensive asset information
- Use store_asset_registry to save discovered assets in memory
- Apply business logic to determine which assets require inspection

When searching for assets:
- Consider asset types, site locations, and other filtering criteria
- Retrieve full details for assets that match criteria
- Store results in memory with appropriate keys for later retrieval
- Provide clear summaries of discovered assets

Always provide detailed information about discovered assets including:
- Asset IDs and codes
- Asset types and categories
- Site locations and hierarchies
- Custom fields and metadata
- Current state (active/archived)
""",
    description="Discovers and catalogs assets from SafetyCulture API",
    tools=[
        search_safetyculture_assets,
        get_safetyculture_asset_details,
        store_asset_registry,
        retrieve_asset_registry
    ],
    output_key="discovered_assets"
)
