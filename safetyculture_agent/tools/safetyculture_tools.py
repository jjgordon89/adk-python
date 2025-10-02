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

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.adk.tools.function_tool import FunctionTool

from .safetyculture_api_client import SafetyCultureAPIClient
from ..config.api_config import DEFAULT_CONFIG
from ..config.field_mapping_loader import get_field_loader
from ..exceptions import (
  SafetyCultureAPIError,
  SafetyCultureAuthError,
  SafetyCultureValidationError,
)
from ..utils.secure_header_manager import SecureHeaderManager

logger = logging.getLogger(__name__)

# HTTP/API related constants
DEFAULT_ASSET_SEARCH_LIMIT = 50  # Default asset search limit
DEFAULT_INSPECTION_SEARCH_LIMIT = 100  # Default inspection search limit

# Shared header manager for error sanitization
_header_manager = SecureHeaderManager()


async def search_safetyculture_assets(
    asset_types: Optional[List[str]] = None,
    site_names: Optional[List[str]] = None,
    limit: int = DEFAULT_ASSET_SEARCH_LIMIT
) -> str:
  """
  Search for assets in SafetyCulture.
  
  Args:
    asset_types: List of asset type names to filter by (e.g., ['Car', 'Equipment'])
    site_names: List of site names to filter by
    limit: Maximum number of assets to return (default: 50)
  
  Returns:
    JSON string containing asset information including IDs, types, and metadata
  """
  try:
    async with SafetyCultureAPIClient(DEFAULT_CONFIG) as client:
      # First get sites if site names provided
      site_ids = None
      if site_names:
        site_ids = []
        for site_name in site_names:
          sites_response = await client.search_sites(name_filter=site_name)
          for site in sites_response.get('folders', []):
            if site.get('folder', {}).get('name') == site_name:
              site_ids.append(site['folder']['id'])
      
      # Search for assets
      response = await client.search_assets(
          asset_types=asset_types,
          site_ids=site_ids,
          limit=limit
      )
      
      return json.dumps(response, indent=2)
  
  except SafetyCultureAPIError as e:
    # Sanitize error message before returning
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Asset search failed: {safe_error}")
    raise SafetyCultureAPIError(f"Asset search failed: {safe_error}") from e

  except SafetyCultureValidationError as e:
    # Validation errors are safe to pass through
    logger.warning(f"Invalid search parameters: {e}")
    raise

  except Exception as e:
    # Catch-all with sanitization
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Unexpected error in asset search: {safe_error}")
    raise SafetyCultureAPIError(
      f"Unexpected error in asset search: {safe_error}"
    ) from e


async def get_safetyculture_asset_details(asset_id: str) -> str:
  """
  Get detailed information about a specific asset.
  
  Args:
    asset_id: The unique ID of the asset
  
  Returns:
    JSON string containing detailed asset information
  """
  try:
    async with SafetyCultureAPIClient(DEFAULT_CONFIG) as client:
      response = await client.get_asset(asset_id)
      return json.dumps(response, indent=2)
  
  except SafetyCultureAPIError as e:
    # Sanitize error message before returning
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Asset details retrieval failed: {safe_error}")
    raise SafetyCultureAPIError(
      f"Asset details retrieval failed: {safe_error}"
    ) from e

  except SafetyCultureValidationError as e:
    # Validation errors are safe to pass through
    logger.warning(f"Invalid asset ID: {e}")
    raise

  except Exception as e:
    # Catch-all with sanitization
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Unexpected error getting asset details: {safe_error}")
    raise SafetyCultureAPIError(
      f"Unexpected error getting asset details: {safe_error}"
    ) from e


async def search_safetyculture_templates(
    template_name_filter: Optional[str] = None,
    include_archived: bool = False
) -> str:
  """
  Search for inspection templates in SafetyCulture.
  
  Args:
    template_name_filter: Optional filter to search for templates by name
    include_archived: Whether to include archived templates (default: False)
  
  Returns:
    JSON string containing template information
  """
  try:
    async with SafetyCultureAPIClient(DEFAULT_CONFIG) as client:
      response = await client.search_templates(
          fields=['template_id', 'name', 'modified_at', 'created_at'],
          archived=include_archived
      )
      
      # Filter by name if provided
      if template_name_filter:
        filtered_templates = []
        for template in response.get('templates', []):
          if template_name_filter.lower() in template.get('name', '').lower():
            filtered_templates.append(template)
        response['templates'] = filtered_templates
        response['count'] = len(filtered_templates)
      
      return json.dumps(response, indent=2)
  
  except SafetyCultureAPIError as e:
    # Sanitize error message before returning
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Template search failed: {safe_error}")
    raise SafetyCultureAPIError(
      f"Template search failed: {safe_error}"
    ) from e

  except SafetyCultureValidationError as e:
    # Validation errors are safe to pass through
    logger.warning(f"Invalid template search parameters: {e}")
    raise

  except Exception as e:
    # Catch-all with sanitization
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Unexpected error in template search: {safe_error}")
    raise SafetyCultureAPIError(
      f"Unexpected error in template search: {safe_error}"
    ) from e


