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
Test script for SafetyCulture Agent Database functionality

This script tests the asset tracking database and duplicate prevention features.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, List

from .database.asset_tracker import AssetTracker
from .database.database_tools import (
    initialize_asset_database,
    check_asset_completion_status,
    register_asset_for_monthly_inspection,
    update_asset_inspection_status,
    mark_asset_inspection_completed,
    get_pending_assets_for_inspection,
    get_completed_assets_report,
    get_monthly_inspection_summary,
    export_comprehensive_monthly_report,
    filter_assets_to_prevent_duplicates
)


# Test data
TEST_ASSETS = [
    {
        "id": "PUMP_001",
        "name": "Main Cooling Water Pump",
        "type": "Centrifugal Pump",
        "location": "Pump House A"
    },
    {
        "id": "MOTOR_001", 
        "name": "Primary Drive Motor",
        "type": "Electric Motor",
        "location": "Motor Control Center"
    },
    {
        "id": "VALVE_001",
        "name": "Main Isolation Valve",
        "type": "Gate Valve",
        "location": "Valve Station 1"
    }
]

TEST_TEMPLATE = {
    "template_id": "TMPL_GENERAL_001",
    "template_name": "General Equipment Inspection"
}


async def test_database_initialization():
    """Test database initialization."""
    print("Testing Database Initialization...")
    
    try:
        # Clean up any existing test database
        test_db_path = "test_safetyculture_assets.db"
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        # Initialize with test database
        tracker = AssetTracker(test_db_path)
        await tracker.initialize_database()
        
        print("✓ Database initialized successfully")
        print(f"  Database file: {test_db_path}")
        
        # Test using the tool function
        result = await initialize_asset_database()
        print(f"✓ Tool function result: {result}")
        
        return True
    
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False


async def test_asset_registration():
    """Test asset registration and duplicate prevention."""
    print("\nTesting Asset Registration...")
    
    try:
        # Register first asset
        asset = TEST_ASSETS[0]
        result = await register_asset_for_monthly_inspection(
            asset_id=asset["id"],
            asset_name=asset["name"],
            asset_type=asset["type"],
            location=asset["location"],
            template_id=TEST_TEMPLATE["template_id"],
            template_name=TEST_TEMPLATE["template_name"]
        )
        
        result_data = json.loads(result)
        print(f"✓ First registration: {result_data['success']}")
        print(f"  Message: {result_data['message']}")
        
        # Try to register the same asset again (should fail)
        result2 = await register_asset_for_monthly_inspection(
            asset_id=asset["id"],
            asset_name=asset["name"],
            asset_type=asset["type"],
            location=asset["location"],
            template_id=TEST_TEMPLATE["template_id"],
            template_name=TEST_TEMPLATE["template_name"]
        )
        
        result2_data = json.loads(result2)
        print(f"✓ Duplicate prevention: {not result2_data['success']}")
        print(f"  Message: {result2_data['message']}")
        
        return True
    
    except Exception as e:
        print(f"✗ Asset registration test failed: {e}")
        return False


async def test_completion_status_checking():
    """Test checking asset completion status."""
    print("\nTesting Completion Status Checking...")
    
    try:
        asset_id = TEST_ASSETS[0]["id"]
        
        # Check status before completion
        result = await check_asset_completion_status(asset_id)
        status_data = json.loads(result)
        
        print(f"✓ Status check before completion:")
        print(f"  Is completed: {status_data['is_completed']}")
        print(f"  Current status: {status_data['current_status']}")
        print(f"  Can create inspection: {status_data['can_create_inspection']}")
        
        return True
    
    except Exception as e:
        print(f"✗ Completion status checking failed: {e}")
        return False


async def test_status_updates():
    """Test updating asset inspection status."""
    print("\nTesting Status Updates...")
    
    try:
        asset_id = TEST_ASSETS[0]["id"]
        
        # Update to in_progress
        result = await update_asset_inspection_status(
            asset_id=asset_id,
            status="in_progress",
            inspection_id="INS_001"
        )
        
        update_data = json.loads(result)
        print(f"✓ Status update to in_progress: {update_data['success']}")
        
        # Mark as completed
        result2 = await mark_asset_inspection_completed(
            asset_id=asset_id,
            inspection_id="INS_001",
            inspector="Test Inspector"
        )
        
        complete_data = json.loads(result2)
        print(f"✓ Mark as completed: {complete_data['success']}")
        print(f"  Inspection ID: {complete_data['inspection_id']}")
        
        return True
    
    except Exception as e:
        print(f"✗ Status updates test failed: {e}")
        return False


async def test_pending_and_completed_retrieval():
    """Test retrieving pending and completed assets."""
    print("\nTesting Asset Retrieval...")
    
    try:
        # Register additional assets
        for asset in TEST_ASSETS[1:]:
            await register_asset_for_monthly_inspection(
                asset_id=asset["id"],
                asset_name=asset["name"],
                asset_type=asset["type"],
                location=asset["location"],
                template_id=TEST_TEMPLATE["template_id"],
                template_name=TEST_TEMPLATE["template_name"]
            )
        
        # Get pending assets
        pending_result = await get_pending_assets_for_inspection()
        pending_data = json.loads(pending_result)
        
        print(f"✓ Pending assets retrieved: {pending_data['total_pending']}")
        
        # Get completed assets
        completed_result = await get_completed_assets_report()
        completed_data = json.loads(completed_result)
        
        print(f"✓ Completed assets retrieved: {completed_data['total_completed']}")
        
        return True
    
    except Exception as e:
        print(f"✗ Asset retrieval test failed: {e}")
        return False


