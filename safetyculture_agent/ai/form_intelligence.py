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
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
import base64


@dataclass
class ImageAnalysisResult:
    """Result of computer vision analysis on asset images."""
    asset_condition: str
    visible_damage: List[str]
    safety_concerns: List[str]
    maintenance_indicators: List[str]
    confidence_score: float
    extracted_text: List[str]


@dataclass
class MaintenanceLogEntry:
    """Parsed maintenance log entry."""
    date: str
    action: str
    technician: str
    parts_replaced: List[str]
    issues_found: List[str]
    recommendations: List[str]


@dataclass
class HistoricalPattern:
    """Historical pattern identified from past inspections."""
    pattern_type: str
    frequency: str
    typical_values: Dict[str, Any]
    trend_direction: str
    confidence: float


class EnhancedFormIntelligence:
    """Enhanced form intelligence with computer vision and NLP capabilities."""
    
    def __init__(self):
        self.condition_keywords = self._load_condition_keywords()
        self.safety_keywords = self._load_safety_keywords()
        self.maintenance_patterns = self._load_maintenance_patterns()
        self.historical_data_cache: Dict[str, List[Dict[str, Any]]] = {}
    
    def _load_condition_keywords(self) -> Dict[str, List[str]]:
        """Load keywords for asset condition assessment."""
        return {
            "excellent": ["new", "pristine", "perfect", "excellent", "like new"],
            "good": ["good", "satisfactory", "acceptable", "functional", "working"],
            "fair": ["fair", "moderate", "some wear", "minor issues", "serviceable"],
            "poor": ["poor", "worn", "damaged", "deteriorated", "needs attention"],
            "critical": ["critical", "failed", "broken", "unsafe", "immediate attention"]
        }
    
    def _load_safety_keywords(self) -> List[str]:
        """Load keywords that indicate safety concerns."""
        return [
            "leak", "crack", "corrosion", "rust", "damage", "wear", "loose",
            "missing", "broken", "unsafe", "hazard", "risk", "danger",
            "exposed", "frayed", "bent", "dent", "hole", "tear"
        ]
    
    def _load_maintenance_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load common maintenance patterns and indicators."""
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
    
    async def analyze_asset_image(self, image_data: str, asset_type: str) -> ImageAnalysisResult:
        """Analyze asset image using computer vision (simulated for now)."""
        
        # In production, this would use actual computer vision APIs
        # For now, we'll simulate the analysis
        
        # Simulate image analysis results based on asset type
        asset_type_lower = asset_type.lower()
        
        if 'electrical' in asset_type_lower:
            return ImageAnalysisResult(
                asset_condition="good",
                visible_damage=["Minor surface corrosion on housing"],
                safety_concerns=["Exposed wiring near junction box"],
                maintenance_indicators=["Terminal connections need tightening"],
                confidence_score=0.85,
                extracted_text=["DANGER HIGH VOLTAGE", "Model: XYZ-123", "Serial: ABC789"]
            )
        elif 'pump' in asset_type_lower:
            return ImageAnalysisResult(
                asset_condition="fair",
                visible_damage=["Oil stain beneath pump", "Rust on mounting bolts"],
                safety_concerns=["Loose coupling guard"],
                maintenance_indicators=["Oil level appears low", "Belt shows wear"],
                confidence_score=0.78,
                extracted_text=["PUMP MODEL P-456", "MAX PRESSURE 150 PSI"]
            )
        else:
            return ImageAnalysisResult(
                asset_condition="good",
                visible_damage=[],
                safety_concerns=[],
                maintenance_indicators=["Regular maintenance recommended"],
                confidence_score=0.70,
                extracted_text=[]
            )
    
    def parse_maintenance_logs(self, log_text: str) -> List[MaintenanceLogEntry]:
        """Parse maintenance logs using NLP techniques."""
        
        entries = []
        
        # Split log into individual entries (assuming date-separated entries)
        date_pattern = r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}'
        log_sections = re.split(f'({date_pattern})', log_text)
        
        for i in range(1, len(log_sections), 2):
            if i + 1 < len(log_sections):
                date_str = log_sections[i]
                content = log_sections[i + 1]
                
                entry = self._parse_single_log_entry(date_str, content)
                if entry:
                    entries.append(entry)
        
        return entries
    
    def _parse_single_log_entry(self, date_str: str, content: str) -> Optional[MaintenanceLogEntry]:
        """Parse a single maintenance log entry."""
        
        try:
            # Extract technician name
            tech_pattern = r'(?:tech|technician|by|performed by):?\s*([A-Za-z\s]+)'
            tech_match = re.search(tech_pattern, content, re.IGNORECASE)
            technician = tech_match.group(1).strip() if tech_match else "Unknown"
            
            # Extract action performed
            action_keywords = ["replaced", "repaired", "inspected", "cleaned", "adjusted", "calibrated"]
            action = "Maintenance performed"
            for keyword in action_keywords:
                if keyword in content.lower():
                    action = f"{keyword.capitalize()} components"
                    break
            
            # Extract parts replaced
            parts_pattern = r'(?:replaced|changed|installed)\s+([^.]+)'
            parts_matches = re.findall(parts_pattern, content, re.IGNORECASE)
            parts_replaced = [part.strip() for part in parts_matches]
            
            # Extract issues found
            issue_keywords = ["issue", "problem", "fault", "failure", "damage", "wear"]
            issues_found = []
            for keyword in issue_keywords:
                if keyword in content.lower():
                    # Extract sentence containing the issue
                    sentences = content.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            issues_found.append(sentence.strip())
            
            # Extract recommendations
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
            return None
    
    async def analyze_historical_patterns(
        self,
        asset_id: str,
        inspection_history: List[Dict[str, Any]]
    ) -> List[HistoricalPattern]:
        """Analyze historical inspection data to identify patterns."""
        
        patterns = []
        
        if not inspection_history:
            return patterns
        
        # Analyze inspection frequency patterns
        dates = [datetime.fromisoformat(insp.get('date', '2024-01-01')) for insp in inspection_history]
        dates.sort()
        
        if len(dates) > 1:
            intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            avg_interval = sum(intervals) / len(intervals)
            
            if avg_interval < 35:
                frequency = "monthly"
            elif avg_interval < 95:
                frequency = "quarterly"
            elif avg_interval < 190:
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
        
        # Analyze condition trends
        conditions = []
        for insp in inspection_history:
            condition = insp.get('overall_condition', '').lower()
            if condition:
                conditions.append(condition)
        
        if conditions:
            condition_trend = self._analyze_condition_trend(conditions)
            patterns.append(condition_trend)
        
        # Analyze common issues
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
    
    def _analyze_condition_trend(self, conditions: List[str]) -> HistoricalPattern:
        """Analyze trend in asset conditions over time."""
        
        condition_scores = {
            "excellent": 5, "good": 4, "fair": 3, "poor": 2, "critical": 1
        }
        
        scores = []
        for condition in conditions:
            for level, score in condition_scores.items():
                if level in condition:
                    scores.append(score)
                    break
            else:
                scores.append(3)  # Default to fair
        
        if len(scores) < 2:
            trend = "stable"
        else:
            recent_avg = sum(scores[-3:]) / len(scores[-3:])
            older_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else recent_avg
            
            if recent_avg > older_avg + 0.5:
                trend = "improving"
            elif recent_avg < older_avg - 0.5:
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
        """Find commonly occurring issues."""
        
        issue_counts = {}
        for issue in issues:
            issue_lower = issue.lower()
            for keyword in self.safety_keywords:
                if keyword in issue_lower:
                    issue_counts[keyword] = issue_counts.get(keyword, 0) + 1
        
        # Return issues that occur more than once
        common_issues = [issue for issue, count in issue_counts.items() if count > 1]
        return common_issues[:5]  # Top 5 most common
    
    async def generate_intelligent_form_data(
        self,
        asset: Dict[str, Any],
        template: Dict[str, Any],
        image_analysis: Optional[ImageAnalysisResult] = None,
        maintenance_logs: Optional[List[MaintenanceLogEntry]] = None,
        historical_patterns: Optional[List[HistoricalPattern]] = None
    ) -> Dict[str, Any]:
        """Generate intelligent form data using all available information sources."""
        
        form_data = {}
        
        # Basic asset information
        form_data["asset_id"] = asset.get("id", "")
        form_data["asset_type"] = asset.get("type", "")
        form_data["inspection_date"] = datetime.now().isoformat()
        
        # Use image analysis if available
        if image_analysis:
            form_data["visual_condition"] = image_analysis.asset_condition
            form_data["visible_damage"] = ", ".join(image_analysis.visible_damage)
            form_data["safety_concerns"] = ", ".join(image_analysis.safety_concerns)
            
            # Extract specific measurements from OCR text
            for text in image_analysis.extracted_text:
                if "pressure" in text.lower():
                    pressure_match = re.search(r'(\d+\.?\d*)\s*psi', text.lower())
                    if pressure_match:
                        form_data["pressure_reading"] = pressure_match.group(1)
                
                if "voltage" in text.lower():
                    voltage_match = re.search(r'(\d+\.?\d*)\s*v', text.lower())
                    if voltage_match:
                        form_data["voltage_reading"] = voltage_match.group(1)
        
        # Use maintenance log information
        if maintenance_logs:
            recent_logs = maintenance_logs[-3:]  # Last 3 entries
            
            # Aggregate recent maintenance actions
            recent_actions = []
            recent_issues = []
            recent_recommendations = []
            
            for log in recent_logs:
                recent_actions.extend([log.action])
                recent_issues.extend(log.issues_found)
                recent_recommendations.extend(log.recommendations)
            
            form_data["recent_maintenance"] = ", ".join(recent_actions[:3])
            form_data["known_issues"] = ", ".join(recent_issues[:3])
            form_data["previous_recommendations"] = ", ".join(recent_recommendations[:3])
        
        # Use historical patterns
        if historical_patterns:
            for pattern in historical_patterns:
                if pattern.pattern_type == "condition_trend":
                    if pattern.trend_direction == "declining":
                        form_data["condition_trend"] = "Asset condition declining - increased monitoring recommended"
                    elif pattern.trend_direction == "improving":
                        form_data["condition_trend"] = "Asset condition improving - current maintenance effective"
                    else:
                        form_data["condition_trend"] = "Asset condition stable"
                
                elif pattern.pattern_type == "common_issues":
                    common_issues = pattern.typical_values.get("issues", [])
                    if common_issues:
                        form_data["recurring_issues"] = f"Watch for: {', '.join(common_issues[:3])}"
        
        # Generate intelligent recommendations
        recommendations = self._generate_intelligent_recommendations(
            asset, image_analysis, maintenance_logs, historical_patterns
        )
        form_data["ai_recommendations"] = recommendations
        
        # Predict next inspection date based on patterns
        next_inspection = self._predict_next_inspection_date(asset, historical_patterns)
        form_data["next_inspection_date"] = next_inspection
        
        return form_data
    
    def _generate_intelligent_recommendations(
        self,
        asset: Dict[str, Any],
        image_analysis: Optional[ImageAnalysisResult],
        maintenance_logs: Optional[List[MaintenanceLogEntry]],
        historical_patterns: Optional[List[HistoricalPattern]]
    ) -> str:
        """Generate intelligent maintenance recommendations."""
        
        recommendations = []
        
        # Image-based recommendations
        if image_analysis:
            if image_analysis.safety_concerns:
                recommendations.append("PRIORITY: Address safety concerns identified in visual inspection")
            
            if "corrosion" in " ".join(image_analysis.visible_damage).lower():
                recommendations.append("Apply corrosion protection treatment")
            
            if "leak" in " ".join(image_analysis.visible_damage).lower():
                recommendations.append("Investigate and repair leak source")
        
        # Maintenance log-based recommendations
        if maintenance_logs:
            recent_issues = []
            for log in maintenance_logs[-2:]:  # Last 2 entries
                recent_issues.extend(log.issues_found)
            
            if recent_issues:
                recommendations.append(f"Monitor for recurring issues: {', '.join(recent_issues[:2])}")
        
        # Historical pattern-based recommendations
        if historical_patterns:
            for pattern in historical_patterns:
                if pattern.pattern_type == "condition_trend" and pattern.trend_direction == "declining":
                    recommendations.append("Increase inspection frequency due to declining condition trend")
                
                elif pattern.pattern_type == "common_issues":
                    common_issues = pattern.typical_values.get("issues", [])
                    if common_issues:
                        recommendations.append(f"Preventive action for common issues: {', '.join(common_issues[:2])}")
        
        # Asset type-specific recommendations
        asset_type = asset.get("type", "").lower()
        if "electrical" in asset_type:
            recommendations.append("Verify electrical connections and insulation integrity")
        elif "mechanical" in asset_type:
            recommendations.append("Check lubrication levels and mechanical wear points")
        elif "pressure" in asset_type:
            recommendations.append("Verify pressure relief systems and safety valves")
        
        return "; ".join(recommendations) if recommendations else "Continue regular maintenance schedule"
    
    def _predict_next_inspection_date(
        self,
        asset: Dict[str, Any],
        historical_patterns: Optional[List[HistoricalPattern]]
    ) -> str:
        """Predict the next inspection date based on historical patterns."""
        
        # Default intervals based on asset criticality
        criticality = asset.get("criticality", "medium").lower()
        
        if criticality in ["high", "critical"]:
            default_days = 30  # Monthly for critical assets
        elif criticality == "medium":
            default_days = 90  # Quarterly for medium criticality
        else:
            default_days = 180  # Semi-annually for low criticality
        
        # Adjust based on historical patterns
        if historical_patterns:
            for pattern in historical_patterns:
                if pattern.pattern_type == "inspection_frequency":
                    avg_days = pattern.typical_values.get("average_days", default_days)
                    default_days = int(avg_days)
                    break
                
                elif pattern.pattern_type == "condition_trend":
                    if pattern.trend_direction == "declining":
                        default_days = int(default_days * 0.7)  # More frequent inspections
                    elif pattern.trend_direction == "improving":
                        default_days = int(default_days * 1.2)  # Less frequent inspections
        
        # Calculate next inspection date
        next_date = datetime.now() + timedelta(days=default_days)
        return next_date.isoformat()
    
    def extract_measurements_from_text(self, text: str) -> Dict[str, str]:
        """Extract numerical measurements from text using regex patterns."""
        
        measurements = {}
        
        # Pressure measurements
        pressure_pattern = r'(\d+\.?\d*)\s*(psi|bar|kpa|pascal)'
        pressure_matches = re.findall(pressure_pattern, text.lower())
        if pressure_matches:
            value, unit = pressure_matches[0]
            measurements["pressure"] = f"{value} {unit.upper()}"
        
        # Temperature measurements
        temp_pattern = r'(\d+\.?\d*)\s*(°?[cf]|celsius|fahrenheit)'
        temp_matches = re.findall(temp_pattern, text.lower())
        if temp_matches:
            value, unit = temp_matches[0]
            measurements["temperature"] = f"{value}°{unit[0].upper()}"
        
        # Voltage measurements
        voltage_pattern = r'(\d+\.?\d*)\s*(v|volt|voltage)'
        voltage_matches = re.findall(voltage_pattern, text.lower())
        if voltage_matches:
            value, unit = voltage_matches[0]
            measurements["voltage"] = f"{value}V"
        
        # Flow rate measurements
        flow_pattern = r'(\d+\.?\d*)\s*(gpm|lpm|cfm|m3/h)'
        flow_matches = re.findall(flow_pattern, text.lower())
        if flow_matches:
            value, unit = flow_matches[0]
            measurements["flow_rate"] = f"{value} {unit.upper()}"
        
        return measurements
    
    def assess_condition_from_multiple_sources(
        self,
        image_analysis: Optional[ImageAnalysisResult],
        maintenance_logs: Optional[List[MaintenanceLogEntry]],
        historical_patterns: Optional[List[HistoricalPattern]]
    ) -> Tuple[str, float]:
        """Assess overall asset condition from multiple information sources."""
        
        condition_scores = []
        confidence_scores = []
        
        # Image analysis contribution
        if image_analysis:
            condition_map = {
                "excellent": 5, "good": 4, "fair": 3, "poor": 2, "critical": 1
            }
            score = condition_map.get(image_analysis.asset_condition, 3)
            condition_scores.append(score)
            confidence_scores.append(image_analysis.confidence_score)
        
        # Maintenance log contribution
        if maintenance_logs:
            recent_issues = []
            for log in maintenance_logs[-2:]:
                recent_issues.extend(log.issues_found)
            
            if not recent_issues:
                condition_scores.append(4)  # Good if no recent issues
            elif len(recent_issues) <= 2:
                condition_scores.append(3)  # Fair if few issues
            else:
                condition_scores.append(2)  # Poor if many issues
            
            confidence_scores.append(0.7)
        
        # Historical pattern contribution
        if historical_patterns:
            for pattern in historical_patterns:
                if pattern.pattern_type == "condition_trend":
                    if pattern.trend_direction == "improving":
                        condition_scores.append(4)
                    elif pattern.trend_direction == "declining":
                        condition_scores.append(2)
                    else:
                        condition_scores.append(3)
                    
                    confidence_scores.append(pattern.confidence)
                    break
        
        # Calculate weighted average
        if condition_scores:
            weights = confidence_scores if confidence_scores else [1.0] * len(condition_scores)
            weighted_score = sum(s * w for s, w in zip(condition_scores, weights)) / sum(weights)
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        else:
            weighted_score = 3.0  # Default to fair
            overall_confidence = 0.5
        
        # Convert score back to condition
        if weighted_score >= 4.5:
            condition = "excellent"
        elif weighted_score >= 3.5:
            condition = "good"
        elif weighted_score >= 2.5:
            condition = "fair"
        elif weighted_score >= 1.5:
            condition = "poor"
        else:
            condition = "critical"
        
        return condition, overall_confidence