async def get_safetyculture_template_details(template_id: str) -> str:
  """
  Get detailed information about a specific inspection template.
  
  Args:
    template_id: The unique ID of the template
  
  Returns:
    JSON string containing detailed template information including structure
  """
  try:
    async with SafetyCultureAPIClient(DEFAULT_CONFIG) as client:
      response = await client.get_template(template_id)
      return json.dumps(response, indent=2)
  
  except SafetyCultureAPIError as e:
    # Sanitize error message before returning
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Template details retrieval failed: {safe_error}")
    raise SafetyCultureAPIError(
      f"Template details retrieval failed: {safe_error}"
    ) from e

  except SafetyCultureValidationError as e:
    # Validation errors are safe to pass through
    logger.warning(f"Invalid template ID: {e}")
    raise

  except Exception as e:
    # Catch-all with sanitization
    safe_error = _header_manager.sanitize_error(e)
    logger.error(
      f"Unexpected error getting template details: {safe_error}"
    )
    raise SafetyCultureAPIError(
      f"Unexpected error getting template details: {safe_error}"
    ) from e


async def create_safetyculture_inspection(
    template_id: str,
    inspection_title: Optional[str] = None,
    conducted_by: Optional[str] = None,
    site_location: Optional[str] = None,
    asset_id: Optional[str] = None
) -> str:
  """
  Create a new inspection from a template.
  
  Args:
    template_id: The ID of the template to use
    inspection_title: Optional title for the inspection
    conducted_by: Optional name of the person conducting the inspection
    site_location: Optional site/location name
    asset_id: Optional asset ID being inspected
  
  Returns:
    JSON string containing the created inspection details including audit_id
  """
  try:
    async with SafetyCultureAPIClient(DEFAULT_CONFIG) as client:
      # Build header items for pre-filling
      header_items = []
      
      # Load field mappings
      field_loader = get_field_loader()
      
      if inspection_title:
        header_items.append({
            "item_id": field_loader.get_field_id('standard_title'),
            "label": "Inspection Title",
            "type": "textsingle",
            "responses": {
                "text": inspection_title
            }
        })
      
      if conducted_by:
        header_items.append({
            "item_id": field_loader.get_field_id('inspector_name'),
            "label": "Conducted By",
            "type": "textsingle",
            "responses": {
                "text": conducted_by
            }
        })
      
      response = await client.create_inspection(
          template_id=template_id,
          header_items=header_items if header_items else None
      )
      
      return json.dumps(response, indent=2)
  
  except SafetyCultureAPIError as e:
    # Sanitize error message before returning
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Inspection creation failed: {safe_error}")
    raise SafetyCultureAPIError(
      f"Inspection creation failed: {safe_error}"
    ) from e

  except SafetyCultureValidationError as e:
    # Validation errors are safe to pass through
    logger.warning(f"Invalid inspection creation parameters: {e}")
    raise

  except Exception as e:
    # Catch-all with sanitization
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Unexpected error creating inspection: {safe_error}")
    raise SafetyCultureAPIError(
      f"Unexpected error creating inspection: {safe_error}"
    ) from e


async def update_safetyculture_inspection(
    audit_id: str,
    field_updates: List[Dict[str, Any]]
) -> str:
  """
  Update inspection responses with field values.
  
  Args:
    audit_id: The ID of the inspection to update
    field_updates: List of field updates, each containing:
      - item_id: The field ID to update
      - field_type: Type of field (textsingle, datetime, etc.)
      - value: The value to set
  
  Returns:
    JSON string containing the update response
  """
  try:
    async with SafetyCultureAPIClient(DEFAULT_CONFIG) as client:
      # Convert field updates to SafetyCulture format
      items = []
      for update in field_updates:
        item = {
            "item_id": update["item_id"],
            "type": update["field_type"]
        }
        
        # Set response based on field type
        if update["field_type"] == "textsingle":
          item["responses"] = {"text": update["value"]}
        elif update["field_type"] == "datetime":
          item["responses"] = {"datetime": update["value"]}
        elif update["field_type"] == "checkbox":
          item["responses"] = {"value": str(update["value"])}
        else:
          item["responses"] = {"text": str(update["value"])}
        
        items.append(item)
      
      response = await client.update_inspection(audit_id, items)
      return json.dumps(response, indent=2)
  
  except SafetyCultureAPIError as e:
    # Sanitize error message before returning
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Inspection update failed: {safe_error}")
    raise SafetyCultureAPIError(
      f"Inspection update failed: {safe_error}"
    ) from e

  except SafetyCultureValidationError as e:
    # Validation errors are safe to pass through
    logger.warning(f"Invalid inspection update parameters: {e}")
    raise

  except Exception as e:
    # Catch-all with sanitization
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Unexpected error updating inspection: {safe_error}")
    raise SafetyCultureAPIError(
      f"Unexpected error updating inspection: {safe_error}"
    ) from e


