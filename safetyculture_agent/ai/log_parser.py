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

"""Log parsing and data extraction for maintenance records.

This module provides Natural Language Processing capabilities for parsing
maintenance logs, extracting structured data from unstructured text, and
identifying maintenance actions, issues, and recommendations.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MaintenanceLogEntry:
  """Parsed maintenance log entry.
  
  Attributes:
    date: Date of maintenance activity in string format.
    action: Primary maintenance action performed.
    technician: Name of technician who performed maintenance.
    parts_replaced: List of parts that were replaced during maintenance.
    issues_found: List of issues identified during maintenance.
    recommendations: List of recommendations for future maintenance.
  """
  date: str
  action: str
  technician: str
  parts_replaced: List[str]
  issues_found: List[str]
  recommendations: List[str]


class LogParser:
  """Parses maintenance logs to extract structured information.
  
  Uses NLP techniques and regex patterns to parse unstructured maintenance
  logs and extract key information including dates, actions, technician names,
  parts replaced, issues found, and recommendations.
  
  Attributes:
    action_keywords: Keywords that indicate maintenance actions.
    issue_keywords: Keywords that indicate problems or issues.
  """
  
  def __init__(self):
    """Initialize log parser with keyword patterns."""
    self.action_keywords = [
      "replaced",
      "repaired",
      "inspected",
      "cleaned",
      "adjusted",
      "calibrated"
    ]
    self.issue_keywords = [
      "issue",
      "problem",
      "fault",
      "failure",
      "damage",
      "wear"
    ]
    logger.info("LogParser initialized")
  
  def parse_maintenance_logs(self, log_text: str) -> List[MaintenanceLogEntry]:
    """Parse maintenance logs using NLP techniques.
    
    Splits log text into individual entries based on date patterns, then
    extracts structured information from each entry including technician,
    actions, parts, issues, and recommendations.
    
    Args:
      log_text: Raw maintenance log text to parse.
    
    Returns:
      List of parsed MaintenanceLogEntry objects.
    """
    entries = []
    
    # Split log into individual entries using date patterns.
    # Supports multiple date formats: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY.
    date_pattern = r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}'
    log_sections = re.split(f'({date_pattern})', log_text)
    
    # Process pairs of date + content sections.
    for i in range(1, len(log_sections), 2):
      if i + 1 < len(log_sections):
        date_str = log_sections[i]
        content = log_sections[i + 1]
        
        entry = self._parse_single_log_entry(date_str, content)
        if entry:
          entries.append(entry)
    
    return entries
  
  def _parse_single_log_entry(
    self,
    date_str: str,
    content: str
  ) -> Optional[MaintenanceLogEntry]:
    """Parse a single maintenance log entry.
    
    Extracts structured data from a single log entry including technician
    identification, maintenance actions, parts replaced, issues found,
    and recommendations for future work.
    
    Args:
      date_str: Date string from log entry.
      content: Content text of the log entry.
    
    Returns:
      MaintenanceLogEntry if parsing succeeds, None otherwise.
    """
    try:
      # Extract technician name using common patterns.
      tech_pattern = r'(?:tech|technician|by|performed by):?\s*([A-Za-z\s]+)'
      tech_match = re.search(tech_pattern, content, re.IGNORECASE)
      technician = tech_match.group(1).strip() if tech_match else "Unknown"
      
      # Extract action performed based on keywords.
      action = "Maintenance performed"
      for keyword in self.action_keywords:
        if keyword in content.lower():
          action = f"{keyword.capitalize()} components"
          break
      
      # Extract parts replaced using action keywords.
      parts_pattern = r'(?:replaced|changed|installed)\s+([^.]+)'
      parts_matches = re.findall(parts_pattern, content, re.IGNORECASE)
      parts_replaced = [part.strip() for part in parts_matches]
      
      # Extract issues found by searching for issue keywords.
      issues_found = []
      for keyword in self.issue_keywords:
        if keyword in content.lower():
          # Extract sentences containing the issue keyword.
          sentences = content.split('.')
          for sentence in sentences:
            if keyword in sentence.lower():
              issues_found.append(sentence.strip())
      
      # Extract recommendations using recommendation indicators.
      rec_pattern = r'(?:recommend|suggest|advise|should)([^.]+)'
      rec_matches = re.findall(rec_pattern, content, re.IGNORECASE)
      recommendations = [rec.strip() for rec in rec_matches]
      
      return MaintenanceLogEntry(
        date=date_str,
        action=action,
        technician=technician,
        parts_replaced=parts_replaced,
        issues_found=issues_found,
        recommendations=recommendations
      )
      
    except Exception:
      # Return None if parsing fails for any reason.
      return None
  
  def aggregate_recent_maintenance(
    self,
    maintenance_logs: List[MaintenanceLogEntry],
    count: int = 3
  ) -> tuple[List[str], List[str], List[str]]:
    """Aggregate recent maintenance information.
    
    Extracts and aggregates the most recent maintenance actions, issues,
    and recommendations from a list of log entries.
    
    Args:
      maintenance_logs: List of parsed maintenance log entries.
      count: Number of recent entries to aggregate (default: 3).
    
    Returns:
      Tuple of (recent_actions, recent_issues, recent_recommendations).
    """
    recent_logs = maintenance_logs[-count:]
    
    recent_actions = []
    recent_issues = []
    recent_recommendations = []
    
    for log in recent_logs:
      recent_actions.append(log.action)
      recent_issues.extend(log.issues_found)
      recent_recommendations.extend(log.recommendations)
    
    return recent_actions, recent_issues, recent_recommendations