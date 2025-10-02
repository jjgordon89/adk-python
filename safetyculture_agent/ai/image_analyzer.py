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

"""Image analysis for form field extraction and processing.

This module provides computer vision capabilities for analyzing asset images,
detecting damage, extracting text via OCR, and identifying maintenance needs.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Dict, List

logger = logging.getLogger(__name__)

# Image analysis confidence thresholds
ELECTRICAL_CONFIDENCE_SCORE = 0.85  # High confidence for electrical analysis
PUMP_CONFIDENCE_SCORE = 0.78  # Good confidence for pump analysis
DEFAULT_CONFIDENCE_SCORE = 0.70  # Default confidence for general analysis


@dataclass
class ImageAnalysisResult:
  """Result of computer vision analysis on asset images.
  
  Attributes:
    asset_condition: Overall condition assessment (excellent/good/fair/poor).
    visible_damage: List of damage observations from visual inspection.
    safety_concerns: List of identified safety issues requiring attention.
    maintenance_indicators: List of maintenance needs detected in image.
    confidence_score: Confidence level of the analysis (0.0-1.0).
    extracted_text: Text extracted from image via OCR.
  """
  asset_condition: str
  visible_damage: List[str]
  safety_concerns: List[str]
  maintenance_indicators: List[str]
  confidence_score: float
  extracted_text: List[str]


class ImageAnalyzer:
  """Analyzes images to extract form field information.
  
  Uses computer vision and AI models to process form images, detect fields,
  extract text, and understand form structure. Identifies asset conditions,
  damage, and maintenance needs from visual inspection.
  
  Attributes:
    condition_keywords: Mapping of condition levels to identifying keywords.
    safety_keywords: Keywords that indicate potential safety concerns.
  """
  
  def __init__(self):
    """Initialize image analyzer with keyword mappings."""
    self.condition_keywords = self._load_condition_keywords()
    self.safety_keywords = self._load_safety_keywords()
    logger.info("ImageAnalyzer initialized")
  
  def _load_condition_keywords(self) -> Dict[str, List[str]]:
    """Load keywords for asset condition assessment.
    
    Returns:
      Dictionary mapping condition levels to keyword lists.
    """
    return {
      "excellent": ["new", "pristine", "perfect", "excellent", "like new"],
      "good": [
        "good",
        "satisfactory",
        "acceptable",
        "functional",
        "working"
      ],
      "fair": [
        "fair",
        "moderate",
        "some wear",
        "minor issues",
        "serviceable"
      ],
      "poor": [
        "poor",
        "worn",
        "damaged",
        "deteriorated",
        "needs attention"
      ],
      "critical": [
        "critical",
        "failed",
        "broken",
        "unsafe",
        "immediate attention"
      ]
    }
  
  def _load_safety_keywords(self) -> List[str]:
    """Load keywords that indicate safety concerns.
    
    Returns:
      List of safety-related keywords.
    """
    return [
      "leak",
      "crack",
      "corrosion",
      "rust",
      "damage",
      "wear",
      "loose",
      "missing",
      "broken",
      "unsafe",
      "hazard",
      "risk",
      "danger",
      "exposed",
      "frayed",
      "bent",
      "dent",
      "hole",
      "tear"
    ]
  
  async def analyze_asset_image(
    self,
    image_data: str,
    asset_type: str
  ) -> ImageAnalysisResult:
    """Analyze asset image using computer vision.
    
    In production, this would integrate with actual computer vision APIs
    (e.g., Google Cloud Vision API, Vertex AI Vision). Currently provides
    simulated analysis based on asset type for testing and development.
    
    Args:
      image_data: Base64-encoded image data or image path.
      asset_type: Type of asset being analyzed (e.g., 'electrical', 'pump').
    
    Returns:
      ImageAnalysisResult containing detected conditions and concerns.
    """
    asset_type_lower = asset_type.lower()
    
    # Simulate analysis based on asset type.
    # In production, this would call actual CV APIs.
    if 'electrical' in asset_type_lower:
      return ImageAnalysisResult(
        asset_condition="good",
        visible_damage=["Minor surface corrosion on housing"],
        safety_concerns=["Exposed wiring near junction box"],
        maintenance_indicators=["Terminal connections need tightening"],
        confidence_score=ELECTRICAL_CONFIDENCE_SCORE,
        extracted_text=[
          "DANGER HIGH VOLTAGE",
          "Model: XYZ-123",
          "Serial: ABC789"
        ]
      )
    elif 'pump' in asset_type_lower:
      return ImageAnalysisResult(
        asset_condition="fair",
        visible_damage=["Oil stain beneath pump", "Rust on mounting bolts"],
        safety_concerns=["Loose coupling guard"],
        maintenance_indicators=["Oil level appears low", "Belt shows wear"],
        confidence_score=PUMP_CONFIDENCE_SCORE,
        extracted_text=["PUMP MODEL P-456", "MAX PRESSURE 150 PSI"]
      )
    else:
      return ImageAnalysisResult(
        asset_condition="good",
        visible_damage=[],
        safety_concerns=[],
        maintenance_indicators=["Regular maintenance recommended"],
        confidence_score=DEFAULT_CONFIDENCE_SCORE,
        extracted_text=[]
      )
  
  def extract_measurements_from_text(self, text: str) -> Dict[str, str]:
    """Extract numerical measurements from text using regex patterns.
    
    Identifies and extracts common measurement types including pressure,
    temperature, voltage, and flow rates from unstructured text.
    
    Args:
      text: Text to analyze for measurements.
    
    Returns:
      Dictionary mapping measurement types to extracted values with units.
    """
    measurements = {}
    
    # Pressure measurements (PSI, Bar, kPa, Pascal).
    pressure_pattern = r'(\d+\.?\d*)\s*(psi|bar|kpa|pascal)'
    pressure_matches = re.findall(pressure_pattern, text.lower())
    if pressure_matches:
      value, unit = pressure_matches[0]
      measurements["pressure"] = f"{value} {unit.upper()}"
    
    # Temperature measurements (Celsius, Fahrenheit).
    temp_pattern = r'(\d+\.?\d*)\s*(°?[cf]|celsius|fahrenheit)'
    temp_matches = re.findall(temp_pattern, text.lower())
    if temp_matches:
      value, unit = temp_matches[0]
      measurements["temperature"] = f"{value}°{unit[0].upper()}"
    
    # Voltage measurements.
    voltage_pattern = r'(\d+\.?\d*)\s*(v|volt|voltage)'
    voltage_matches = re.findall(voltage_pattern, text.lower())
    if voltage_matches:
      value, unit = voltage_matches[0]
      measurements["voltage"] = f"{value}V"
    
    # Flow rate measurements (GPM, LPM, CFM, m3/h).
    flow_pattern = r'(\d+\.?\d*)\s*(gpm|lpm|cfm|m3/h)'
    flow_matches = re.findall(flow_pattern, text.lower())
    if flow_matches:
      value, unit = flow_matches[0]
      measurements["flow_rate"] = f"{value} {unit.upper()}"
    
    return measurements
  
  def extract_specific_measurements_from_ocr(
    self,
    image_analysis: ImageAnalysisResult
  ) -> Dict[str, str]:
    """Extract specific measurements from OCR text in image analysis.
    
    Processes extracted text from image analysis to identify and extract
    specific measurement values like pressure and voltage readings.
    
    Args:
      image_analysis: Results from image analysis containing OCR text.
    
    Returns:
      Dictionary of extracted measurements.
    """
    extracted_values = {}
    
    for text in image_analysis.extracted_text:
      # Extract pressure readings.
      if "pressure" in text.lower():
        pressure_match = re.search(r'(\d+\.?\d*)\s*psi', text.lower())
        if pressure_match:
          extracted_values["pressure_reading"] = pressure_match.group(1)
      
      # Extract voltage readings.
      if "voltage" in text.lower():
        voltage_match = re.search(r'(\d+\.?\d*)\s*v', text.lower())
        if voltage_match:
          extracted_values["voltage_reading"] = voltage_match.group(1)
    
    return extracted_values