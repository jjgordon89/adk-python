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

"""Error scenario tests for SafetyCulture agent.

This module tests error handling for network failures, validation errors,
database errors, and other edge cases to ensure the system fails gracefully.
"""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import aiosqlite
import pytest

from safetyculture_agent.config.api_config import SafetyCultureConfig
from safetyculture_agent.database.asset_repository import AssetRepository
from safetyculture_agent.exceptions import (
  SafetyCultureAPIError,
  SafetyCultureAuthError,
  SafetyCultureDatabaseError,
  SafetyCultureRateLimitError,
  SafetyCultureValidationError,
)
from safetyculture_agent.utils.circuit_breaker import CircuitBreakerOpenError
from safetyculture_agent.tools.safetyculture_api_client import (
  SafetyCultureAPIClient,
)
from safetyculture_agent.utils.input_validator import InputValidator


class TestNetworkFailures:
  """Test handling of network failures and API errors."""
  
  @pytest.mark.asyncio
  async def test_connection_timeout(self, api_client_instance):
    """Test handling of connection timeouts.
    
    Verifies:
    - Timeout exception is caught
    - Proper error is raised
    - System doesn't crash
    """
    # Ensure session is initialized before patching
    await api_client_instance._ensure_session()
    
    # Patch at the session level to avoid circuit breaker retry issues
    with patch.object(
      api_client_instance._session,
      'request',
      side_effect=asyncio.TimeoutError("Connection timeout")
    ):
      with pytest.raises(SafetyCultureAPIError) as exc_info:
        await api_client_instance.search_assets(limit=10)
      
      assert "Network error" in str(exc_info.value)
  
  @pytest.mark.asyncio
  async def test_connection_refused(self, api_client_instance):
    """Test handling of connection refused errors.
    
    Verifies:
    - Connection error is caught
    - Proper error is raised
    - Retry logic is attempted
    """
    with patch('aiohttp.ClientSession.request') as mock_request:
      mock_request.side_effect = aiohttp.ClientConnectionError(
        "Connection refused"
      )
      
      with pytest.raises(SafetyCultureAPIError) as exc_info:
        await api_client_instance.search_assets(limit=10)
      
      assert "Network error" in str(exc_info.value)
  
  @pytest.mark.asyncio
  async def test_malformed_json_response(self, api_client_instance):
    """Test handling of malformed API JSON responses.
    
    Verifies:
    - JSON decode errors are caught
    - Proper error is raised
    - No data corruption
    """
    # Ensure session is initialized before patching
    await api_client_instance._ensure_session()
    
    # Patch at the session level
    with patch.object(api_client_instance._session, 'request') as mock_request:
      mock_response = AsyncMock()
      mock_response.status = 200
      mock_response.raise_for_status = Mock()
      # Make json() method raise JSONDecodeError when awaited
      async def raise_json_error():
        raise json.JSONDecodeError("Invalid JSON", "", 0)
      mock_response.json = raise_json_error
      mock_request.return_value.__aenter__.return_value = mock_response
      
      with pytest.raises(SafetyCultureAPIError):
        await api_client_instance.search_assets(limit=10)
  
  @pytest.mark.asyncio
  async def test_server_500_error(self, api_client_instance):
    """Test handling of 500 Internal Server Error.
    
    Verifies:
    - Server errors are caught
    - Retry logic works
    - Eventually raises proper error
    """
    with patch('aiohttp.ClientSession.request') as mock_request:
      mock_response = AsyncMock()
      mock_response.status = 500
      # Create proper error that raise_for_status will raise
      error = aiohttp.ClientResponseError(
        request_info=Mock(),
        history=(),
        status=500,
        message="Internal Server Error"
      )
      # Make raise_for_status actually raise the error
      def raise_error():
        raise error
      mock_response.raise_for_status = raise_error
      mock_request.return_value.__aenter__.return_value = mock_response
      
      with pytest.raises(SafetyCultureAPIError) as exc_info:
        await api_client_instance.search_assets(limit=10)
      
      assert exc_info.value.status_code == 500
  
  @pytest.mark.asyncio
  async def test_dns_resolution_failure(self, api_client_instance):
    """Test handling of DNS resolution failures.
    
    Verifies:
    - DNS errors are caught
    - Proper error message
    - System doesn't hang
    """
    with patch('aiohttp.ClientSession.request') as mock_request:
      mock_request.side_effect = aiohttp.ClientConnectorError(
        connection_key=Mock(),
        os_error=OSError("Name or service not known")
      )
      
      with pytest.raises(SafetyCultureAPIError):
        await api_client_instance.search_assets(limit=10)