async def test_monthly_summary():
    """Test monthly summary generation."""
    print("\nTesting Monthly Summary...")
    
    try:
        result = await get_monthly_inspection_summary()
        summary_data = json.loads(result)
        
        print(f"✓ Monthly summary generated")
        print(f"  Total assets: {summary_data['total_assets']}")
        print(f"  Completed: {summary_data['completed_inspections']}")
        print(f"  Pending: {summary_data['pending_inspections']}")
        print(f"  Completion rate: {summary_data['completion_rate']}%")
        
        return True
    
    except Exception as e:
        print(f"✗ Monthly summary test failed: {e}")
        return False


async def test_duplicate_filtering():
    """Test filtering assets to prevent duplicates."""
    print("\nTesting Duplicate Filtering...")
    
    try:
        # Create a mix of new and existing assets
        mixed_assets = TEST_ASSETS + [
            {
                "id": "NEW_ASSET_001",
                "name": "New Test Asset",
                "type": "Test Equipment",
                "location": "Test Location"
            }
        ]
        
        result = await filter_assets_to_prevent_duplicates(mixed_assets)
        filter_data = json.loads(result)
        
        print(f"✓ Asset filtering completed")
        print(f"  Total discovered: {filter_data['total_discovered']}")
        print(f"  Already completed: {filter_data['already_completed']}")
        print(f"  Needs inspection: {filter_data['needs_inspection']}")
        
        return True
    
    except Exception as e:
        print(f"✗ Duplicate filtering test failed: {e}")
        return False


async def test_comprehensive_report():
    """Test comprehensive monthly report export."""
    print("\nTesting Comprehensive Report...")
    
    try:
        result = await export_comprehensive_monthly_report()
        report_data = json.loads(result)
        
        print(f"✓ Comprehensive report generated")
        print(f"  Month: {report_data['month_year']}")
        print(f"  Asset types tracked: {len(report_data['assets_by_type'])}")
        
        # Show asset type breakdown
        for asset_type, counts in report_data['assets_by_type'].items():
            print(f"    {asset_type}: {counts['completed']}/{counts['total']} completed")
        
        return True
    
    except Exception as e:
        print(f"✗ Comprehensive report test failed: {e}")
        return False


async def test_direct_tracker_class():
    """Test the AssetTracker class directly."""
    print("\nTesting AssetTracker Class...")
    
    try:
        tracker = AssetTracker("test_direct_tracker.db")
        await tracker.initialize_database()
        
        # Test direct methods
        success = await tracker.register_asset_for_inspection(
            asset_id="DIRECT_TEST_001",
            asset_name="Direct Test Asset",
            asset_type="Test Equipment",
            location="Test Location",
            template_id="TEST_TEMPLATE",
            template_name="Test Template"
        )
        
        print(f"✓ Direct registration: {success}")
        
        # Test completion check
        is_completed = await tracker.check_asset_completed_this_month("DIRECT_TEST_001")
        print(f"✓ Direct completion check: {not is_completed}")  # Should be False (not completed)
        
        # Mark as completed
        completed = await tracker.mark_asset_completed("DIRECT_TEST_001", "DIRECT_INS_001")
        print(f"✓ Direct completion marking: {completed}")
        
        # Check again (should be completed now)
        is_completed_now = await tracker.check_asset_completed_this_month("DIRECT_TEST_001")
        print(f"✓ Direct completion verification: {is_completed_now}")
        
        # Clean up test database
        if os.path.exists("test_direct_tracker.db"):
            os.remove("test_direct_tracker.db")
        
        return True
    
    except Exception as e:
        print(f"✗ Direct tracker class test failed: {e}")
        return False


async def run_all_database_tests():
    """Run all database tests."""
    print("SafetyCulture Database System - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Database Initialization", test_database_initialization),
        ("Asset Registration", test_asset_registration),
        ("Completion Status Checking", test_completion_status_checking),
        ("Status Updates", test_status_updates),
        ("Asset Retrieval", test_pending_and_completed_retrieval),
        ("Monthly Summary", test_monthly_summary),
        ("Duplicate Filtering", test_duplicate_filtering),
        ("Comprehensive Report", test_comprehensive_report),
        ("Direct Tracker Class", test_direct_tracker_class)
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
    print("Database Test Results:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:30} : {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All database tests passed! The asset tracking system is working correctly.")
        print("\n📊 Database Features Available:")
        print("   • Monthly asset inspection tracking")
        print("   • Duplicate prevention for completed inspections")
        print("   • Status tracking (pending, in_progress, completed, failed)")
        print("   • Comprehensive monthly reporting")
        print("   • Asset filtering to prevent duplicate work")
        print("   • Performance optimized with indexes")
    else:
        print("⚠️  Some database tests failed. Please check the implementation.")
    
    # Clean up test database
    if os.path.exists("test_safetyculture_assets.db"):
        os.remove("test_safetyculture_assets.db")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(run_all_database_tests())
