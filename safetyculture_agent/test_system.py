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
Test script for SafetyCulture Agent System

This script provides basic validation of the system components
without requiring actual SafetyCulture API credentials.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

from .config.api_config import DEFAULT_CONFIG
from .config.business_rules import FIELD_MAPPING_RULES, ASSET_TYPE_TEMPLATE_MAPPING
from .tools.safetyculture_api_client import SafetyCultureAPIClient


async def test_api_client_initialization():
    """Test that the API client can be initialized properly."""
    print("Testing API client initialization...")
    
    try:
        async with SafetyCultureAPIClient(DEFAULT_CONFIG) as client:
            print("✓ API client initialized successfully")
            print(f"  Base URL: {client.config.base_url}")
            print(f"  Request timeout: {client.config.request_timeout}s")
            print(f"  Rate limit: {client.config.requests_per_second} req/s")
            return True
    except Exception as e:
        print(f"✗ API client initialization failed: {e}")
        return False


def test_configuration():
    """Test that configuration is loaded properly."""
    print("\nTesting configuration...")
    
    try:
        # Test API config
        print(f"✓ API config loaded")
        print(f"  Base URL: {DEFAULT_CONFIG.base_url}")
        print(f"  Headers configured: {len(DEFAULT_CONFIG.headers)} headers")
        
        # Test business rules
        print(f"✓ Business rules loaded")
        print(f"  Field mappings: {len(FIELD_MAPPING_RULES)} rules")
        print(f"  Asset-template mappings: {len(ASSET_TYPE_TEMPLATE_MAPPING)} mappings")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


async def test_memory_tools():
    """Test memory tool functions."""
    print("\nTesting memory tools...")
    
    try:
        from .memory.memory_tools import (
            store_asset_registry,
            retrieve_asset_registry,
            store_template_library
        )
        
        # Test storing assets
        test_assets = [
            {"id": "asset_1", "type": "Equipment", "name": "Test Asset 1"},
            {"id": "asset_2", "type": "Vehicle", "name": "Test Asset 2"}
        ]
        
        result = await store_asset_registry(test_assets, "test_registry")
        print(f"✓ Asset storage test: {result}")
        
        # Test retrieving assets
        result = await retrieve_asset_registry("test_registry", "Equipment")
        print(f"✓ Asset retrieval test: {result[:100]}...")
        
        return True
    except Exception as e:
        print(f"✗ Memory tools test failed: {e}")
        return False


def test_agent_imports():
    """Test that all agents can be imported."""
    print("\nTesting agent imports...")
    
    try:
        from .agents.asset_discovery_agent import asset_discovery_agent
        from .agents.template_selection_agent import template_selection_agent
        from .agents.inspection_creation_agent import inspection_creation_agent
        from .agents.form_filling_agent import form_filling_agent
        from .agent import root_agent
        
        print(f"✓ AssetDiscoveryAgent: {asset_discovery_agent.name}")
        print(f"✓ TemplateSelectionAgent: {template_selection_agent.name}")
        print(f"✓ InspectionCreationAgent: {inspection_creation_agent.name}")
        print(f"✓ FormFillingAgent: {form_filling_agent.name}")
        print(f"✓ Root agent: {root_agent.name}")
        
        return True
    except Exception as e:
        print(f"✗ Agent import test failed: {e}")
        return False


def test_tools_import():
    """Test that all tools can be imported."""
    print("\nTesting tools import...")
    
    try:
        from .tools.safetyculture_tools import (
            search_safetyculture_assets,
            get_safetyculture_asset_details,
            search_safetyculture_templates,
            create_safetyculture_inspection,
            update_safetyculture_inspection
        )
        
        print("✓ All SafetyCulture tools imported successfully")
        print(f"  - search_safetyculture_assets: {search_safetyculture_assets.__name__}")
        print(f"  - get_safetyculture_asset_details: {get_safetyculture_asset_details.__name__}")
        print(f"  - search_safetyculture_templates: {search_safetyculture_templates.__name__}")
        print(f"  - create_safetyculture_inspection: {create_safetyculture_inspection.__name__}")
        print(f"  - update_safetyculture_inspection: {update_safetyculture_inspection.__name__}")
        
        return True
    except Exception as e:
        print(f"✗ Tools import test failed: {e}")
        return False


async def run_all_tests():
    """Run all system tests."""
    print("SafetyCulture Agent System - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Tools Import", test_tools_import),
        ("Agent Imports", test_agent_imports),
        ("API Client", test_api_client_initialization),
        ("Memory Tools", test_memory_tools)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the configuration and dependencies.")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(run_all_tests())