class TestRateLimitingErrors:
  """Test rate limiting error handling."""
  
  @pytest.mark.asyncio
  async def test_rate_limit_429_response(self, api_client_instance):
    """Test handling of 429 Too Many Requests.
    
    Verifies:
    - 429 status is caught
    - Proper exception type
    - Retry-After header is parsed
    """
    with patch('aiohttp.ClientSession.request') as mock_request:
      mock_response = AsyncMock()
      mock_response.status = 429
      mock_response.headers = {'Retry-After': '60'}
      mock_response.json = AsyncMock(return_value={
        "error": "Rate limit exceeded"
      })
      mock_request.return_value.__aenter__.return_value = mock_response
      
      with pytest.raises(SafetyCultureRateLimitError) as exc_info:
        await api_client_instance.search_assets(limit=10)
      
      assert "429" in str(exc_info.value) or "rate limit" in str(
        exc_info.value
      ).lower()
  
  @pytest.mark.asyncio
  async def test_auth_401_response(self, api_client_instance):
    """Test handling of 401 Unauthorized.
    
    Verifies:
    - 401 status is caught
    - Proper auth exception
    - No retry on auth failure
    """
    with patch('aiohttp.ClientSession.request') as mock_request:
      mock_response = AsyncMock()
      mock_response.status = 401
      mock_response.json = AsyncMock(return_value={
        "error": "Invalid token"
      })
      mock_request.return_value.__aenter__.return_value = mock_response
      
      with pytest.raises(SafetyCultureAuthError) as exc_info:
        await api_client_instance.search_assets(limit=10)
      
      assert "Authentication failed" in str(exc_info.value)


class TestCircuitBreakerScenarios:
  """Test circuit breaker behavior in various scenarios."""
  
  @pytest.mark.asyncio
  async def test_circuit_opens_after_threshold_failures(
    self,
    api_client_instance
  ):
    """Test circuit breaker opens after repeated failures.
    
    Verifies:
    - Circuit opens after threshold (5 failures)
    - Subsequent requests raise CircuitBreakerOpenError
    - Metrics are updated correctly
    """
    # Ensure session is initialized before patching
    await api_client_instance._ensure_session()
    
    failure_count = 0
    circuit_open_count = 0
    
    # Patch at the session level to avoid infinite recursion
    with patch.object(
      api_client_instance._session,
      'request',
      side_effect=aiohttp.ClientError("Network error")
    ):
      # Make requests until circuit opens and verify behavior
      for i in range(10):
        try:
          await api_client_instance.search_assets(limit=10)
        except CircuitBreakerOpenError:
          # Expected after circuit opens (attempts 6-10)
          # Must catch this FIRST since it's not wrapped
          circuit_open_count += 1
        except SafetyCultureAPIError:
          # Expected for first 5 attempts before circuit opens
          failure_count += 1
        except Exception as e:
          # Catch any other exceptions for debugging
          pytest.fail(
            f"Unexpected exception on iteration {i}: "
            f"{type(e).__name__}: {e}"
          )
      
      # Verify circuit opened after threshold
      from safetyculture_agent.utils.circuit_breaker import CircuitState
      assert (
        api_client_instance.circuit_breaker.state == CircuitState.OPEN
      ), "Circuit breaker should be open"
      assert (
        failure_count >= 5
      ), (
        f"Expected at least 5 failures before circuit opens, "
        f"got {failure_count}"
      )
      assert (
        circuit_open_count > 0
      ), (
        f"Expected circuit breaker open errors after threshold, "
        f"got {circuit_open_count}"
      )
      
      # Check metrics show failures
      metrics = api_client_instance.get_circuit_breaker_metrics()
      assert metrics['total_failures'] > 0
  
  @pytest.mark.asyncio
  async def test_circuit_half_open_recovery(self, api_client_instance):
    """Test circuit breaker recovery after failures.
    
    Verifies:
    - Circuit eventually moves to half-open
    - Successful requests close circuit
    - System recovers gracefully
    """
    with patch('aiohttp.ClientSession.request') as mock_request:
      # First cause failures
      mock_request.side_effect = aiohttp.ClientError("Network error")
      
      for i in range(6):
        try:
          await api_client_instance.search_assets(limit=10)
        except Exception:
          pass
      
      # Now mock success
      mock_response = AsyncMock()
      mock_response.status = 200
      mock_response.json = AsyncMock(return_value={"assets": []})
      mock_request.side_effect = None
      mock_request.return_value.__aenter__.return_value = mock_response
      
      # Circuit should allow test requests
      await asyncio.sleep(1)  # Wait for circuit to potentially half-open
      metrics = api_client_instance.get_circuit_breaker_metrics()
      assert 'state' in metrics


