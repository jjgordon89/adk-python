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
from typing import Any, Dict, List, Optional

from google.adk.tools.function_tool import FunctionTool

from .template_matcher import AITemplateMatcher, AssetProfile, TemplateMatch
from .form_intelligence import EnhancedFormIntelligence, ImageAnalysisResult, MaintenanceLogEntry


async def ai_match_templates_to_asset(
    asset_data: Dict[str, Any],
    available_templates: List[Dict[str, Any]]
) -> str:
    """
    Use AI to match templates to an asset based on semantic similarity and compliance requirements.
    
    Args:
        asset_data: Dictionary containing asset information
        available_templates: List of available template dictionaries
    
    Returns:
        JSON string containing ranked template matches with confidence scores and reasons
    """
    try:
        matcher = AITemplateMatcher()
        
        # Create asset profile
        asset_profile = AssetProfile(
            asset_id=asset_data.get("id", ""),
            asset_type=asset_data.get("type", ""),
            asset_name=asset_data.get("name", ""),
            description=asset_data.get("description", ""),
            location=asset_data.get("location", ""),
            criticality=asset_data.get("criticality", "medium"),
            compliance_requirements=asset_data.get("compliance_requirements", []),
            maintenance_history=asset_data.get("maintenance_history", []),
            custom_attributes=asset_data.get("custom_attributes", {})
        )
        
        # Get template matches
        matches = await matcher.match_templates_to_asset(asset_profile, available_templates)
        
        # Convert to serializable format
        result = {
            "asset_id": asset_profile.asset_id,
            "matches": [
                {
                    "template_id": match.template_id,
                    "template_name": match.template_name,
                    "confidence_score": match.confidence_score,
                    "match_reasons": match.match_reasons,
                    "compliance_requirements": match.compliance_requirements
                }
                for match in matches
            ],
            "best_match": {
                "template_id": matches[0].template_id,
                "confidence": matches[0].confidence_score
            } if matches else None
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Error in AI template matching: {str(e)}"


async def generate_dynamic_template_for_asset(
    asset_data: Dict[str, Any]
) -> str:
    """
    Generate a custom inspection template dynamically based on asset characteristics.
    
    Args:
        asset_data: Dictionary containing asset information
    
    Returns:
        JSON string containing the generated template
    """
    try:
        matcher = AITemplateMatcher()
        
        # Create asset profile
        asset_profile = AssetProfile(
            asset_id=asset_data.get("id", ""),
            asset_type=asset_data.get("type", ""),
            asset_name=asset_data.get("name", ""),
            description=asset_data.get("description", ""),
            location=asset_data.get("location", ""),
            criticality=asset_data.get("criticality", "medium"),
            compliance_requirements=asset_data.get("compliance_requirements", []),
            maintenance_history=asset_data.get("maintenance_history", []),
            custom_attributes=asset_data.get("custom_attributes", {})
        )
        
        # Generate dynamic template
        template = await matcher.generate_dynamic_template(asset_profile)
        
        return json.dumps(template, indent=2)
    
    except Exception as e:
        return f"Error generating dynamic template: {str(e)}"


async def analyze_asset_image_for_inspection(
    image_base64: str,
    asset_type: str
) -> str:
    """
    Analyze an asset image to extract condition information for inspection forms.
    
    Args:
        image_base64: Base64 encoded image data
        asset_type: Type of asset being analyzed
    
    Returns:
        JSON string containing image analysis results
    """
    try:
        form_intelligence = EnhancedFormIntelligence()
        
        # Analyze the image
        analysis = await form_intelligence.analyze_asset_image(image_base64, asset_type)
        
        result = {
            "asset_condition": analysis.asset_condition,
            "visible_damage": analysis.visible_damage,
            "safety_concerns": analysis.safety_concerns,
            "maintenance_indicators": analysis.maintenance_indicators,
            "confidence_score": analysis.confidence_score,
            "extracted_text": analysis.extracted_text
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Error analyzing asset image: {str(e)}"


async def parse_maintenance_logs_for_insights(
    maintenance_log_text: str
) -> str:
    """
    Parse maintenance logs to extract structured information for inspection forms.
    
    Args:
        maintenance_log_text: Raw maintenance log text
    
    Returns:
        JSON string containing parsed maintenance log entries
    """
    try:
        form_intelligence = EnhancedFormIntelligence()
        
        # Parse the maintenance logs
        entries = form_intelligence.parse_maintenance_logs(maintenance_log_text)
        
        result = {
            "total_entries": len(entries),
            "entries": [
                {
                    "date": entry.date,
                    "action": entry.action,
                    "technician": entry.technician,
                    "parts_replaced": entry.parts_replaced,
                    "issues_found": entry.issues_found,
                    "recommendations": entry.recommendations
                }
                for entry in entries
            ]
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Error parsing maintenance logs: {str(e)}"


async def analyze_historical_inspection_patterns(
    asset_id: str,
    inspection_history: List[Dict[str, Any]]
) -> str:
    """
    Analyze historical inspection data to identify patterns and trends.
    
    Args:
        asset_id: ID of the asset to analyze
        inspection_history: List of historical inspection data
    
    Returns:
        JSON string containing identified patterns and trends
    """
    try:
        form_intelligence = EnhancedFormIntelligence()
        
        # Analyze patterns
        patterns = await form_intelligence.analyze_historical_patterns(asset_id, inspection_history)
        
        result = {
            "asset_id": asset_id,
            "patterns_found": len(patterns),
            "patterns": [
                {
                    "pattern_type": pattern.pattern_type,
                    "frequency": pattern.frequency,
                    "typical_values": pattern.typical_values,
                    "trend_direction": pattern.trend_direction,
                    "confidence": pattern.confidence
                }
                for pattern in patterns
            ]
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Error analyzing historical patterns: {str(e)}"


async def generate_intelligent_inspection_data(
    asset_data: Dict[str, Any],
    template_data: Dict[str, Any],
    image_base64: Optional[str] = None,
    maintenance_log_text: Optional[str] = None,
    inspection_history: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generate intelligent inspection form data using multiple AI capabilities.
    
    Args:
        asset_data: Asset information dictionary
        template_data: Template structure dictionary
        image_base64: Optional base64 encoded asset image
        maintenance_log_text: Optional maintenance log text
        inspection_history: Optional historical inspection data
    
    Returns:
        JSON string containing intelligent form data for all fields
    """
    try:
        form_intelligence = EnhancedFormIntelligence()
        
        # Analyze image if provided
        image_analysis = None
        if image_base64:
            image_analysis = await form_intelligence.analyze_asset_image(
                image_base64, asset_data.get("type", "")
            )
        
        # Parse maintenance logs if provided
        maintenance_logs = None
        if maintenance_log_text:
            maintenance_logs = form_intelligence.parse_maintenance_logs(maintenance_log_text)
        
        # Analyze historical patterns if provided
        historical_patterns = None
        if inspection_history:
            historical_patterns = await form_intelligence.analyze_historical_patterns(
                asset_data.get("id", ""), inspection_history
            )
        
        # Generate intelligent form data
        form_data = await form_intelligence.generate_intelligent_form_data(
            asset_data,
            template_data,
            image_analysis,
            maintenance_logs,
            historical_patterns
        )
        
        # Add analysis metadata
        result = {
            "asset_id": asset_data.get("id", ""),
            "template_id": template_data.get("template_id", ""),
            "generated_at": form_intelligence._predict_next_inspection_date(asset_data, historical_patterns),
            "data_sources_used": {
                "image_analysis": image_analysis is not None,
                "maintenance_logs": maintenance_logs is not None,
                "historical_patterns": historical_patterns is not None
            },
            "form_data": form_data,
            "confidence_assessment": form_intelligence.assess_condition_from_multiple_sources(
                image_analysis, maintenance_logs, historical_patterns
            )
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Error generating intelligent inspection data: {str(e)}"


# Create FunctionTool instances for the AI capabilities
AI_ENHANCED_TOOLS = [
    FunctionTool(ai_match_templates_to_asset),
    FunctionTool(generate_dynamic_template_for_asset),
    FunctionTool(analyze_asset_image_for_inspection),
    FunctionTool(parse_maintenance_logs_for_insights),
    FunctionTool(analyze_historical_inspection_patterns),
    FunctionTool(generate_intelligent_inspection_data)
]

# Export individual functions for direct use
__all__ = [
    'ai_match_templates_to_asset',
    'generate_dynamic_template_for_asset',
    'analyze_asset_image_for_inspection',
    'parse_maintenance_logs_for_insights',
    'analyze_historical_inspection_patterns',
    'generate_intelligent_inspection_data',
    'AI_ENHANCED_TOOLS'
]
