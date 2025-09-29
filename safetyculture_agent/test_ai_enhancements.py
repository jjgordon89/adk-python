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

"""
Test script for AI-enhanced SafetyCulture Agent capabilities

This script tests the new Smart Template Selection and Enhanced Form Intelligence features.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List

from .ai.template_matcher import AITemplateMatcher, AssetProfile
from .ai.form_intelligence import EnhancedFormIntelligence
from .ai.ai_tools import (
    ai_match_templates_to_asset,
    generate_dynamic_template_for_asset,
    analyze_asset_image_for_inspection,
    parse_maintenance_logs_for_insights,
    analyze_historical_inspection_patterns,
    generate_intelligent_inspection_data
)


# Test data
SAMPLE_ASSET = {
    "id": "PUMP_001",
    "type": "Centrifugal Pump",
    "name": "Main Cooling Water Pump",
    "description": "Primary cooling water circulation pump for reactor cooling system",
    "location": "Pump House A",
    "criticality": "high",
    "compliance_requirements": [
        "ASME Boiler and Pressure Vessel Code",
        "OSHA 29 CFR 1910.147",
        "API 610 Centrifugal Pumps"
    ],
    "maintenance_history": [
        "2024-01-15: Replaced impeller and shaft seals",
        "2024-02-20: Lubrication service performed",
        "2024-03-10: Vibration analysis completed - normal readings"
    ],
    "custom_attributes": {
        "flow_rate": "500 GPM",
        "head": "150 ft",
        "power": "25 HP"
    }
}

SAMPLE_TEMPLATES = [
    {
        "template_id": "TMPL_PUMP_001",
        "name": "Centrifugal Pump Inspection",
        "description": "Standard inspection template for centrifugal pumps",
        "items": [
            {"label": "Pump Vibration Check", "type": "textsingle"},
            {"label": "Seal Condition", "type": "textsingle"},
            {"label": "Lubrication Level", "type": "textsingle"},
            {"label": "Flow Rate Measurement", "type": "textsingle"}
        ]
    },
    {
        "template_id": "TMPL_GEN_001",
        "name": "General Equipment Inspection",
        "description": "Generic inspection template for all equipment",
        "items": [
            {"label": "Visual Condition", "type": "textsingle"},
            {"label": "Safety Check", "type": "checkbox"},
            {"label": "General Notes", "type": "textsingle"}
        ]
    },
    {
        "template_id": "TMPL_SAFETY_001",
        "name": "Safety Critical Equipment Inspection",
        "description": "Enhanced inspection for safety-critical equipment",
        "items": [
            {"label": "Safety System Test", "type": "checkbox"},
            {"label": "Emergency Shutdown Test", "type": "checkbox"},
            {"label": "Compliance Verification", "type": "checkbox"},
            {"label": "Risk Assessment", "type": "textsingle"}
        ]
    }
]

SAMPLE_MAINTENANCE_LOG = """
2024-01-15: Technician: John Smith
Replaced impeller and shaft seals due to excessive wear. Found minor corrosion on impeller blades.
Recommend monitoring for cavitation. Parts replaced: impeller assembly, mechanical seal kit.

2024-02-20: Technician: Mary Johnson  
Performed routine lubrication service. Oil level was low, topped up with ISO 46 hydraulic oil.
No issues found during inspection. Recommend checking oil level weekly.