async def get_safetyculture_inspection_details(audit_id: str) -> str:
  """
  Get detailed information about a specific inspection.
  
  Args:
    audit_id: The unique ID of the inspection
  
  Returns:
    JSON string containing detailed inspection information
  """
  try:
    async with SafetyCultureAPIClient(DEFAULT_CONFIG) as client:
      response = await client.get_inspection(audit_id)
      return json.dumps(response, indent=2)
  
  except SafetyCultureAPIError as e:
    # Sanitize error message before returning
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Inspection details retrieval failed: {safe_error}")
    raise SafetyCultureAPIError(
      f"Inspection details retrieval failed: {safe_error}"
    ) from e

  except SafetyCultureValidationError as e:
    # Validation errors are safe to pass through
    logger.warning(f"Invalid inspection ID: {e}")
    raise

  except Exception as e:
    # Catch-all with sanitization
    safe_error = _header_manager.sanitize_error(e)
    logger.error(
      f"Unexpected error getting inspection details: {safe_error}"
    )
    raise SafetyCultureAPIError(
      f"Unexpected error getting inspection details: {safe_error}"
    ) from e


async def share_safetyculture_inspection(
    audit_id: str,
    user_emails: List[str],
    permission: str = "edit"
) -> str:
  """
  Share an inspection with users.
  
  Args:
    audit_id: The ID of the inspection to share
    user_emails: List of user email addresses to share with
    permission: Permission level ('view', 'edit', or 'delete')
  
  Returns:
    JSON string containing the sharing response
  """
  try:
    async with SafetyCultureAPIClient(DEFAULT_CONFIG) as client:
      # First get user IDs from emails
      shares = []
      for email in user_emails:
        users_response = await client.search_users(email=email)
        users = users_response.get('users', [])
        if users:
          shares.append({
              "id": users[0]["id"],
              "permission": permission
          })
      
      if not shares:
        return json.dumps({"error": "No valid users found for the provided emails"})
      
      response = await client.share_inspection(audit_id, shares)
      return json.dumps(response, indent=2)
  
  except SafetyCultureAPIError as e:
    # Sanitize error message before returning
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Inspection sharing failed: {safe_error}")
    raise SafetyCultureAPIError(
      f"Inspection sharing failed: {safe_error}"
    ) from e

  except SafetyCultureValidationError as e:
    # Validation errors are safe to pass through
    logger.warning(f"Invalid inspection sharing parameters: {e}")
    raise

  except Exception as e:
    # Catch-all with sanitization
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Unexpected error sharing inspection: {safe_error}")
    raise SafetyCultureAPIError(
      f"Unexpected error sharing inspection: {safe_error}"
    ) from e


async def search_safetyculture_inspections(
    template_id: Optional[str] = None,
    modified_after: Optional[str] = None,
    limit: int = DEFAULT_INSPECTION_SEARCH_LIMIT
) -> str:
  """
  Search for existing inspections.
  
  Args:
    template_id: Optional template ID to filter by
    modified_after: Optional ISO datetime to filter inspections modified after this date
    limit: Maximum number of inspections to return
  
  Returns:
    JSON string containing inspection search results
  """
  try:
    async with SafetyCultureAPIClient(DEFAULT_CONFIG) as client:
      response = await client.search_inspections(
          fields=['audit_id', 'modified_at', 'template_id', 'created_at'],
          template_id=template_id,
          modified_after=modified_after,
          limit=limit
      )
      
      return json.dumps(response, indent=2)
  
  except SafetyCultureAPIError as e:
    # Sanitize error message before returning
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Inspection search failed: {safe_error}")
    raise SafetyCultureAPIError(
      f"Inspection search failed: {safe_error}"
    ) from e

  except SafetyCultureValidationError as e:
    # Validation errors are safe to pass through
    logger.warning(f"Invalid inspection search parameters: {e}")
    raise

  except Exception as e:
    # Catch-all with sanitization
    safe_error = _header_manager.sanitize_error(e)
    logger.error(f"Unexpected error in inspection search: {safe_error}")
    raise SafetyCultureAPIError(
      f"Unexpected error in inspection search: {safe_error}"
    ) from e


# Create FunctionTool instances
SAFETYCULTURE_TOOLS = [
    FunctionTool(search_safetyculture_assets),
    FunctionTool(get_safetyculture_asset_details),
    FunctionTool(search_safetyculture_templates),
    FunctionTool(get_safetyculture_template_details),
    FunctionTool(create_safetyculture_inspection),
    FunctionTool(update_safetyculture_inspection),
    FunctionTool(get_safetyculture_inspection_details),
    FunctionTool(share_safetyculture_inspection),
    FunctionTool(search_safetyculture_inspections)
]
