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

# Business rule constants
DEFAULT_PRIORITY = 0  # Default priority for inspection rules
HIGH_PRIORITY = 1  # High priority for critical fields
MEDIUM_PRIORITY = 2  # Medium priority for standard fields
DEFAULT_RECENT_INSPECTION_DAYS = 30  # Days to consider recent inspection
DEFAULT_MAX_INSPECTIONS_PER_BATCH = 100  # Maximum inspections per batch
DEFAULT_INSPECTION_DUE_DAYS = 7  # Days until inspection is due
BATCH_SIZE_LIMIT = 50  # Batch processing size limit


@dataclass
class InspectionRule:
  """Business rule for inspection automation."""
  
  field_name: str
  field_type: str
  auto_fill_value: Optional[Any] = None
  condition: Optional[str] = None
  priority: int = DEFAULT_PRIORITY
  
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
  recent_inspection_days: int = DEFAULT_RECENT_INSPECTION_DAYS
  
  # Template selection
  template_priority: Optional[Dict[str, int]] = None
  default_template: Optional[str] = None
  
  # Inspection scheduling
  max_inspections_per_batch: int = DEFAULT_MAX_INSPECTIONS_PER_BATCH
  schedule_future_inspections: bool = False
  inspection_due_days: int = DEFAULT_INSPECTION_DUE_DAYS
  
  def __post_init__(self) -> None:
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
        priority=HIGH_PRIORITY
    ),
    InspectionRule(
        field_name="Asset Type",
        field_type="textsingle",
        auto_fill_value="asset.type.name",
        priority=HIGH_PRIORITY
    ),
    InspectionRule(
        field_name="Site Location",
        field_type="textsingle",
        auto_fill_value="asset.site.name",
        priority=HIGH_PRIORITY
    ),
    InspectionRule(
        field_name="Inspector Name",
        field_type="textsingle",
        auto_fill_value="current_user.name",
        priority=MEDIUM_PRIORITY
    ),
    InspectionRule(
        field_name="Inspection Date",
        field_type="datetime",
        auto_fill_value="current_datetime",
        priority=HIGH_PRIORITY
    )
]

DEFAULT_BATCH_RULES = BatchProcessingRules(
    asset_types=["Car", "Equipment", "Machinery"],
    exclude_recently_inspected=True,
    recent_inspection_days=DEFAULT_RECENT_INSPECTION_DAYS,
    max_inspections_per_batch=BATCH_SIZE_LIMIT
)
