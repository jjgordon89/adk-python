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

"""Facade for coordinating form intelligence operations.

This module provides a unified interface to form intelligence by coordinating
between ImageAnalyzer, LogParser, and PatternDetector. Maintains backward
compatibility with the original API while delegating work to specialized
components.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .image_analyzer import ImageAnalysisResult, ImageAnalyzer
from .log_parser import LogParser, MaintenanceLogEntry
from .pattern_detector import HistoricalPattern, PatternDetector

logger = logging.getLogger(__name__)


class EnhancedFormIntelligence:
  """Enhanced form intelligence with computer vision and NLP capabilities.
  
  Facade class that coordinates between specialized analyzers for
  comprehensive form processing and intelligence extraction. Provides
  a unified interface for image analysis, log parsing, pattern detection,
  and intelligent form data generation.
  
  Attributes:
    image_analyzer: ImageAnalyzer for computer vision tasks.
    log_parser: LogParser for maintenance log processing.
    pattern_detector: PatternDetector for historical analysis.
    maintenance_patterns: Common maintenance patterns and indicators.
    historical_data_cache: Cache for historical data.
  """
  
  def __init__(self):
    """Initialize form intelligence with specialized analyzers."""
    self.image_analyzer = ImageAnalyzer()
    self.log_parser = LogParser()
    self.pattern_detector = PatternDetector()
    self.maintenance_patterns = self._load_maintenance_patterns()
    self.historical_data_cache: Dict[str, List[Dict[str, Any]]] = {}
    logger.info("EnhancedFormIntelligence initialized")
  
  def _load_maintenance_patterns(self) -> Dict[str, Dict[str, Any]]:
    """Load common maintenance patterns and indicators.
    
    Returns:
      Dictionary mapping maintenance types to their patterns.
    """
    return {
      "lubrication": {
        "indicators": ["oil level", "grease", "lubrication", "bearing"],
        "typical_interval": "monthly",
        "critical_keywords": ["dry", "low oil", "no grease"]
      },
      "filter_replacement": {
        "indicators": ["filter", "air filter", "oil filter", "fuel filter"],
        "typical_interval": "quarterly",
        "critical_keywords": ["dirty", "clogged", "blocked"]
      },
      "belt_inspection": {
        "indicators": ["belt", "drive belt", "v-belt", "timing belt"],
        "typical_interval": "monthly",
        "critical_keywords": ["frayed", "cracked", "loose", "worn"]
      },
      "electrical_check": {
        "indicators": ["wiring", "electrical", "connection", "terminal"],
        "typical_interval": "quarterly",
        "critical_keywords": ["loose", "corroded", "burned", "exposed"]
      }
    }
  
  async def analyze_asset_image(
    self,
    image_data: str,
    asset_type: str
  ) -> ImageAnalysisResult:
    """Analyze asset image using computer vision.
    
    Delegates to ImageAnalyzer for actual analysis.
    
    Args:
      image_data: Base64-encoded image data or image path.
      asset_type: Type of asset being analyzed.
    
    Returns:
      ImageAnalysisResult containing detected conditions and concerns.
    """
    return await self.image_analyzer.analyze_asset_image(
      image_data,
      asset_type
    )
  
  def parse_maintenance_logs(self, log_text: str) -> List[MaintenanceLogEntry]:
    """Parse maintenance logs using NLP techniques.
    
    Delegates to LogParser for actual parsing.
    
    Args:
      log_text: Raw maintenance log text to parse.
    
    Returns:
      List of parsed MaintenanceLogEntry objects.
    """
    return self.log_parser.parse_maintenance_logs(log_text)
  
  async def analyze_historical_patterns(
    self,
    asset_id: str,
    inspection_history: List[Dict[str, Any]]
  ) -> List[HistoricalPattern]:
    """Analyze historical inspection data to identify patterns.
    
    Delegates to PatternDetector for actual analysis.
    
    Args:
      asset_id: Identifier of the asset being analyzed.
      inspection_history: List of historical inspection records.
    
    Returns:
      List of identified HistoricalPattern objects.
    """
    return await self.pattern_detector.analyze_historical_patterns(
      asset_id,
      inspection_history
    )
  
  async def generate_intelligent_form_data(
    self,
    asset: Dict[str, Any],
    template: Dict[str, Any],
    image_analysis: Optional[ImageAnalysisResult] = None,
    maintenance_logs: Optional[List[MaintenanceLogEntry]] = None,
    historical_patterns: Optional[List[HistoricalPattern]] = None
  ) -> Dict[str, Any]:
    """Generate intelligent form data using all available information.
    
    Combines insights from image analysis, maintenance logs, and historical
    patterns to generate comprehensive form data with AI-powered
    recommendations and predictions.
    
    Args:
      asset: Asset information dictionary.
      template: Form template dictionary.
      image_analysis: Optional image analysis results.
      maintenance_logs: Optional parsed maintenance logs.
      historical_patterns: Optional historical pattern analysis.
    
    Returns:
      Dictionary of intelligently generated form data.
    """
    form_data = {}
    
    # Basic asset information.
    form_data["asset_id"] = asset.get("id", "")
    form_data["asset_type"] = asset.get("type", "")
    form_data["inspection_date"] = datetime.now().isoformat()
    
    # Use image analysis if available.
    if image_analysis:
      form_data["visual_condition"] = image_analysis.asset_condition
      form_data["visible_damage"] = ", ".join(image_analysis.visible_damage)
      form_data["safety_concerns"] = ", ".join(
        image_analysis.safety_concerns
      )
      
      # Extract specific measurements from OCR text.
      extracted = self.image_analyzer.extract_specific_measurements_from_ocr(
        image_analysis
      )
      form_data.update(extracted)
    
    # Use maintenance log information.
    if maintenance_logs:
      (
        recent_actions,
        recent_issues,
        recent_recommendations
      ) = self.log_parser.aggregate_recent_maintenance(maintenance_logs, 3)
      
      form_data["recent_maintenance"] = ", ".join(recent_actions[:3])
      form_data["known_issues"] = ", ".join(recent_issues[:3])
      form_data["previous_recommendations"] = ", ".join(
        recent_recommendations[:3]
      )
    
    # Use historical patterns.
    if historical_patterns:
      for pattern in historical_patterns:
        if pattern.pattern_type == "condition_trend":
          if pattern.trend_direction == "declining":
            form_data["condition_trend"] = (
              "Asset condition declining - increased monitoring recommended"
            )
          elif pattern.trend_direction == "improving":
            form_data["condition_trend"] = (
              "Asset condition improving - current maintenance effective"
            )
          else:
            form_data["condition_trend"] = "Asset condition stable"
        
        elif pattern.pattern_type == "common_issues":
          common_issues = pattern.typical_values.get("issues", [])
          if common_issues:
            form_data["recurring_issues"] = (
              f"Watch for: {', '.join(common_issues[:3])}"
            )
    
    # Generate intelligent recommendations.
    recommendations = self._generate_intelligent_recommendations(
      asset,
      image_analysis,
      maintenance_logs,
      historical_patterns
    )
    form_data["ai_recommendations"] = recommendations
    
    # Predict next inspection date based on patterns.
    next_inspection = self._predict_next_inspection_date(
      asset,
      historical_patterns
    )
    form_data["next_inspection_date"] = next_inspection
    
    return form_data
  
  def _generate_intelligent_recommendations(
    self,
    asset: Dict[str, Any],
    image_analysis: Optional[ImageAnalysisResult],
    maintenance_logs: Optional[List[MaintenanceLogEntry]],
    historical_patterns: Optional[List[HistoricalPattern]]
  ) -> str:
    """Generate intelligent maintenance recommendations.
    
    Args:
      asset: Asset information dictionary.
      image_analysis: Optional image analysis results.
      maintenance_logs: Optional parsed maintenance logs.
      historical_patterns: Optional historical pattern analysis.
    
    Returns:
      Formatted string of recommendations.
    """
    recommendations = []
    
    # Image-based recommendations.
    if image_analysis:
      if image_analysis.safety_concerns:
        recommendations.append(
          "PRIORITY: Address safety concerns identified in visual inspection"
        )
      
      damage_text = " ".join(image_analysis.visible_damage).lower()
      if "corrosion" in damage_text:
        recommendations.append("Apply corrosion protection treatment")
      
      if "leak" in damage_text:
        recommendations.append("Investigate and repair leak source")
    
    # Maintenance log-based recommendations.
    if maintenance_logs:
      recent_issues = []
      for log in maintenance_logs[-2:]:
        recent_issues.extend(log.issues_found)
      
      if recent_issues:
        recommendations.append(
          f"Monitor for recurring issues: {', '.join(recent_issues[:2])}"
        )
    
    # Historical pattern-based recommendations.
    if historical_patterns:
      for pattern in historical_patterns:
        if (pattern.pattern_type == "condition_trend" and
            pattern.trend_direction == "declining"):
          recommendations.append(
            "Increase inspection frequency due to declining condition trend"
          )
        
        elif pattern.pattern_type == "common_issues":
          common_issues = pattern.typical_values.get("issues", [])
          if common_issues:
            recommendations.append(
              f"Preventive action for common issues: "
              f"{', '.join(common_issues[:2])}"
            )
    
    # Asset type-specific recommendations.
    asset_type = asset.get("type", "").lower()
    if "electrical" in asset_type:
      recommendations.append(
        "Verify electrical connections and insulation integrity"
      )
    elif "mechanical" in asset_type:
      recommendations.append(
        "Check lubrication levels and mechanical wear points"
      )
    elif "pressure" in asset_type:
      recommendations.append(
        "Verify pressure relief systems and safety valves"
      )
    
    return (
      "; ".join(recommendations)
      if recommendations
      else "Continue regular maintenance schedule"
    )
  
  def _predict_next_inspection_date(
    self,
    asset: Dict[str, Any],
    historical_patterns: Optional[List[HistoricalPattern]]
  ) -> str:
    """Predict the next inspection date based on historical patterns.
    
    Args:
      asset: Asset information dictionary.
      historical_patterns: Optional historical pattern analysis.
    
    Returns:
      ISO format date string for next inspection.
    """
    # Default intervals based on asset criticality.
    criticality = asset.get("criticality", "medium").lower()
    
    if criticality in ["high", "critical"]:
      default_days = 30  # Monthly for critical assets.
    elif criticality == "medium":
      default_days = 90  # Quarterly for medium criticality.
    else:
      default_days = 180  # Semi-annually for low criticality.
    
    # Adjust based on historical patterns.
    if historical_patterns:
      for pattern in historical_patterns:
        if pattern.pattern_type == "inspection_frequency":
          avg_days = pattern.typical_values.get("average_days", default_days)
          default_days = int(avg_days)
          break
        
        elif pattern.pattern_type == "condition_trend":
          if pattern.trend_direction == "declining":
            default_days = int(default_days * 0.7)  # More frequent.
          elif pattern.trend_direction == "improving":
            default_days = int(default_days * 1.2)  # Less frequent.
    
    # Calculate next inspection date.
    next_date = datetime.now() + timedelta(days=default_days)
    return next_date.isoformat()
  
  def extract_measurements_from_text(self, text: str) -> Dict[str, str]:
    """Extract numerical measurements from text using regex patterns.
    
    Delegates to ImageAnalyzer for measurement extraction.
    
    Args:
      text: Text to analyze for measurements.
    
    Returns:
      Dictionary mapping measurement types to extracted values.
    """
    return self.image_analyzer.extract_measurements_from_text(text)
  
  def assess_condition_from_multiple_sources(
    self,
    image_analysis: Optional[ImageAnalysisResult],
    maintenance_logs: Optional[List[MaintenanceLogEntry]],
    historical_patterns: Optional[List[HistoricalPattern]]
  ) -> Tuple[str, float]:
    """Assess overall asset condition from multiple information sources.
    
    Delegates to PatternDetector for multi-source condition assessment.
    
    Args:
      image_analysis: Optional image analysis results.
      maintenance_logs: Optional parsed maintenance logs.
      historical_patterns: Optional historical pattern analysis.
    
    Returns:
      Tuple of (overall_condition, overall_confidence).
    """
    # Extract necessary data for pattern detector.
    image_condition = "fair"
    image_confidence = 0.5
    if image_analysis:
      image_condition = image_analysis.asset_condition
      image_confidence = image_analysis.confidence_score
    
    recent_issues_count = 0
    if maintenance_logs:
      for log in maintenance_logs[-2:]:
        recent_issues_count += len(log.issues_found)
    
    trend_direction = "stable"
    trend_confidence = 0.5
    if historical_patterns:
      for pattern in historical_patterns:
        if pattern.pattern_type == "condition_trend":
          trend_direction = pattern.trend_direction
          trend_confidence = pattern.confidence
          break
    
    return self.pattern_detector.assess_condition_from_multiple_sources(
      image_condition,
      image_confidence,
      recent_issues_count,
      trend_direction,
      trend_confidence
    )
