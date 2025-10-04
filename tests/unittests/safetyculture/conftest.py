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

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict
from unittest.mock import AsyncMock, Mock

import aiohttp
import pytest

from safetyculture_agent.config.api_config import SafetyCultureConfig
from safetyculture_agent.database.asset_repository import AssetRepository
from safetyculture_agent.database.asset_tracker import AssetTracker
from safetyculture_agent.tools.safetyculture_api_client import (
  SafetyCultureAPIClient
)


# ============================================================================
# Environment and Configuration Fixtures
# ============================================================================


@pytest.fixture
def mock_env_token(monkeypatch):
  """Patch SAFETYCULTURE_API_TOKEN environment variable.
  
  This fixture is used across most tests to provide a valid test token.
  The token is long enough (21 chars) to pass length validation checks.
  
  Args:
      monkeypatch: pytest monkeypatch fixture
  
  Yields:
      str: The test token value
  """
  token = "test_token_1234567890"
  monkeypatch.setenv("SAFETYCULTURE_API_TOKEN", token)
  yield token


@pytest.fixture
def test_config(mock_env_token):
  """Provide test configuration with mocked environment.
  
  SafetyCultureConfig loads api_token from environment variables via
  SecureCredentialManager. This fixture ensures the token is available.
  
  Args:
      mock_env_token: Fixture that patches environment variable
  
  Returns:
      SafetyCultureConfig: Configuration instance for testing
  """
  return SafetyCultureConfig(
    base_url="https://test.api.safetyculture.io",
    request_timeout=30,
    max_retries=3,
    retry_delay=1,
    requests_per_second=10
  )


# ============================================================================
# HTTP Response Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_http_response():
  """Factory fixture for creating HTTP response mocks.
  
  Creates AsyncMock objects configured to mimic aiohttp.ClientResponse
  behavior. Supports common response scenarios including success,
  errors, and JSON responses.
  
  Returns:
      Callable: Factory function that creates response mocks
  
  Example:
      response = mock_http_response(status=200, json_data={"key": "value"})
      response = mock_http_response(status=404, error=True)
  """
  def _create_response(
    status: int = 200,
    json_data: Dict[str, Any] | None = None,
    error: bool = False,
    headers: Dict[str, str] | None = None
  ) -> AsyncMock:
    """Create a mock HTTP response.
    
    Args:
        status: HTTP status code
        json_data: JSON response data
        error: Whether raise_for_status should raise an error
        headers: Response headers
    
    Returns:
        AsyncMock: Configured response mock
    """
    response = AsyncMock()
    response.status = status
    response.headers = headers or {}
    
    if json_data is not None:
      response.json = AsyncMock(return_value=json_data)
    else:
      response.json = AsyncMock(return_value={})
    
    if error:
      response.raise_for_status = Mock(
        side_effect=aiohttp.ClientResponseError(
          request_info=Mock(),
          history=(),
          status=status,
          message=f"HTTP {status}"
        )
      )
    else:
      response.raise_for_status = Mock()
    
    return response
  
  return _create_response


@pytest.fixture
def mock_successful_response(mock_http_response):
  """Provide a standard successful HTTP 200 response.
  
  Args:
      mock_http_response: Factory fixture for creating responses
  
  Returns:
      AsyncMock: Mock response with status 200 and empty data
  """
  return mock_http_response(status=200, json_data={"data": "success"})


@pytest.fixture
def mock_error_response(mock_http_response):
  """Provide a standard error HTTP response.
  
  Args:
      mock_http_response: Factory fixture for creating responses
  
  Returns:
      AsyncMock: Mock response with status 500 and error flag
  """
  return mock_http_response(status=500, error=True)


@pytest.fixture
def mock_auth_error_response(mock_http_response):
  """Provide a 401 Unauthorized HTTP response.
  
  Args:
      mock_http_response: Factory fixture for creating responses
  
  Returns:
      AsyncMock: Mock response with status 401
  """
  return mock_http_response(
    status=401,
    json_data={"error": "Invalid token"}
  )


@pytest.fixture
def mock_rate_limit_response(mock_http_response):
  """Provide a 429 Rate Limit HTTP response.
  
  Args:
      mock_http_response: Factory fixture for creating responses
  
  Returns:
      AsyncMock: Mock response with status 429 and Retry-After header
  """
  return mock_http_response(
    status=429,
    json_data={"error": "Rate limit exceeded"},
    headers={"Retry-After": "60"}
  )


# ============================================================================
# API Client Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_api_client():
  """Provide mocked API client with default return values.
  
  Creates an AsyncMock that mimics SafetyCultureAPIClient behavior
  with sensible defaults for common operations.
  
  Returns:
      AsyncMock: Mocked SafetyCultureAPIClient with default responses
  """
  client = AsyncMock(spec=SafetyCultureAPIClient)
  client.search_assets.return_value = {"assets": [], "total": 0}
  client.search_templates.return_value = {"templates": []}
  client.search_inspections.return_value = {"audits": []}
  client.get_asset.return_value = None
  client.get_template.return_value = None
  return client


@pytest.fixture
def mock_aiohttp_session(mock_successful_response):
  """Provide mocked aiohttp ClientSession.
  
  Creates a mock session that returns successful responses by default.
  Can be customized in tests by changing the return value or side effect.
  
  Args:
      mock_successful_response: Default successful response
  
  Returns:
      Mock: Mocked aiohttp ClientSession
  """
  mock_session = Mock()
  mock_session.request = Mock(
    return_value=AsyncMock(
      __aenter__=AsyncMock(return_value=mock_successful_response)
    )
  )
  return mock_session


# ============================================================================
# Database Mock Fixtures
# ============================================================================


@pytest.fixture
async def temp_database():
  """Provide temporary database for testing.
  
  Creates a temporary SQLite database file, initializes an AssetTracker,
  and cleans up after the test completes.
  
  Yields:
      AssetTracker: Initialized tracker with temporary database
  """
  with tempfile.NamedTemporaryFile(
    suffix='.db',
    delete=False
  ) as f:
    db_path = f.name
  
  try:
    tracker = AssetTracker(db_path=db_path)
    await tracker.initialize_database()
    yield tracker
  finally:
    # Cleanup
    try:
      Path(db_path).unlink()
    except Exception:
      pass


@pytest.fixture
async def temp_repository():
  """Provide temporary AssetRepository for testing.
  
  Creates a temporary SQLite database, initializes an AssetRepository,
  and cleans up after the test completes.
  
  Yields:
      AssetRepository: Initialized repository with temporary database
  """
  with tempfile.NamedTemporaryFile(
    suffix='.db',
    delete=False
  ) as f:
    db_path = f.name
  
  try:
    repo = AssetRepository(db_path=db_path)
    await repo.initialize()
    yield repo
  finally:
    # Cleanup
    try:
      Path(db_path).unlink()
    except Exception:
      pass


# ============================================================================
# Sample Data Fixtures
# ============================================================================


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


# ============================================================================
# API Client Instance Fixtures
# ============================================================================


@pytest.fixture
def api_client_instance(test_config):
  """Provide configured SafetyCultureAPIClient instance.
  
  Creates a real API client instance with test configuration.
  Use this when you need to test actual client behavior with mocked
  HTTP responses.
  
  Args:
      test_config: Test configuration fixture
  
  Returns:
      SafetyCultureAPIClient: Configured client instance
  """
  return SafetyCultureAPIClient(config=test_config)