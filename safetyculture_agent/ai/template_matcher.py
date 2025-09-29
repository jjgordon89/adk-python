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

import json
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
import re


@dataclass
class TemplateMatch:
    """Represents a template match with confidence score."""
    template_id: str
    template_name: str
    confidence_score: float
    match_reasons: List[str]
    compliance_requirements: List[str]


@dataclass
class AssetProfile:
    """Represents an asset profile for template matching."""
    asset_id: str
    asset_type: str
    asset_name: str
    description: str
    location: str
    criticality: str
    compliance_requirements: List[str]
    maintenance_history: List[str]
    custom_attributes: Dict[str, Any]


class AITemplateMatcher:
    """AI-powered template matching using embeddings and semantic analysis."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-001"):
        self.model_name = model_name
        self.template_embeddings_cache: Dict[str, np.ndarray] = {}
        self.compliance_rules = self._load_compliance_rules()
    
    def _load_compliance_rules(self) -> Dict[str, List[str]]:
        """Load compliance rules for different asset types and industries."""
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
    
    async def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text using keyword-based analysis."""
        # Use simple keyword-based embedding for now
        # In production, this would use a proper embedding model
        return self._create_simple_embedding(text)
    
    def _create_simple_embedding(self, text: str) -> np.ndarray:
        """Create a simple keyword-based embedding as fallback."""
        text_lower = text.lower()
        keywords = [
            'pressure', 'electrical', 'mechanical', 'safety', 'fire', 'hvac',
            'pump', 'valve', 'motor', 'tank', 'pipe', 'vessel', 'crane',
            'inspection', 'maintenance', 'compliance', 'regulatory'
        ]
        
        features = []
        for keyword in keywords:
            features.append(float(keyword in text_lower))
        
        return np.array(features, dtype=np.float32)
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        if np.linalg.norm(embedding1) == 0 or np.linalg.norm(embedding2) == 0:
            return 0.0
        
        return float(np.dot(embedding1, embedding2) / 
                    (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))
    
    async def match_templates_to_asset(
        self,
        asset: AssetProfile,
        available_templates: List[Dict[str, Any]]
    ) -> List[TemplateMatch]:
        """Match templates to an asset using AI-powered analysis."""
        
        # Create asset description for embedding
        asset_description = f"""
        Asset Type: {asset.asset_type}
        Name: {asset.asset_name}
        Description: {asset.description}
        Location: {asset.location}
        Criticality: {asset.criticality}
        Compliance Requirements: {', '.join(asset.compliance_requirements)}
        Maintenance History: {', '.join(asset.maintenance_history[-3:])}  # Last 3 entries
        """
        
        # Generate asset embedding
        asset_embedding = await self.generate_embedding(asset_description)
        
        matches = []
        
        for template in available_templates:
            template_id = template.get('template_id', '')
            template_name = template.get('name', '')
            template_description = template.get('description', '')
            
            # Create template description for embedding
            template_text = f"""
            Template Name: {template_name}
            Description: {template_description}
            Fields: {', '.join([item.get('label', '') for item in template.get('items', [])])}
            """
            
            # Generate or retrieve cached template embedding
            if template_id not in self.template_embeddings_cache:
                self.template_embeddings_cache[template_id] = await self.generate_embedding(template_text)
            
            template_embedding = self.template_embeddings_cache[template_id]
            
            # Calculate similarity
            similarity_score = self.calculate_similarity(asset_embedding, template_embedding)
            
            # Apply compliance boost
            compliance_boost = self._calculate_compliance_boost(asset, template)
            final_score = similarity_score + compliance_boost
            
            # Generate match reasons
            match_reasons = self._generate_match_reasons(asset, template, similarity_score)
            
            # Get compliance requirements
            compliance_reqs = self._get_compliance_requirements(asset.asset_type)
            
            matches.append(TemplateMatch(
                template_id=template_id,
                template_name=template_name,
                confidence_score=min(final_score, 1.0),  # Cap at 1.0
                match_reasons=match_reasons,
                compliance_requirements=compliance_reqs
            ))
        
        # Sort by confidence score
        matches.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return matches
    
    def _calculate_compliance_boost(self, asset: AssetProfile, template: Dict[str, Any]) -> float:
        """Calculate compliance boost based on regulatory requirements."""
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
        
        # Check asset compliance requirements
        asset_compliance = [req.lower() for req in asset.compliance_requirements]
        template_name = template.get('name', '').lower()
        
        for req in asset_compliance:
            if any(word in template_name for word in req.split()):
                boost += 0.15
        
        return min(boost, 0.3)  # Cap boost at 0.3
    
    def _generate_match_reasons(
        self,
        asset: AssetProfile,
        template: Dict[str, Any],
        similarity_score: float
    ) -> List[str]:
        """Generate human-readable reasons for the template match."""
        reasons = []
        
        if similarity_score > 0.8:
            reasons.append("High semantic similarity between asset and template")
        elif similarity_score > 0.6:
            reasons.append("Good semantic match for asset characteristics")
        elif similarity_score > 0.4:
            reasons.append("Moderate compatibility with asset type")
        
        # Check for specific matches
        asset_type_lower = asset.asset_type.lower()
        template_name_lower = template.get('name', '').lower()
        
        if asset_type_lower in template_name_lower:
            reasons.append(f"Template specifically designed for {asset.asset_type}")
        
        # Check compliance alignment
        if asset.compliance_requirements:
            reasons.append("Template supports required compliance standards")
        
        # Check criticality alignment
        if asset.criticality.lower() in ['high', 'critical']:
            if 'safety' in template_name_lower or 'critical' in template_name_lower:
                reasons.append("Template appropriate for high-criticality assets")
        
        return reasons
    
    def _get_compliance_requirements(self, asset_type: str) -> List[str]:
        """Get compliance requirements for asset type."""
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
    
    async def generate_dynamic_template(self, asset: AssetProfile) -> Dict[str, Any]:
        """Generate a custom template based on asset characteristics."""
        
        # For now, create a rule-based dynamic template
        # In production, this would use an AI model to generate templates
        return self._create_dynamic_template_from_rules(asset)
    
    def _create_dynamic_template_from_rules(self, asset: AssetProfile) -> Dict[str, Any]:
        """Create a dynamic template based on asset characteristics and rules."""
        
        # Base template items
        items = [
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
        
        # Add asset-type specific fields
        asset_type_lower = asset.asset_type.lower()
        
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
        
        # Add criticality-based fields
        if asset.criticality.lower() in ['high', 'critical']:
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
        
        # Add compliance fields based on requirements
        for req in asset.compliance_requirements:
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
        
        # Always add final fields
        items.extend([
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
        ])
        
        return {
            "template_id": f"dynamic_{asset.asset_id}_{asset.asset_type.lower().replace(' ', '_')}",
            "name": f"Dynamic {asset.asset_type} Inspection - {asset.asset_name}",
            "description": f"Dynamically generated inspection template for {asset.asset_type} based on asset characteristics and compliance requirements",
            "created_for_asset": asset.asset_id,
            "auto_generated": True,
            "items": items
        }
    
    def _create_fallback_template(self, asset: AssetProfile) -> Dict[str, Any]:
        """Create a basic fallback template."""
        return {
            "template_id": f"fallback_{asset.asset_id}",
            "name": f"Basic {asset.asset_type} Inspection",
            "description": f"Basic inspection template for {asset.asset_type}",
            "created_for_asset": asset.asset_id,
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
