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

"""Shared test fixtures for SafetyCulture agent tests."""

from __future__ import annotations

import tempfile
from typing import Any, Dict
from unittest.mock import AsyncMock

import pytest

from safetyculture_agent.config.api_config import SafetyCultureConfig
from safetyculture_agent.database.asset_tracker import AssetTracker
from safetyculture_agent.tools.safetyculture_api_client import (
  SafetyCultureAPIClient
)


@pytest.fixture
async def temp_database():
  """Provide temporary database for testing.
  
  Yields:
      AssetTracker: Initialized tracker with temporary database
  """
  with tempfile.NamedTemporaryFile(
    suffix='.db',
    delete=False
  ) as f:
    tracker = AssetTracker(db_path=f.name)
    await tracker.initialize_database()
    yield tracker
    # Cleanup handled by tempfile


@pytest.fixture
def mock_api_client():
  """Provide mocked API client.
  
  Returns:
      AsyncMock: Mocked SafetyCultureAPIClient with default responses
  """
  client = AsyncMock(spec=SafetyCultureAPIClient)
  client.search_assets.return_value = {"assets": [], "total": 0}
  client.search_templates.return_value = {"templates": []}
  client.search_inspections.return_value = {"audits": []}
  return client


@pytest.fixture
def test_config():
  """Provide test configuration.
  
  Returns:
      SafetyCultureConfig: Configuration instance for testing
  """
  return SafetyCultureConfig(
    api_token="test_token_12345",
    base_url="https://test.api.safetyculture.io",
    request_timeout=30,
    max_retries=3,
    retry_delay=1,
    requests_per_second=10
  )


@pytest.fixture
def sample_asset():
  """Provide sample asset data for testing.
  
  Returns:
      Dict[str, Any]: Sample asset data structure
  """
  return {
    "asset_id": "test_asset_001",
    "name": "Test Equipment",
    "type": "Equipment",
    "status": "Active",
    "location": "Test Site",
    "last_inspection": "2024-01-15T10:00:00Z"
  }


@pytest.fixture
def sample_template():
  """Provide sample template data for testing.
  
  Returns:
      Dict[str, Any]: Sample template data structure
  """
  return {
    "template_id": "template_001",
    "name": "Equipment Inspection",
    "description": "Standard equipment inspection template",
    "fields": [
      {"id": "field1", "label": "Condition", "type": "text"},
      {"id": "field2", "label": "Notes", "type": "textarea"}
    ]
  }


@pytest.fixture
def sample_inspection():
  """Provide sample inspection data for testing.
  
  Returns:
      Dict[str, Any]: Sample inspection data structure
  """
  return {
    "audit_id": "audit_001",
    "template_id": "template_001",
    "asset_id": "test_asset_001",
    "status": "completed",
    "created_at": "2024-01-15T10:00:00Z",
    "completed_at": "2024-01-15T11:30:00Z",
    "inspector": "SafetyCulture Agent"
  }


@pytest.fixture
def sample_site():
  """Provide sample site data for testing.
  
  Returns:
      Dict[str, Any]: Sample site data structure
  """
  return {
    "site_id": "site_001",
    "name": "Main Warehouse",
    "location": "123 Test Street",
    "region": "North"
  }