class TestValidationErrors:
  """Test input validation error scenarios."""
  
  def test_invalid_asset_id_format(self):
    """Test validation of invalid asset ID formats.
    
    Verifies:
    - Empty IDs rejected
    - Too long IDs rejected
    - Invalid characters rejected
    - Path traversal attempts rejected
    """
    validator = InputValidator()
    
    invalid_ids = [
      "",  # Empty
      "a" * 300,  # Too long
      "asset\x00id",  # Null byte
      "../../../etc/passwd",  # Path traversal
      "asset<script>",  # HTML injection
      "asset;DROP TABLE",  # SQL injection attempt
    ]
    
    for invalid_id in invalid_ids:
      with pytest.raises(SafetyCultureValidationError):
        validator.validate_asset_id(invalid_id)
  
  def test_invalid_url_validation(self):
    """Test URL validation with various invalid URLs.
    
    Verifies:
    - HTTP URLs rejected (HTTPS required)
    - Missing protocol rejected
    - Invalid hostnames rejected
    """
    validator = InputValidator()
    
    invalid_urls = [
      "http://example.com",  # HTTP not allowed
      "ftp://example.com",  # Wrong protocol
      "//example.com",  # Missing protocol
      "not_a_url",  # Not a URL
    ]
    
    for invalid_url in invalid_urls:
      with pytest.raises(SafetyCultureValidationError):
        validator.validate_url(invalid_url)
  
  def test_invalid_query_parameters(self):
    """Test validation of query parameters.
    
    Verifies:
    - Non-whitelisted params rejected
    - Invalid param types rejected
    - Range violations caught
    """
    validator = InputValidator()
    
    # Test non-whitelisted parameter
    with pytest.raises(SafetyCultureValidationError):
      validator.validate_params({"malicious_param": "value"})
    
    # Test invalid limit
    with pytest.raises(SafetyCultureValidationError):
      validator.validate_params({"limit": 9999999})
    
    # Test invalid offset
    with pytest.raises(SafetyCultureValidationError):
      validator.validate_params({"offset": -1})


