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

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class TemplateGenerator:
  """Generates dynamic inspection templates based on asset characteristics.
  
  Creates customized inspection templates by analyzing asset type,
  criticality, compliance requirements, and other characteristics.
  Templates are dynamically constructed with appropriate fields and
  validation rules for each asset category.
  
  Attributes:
      None
  """
  
  def __init__(self):
    """Initialize template generator."""
    logger.info("TemplateGenerator initialized")
  
  def create_dynamic_template(
      self,
      asset_id: str,
      asset_type: str,
      asset_name: str,
      criticality: str,
      compliance_requirements: List[str]
  ) -> Dict[str, Any]:
    """Create a dynamic template based on asset characteristics.
    
    Args:
        asset_id: Unique identifier for the asset
        asset_type: Type/category of the asset
        asset_name: Display name of the asset
        criticality: Criticality level (high, medium, low)
        compliance_requirements: List of compliance standards
    
    Returns:
        Dictionary containing complete template structure
    """
    items = self._get_base_items()
    items.extend(self._get_asset_type_items(asset_type))
    items.extend(self._get_criticality_items(criticality))
    items.extend(self._get_compliance_items(compliance_requirements))
    items.extend(self._get_final_items())
    
    template_id = f"dynamic_{asset_id}_{asset_type.lower().replace(' ', '_')}"
    
    return {
      "template_id": template_id,
      "name": f"Dynamic {asset_type} Inspection - {asset_name}",
      "description": (
          f"Dynamically generated inspection template for {asset_type} "
          f"based on asset characteristics and compliance requirements"
      ),
      "created_for_asset": asset_id,
      "auto_generated": True,
      "items": items
    }
  
  def create_fallback_template(
      self,
      asset_id: str,
      asset_type: str
  ) -> Dict[str, Any]:
    """Create a basic fallback template.
    
    Args:
        asset_id: Unique identifier for the asset
        asset_type: Type/category of the asset
    
    Returns:
        Dictionary containing basic template structure
    """
    return {
      "template_id": f"fallback_{asset_id}",
      "name": f"Basic {asset_type} Inspection",
      "description": f"Basic inspection template for {asset_type}",
      "created_for_asset": asset_id,
      "auto_generated": True,
      "items": [
        {
          "item_id": "asset_id",
          "label": "Asset ID",
          "type": "textsingle",
          "required": True,
          "description": "Unique asset identifier"
        },
        {
          "item_id": "inspection_date",
          "label": "Inspection Date",
          "type": "datetime",
          "required": True,
          "description": "Date of inspection"
        },
        {
          "item_id": "inspector_name",
          "label": "Inspector Name",
          "type": "textsingle",
          "required": True,
          "description": "Name of person conducting inspection"
        },
        {
          "item_id": "visual_condition",
          "label": "Visual Condition",
          "type": "textsingle",
          "required": True,
          "description": "Overall visual condition of asset"
        },
        {
          "item_id": "safety_check",
          "label": "Safety Check Passed",
          "type": "checkbox",
          "required": True,
          "description": "Confirm safety requirements are met"
        },
        {
          "item_id": "recommendations",
          "label": "Maintenance Recommendations",
          "type": "textsingle",
          "required": False,
          "description": "Any maintenance recommendations"
        }
      ]
    }
  
  def _get_base_items(self) -> List[Dict[str, Any]]:
    """Get base template items common to all templates."""
    return [
      {
        "item_id": "asset_id",
        "label": "Asset ID",
        "type": "textsingle",
        "required": True,
        "description": "Unique asset identifier"
      },
      {
        "item_id": "inspection_date",
        "label": "Inspection Date",
        "type": "datetime",
        "required": True,
        "description": "Date of inspection"
      },
      {
        "item_id": "inspector_name",
        "label": "Inspector Name",
        "type": "textsingle",
        "required": True,
        "description": "Name of person conducting inspection"
      }
    ]
  
  def _get_asset_type_items(self, asset_type: str) -> List[Dict[str, Any]]:
    """Get asset-type specific template items.
    
    Args:
        asset_type: Type/category of the asset
    
    Returns:
        List of template items specific to the asset type
    """
    items = []
    asset_type_lower = asset_type.lower()
    
    if 'electrical' in asset_type_lower:
      items.extend([
        {
          "item_id": "voltage_check",
          "label": "Voltage Reading",
          "type": "textsingle",
          "required": True,
          "description": "Voltage measurement"
        },
        {
          "item_id": "insulation_test",
          "label": "Insulation Test Passed",
          "type": "checkbox",
          "required": True,
          "description": "Insulation resistance test"
        }
      ])
    
    if 'pressure' in asset_type_lower or 'vessel' in asset_type_lower:
      items.extend([
        {
          "item_id": "pressure_test",
          "label": "Pressure Test Result",
          "type": "textsingle",
          "required": True,
          "description": "Pressure test measurement"
        },
        {
          "item_id": "leak_check",
          "label": "Leak Check Passed",
          "type": "checkbox",
          "required": True,
          "description": "Visual leak inspection"
        }
      ])
    
    if 'mechanical' in asset_type_lower or 'pump' in asset_type_lower:
      items.extend([
        {
          "item_id": "vibration_check",
          "label": "Vibration Analysis",
          "type": "textsingle",
          "required": True,
          "description": "Vibration measurement and analysis"
        },
        {
          "item_id": "lubrication_check",
          "label": "Lubrication Status",
          "type": "textsingle",
          "required": True,
          "description": "Lubrication level and condition"
        }
      ])
    
    return items
  
  def _get_criticality_items(self, criticality: str) -> List[Dict[str, Any]]:
    """Get criticality-based template items.
    
    Args:
        criticality: Criticality level of the asset
    
    Returns:
        List of template items for critical assets
    """
    items = []
    
    if criticality.lower() in ['high', 'critical']:
      items.extend([
        {
          "item_id": "safety_shutdown_test",
          "label": "Safety Shutdown Test",
          "type": "checkbox",
          "required": True,
          "description": "Emergency shutdown system test"
        },
        {
          "item_id": "backup_systems_check",
          "label": "Backup Systems Check",
          "type": "checkbox",
          "required": True,
          "description": "Backup and redundant systems verification"
        }
      ])
    
    return items
  
  def _get_compliance_items(
      self,
      compliance_requirements: List[str]
  ) -> List[Dict[str, Any]]:
    """Get compliance-based template items.
    
    Args:
        compliance_requirements: List of compliance standards
    
    Returns:
        List of compliance-related template items
    """
    items = []
    
    for req in compliance_requirements:
      if 'osha' in req.lower():
        items.append({
          "item_id": "osha_compliance",
          "label": "OSHA Compliance Verified",
          "type": "checkbox",
          "required": True,
          "description": "OSHA safety standards compliance check"
        })
      if 'api' in req.lower():
        items.append({
          "item_id": "api_standards",
          "label": "API Standards Compliance",
          "type": "checkbox",
          "required": True,
          "description": "API industry standards compliance"
        })
    
    return items
  
  def _get_final_items(self) -> List[Dict[str, Any]]:
    """Get final template items common to all templates."""
    return [
      {
        "item_id": "overall_condition",
        "label": "Overall Asset Condition",
        "type": "textsingle",
        "required": True,
        "description": "Overall assessment of asset condition"
      },
      {
        "item_id": "recommendations",
        "label": "Maintenance Recommendations",
        "type": "textsingle",
        "required": False,
        "description": "Recommended maintenance actions"
      },
      {
        "item_id": "next_inspection_date",
        "label": "Next Inspection Date",
        "type": "datetime",
        "required": False,
        "description": "Recommended date for next inspection"
      }
    ]