2024-03-10: Technician: Bob Wilson
Completed vibration analysis using portable analyzer. Readings within normal range.
Slight increase in bearing frequencies noted. Recommend continued monitoring.
"""

SAMPLE_INSPECTION_HISTORY = [
    {
        "date": "2024-01-01",
        "overall_condition": "good",
        "issues_found": ["Minor oil leak", "Loose mounting bolt"],
        "inspector": "Jane Doe"
    },
    {
        "date": "2024-02-01", 
        "overall_condition": "good",
        "issues_found": ["Vibration slightly elevated"],
        "inspector": "John Smith"
    },
    {
        "date": "2024-03-01",
        "overall_condition": "fair",
        "issues_found": ["Seal weepage", "Bearing noise"],
        "inspector": "Mary Johnson"
    }
]


async def test_ai_template_matching():
    """Test AI-powered template matching."""
    print("Testing AI Template Matching...")
    
    try:
        result = await ai_match_templates_to_asset(SAMPLE_ASSET, SAMPLE_TEMPLATES)
        result_data = json.loads(result)
        
        print(f"✓ Template matching completed")
        print(f"  Asset ID: {result_data['asset_id']}")
        print(f"  Templates evaluated: {len(result_data['matches'])}")
        
        if result_data['best_match']:
            best_match = result_data['best_match']
            print(f"  Best match: {best_match['template_id']} (confidence: {best_match['confidence']:.2f})")
        
        # Display top 3 matches
        for i, match in enumerate(result_data['matches'][:3]):
            print(f"  {i+1}. {match['template_name']} - {match['confidence_score']:.2f}")
            print(f"     Reasons: {', '.join(match['match_reasons'][:2])}")
        
        return True
    
    except Exception as e:
        print(f"✗ Template matching failed: {e}")
        return False


async def test_dynamic_template_generation():
    """Test dynamic template generation."""
    print("\nTesting Dynamic Template Generation...")
    
    try:
        result = await generate_dynamic_template_for_asset(SAMPLE_ASSET)
        template_data = json.loads(result)
        
        print(f"✓ Dynamic template generated")
        print(f"  Template ID: {template_data['template_id']}")
        print(f"  Template Name: {template_data['name']}")
        print(f"  Fields generated: {len(template_data['items'])}")
        
        # Show some generated fields
        for i, item in enumerate(template_data['items'][:5]):
            print(f"  {i+1}. {item['label']} ({item['type']})")
        
        return True
    
    except Exception as e:
        print(f"✗ Dynamic template generation failed: {e}")
        return False


async def test_image_analysis():
    """Test computer vision image analysis."""
    print("\nTesting Image Analysis...")
    
    try:
        # Simulate base64 image data
        fake_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        result = await analyze_asset_image_for_inspection(fake_image_data, SAMPLE_ASSET["type"])
        analysis_data = json.loads(result)
        
        print(f"✓ Image analysis completed")
        print(f"  Asset condition: {analysis_data['asset_condition']}")
        print(f"  Visible damage: {len(analysis_data['visible_damage'])} items")
        print(f"  Safety concerns: {len(analysis_data['safety_concerns'])} items")
        print(f"  Confidence: {analysis_data['confidence_score']:.2f}")
        
        if analysis_data['extracted_text']:
            print(f"  Extracted text: {', '.join(analysis_data['extracted_text'][:3])}")
        
        return True
    
    except Exception as e:
        print(f"✗ Image analysis failed: {e}")
        return False


async def test_maintenance_log_parsing():
    """Test NLP maintenance log parsing."""
    print("\nTesting Maintenance Log Parsing...")
    
    try:
        result = await parse_maintenance_logs_for_insights(SAMPLE_MAINTENANCE_LOG)
        log_data = json.loads(result)
        
        print(f"✓ Maintenance log parsing completed")
        print(f"  Total entries parsed: {log_data['total_entries']}")
        
        for i, entry in enumerate(log_data['entries']):
            print(f"  Entry {i+1}: {entry['date']} - {entry['action']}")
            print(f"    Technician: {entry['technician']}")
            if entry['parts_replaced']:
                print(f"    Parts: {', '.join(entry['parts_replaced'][:2])}")
        
        return True
    
    except Exception as e:
        print(f"✗ Maintenance log parsing failed: {e}")
        return False


async def test_historical_pattern_analysis():
    """Test historical pattern analysis."""
    print("\nTesting Historical Pattern Analysis...")
    
    try:
        result = await analyze_historical_inspection_patterns(
            SAMPLE_ASSET["id"], 
            SAMPLE_INSPECTION_HISTORY
        )
        pattern_data = json.loads(result)
        
        print(f"✓ Historical pattern analysis completed")
        print(f"  Asset ID: {pattern_data['asset_id']}")
        print(f"  Patterns found: {pattern_data['patterns_found']}")
        
        for pattern in pattern_data['patterns']:
            print(f"  - {pattern['pattern_type']}: {pattern['trend_direction']} trend")
            print(f"    Confidence: {pattern['confidence']:.2f}")
        
        return True
    
    except Exception as e:
        print(f"✗ Historical pattern analysis failed: {e}")
        return False


async def test_intelligent_form_generation():
    """Test comprehensive intelligent form data generation."""
    print("\nTesting Intelligent Form Data Generation...")
    
    try:
        # Use the best template from our sample
        template = SAMPLE_TEMPLATES[0]
        fake_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        result = await generate_intelligent_inspection_data(
            SAMPLE_ASSET,
            template,
            fake_image,
            SAMPLE_MAINTENANCE_LOG,
            SAMPLE_INSPECTION_HISTORY
        )
        form_data = json.loads(result)
        
        print(f"✓ Intelligent form data generation completed")
        print(f"  Asset ID: {form_data['asset_id']}")
        print(f"  Template ID: {form_data['template_id']}")
        
        sources_used = form_data['data_sources_used']
        print(f"  Data sources used:")
        print(f"    Image analysis: {sources_used['image_analysis']}")
        print(f"    Maintenance logs: {sources_used['maintenance_logs']}")
        print(f"    Historical patterns: {sources_used['historical_patterns']}")
        
        # Show some generated form fields
        form_fields = form_data['form_data']
        print(f"  Generated fields: {len(form_fields)}")
        for key, value in list(form_fields.items())[:5]:
            print(f"    {key}: {str(value)[:50]}...")
        
        return True
    
    except Exception as e:
        print(f"✗ Intelligent form generation failed: {e}")
        return False


async def test_template_matcher_class():
    """Test the AITemplateMatcher class directly."""
    print("\nTesting AITemplateMatcher Class...")
    
    try:
        matcher = AITemplateMatcher()
        
        # Create asset profile
        asset_profile = AssetProfile(
            asset_id=SAMPLE_ASSET["id"],
            asset_type=SAMPLE_ASSET["type"],
            asset_name=SAMPLE_ASSET["name"],
            description=SAMPLE_ASSET["description"],
            location=SAMPLE_ASSET["location"],
            criticality=SAMPLE_ASSET["criticality"],
            compliance_requirements=SAMPLE_ASSET["compliance_requirements"],
            maintenance_history=SAMPLE_ASSET["maintenance_history"],
            custom_attributes=SAMPLE_ASSET["custom_attributes"]
        )
        
        # Test embedding generation
        embedding = await matcher.generate_embedding("centrifugal pump mechanical equipment")
        print(f"✓ Embedding generation: {len(embedding)} features")
        
        # Test template matching
        matches = await matcher.match_templates_to_asset(asset_profile, SAMPLE_TEMPLATES)
        print(f"✓ Template matching: {len(matches)} matches found")
        
        # Test dynamic template generation
        dynamic_template = await matcher.generate_dynamic_template(asset_profile)
        print(f"✓ Dynamic template: {len(dynamic_template['items'])} fields generated")
        
        return True
    
    except Exception as e:
        print(f"✗ AITemplateMatcher class test failed: {e}")
        return False


async def test_form_intelligence_class():
    """Test the EnhancedFormIntelligence class directly."""
    print("\nTesting EnhancedFormIntelligence Class...")
    
    try:
        form_intel = EnhancedFormIntelligence()
        
        # Test maintenance log parsing
        entries = form_intel.parse_maintenance_logs(SAMPLE_MAINTENANCE_LOG)
        print(f"✓ Maintenance log parsing: {len(entries)} entries")
        
        # Test historical pattern analysis
        patterns = await form_intel.analyze_historical_patterns(
            SAMPLE_ASSET["id"], 
            SAMPLE_INSPECTION_HISTORY
        )
        print(f"✓ Pattern analysis: {len(patterns)} patterns identified")
        
        # Test measurement extraction
        measurements = form_intel.extract_measurements_from_text(
            "Pressure reading: 150 PSI, Temperature: 75°F, Voltage: 480V"
        )
        print(f"✓ Measurement extraction: {len(measurements)} measurements")
        
        return True
    
    except Exception as e:
        print(f"✗ EnhancedFormIntelligence class test failed: {e}")
        return False


async def run_all_ai_tests():
    """Run all AI enhancement tests."""
    print("SafetyCulture AI Enhancements - Test Suite")
    print("=" * 60)
    
    tests = [
        ("AI Template Matching", test_ai_template_matching),
        ("Dynamic Template Generation", test_dynamic_template_generation),
        ("Image Analysis", test_image_analysis),
        ("Maintenance Log Parsing", test_maintenance_log_parsing),
        ("Historical Pattern Analysis", test_historical_pattern_analysis),
        ("Intelligent Form Generation", test_intelligent_form_generation),
        ("AITemplateMatcher Class", test_template_matcher_class),
        ("EnhancedFormIntelligence Class", test_form_intelligence_class)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("AI Enhancement Test Results:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:35} : {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All AI enhancement tests passed! The new capabilities are working correctly.")
        print("\n🚀 New AI Features Available:")
        print("   • Smart Template Selection with semantic matching")
        print("   • Dynamic Template Generation based on asset characteristics")
        print("   • Computer Vision integration for asset image analysis")
        print("   • NLP-powered maintenance log parsing")
        print("   • Historical pattern analysis and trend detection")
        print("   • Intelligent form data generation using multiple sources")
    else:
        print("⚠️  Some AI enhancement tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(run_all_ai_tests())