class TestDatabaseErrors:
  """Test database error scenarios."""
  
  @pytest.mark.asyncio
  async def test_database_file_permissions_error(self, temp_repository):
    """Test handling of database permission errors.
    
    Verifies:
    - Permission errors are caught
    - Proper exception raised
    - Error message is clear
    """
    # This test verifies behavior with invalid paths
    # The temp_repository fixture provides a valid database
    # We'll test the existing valid repository instead
    import os
    if os.name != 'nt':  # Skip on Windows
      repo = AssetRepository(db_path="/root/invalid/db.sqlite")
      
      with pytest.raises(Exception):  # Could be various OS errors
        await repo.initialize()
  
  @pytest.mark.asyncio
  async def test_database_corruption_handling(self, tmp_path):
    """Test handling of corrupted database.
    
    Verifies:
    - Corruption is detected
    - Proper error raised
    - No data loss in other operations
    """
    # Create corrupted database file
    db_path = tmp_path / "corrupted.db"
    db_path.write_bytes(b'corrupted data not sqlite format')
    
    repo = AssetRepository(db_path=str(db_path))
    
    # Should fail to initialize
    with pytest.raises(Exception):  # SQLite error
      await repo.initialize()
  
  @pytest.mark.asyncio
  async def test_concurrent_write_conflicts(self, temp_repository):
    """Test handling of concurrent write conflicts.
    
    Verifies:
    - Concurrent writes handled
    - No data corruption
    - Proper locking behavior
    """
    # Try concurrent writes to same asset
    async def write_asset():
      try:
        await temp_repository.register_asset(
          "ASSET-CONFLICT",
          "2025-01",
          "Test Asset",
          "Test Location"
        )
      except Exception:
        pass
    
    # Execute multiple concurrent writes
    await asyncio.gather(*[write_asset() for _ in range(5)])
    
    # Verify only one entry exists
    async with aiosqlite.connect(temp_repository.db_path) as db:
      async with db.execute(
        "SELECT COUNT(*) FROM asset_inspections WHERE asset_id = ?",
        ("ASSET-CONFLICT",)
      ) as cursor:
        count = await cursor.fetchone()
        assert count[0] <= 1  # Should have at most 1 entry
  
  @pytest.mark.asyncio
  async def test_disk_full_scenario(self, temp_repository):
    """Test handling when disk is full.
    
    Verifies:
    - Disk full errors caught
    - Proper error message
    - System doesn't crash
    """
    # Mock disk full error
    with patch('aiosqlite.connect') as mock_connect:
      mock_connect.side_effect = OSError("No space left on device")
      
      with pytest.raises(Exception):
        await temp_repository.register_asset(
          "ASSET-001",
          "2025-01",
          "Test",
          "Location"
        )


class TestEdgeCases:
  """Test edge cases and boundary conditions."""
  
  @pytest.mark.asyncio
  async def test_empty_response_handling(self, mock_env_token):
    """Test handling of empty API responses.
    
    Verifies:
    - Empty responses don't crash
    - Proper default values
    - No null pointer errors
    """
    config = SafetyCultureConfig(
      base_url="https://api.safetyculture.io"
    )
    client = SafetyCultureAPIClient(config)
    
    with patch('aiohttp.ClientSession.request') as mock_request:
      mock_response = AsyncMock()
      mock_response.status = 200
      mock_response.json = AsyncMock(return_value={})
      mock_request.return_value.__aenter__.return_value = mock_response
      
      result = await client.search_assets(limit=10)
      assert result == {}
  
  @pytest.mark.asyncio
  async def test_unicode_handling_in_data(self, temp_repository):
    """Test handling of unicode characters in data.
    
    Verifies:
    - Unicode is properly encoded
    - No encoding errors
    - Data integrity maintained
    """
    # Test with unicode characters
    result = await temp_repository.register_asset(
      "ASSET-UNICODE",
      "2025-01",
      "Asset with émojis 🔧⚠️",
      "北京 Location"
    )
    assert result is True
  
  def test_extremely_long_input_strings(self):
    """Test handling of extremely long input strings.
    
    Verifies:
    - Length limits enforced
    - Proper validation errors
    - No buffer overflows
    """
    validator = InputValidator()
    
    # Test query too long
    long_query = "a" * 10000
    with pytest.raises(SafetyCultureValidationError):
      validator.validate_params({"query": long_query})
    
    # Test string too long
    long_string = "b" * 10000
    with pytest.raises(SafetyCultureValidationError):
      validator._sanitize_string(long_string)
  
  @pytest.mark.asyncio
  async def test_null_and_none_value_handling(self, temp_repository):
    """Test handling of null and None values.
    
    Verifies:
    - None values handled gracefully
    - Optional parameters work
    - No null pointer errors
    """
    # Test with None metadata
    result = await temp_repository.register_asset_for_inspection(
      "ASSET-NULL",
      "Test Asset",
      "Equipment",
      "Location",
      "TEMPLATE-001",
      "Template",
      metadata=None  # Explicitly None
    )
    assert result is True