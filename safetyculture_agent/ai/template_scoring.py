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


class TemplateScorer:
  """Calculates confidence scores for template matching.
  
  Implements scoring algorithms that consider compliance requirements,
  keyword similarity, and asset characteristics to determine the best
  template match for each asset. Applies compliance boosts and generates
  human-readable match reasons.
  
  Attributes:
      compliance_rules: Dictionary mapping asset types to compliance standards
  """
  
  def __init__(self):
    """Initialize template scorer with compliance rules."""
    self.compliance_rules = self._load_compliance_rules()
    logger.info("TemplateScorer initialized")
  
  def _load_compliance_rules(self) -> Dict[str, List[str]]:
    """Load compliance rules for different asset types and industries.
    
    Returns:
        Dictionary mapping asset type keys to compliance standard lists
    """
    return {
      "pressure_vessel": [
        "ASME Boiler and Pressure Vessel Code",
        "API 510 Pressure Vessel Inspection Code",
        "OSHA 29 CFR 1910.106"
      ],
      "electrical_equipment": [
        "NFPA 70E Standard for Electrical Safety",
        "IEEE C57.12.00 Standard for Transformers",
        "OSHA 29 CFR 1910.303"
      ],
      "lifting_equipment": [
        "ASME B30.2 Overhead and Gantry Cranes",
        "OSHA 29 CFR 1926.1400 Cranes and Derricks",
        "API RP 2D Operation and Maintenance"
      ],
      "fire_safety": [
        "NFPA 25 Standard for Fire Protection Systems",
        "NFPA 10 Standard for Portable Fire Extinguishers",
        "OSHA 29 CFR 1910.157"
      ],
      "hvac_systems": [
        "ASHRAE Standard 62.1 Ventilation",
        "NFPA 90A Air Conditioning Systems",
        "EPA Clean Air Act Requirements"
      ]
    }
  
  def calculate_compliance_boost(
      self,
      asset_compliance_requirements: List[str],
      template: Dict[str, Any]
  ) -> float:
    """Calculate compliance boost based on regulatory requirements.
    
    Analyzes template fields and names to determine compliance alignment
    with asset requirements. Higher boost for templates with more
    compliance-related fields.
    
    Args:
        asset_compliance_requirements: List of compliance standards for asset
        template: Template dictionary with items and metadata
    
    Returns:
        Boost value between 0.0 and 0.3
    """
    boost = 0.0
    
    # Check if template has compliance-related fields
    template_items = template.get('items', [])
    compliance_fields = [
      'compliance', 'regulatory', 'standard', 'code', 'regulation',
      'permit', 'certificate', 'inspection_date', 'next_inspection'
    ]
    
    for item in template_items:
      label = item.get('label', '').lower()
      if any(field in label for field in compliance_fields):
        boost += 0.1
    
    # Check asset compliance requirements against template name
    asset_compliance = [req.lower() for req in asset_compliance_requirements]
    template_name = template.get('name', '').lower()
    
    for req in asset_compliance:
      if any(word in template_name for word in req.split()):
        boost += 0.15
    
    return min(boost, 0.3)  # Cap boost at 0.3
  
  def generate_match_reasons(
      self,
      asset_type: str,
      asset_criticality: str,
      asset_compliance_requirements: List[str],
      template: Dict[str, Any],
      similarity_score: float
  ) -> List[str]:
    """Generate human-readable reasons for the template match.
    
    Creates explanatory reasons based on similarity scores, asset type
    alignment, compliance requirements, and criticality matching.
    
    Args:
        asset_type: Type/category of the asset
        asset_criticality: Criticality level of the asset
        asset_compliance_requirements: Compliance standards for asset
        template: Template dictionary with metadata
        similarity_score: Calculated similarity score (0.0 to 1.0)
    
    Returns:
        List of human-readable match reason strings
    """
    reasons = []
    
    # Similarity-based reasons
    if similarity_score > 0.8:
      reasons.append("High semantic similarity between asset and template")
    elif similarity_score > 0.6:
      reasons.append("Good semantic match for asset characteristics")
    elif similarity_score > 0.4:
      reasons.append("Moderate compatibility with asset type")
    
    # Asset type matching
    asset_type_lower = asset_type.lower()
    template_name_lower = template.get('name', '').lower()
    
    if asset_type_lower in template_name_lower:
      reasons.append(f"Template specifically designed for {asset_type}")
    
    # Compliance alignment
    if asset_compliance_requirements:
      reasons.append("Template supports required compliance standards")
    
    # Criticality alignment
    if asset_criticality.lower() in ['high', 'critical']:
      if 'safety' in template_name_lower or 'critical' in template_name_lower:
        reasons.append("Template appropriate for high-criticality assets")
    
    return reasons
  
  def get_compliance_requirements(self, asset_type: str) -> List[str]:
    """Get compliance requirements for asset type.
    
    Matches asset type against known compliance rule categories and
    returns applicable standards. Returns default requirements if no
    specific match found.
    
    Args:
        asset_type: Type/category of the asset
    
    Returns:
        List of compliance requirement strings
    """
    asset_type_lower = asset_type.lower()
    
    for compliance_type, requirements in self.compliance_rules.items():
      if compliance_type.replace('_', ' ') in asset_type_lower:
        return requirements
    
    # Default compliance requirements
    return [
      "General Safety Standards",
      "Workplace Safety Regulations",
      "Equipment Maintenance Standards"
    ]