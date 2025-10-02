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
import logging
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .template_generation import TemplateGenerator
from .template_scoring import TemplateScorer

logger = logging.getLogger(__name__)


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
  """AI-powered template matching using embeddings and semantic analysis.
  
  Matches assets to appropriate inspection templates using AI-powered
  analysis that considers asset characteristics, compliance requirements,
  and historical patterns. Delegates template generation and scoring to
  specialized components for better organization.
  
  Attributes:
      model_name: Name of the AI model to use for embeddings
      template_embeddings_cache: Cache of template embeddings
      generator: TemplateGenerator for creating dynamic templates
      scorer: TemplateScorer for calculating confidence scores
  """
  
  def __init__(self, model_name: str = "gemini-2.0-flash-001"):
    """Initialize template matcher with AI model and components.
    
    Args:
        model_name: Name of AI model for embeddings (default: gemini-2.0)
    """
    self.model_name = model_name
    self.template_embeddings_cache: Dict[str, np.ndarray] = {}
    self.generator = TemplateGenerator()
    self.scorer = TemplateScorer()
    logger.info(f"AITemplateMatcher initialized with model: {model_name}")
  
  async def generate_embedding(self, text: str) -> np.ndarray:
    """Generate embedding for text using keyword-based analysis.
    
    Uses simple keyword-based embedding as fallback. In production,
    this would use a proper embedding model from the configured AI service.
    
    Args:
        text: Text to generate embedding for
    
    Returns:
        NumPy array representing the text embedding
    """
    return self._create_simple_embedding(text)
  
  def _create_simple_embedding(self, text: str) -> np.ndarray:
    """Create a simple keyword-based embedding as fallback.
    
    Creates feature vector based on presence of industry keywords.
    This is a placeholder for production embedding models.
    
    Args:
        text: Text to create embedding for
    
    Returns:
        NumPy array with binary features for keywords
    """
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
  
  def calculate_similarity(
      self,
      embedding1: np.ndarray,
      embedding2: np.ndarray
  ) -> float:
    """Calculate cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
    
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if np.linalg.norm(embedding1) == 0 or np.linalg.norm(embedding2) == 0:
      return 0.0
    
    return float(
        np.dot(embedding1, embedding2) /
        (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    )
  
  async def match_templates_to_asset(
      self,
      asset: AssetProfile,
      available_templates: List[Dict[str, Any]]
  ) -> List[TemplateMatch]:
    """Match templates to an asset using AI-powered analysis.
    
    Analyzes asset characteristics and available templates to find the
    best matches using embedding similarity and compliance scoring.
    
    Args:
        asset: AssetProfile containing asset details
        available_templates: List of template dictionaries
    
    Returns:
        List of TemplateMatch objects sorted by confidence score
    """
    asset_description = self._create_asset_description(asset)
    asset_embedding = await self.generate_embedding(asset_description)
    
    matches = []
    
    for template in available_templates:
      template_id = template.get('template_id', '')
      template_name = template.get('name', '')
      template_description = template.get('description', '')
      
      template_text = self._create_template_description(
          template_name, template_description, template
      )
      
      # Generate or retrieve cached template embedding
      if template_id not in self.template_embeddings_cache:
        template_embedding = await self.generate_embedding(template_text)
        self.template_embeddings_cache[template_id] = template_embedding
      
      template_embedding = self.template_embeddings_cache[template_id]
      
      # Calculate similarity score
      similarity_score = self.calculate_similarity(
          asset_embedding, template_embedding
      )
      
      # Apply compliance boost using scorer
      compliance_boost = self.scorer.calculate_compliance_boost(
          asset.compliance_requirements, template
      )
      final_score = similarity_score + compliance_boost
      
      # Generate match reasons using scorer
      match_reasons = self.scorer.generate_match_reasons(
          asset.asset_type,
          asset.criticality,
          asset.compliance_requirements,
          template,
          similarity_score
      )
      
      # Get compliance requirements using scorer
      compliance_reqs = self.scorer.get_compliance_requirements(
          asset.asset_type
      )
      
      matches.append(TemplateMatch(
          template_id=template_id,
          template_name=template_name,
          confidence_score=min(final_score, 1.0),
          match_reasons=match_reasons,
          compliance_requirements=compliance_reqs
      ))
    
    # Sort by confidence score
    matches.sort(key=lambda x: x.confidence_score, reverse=True)
    
    return matches
  
  def _create_asset_description(self, asset: AssetProfile) -> str:
    """Create comprehensive asset description for embedding.
    
    Args:
        asset: AssetProfile to describe
    
    Returns:
        Formatted string with asset details
    """
    return f"""
    Asset Type: {asset.asset_type}
    Name: {asset.asset_name}
    Description: {asset.description}
    Location: {asset.location}
    Criticality: {asset.criticality}
    Compliance Requirements: {', '.join(asset.compliance_requirements)}
    Maintenance History: {', '.join(asset.maintenance_history[-3:])}
    """
  
  def _create_template_description(
      self,
      name: str,
      description: str,
      template: Dict[str, Any]
  ) -> str:
    """Create template description for embedding.
    
    Args:
        name: Template name
        description: Template description
        template: Full template dictionary
    
    Returns:
        Formatted string with template details
    """
    items = template.get('items', [])
    field_labels = [item.get('label', '') for item in items]
    
    return f"""
    Template Name: {name}
    Description: {description}
    Fields: {', '.join(field_labels)}
    """
  
  async def generate_dynamic_template(
      self,
      asset: AssetProfile
  ) -> Dict[str, Any]:
    """Generate a custom template based on asset characteristics.
    
    Delegates to TemplateGenerator for template creation.
    
    Args:
        asset: AssetProfile to generate template for
    
    Returns:
        Dictionary containing complete template structure
    """
    return self.generator.create_dynamic_template(
        asset.asset_id,
        asset.asset_type,
        asset.asset_name,
        asset.criticality,
        asset.compliance_requirements
    )
  
  def _create_dynamic_template_from_rules(
      self,
      asset: AssetProfile
  ) -> Dict[str, Any]:
    """Create dynamic template using generator (backward compatibility).
    
    Args:
        asset: AssetProfile to generate template for
    
    Returns:
        Dictionary containing complete template structure
    """
    return self.generator.create_dynamic_template(
        asset.asset_id,
        asset.asset_type,
        asset.asset_name,
        asset.criticality,
        asset.compliance_requirements
    )
  
  def _create_fallback_template(self, asset: AssetProfile) -> Dict[str, Any]:
    """Create a basic fallback template.
    
    Delegates to TemplateGenerator for fallback template creation.
    
    Args:
        asset: AssetProfile to generate fallback template for
    
    Returns:
        Dictionary containing basic template structure
    """
    return self.generator.create_fallback_template(
        asset.asset_id,
        asset.asset_type
    )
  
  def _calculate_compliance_boost(
      self,
      asset: AssetProfile,
      template: Dict[str, Any]
  ) -> float:
    """Calculate compliance boost (backward compatibility wrapper).
    
    Args:
        asset: AssetProfile with compliance requirements
        template: Template to evaluate
    
    Returns:
        Boost value between 0.0 and 0.3
    """
    return self.scorer.calculate_compliance_boost(
        asset.compliance_requirements,
        template
    )
  
  def _generate_match_reasons(
      self,
      asset: AssetProfile,
      template: Dict[str, Any],
      similarity_score: float
  ) -> List[str]:
    """Generate match reasons (backward compatibility wrapper).
    
    Args:
        asset: AssetProfile with asset details
        template: Template that was matched
        similarity_score: Calculated similarity score
    
    Returns:
        List of human-readable reason strings
    """
    return self.scorer.generate_match_reasons(
        asset.asset_type,
        asset.criticality,
        asset.compliance_requirements,
        template,
        similarity_score
    )
  
  def _get_compliance_requirements(self, asset_type: str) -> List[str]:
    """Get compliance requirements (backward compatibility wrapper).
    
    Args:
        asset_type: Type/category of the asset
    
    Returns:
        List of compliance requirement strings
    """
    return self.scorer.get_compliance_requirements(asset_type)
  
  def _load_compliance_rules(self) -> Dict[str, List[str]]:
    """Load compliance rules (backward compatibility wrapper).
    
    Returns:
        Dictionary mapping asset types to compliance standards
    """
    return self.scorer.compliance_rules
