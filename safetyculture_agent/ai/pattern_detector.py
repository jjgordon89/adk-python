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

"""Pattern recognition and anomaly detection for asset inspection history.

This module analyzes historical inspection data to identify patterns, trends,
and anomalies that inform maintenance scheduling and risk assessment.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

# Pattern detection constants
MONTHLY_INSPECTION_DAYS = 35  # Upper bound for monthly inspection frequency
QUARTERLY_INSPECTION_DAYS = 95  # Upper bound for quarterly inspection frequency
SEMIANNUAL_INSPECTION_DAYS = 190  # Upper bound for semi-annual inspection
EXCELLENT_CONDITION_SCORE = 5  # Score for excellent asset condition
GOOD_CONDITION_SCORE = 4  # Score for good asset condition
FAIR_CONDITION_SCORE = 3  # Score for fair asset condition
POOR_CONDITION_SCORE = 2  # Score for poor asset condition
CRITICAL_CONDITION_SCORE = 1  # Score for critical asset condition
DEFAULT_CONDITION_SCORE = 3  # Default score when no match found
RECENT_TREND_WINDOW = 3  # Number of recent scores for trend analysis
TREND_THRESHOLD = 0.5  # Minimum difference to detect trend change
TOP_COMMON_ISSUES_LIMIT = 5  # Maximum number of common issues to return
NO_ISSUES_CONDITION_SCORE = 4  # Condition score when no recent issues
FEW_ISSUES_CONDITION_SCORE = 3  # Condition score for few recent issues
MANY_ISSUES_CONDITION_SCORE = 2  # Condition score for many recent issues
FEW_ISSUES_THRESHOLD = 2  # Maximum issues considered "few"
MAINTENANCE_LOG_CONFIDENCE = 0.7  # Confidence score for maintenance log data
IMPROVING_TREND_SCORE = 4  # Score for assets with improving trend
DECLINING_TREND_SCORE = 2  # Score for assets with declining trend
STABLE_TREND_SCORE = 3  # Score for assets with stable trend
EXCELLENT_THRESHOLD = 4.5  # Minimum weighted score for excellent condition
GOOD_THRESHOLD = 3.5  # Minimum weighted score for good condition
FAIR_THRESHOLD = 2.5  # Minimum weighted score for fair condition
POOR_THRESHOLD = 1.5  # Minimum weighted score for poor condition


@dataclass
class HistoricalPattern:
  """Historical pattern identified from past inspections.
  
  Attributes:
    pattern_type: Type of pattern (e.g., 'inspection_frequency',
      'condition_trend', 'common_issues').
    frequency: How often the pattern occurs (e.g., 'monthly', 'recurring').
    typical_values: Dictionary of typical values associated with pattern.
    trend_direction: Direction of trend (e.g., 'improving', 'declining',
      'stable').
    confidence: Confidence level in pattern identification (0.0-1.0).
  """
  pattern_type: str
  frequency: str
  typical_values: Dict[str, Any]
  trend_direction: str
  confidence: float


class PatternDetector:
  """Detects patterns and anomalies in historical inspection data.
  
  Analyzes inspection history to identify trends in asset condition,
  maintenance frequency patterns, recurring issues, and predict future
  maintenance needs based on historical data.
  
  Attributes:
    safety_keywords: Keywords that indicate safety concerns.
  """
  
  def __init__(self):
    """Initialize pattern detector with keyword mappings."""
    self.safety_keywords = self._load_safety_keywords()
    logger.info("PatternDetector initialized")
  
  def _load_safety_keywords(self) -> List[str]:
    """Load keywords that indicate safety concerns.
    
    Returns:
      List of safety-related keywords for pattern detection.
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
  
  async def analyze_historical_patterns(
    self,
    asset_id: str,
    inspection_history: List[Dict[str, Any]]
  ) -> List[HistoricalPattern]:
    """Analyze historical inspection data to identify patterns.
    
    Examines inspection frequency, condition trends, and recurring issues
    to provide insights for maintenance planning and risk assessment.
    
    Args:
      asset_id: Identifier of the asset being analyzed.
      inspection_history: List of historical inspection records.
    
    Returns:
      List of identified HistoricalPattern objects.
    """
    patterns = []
    
    if not inspection_history:
      return patterns
    
    # Analyze inspection frequency patterns.
    dates = [
      datetime.fromisoformat(insp.get('date', '2024-01-01'))
      for insp in inspection_history
    ]
    dates.sort()
    
    if len(dates) > 1:
      intervals = [
        (dates[i] - dates[i-1]).days
        for i in range(1, len(dates))
      ]
      avg_interval = sum(intervals) / len(intervals)
      
      # Categorize frequency based on average interval.
      if avg_interval < MONTHLY_INSPECTION_DAYS:
        frequency = "monthly"
      elif avg_interval < QUARTERLY_INSPECTION_DAYS:
        frequency = "quarterly"
      elif avg_interval < SEMIANNUAL_INSPECTION_DAYS:
        frequency = "semi-annually"
      else:
        frequency = "annually"
      
      patterns.append(HistoricalPattern(
        pattern_type="inspection_frequency",
        frequency=frequency,
        typical_values={"average_days": avg_interval},
        trend_direction="stable",
        confidence=0.8
      ))
    
    # Analyze condition trends.
    conditions = []
    for insp in inspection_history:
      condition = insp.get('overall_condition', '').lower()
      if condition:
        conditions.append(condition)
    
    if conditions:
      condition_trend = self._analyze_condition_trend(conditions)
      patterns.append(condition_trend)
    
    # Analyze common issues.
    all_issues = []
    for insp in inspection_history:
      issues = insp.get('issues_found', [])
      all_issues.extend(issues)
    
    if all_issues:
      common_issues = self._find_common_issues(all_issues)
      patterns.append(HistoricalPattern(
        pattern_type="common_issues",
        frequency="recurring",
        typical_values={"issues": common_issues},
        trend_direction="stable",
        confidence=0.7
      ))
    
    return patterns
  
  def _analyze_condition_trend(
    self,
    conditions: List[str]
  ) -> HistoricalPattern:
    """Analyze trend in asset conditions over time.
    
    Converts condition strings to numerical scores and analyzes whether
    the asset condition is improving, declining, or stable over time.
    
    Args:
      conditions: List of condition strings from inspection history.
    
    Returns:
      HistoricalPattern describing the condition trend.
    """
    condition_scores = {
      "excellent": EXCELLENT_CONDITION_SCORE,
      "good": GOOD_CONDITION_SCORE,
      "fair": FAIR_CONDITION_SCORE,
      "poor": POOR_CONDITION_SCORE,
      "critical": CRITICAL_CONDITION_SCORE
    }
    
    scores = []
    for condition in conditions:
      for level, score in condition_scores.items():
        if level in condition:
          scores.append(score)
          break
      else:
        scores.append(DEFAULT_CONDITION_SCORE)
    
    if len(scores) < 2:
      trend = "stable"
    else:
      # Compare recent average to older average.
      recent_avg = sum(scores[-RECENT_TREND_WINDOW:]) / len(
        scores[-RECENT_TREND_WINDOW:]
      )
      older_avg = (
        sum(scores[:-RECENT_TREND_WINDOW]) / len(scores[:-RECENT_TREND_WINDOW])
        if len(scores) > RECENT_TREND_WINDOW
        else recent_avg
      )
      
      if recent_avg > older_avg + TREND_THRESHOLD:
        trend = "improving"
      elif recent_avg < older_avg - TREND_THRESHOLD:
        trend = "declining"
      else:
        trend = "stable"
    
    return HistoricalPattern(
      pattern_type="condition_trend",
      frequency="ongoing",
      typical_values={"average_score": sum(scores) / len(scores)},
      trend_direction=trend,
      confidence=0.75
    )
  
  def _find_common_issues(self, issues: List[str]) -> List[str]:
    """Find commonly occurring issues in inspection history.
    
    Analyzes issue descriptions to identify keywords that appear
    repeatedly, indicating systemic or recurring problems.
    
    Args:
      issues: List of issue descriptions from inspections.
    
    Returns:
      List of commonly occurring issue keywords.
    """
    issue_counts = {}
    for issue in issues:
      issue_lower = issue.lower()
      for keyword in self.safety_keywords:
        if keyword in issue_lower:
          issue_counts[keyword] = issue_counts.get(keyword, 0) + 1
    
    # Return issues that occur more than once.
    common_issues = [
      issue
      for issue, count in issue_counts.items()
      if count > 1
    ]
    return common_issues[:TOP_COMMON_ISSUES_LIMIT]
  
  def assess_condition_from_multiple_sources(
    self,
    image_condition: str,
    image_confidence: float,
    recent_issues_count: int,
    trend_direction: str,
    trend_confidence: float
  ) -> Tuple[str, float]:
    """Assess overall asset condition from multiple information sources.
    
    Combines data from image analysis, maintenance logs, and historical
    patterns to provide a comprehensive condition assessment with confidence.
    
    Args:
      image_condition: Condition from image analysis (e.g., 'good').
      image_confidence: Confidence score from image analysis (0.0-1.0).
      recent_issues_count: Number of issues in recent maintenance logs.
      trend_direction: Trend direction from historical analysis.
      trend_confidence: Confidence in trend analysis (0.0-1.0).
    
    Returns:
      Tuple of (overall_condition, overall_confidence).
    """
    condition_scores = []
    confidence_scores = []
    
    # Image analysis contribution.
    condition_map = {
      "excellent": 5,
      "good": 4,
      "fair": 3,
      "poor": 2,
      "critical": 1
    }
    score = condition_map.get(image_condition, 3)
    condition_scores.append(score)
    confidence_scores.append(image_confidence)
    
    # Maintenance log contribution based on issue count.
    if recent_issues_count == 0:
      condition_scores.append(NO_ISSUES_CONDITION_SCORE)
    elif recent_issues_count <= FEW_ISSUES_THRESHOLD:
      condition_scores.append(FEW_ISSUES_CONDITION_SCORE)
    else:
      condition_scores.append(MANY_ISSUES_CONDITION_SCORE)
    confidence_scores.append(MAINTENANCE_LOG_CONFIDENCE)
    
    # Historical pattern contribution.
    if trend_direction == "improving":
      condition_scores.append(IMPROVING_TREND_SCORE)
    elif trend_direction == "declining":
      condition_scores.append(DECLINING_TREND_SCORE)
    else:
      condition_scores.append(STABLE_TREND_SCORE)
    confidence_scores.append(trend_confidence)
    
    # Calculate weighted average.
    weights = confidence_scores
    weighted_score = (
      sum(s * w for s, w in zip(condition_scores, weights)) / sum(weights)
    )
    overall_confidence = sum(confidence_scores) / len(confidence_scores)
    
    # Convert score back to condition.
    if weighted_score >= EXCELLENT_THRESHOLD:
      condition = "excellent"
    elif weighted_score >= GOOD_THRESHOLD:
      condition = "good"
    elif weighted_score >= FAIR_THRESHOLD:
      condition = "fair"
    elif weighted_score >= POOR_THRESHOLD:
      condition = "poor"
    else:
      condition = "critical"
    
    return condition, overall_confidence