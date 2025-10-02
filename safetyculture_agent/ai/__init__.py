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

"""AI-powered form intelligence and analysis capabilities.

This package provides comprehensive AI capabilities for form processing,
including computer vision, natural language processing, pattern detection,
and intelligent template matching for inspections.
"""

from __future__ import annotations

from .form_intelligence import EnhancedFormIntelligence
from .image_analyzer import ImageAnalysisResult, ImageAnalyzer
from .log_parser import LogParser, MaintenanceLogEntry
from .pattern_detector import HistoricalPattern, PatternDetector
from .template_generation import TemplateGenerator
from .template_matcher import AITemplateMatcher, AssetProfile, TemplateMatch
from .template_scoring import TemplateScorer

__all__ = [
  "AITemplateMatcher",
  "AssetProfile",
  "EnhancedFormIntelligence",
  "HistoricalPattern",
  "ImageAnalysisResult",
  "ImageAnalyzer",
  "LogParser",
  "MaintenanceLogEntry",
  "PatternDetector",
  "TemplateGenerator",
  "TemplateMatch",
  "TemplateScorer",
]
