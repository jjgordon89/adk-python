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

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class InspectionRule:
  """Business rule for inspection automation."""
  
  field_name: str
  field_type: str
  auto_fill_value: Optional[Any] = None
  condition: Optional[str] = None
  priority: int = 0
  
  def applies_to_asset(self, asset_data: Dict[str, Any]) -> bool:
    """Check if this rule applies to the given asset."""
    if not self.condition:
      return True
    
    # Simple condition evaluation (can be extended)
    # Format: "asset.type == 'Car'" or "asset.fields.Brand == 'Toyota'"
    try:
      # This is a simplified implementation
      # In production, you'd want a more robust expression evaluator
      if "asset.type ==" in self.condition:
        expected_type = self.condition.split("==")[1].strip().strip("'\"")
        return asset_data.get("type", {}).get("name") == expected_type
      
      if "asset.fields." in self.condition:
        field_path = self.condition.split("==")[0].strip()
        expected_value = self.condition.split("==")[1].strip().strip("'\"")
        field_name = field_path.split(".")[-1]
        
        for field in asset_data.get("fields", []):
          if field.get("name") == field_name:
            return field.get("string_value") == expected_value
      
      return True
    except Exception:
      return False


@dataclass
class BatchProcessingRules:
  """Rules for batch processing inspections."""
  
  # Asset filtering
  asset_types: Optional[List[str]] = None
  site_filters: Optional[List[str]] = None
  exclude_recently_inspected: bool = True
  recent_inspection_days: int = 30
  
  # Template selection
  template_priority: Optional[Dict[str, int]] = None
  default_template: Optional[str] = None
  
  # Inspection scheduling
  max_inspections_per_batch: int = 100
  schedule_future_inspections: bool = False
  inspection_due_days: int = 7
  
  def __post_init__(self):
    """Initialize default values."""
    if self.asset_types is None:
      self.asset_types = []
    if self.site_filters is None:
      self.site_filters = []
    if self.template_priority is None:
      self.template_priority = {}


# Default business rules
DEFAULT_INSPECTION_RULES = [
    InspectionRule(
        field_name="Asset ID",
        field_type="textsingle",
        auto_fill_value="asset.code",
        priority=1
    ),
    InspectionRule(
        field_name="Asset Type",
        field_type="textsingle", 
        auto_fill_value="asset.type.name",
        priority=1
    ),
    InspectionRule(
        field_name="Site Location",
        field_type="textsingle",
        auto_fill_value="asset.site.name",
        priority=1
    ),
    InspectionRule(
        field_name="Inspector Name",
        field_type="textsingle",
        auto_fill_value="current_user.name",
        priority=2
    ),
    InspectionRule(
        field_name="Inspection Date",
        field_type="datetime",
        auto_fill_value="current_datetime",
        priority=1
    )
]

DEFAULT_BATCH_RULES = BatchProcessingRules(
    asset_types=["Car", "Equipment", "Machinery"],
    exclude_recently_inspected=True,
    recent_inspection_days=30,
    max_inspections_per_batch=50
)
