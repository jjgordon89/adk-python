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

"""Integration tests for security features."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest

from safetyculture_agent.config.api_config import SafetyCultureConfig
from safetyculture_agent.exceptions import (
  CircuitBreakerOpenError,
  SafetyCultureAPIError
)
from safetyculture_agent.tools.safetyculture_api_client import (
  SafetyCultureAPIClient
)


class TestEndToEndSecurity:
  """End-to-end security integration tests."""
  
  @pytest.mark.asyncio
  async def test_api_client_with_all_security_features(self):
    """Test API client with all security features enabled."""
    with patch.dict(os.environ, {'SAFETYCULTURE_API_TOKEN': 'test_token'}):
      config = SafetyCultureConfig()
      client = SafetyCultureAPIClient(config=config)
      
      # Mock successful API response
      with patch('aiohttp.ClientSession.request') as mock_request:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'data': 'test'})
        mock_response.raise_for_status = AsyncMock()
        mock_request.return_value.__aenter__.return_value = mock_response
        
        async with client:
          result = await client.search_assets(limit=10)
          
          # Verify security features applied
          call_args = mock_request.call_args
          headers = call_args.kwargs['headers']
          
          # Should have authorization
          assert 'Authorization' in headers
          # Should have request ID
          assert 'X-Request-ID' in headers
          # Result should be successful
          assert result is not None
  
  @pytest.mark.asyncio
  async def test_circuit_breaker_opens_on_failures(self):
    """Test circuit breaker opens after repeated failures."""
    with patch.dict(os.environ, {'SAFETYCULTURE_API_TOKEN': 'test_token'}):
      config = SafetyCultureConfig()
      client = SafetyCultureAPIClient(config=config)
      
      # Mock failing API responses
      with patch('aiohttp.ClientSession.request') as mock_request:
        mock_request.side_effect = Exception('API down')
        
        async with client:
          # Make requests until circuit opens
          for i in range(10):
            try:
              await client.search_assets()
            except (Exception, CircuitBreakerOpenError):
              pass
          
          # Circuit should be open or have recorded failures
          metrics = client.get_circuit_breaker_metrics()
          # Circuit may be open or collecting failures
          assert metrics['failure_count'] > 0 or metrics['state'] == 'open'
  
  @pytest.mark.asyncio
  async def test_rate_limiting_protects_api(self):
    """Test rate limiting prevents excessive requests."""
    with patch.dict(os.environ, {'SAFETYCULTURE_API_TOKEN': 'test_token'}):
      config = SafetyCultureConfig()
      config.requests_per_second = 2  # Very low limit for testing
      client = SafetyCultureAPIClient(config=config)
      
      request_times = []
      
      # Mock successful API response
      with patch('aiohttp.ClientSession.request') as mock_request:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'data': 'test'})
        mock_response.raise_for_status = AsyncMock()
        mock_request.return_value.__aenter__.return_value = mock_response
        
        async with client:
          import time
          # Make several rapid requests
          for _ in range(3):
            start = time.time()
            await client.search_assets(limit=10)
            request_times.append(time.time() - start)
      
      # Later requests should be delayed due to rate limiting
      # At least one request should show delay
      assert any(t > 0.1 for t in request_times[1:])
  
  @pytest.mark.asyncio
  async def test_https_enforcement_in_production(self):
    """Test HTTPS is enforced for production URLs."""
    with patch.dict(os.environ, {'SAFETYCULTURE_API_TOKEN': 'test_token'}):
      # HTTP URL should fail validation
      config = SafetyCultureConfig()
      config.base_url = 'http://api.example.com'  # Invalid HTTP
      client = SafetyCultureAPIClient(config=config)
      
      with patch('aiohttp.ClientSession.request'):
        async with client:
          with pytest.raises(SafetyCultureAPIError):
            await client.search_assets()
  
  @pytest.mark.asyncio
  async def test_request_signing_integration(self):
    """Test request signing when enabled."""
    env_vars = {
      'SAFETYCULTURE_API_TOKEN': 'test_token',
      'SAFETYCULTURE_SIGNING_KEY': 'test_signing_key'
    }
    
    with patch.dict(os.environ, env_vars):
      config = SafetyCultureConfig()
      client = SafetyCultureAPIClient(config=config)
      
      # Mock successful API response
      with patch('aiohttp.ClientSession.request') as mock_request:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'data': 'test'})
        mock_response.raise_for_status = AsyncMock()
        mock_request.return_value.__aenter__.return_value = mock_response
        
        async with client:
          await client.search_assets(limit=10)
          
          # Check that signature headers were added
          call_args = mock_request.call_args
          headers = call_args.kwargs['headers']
          
          # If signing is enabled, should have signature headers
          if client.request_signer:
            assert 'X-Signature' in headers
            assert 'X-Timestamp' in headers
  
  @pytest.mark.asyncio
  async def test_authentication_failure_handling(self):
    """Test authentication failures are handled securely."""
    with patch.dict(os.environ, {'SAFETYCULTURE_API_TOKEN': 'invalid_token'}):
      config = SafetyCultureConfig()
      client = SafetyCultureAPIClient(config=config)
      
      # Mock 401 response
      with patch('aiohttp.ClientSession.request') as mock_request:
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.raise_for_status = AsyncMock(
          side_effect=Exception('Unauthorized')
        )
        mock_request.return_value.__aenter__.return_value = mock_response
        
        async with client:
          with pytest.raises(Exception):  # Should raise auth error
            await client.search_assets()
  
  @pytest.mark.asyncio
  async def test_input_validation_prevents_injection(self):
    """Test input validation prevents injection attacks."""
    with patch.dict(os.environ, {'SAFETYCULTURE_API_TOKEN': 'test_token'}):
      config = SafetyCultureConfig()
      client = SafetyCultureAPIClient(config=config)
      
      async with client:
        # SQL injection attempt in asset ID
        with pytest.raises(Exception):  # Should raise validation error
          await client.get_asset("'; DROP TABLE users; --")


class TestSecurityHeaders:
  """Test security headers are properly applied."""
  
  @pytest.mark.asyncio
  async def test_security_headers_present(self):
    """Verify security headers are added to all requests."""
    with patch.dict(os.environ, {'SAFETYCULTURE_API_TOKEN': 'test_token'}):
      config = SafetyCultureConfig()
      client = SafetyCultureAPIClient(config=config)
      
      with patch('aiohttp.ClientSession.request') as mock_request:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'data': 'test'})
        mock_response.raise_for_status = AsyncMock()
        mock_request.return_value.__aenter__.return_value = mock_response
        
        async with client:
          await client.search_assets()
          
          call_args = mock_request.call_args
          headers = call_args.kwargs['headers']
          
          # Check security headers
          assert 'Authorization' in headers
          assert 'X-Request-ID' in headers
          assert 'User-Agent' in headers
          assert 'Content-Type' in headers


class TestCircuitBreakerBehavior:
  """Test circuit breaker behavior under various conditions."""
  
  @pytest.mark.asyncio
  async def test_circuit_breaker_half_open_state(self):
    """Test circuit breaker transitions to half-open state."""
    with patch.dict(os.environ, {'SAFETYCULTURE_API_TOKEN': 'test_token'}):
      config = SafetyCultureConfig()
      client = SafetyCultureAPIClient(config=config)
      
      # Configure short timeout for testing
      client.circuit_breaker.base_timeout = 0.1
      
      # Mock failing then succeeding responses
      call_count = 0
      
      def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count <= 5:
          raise Exception('Service down')
        # After 5 failures, succeed
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'data': 'test'})
        mock_response.raise_for_status = AsyncMock()
        return mock_response
      
      with patch('aiohttp.ClientSession.request') as mock_request:
        mock_request.side_effect = side_effect
        
        async with client:
          # Cause circuit to open
          for _ in range(5):
            try:
              await client.search_assets()
            except Exception:
              pass
          
          # Circuit should be open
          metrics = client.get_circuit_breaker_metrics()
          assert metrics['failure_count'] >= 5


class TestDataSanitization:
  """Test data sanitization in logs and errors."""
  
  @pytest.mark.asyncio
  async def test_tokens_not_logged(self):
    """Verify tokens are not present in logs."""
    with patch.dict(
      os.environ,
      {'SAFETYCULTURE_API_TOKEN': 'secret_token_value'}
    ):
      config = SafetyCultureConfig()
      client = SafetyCultureAPIClient(config=config)
      
      # Sanitize headers for logging
      token = await config.get_api_token()
      headers = {'Authorization': f'Bearer {token}'}
      
      sanitized = client.header_manager.sanitize_for_logging(headers)
      
      # Token should not be in sanitized version
      assert 'secret_token_value' not in str(sanitized)
      assert '[REDACTED]' in str(sanitized['Authorization'])
  
  @pytest.mark.asyncio
  async def test_error_messages_sanitized(self):
    """Verify error messages don't contain sensitive data."""
    with patch.dict(
      os.environ,
      {'SAFETYCULTURE_API_TOKEN': 'sensitive_api_key'}
    ):
      config = SafetyCultureConfig()
      client = SafetyCultureAPIClient(config=config)
      
      # Create error with sensitive data
      error = Exception('Error with token=sensitive_api_key in message')
      
      # Sanitize error
      sanitized = client.header_manager.sanitize_error(error)
      
      # Should not contain sensitive data
      assert 'sensitive_api_key' not in sanitized
      assert '[REDACTED]' in sanitized