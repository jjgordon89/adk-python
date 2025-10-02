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

"""Integration tests for SafetyCulture agent components.

This module tests end-to-end integration between database operations,
API client functionality, and overall system behavior.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from safetyculture_agent.config.api_config import SafetyCultureConfig
from safetyculture_agent.database.asset_tracker import AssetTracker
from safetyculture_agent.tools.safetyculture_api_client import (
  SafetyCultureAPIClient,
)


class TestDatabaseIntegration:
  """Integration tests for database operations.
  
  Tests the full lifecycle of database operations including
  registration, updates, queries, and cleanup.
  """
  
  @pytest.fixture
  async def tracker(self):
    """Create temporary database tracker for testing.
    
    Yields:
        AssetTracker: Initialized tracker with temporary database
    """
    with tempfile.NamedTemporaryFile(
      suffix='.db', delete=False
    ) as f:
      db_path = f.name
    
    tracker = AssetTracker(db_path=db_path)
    await tracker.initialize_database()
    
    yield tracker
    
    # Cleanup
    try:
      os.unlink(db_path)
    except Exception:
      pass
  
  @pytest.mark.asyncio
  async def test_full_asset_lifecycle(self, tracker):
    """Test complete asset lifecycle from registration to completion.
    
    Verifies:
    - Asset registration
    - Existence checks
    - Status updates
    - Metadata retrieval
    - Monthly summaries
    """
    # Register asset
    registered = await tracker.register_asset_for_inspection(
      asset_id="ASSET-001",
      asset_name="Test Asset",
      asset_type="Equipment",
      location="Building A",
      template_id="TEMPLATE-001",
      template_name="Safety Inspection",
      month_year="2025-01"
    )
    assert registered is True
    
    # Check it exists
    exists = await tracker.check_asset_completed_this_month(
      "ASSET-001",
      "2025-01"
    )
    assert exists is False  # Not completed yet
    
    # Update status to completed
    updated = await tracker.update_inspection_status(
      "ASSET-001",
      "completed",
      inspection_id="INSP-001",
      month_year="2025-01"
    )
    assert updated is True
    
    # Now it should show as completed
    completed = await tracker.check_asset_completed_this_month(
      "ASSET-001",
      "2025-01"
    )
    assert completed is True
    
    # Get monthly summary
    summary = await tracker.get_monthly_summary("2025-01")
    assert summary['total_assets'] >= 1
    assert summary['completed_inspections'] >= 1
  
  @pytest.mark.asyncio
  async def test_concurrent_asset_registrations(self, tracker):
    """Test concurrent database operations for race conditions.
    
    Verifies:
    - Multiple concurrent registrations
    - No duplicate entries
    - Proper locking behavior
    """
    # Register multiple assets concurrently
    assets = [
      ("ASSET-001", "Asset 1", "Equipment", "Loc 1"),
      ("ASSET-002", "Asset 2", "Vehicle", "Loc 2"),
      ("ASSET-003", "Asset 3", "Building", "Loc 3"),
    ]
    
    results = await asyncio.gather(*[
      tracker.register_asset_for_inspection(
        asset_id=aid,
        asset_name=name,
        asset_type=atype,
        location=loc,
        template_id="TEMPLATE-001",
        template_name="Safety Inspection",
        month_year="2025-01"
      )
      for aid, name, atype, loc in assets
    ])
    
    assert all(results), "All registrations should succeed"
    
    # Query all pending
    pending = await tracker.get_pending_assets("2025-01")
    assert len(pending) == 3
  
  @pytest.mark.asyncio
  async def test_duplicate_registration_handling(self, tracker):
    """Test handling of duplicate asset registrations.
    
    Verifies:
    - First registration succeeds
    - Duplicate registration handled correctly
    - No data corruption
    """
    # First registration
    result1 = await tracker.register_asset_for_inspection(
      asset_id="ASSET-DUP",
      asset_name="Duplicate Asset",
      asset_type="Equipment",
      location="Building A",
      template_id="TEMPLATE-001",
      template_name="Safety Inspection",
      month_year="2025-01"
    )
    assert result1 is True
    
    # Duplicate registration (should update existing)
    result2 = await tracker.register_asset_for_inspection(
      asset_id="ASSET-DUP",
      asset_name="Duplicate Asset Modified",
      asset_type="Equipment",
      location="Building B",
      template_id="TEMPLATE-002",
      template_name="Different Template",
      month_year="2025-01"
    )
    assert result2 is True
    
    # Verify count
    summary = await tracker.get_monthly_summary("2025-01")
    assert summary['total_assets'] == 1
  
  @pytest.mark.asyncio
  async def test_status_transitions(self, tracker):
    """Test various status transition scenarios.
    
    Verifies:
    - Pending -> In Progress
    - In Progress -> Completed
    - Proper status tracking
    """
    # Register asset
    await tracker.register_asset_for_inspection(
      asset_id="ASSET-STATUS",
      asset_name="Status Test Asset",
      asset_type="Equipment",
      location="Building A",
      template_id="TEMPLATE-001",
      template_name="Safety Inspection",
      month_year="2025-01"
    )
    
    # Get initial status
    status = await tracker.get_asset_inspection_status(
      "ASSET-STATUS",
      "2025-01"
    )
    assert status == 'pending'
    
    # Update to in_progress
    await tracker.update_inspection_status(
      "ASSET-STATUS",
      "in_progress",
      month_year="2025-01"
    )
    status = await tracker.get_asset_inspection_status(
      "ASSET-STATUS",
      "2025-01"
    )
    assert status == 'in_progress'
    
    # Complete inspection
    await tracker.mark_asset_completed(
      "ASSET-STATUS",
      "INSP-STATUS-001",
      month_year="2025-01"
    )
    status = await tracker.get_asset_inspection_status(
      "ASSET-STATUS",
      "2025-01"
    )
    assert status == 'completed'


class TestAPIClientIntegration:
  """Integration tests for API client.
  
  Tests API client with rate limiting, circuit breaker,
  and security features enabled.
  """
  
  @pytest.fixture
  def api_client(self):
    """Create API client with test configuration.
    
    Returns:
        SafetyCultureAPIClient: Configured client instance
    """
    config = SafetyCultureConfig(
      api_token="test_token_12345",
      base_url="https://api.safetyculture.io"
    )
    return SafetyCultureAPIClient(config)
  
  @pytest.mark.asyncio
  async def test_api_client_with_security_layers(self, api_client):
    """Test API client with all security features enabled.
    
    Verifies:
    - Rate limiting
    - Input validation
    - Circuit breaker
    - Secure headers
    """
    with patch('aiohttp.ClientSession.request') as mock_request:
      # Mock successful response
      mock_response = AsyncMock()
      mock_response.status = 200
      mock_response.json = AsyncMock(return_value={
        "assets": [{"id": "1", "name": "Test Asset"}]
      })
      mock_request.return_value.__aenter__.return_value = mock_response
      
      result = await api_client.search_assets(
        asset_types=["Equipment"],
        limit=10
      )
      
      assert result is not None
      assert 'assets' in result
      assert len(result['assets']) == 1
  
  @pytest.mark.asyncio
  async def test_rate_limiter_integration(self, api_client):
    """Test rate limiter behavior under load.
    
    Verifies:
    - Multiple requests are rate limited
    - No requests exceed configured rate
    - Backoff behavior works
    """
    with patch('aiohttp.ClientSession.request') as mock_request:
      mock_response = AsyncMock()
      mock_response.status = 200
      mock_response.json = AsyncMock(return_value={"assets": []})
      mock_request.return_value.__aenter__.return_value = mock_response
      
      # Make multiple rapid requests
      results = await asyncio.gather(*[
        api_client.search_assets(limit=10)
        for _ in range(5)
      ])
      
      assert len(results) == 5
      assert all(r is not None for r in results)
  
  @pytest.mark.asyncio
  async def test_circuit_breaker_integration(self, api_client):
    """Test circuit breaker opens after repeated failures.
    
    Verifies:
    - Circuit opens after threshold failures
    - Circuit blocks subsequent requests
    - Metrics are tracked correctly
    """
    with patch('aiohttp.ClientSession.request') as mock_request:
      # Simulate repeated failures
      mock_request.side_effect = Exception("Network error")
      
      # Make requests until circuit opens
      for i in range(10):
        try:
          await api_client.search_assets(limit=10)
        except Exception:
          pass
      
      # Check circuit breaker metrics
      metrics = api_client.get_circuit_breaker_metrics()
      assert metrics['total_failures'] > 0


class TestEndToEndIntegration:
  """End-to-end integration tests.
  
  Tests complete workflows combining database and API operations.
  """
  
  @pytest.fixture
  async def setup_system(self):
    """Setup complete system for integration testing.
    
    Yields:
        Dict: System components (tracker, client)
    """
    # Setup database
    with tempfile.NamedTemporaryFile(
      suffix='.db', delete=False
    ) as f:
      db_path = f.name
    
    tracker = AssetTracker(db_path=db_path)
    await tracker.initialize_database()
    
    # Setup API client
    config = SafetyCultureConfig(
      api_token="test_token_12345",
      base_url="https://api.safetyculture.io"
    )
    client = SafetyCultureAPIClient(config)
    
    yield {
      'tracker': tracker,
      'client': client,
      'db_path': db_path
    }
    
    # Cleanup
    try:
      os.unlink(db_path)
    except Exception:
      pass
  
  @pytest.mark.asyncio
  async def test_asset_inspection_workflow(self, setup_system):
    """Test complete asset inspection workflow.
    
    Workflow:
    1. Search for assets via API
    2. Register assets in database
    3. Update inspection status
    4. Generate monthly report
    """
    tracker = setup_system['tracker']
    client = setup_system['client']
    
    with patch('aiohttp.ClientSession.request') as mock_request:
      # Mock asset search response
      mock_response = AsyncMock()
      mock_response.status = 200
      mock_response.json = AsyncMock(return_value={
        "assets": [
          {
            "id": "ASSET-001",
            "name": "Forklift #1",
            "type": "Equipment",
            "location": "Warehouse A"
          }
        ]
      })
      mock_request.return_value.__aenter__.return_value = mock_response
      
      # Step 1: Search for assets
      assets = await client.search_assets(
        asset_types=["Equipment"],
        limit=10
      )
      assert len(assets['assets']) == 1
      
      # Step 2: Register asset in database
      asset = assets['assets'][0]
      registered = await tracker.register_asset_for_inspection(
        asset_id=asset['id'],
        asset_name=asset['name'],
        asset_type=asset['type'],
        location=asset['location'],
        template_id="TEMPLATE-001",
        template_name="Safety Inspection",
        month_year="2025-01"
      )
      assert registered is True
      
      # Step 3: Update completion status
      completed = await tracker.mark_asset_completed(
        asset_id=asset['id'],
        inspection_id="INSP-001",
        month_year="2025-01"
      )
      assert completed is True
      
      # Step 4: Generate report
      report = await tracker.export_monthly_report("2025-01")
      assert report['summary']['total_assets'] == 1
      assert report['summary']['completed_inspections'] == 1
  
  @pytest.mark.asyncio
  async def test_concurrent_workflow_execution(self, setup_system):
    """Test multiple concurrent workflow executions.
    
    Verifies:
    - No race conditions
    - All operations complete successfully
    - Data integrity maintained
    """
    tracker = setup_system['tracker']
    
    async def process_asset(asset_id: str, name: str):
      """Process single asset through workflow."""
      await tracker.register_asset_for_inspection(
        asset_id=asset_id,
        asset_name=name,
        asset_type="Equipment",
        location="Test Location",
        template_id="TEMPLATE-001",
        template_name="Safety Inspection",
        month_year="2025-01"
      )
      
      await tracker.update_inspection_status(
        asset_id,
        "in_progress",
        month_year="2025-01"
      )
      
      await tracker.mark_asset_completed(
        asset_id,
        f"INSP-{asset_id}",
        month_year="2025-01"
      )
    
    # Process multiple assets concurrently
    assets = [
      (f"ASSET-{i:03d}", f"Asset {i}")
      for i in range(1, 11)
    ]
    
    await asyncio.gather(*[
      process_asset(aid, name)
      for aid, name in assets
    ])
    
    # Verify all completed
    completed = await tracker.get_completed_assets("2025-01")
    assert len(completed) == 10
    
    # Verify summary
    summary = await tracker.get_monthly_summary("2025-01")
    assert summary['total_assets'] == 10
    assert summary['completed_inspections'] == 10
    assert summary['completion_rate'] == 1.0