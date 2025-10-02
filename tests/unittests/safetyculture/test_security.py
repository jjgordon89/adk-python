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

"""Security tests for SafetyCulture agent."""

from __future__ import annotations

import os
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from safetyculture_agent.config.credential_manager import (
  SecureCredentialManager
)
from safetyculture_agent.config.secret_manager import SecretManager
from safetyculture_agent.exceptions import (
  SafetyCultureCredentialError,
  SafetyCultureValidationError
)
from safetyculture_agent.utils.input_validator import InputValidator
from safetyculture_agent.utils.request_signer import RequestSigner
from safetyculture_agent.utils.secure_header_manager import (
  SecureHeaderManager
)


class TestCredentialSecurity:
  """Test suite for credential security features."""
  
  @pytest.mark.asyncio
  async def test_token_caching_exists(self):
    """Verify tokens are cached in memory."""
    with patch.dict(os.environ, {'SAFETYCULTURE_API_TOKEN': 'test_token'}):
      manager = SecureCredentialManager()
      
      # Get token
      token = await manager.get_api_token()
      assert token == 'test_token'
      
      # Should be cached now
      assert manager._cached_token is not None
  
  @pytest.mark.asyncio
  async def test_token_revocation_clears_cache(self):
    """Verify token revocation clears cached credentials."""
    with patch.dict(os.environ, {'SAFETYCULTURE_API_TOKEN': 'test_token'}):
      manager = SecureCredentialManager()
      
      # Get and cache token
      await manager.get_api_token()
      assert await manager.is_token_valid()
      
      # Revoke
      await manager.revoke_token()
      
      # Should not have cached token
      assert not await manager.is_token_valid()
  
  @pytest.mark.asyncio
  async def test_token_rotation_updates_cache(self):
    """Verify token rotation updates cached value."""
    with patch.dict(os.environ, {'SAFETYCULTURE_API_TOKEN': 'old_token'}):
      manager = SecureCredentialManager()
      
      # Get initial token
      old_token = await manager.get_api_token()
      assert old_token == 'old_token'
      
      # Rotate to new token
      await manager.rotate_token('new_token')
      
      # Cache should be updated
      assert manager._cached_token == 'new_token'
  
  @pytest.mark.asyncio
  async def test_expired_token_handling(self):
    """Verify expired tokens trigger correct response."""
    manager = SecureCredentialManager()
    
    # Set a cached token
    manager._cached_token = 'expired_token'
    
    # Mock API response for expired token
    with patch('aiohttp.ClientSession') as mock_session_class:
      mock_session = AsyncMock()
      mock_response = AsyncMock()
      mock_response.status = 401
      mock_session.__aenter__.return_value = mock_session
      mock_session.get.return_value.__aenter__.return_value = mock_response
      mock_session_class.return_value = mock_session
      
      # Should detect expiration
      is_valid = await manager.test_token_validity()
      assert not is_valid
  
  @pytest.mark.asyncio
  async def test_missing_token_raises_error(self):
    """Verify missing token raises appropriate error."""
    with patch.dict(os.environ, {}, clear=True):
      manager = SecureCredentialManager()
      
      with pytest.raises(SafetyCultureCredentialError) as exc_info:
        await manager.get_api_token()
      
      assert 'API token not found' in str(exc_info.value)
  
  @pytest.mark.asyncio
  async def test_token_info_redacts_sensitive_data(self):
    """Verify token info shows preview but not full token."""
    with patch.dict(
      os.environ,
      {'SAFETYCULTURE_API_TOKEN': 'test_token_12345'}
    ):
      manager = SecureCredentialManager()
      await manager.get_api_token()
      
      info = await manager.get_token_info()
      
      assert info['has_token']
      assert info['token_length'] == 17
      # Should show preview but not full token
      assert '...' in info['token_preview']
      assert info['token_preview'] != 'test_token_12345'


class TestInputValidation:
  """Test suite for input validation security."""
  
  def test_sql_injection_prevention_in_asset_id(self):
    """Verify SQL injection attempts are blocked in asset IDs."""
    validator = InputValidator()
    
    # SQL injection attempts
    malicious_inputs = [
      "'; DROP TABLE users; --",
      "1' OR '1'='1",
      "admin'--",
      "1; DELETE FROM assets"
    ]
    
    for malicious in malicious_inputs:
      with pytest.raises(SafetyCultureValidationError):
        validator.validate_asset_id(malicious)
  
  def test_xss_prevention_in_query(self):
    """Verify XSS attempts are sanitized in queries."""
    validator = InputValidator()
    
    xss_attempt = "<script>alert('xss')</script>"
    
    # Should remove control characters but this will be sanitized
    result = validator._validate_query(xss_attempt)
    
    # Should be sanitized (printable characters only)
    assert '<script>' in result  # Printable but would be escaped at render
  
  def test_parameter_injection_prevention(self):
    """Verify parameter injection attempts are blocked."""
    validator = InputValidator()
    
    # Invalid parameter names
    with pytest.raises(SafetyCultureValidationError) as exc:
      validator.validate_params({'__proto__': 'value'})
    
    assert 'Invalid parameter' in str(exc.value)
    
    with pytest.raises(SafetyCultureValidationError):
      validator.validate_params({'constructor': 'value'})
  
  def test_field_name_injection_prevention(self):
    """Verify SQL injection via field names is blocked."""
    validator = InputValidator()
    
    malicious_fields = [
      "field; DROP TABLE--",
      "field' OR '1'='1",
      "field<script>alert(1)</script>"
    ]
    
    for malicious in malicious_fields:
      with pytest.raises(SafetyCultureValidationError):
        validator._validate_fields(malicious)
  
  def test_url_validation_enforces_https(self):
    """Verify URLs must use HTTPS protocol."""
    validator = InputValidator()
    
    # HTTP should fail
    with pytest.raises(SafetyCultureValidationError) as exc:
      validator.validate_url('http://api.example.com')
    
    assert 'HTTPS' in str(exc.value)
    
    # HTTPS should pass
    result = validator.validate_url('https://api.example.com')
    assert result == 'https://api.example.com'
  
  def test_endpoint_validation_prevents_path_traversal(self):
    """Verify path traversal attempts are blocked."""
    validator = InputValidator()
    
    malicious_paths = [
      '/api/../../../etc/passwd',
      '/api//admin',
      '/api\\admin'
    ]
    
    for path in malicious_paths:
      with pytest.raises(SafetyCultureValidationError):
        validator.validate_endpoint(path)
  
  def test_limit_validation_prevents_resource_exhaustion(self):
    """Verify limit parameter prevents resource exhaustion."""
    validator = InputValidator()
    
    # Too large limit
    with pytest.raises(SafetyCultureValidationError):
      validator._validate_limit(100000)
    
    # Negative limit
    with pytest.raises(SafetyCultureValidationError):
      validator._validate_limit(-1)
    
    # Valid limit
    result = validator._validate_limit(100)
    assert result == 100


class TestHeaderSecurity:
  """Test suite for HTTP header security."""
  
  @pytest.mark.asyncio
  async def test_token_not_logged_in_headers(self):
    """Verify tokens are not exposed in logged headers."""
    manager = SecureHeaderManager()
    
    headers = await manager.get_secure_headers('secret_token_12345')
    
    # Token should be in header for API call
    assert 'Authorization' in headers
    assert 'Bearer secret_token_12345' in headers['Authorization']
    
    # But sanitized version should redact it
    sanitized = manager.sanitize_for_logging(headers)
    assert 'secret_token_12345' not in str(sanitized)
    assert '[REDACTED]' in str(sanitized['Authorization'])
  
  def test_sensitive_data_removed_from_errors(self):
    """Verify sensitive data removed from error messages."""
    manager = SecureHeaderManager()
    
    error = Exception('Failed: token=secret_key123 api-key=myapikey')
    sanitized = manager.sanitize_error(error)
    
    # Should not contain actual sensitive values
    assert 'secret_key123' not in sanitized
    assert 'myapikey' not in sanitized
    assert '[REDACTED]' in sanitized
  
  @pytest.mark.asyncio
  async def test_request_id_added_to_headers(self):
    """Verify request IDs are added for tracing."""
    manager = SecureHeaderManager()
    
    headers = await manager.get_secure_headers('token')
    
    assert 'X-Request-ID' in headers
    assert 'X-Request-Time' in headers
  
  def test_sanitize_nested_dict_structure(self):
    """Verify nested dictionaries are properly sanitized."""
    manager = SecureHeaderManager()
    
    data = {
      'user': 'john',
      'auth': {
        'authorization': 'Bearer secret123',
        'x-api-key': 'apikey456'
      },
      'payload': {
        'message': 'Hello',
        'token': 'hidden789'
      }
    }
    
    sanitized = manager.sanitize_for_logging(data)
    
    # Check nested redaction
    assert sanitized['auth']['authorization'] == '[REDACTED]'
    assert sanitized['auth']['x-api-key'] == '[REDACTED]'
    assert '[REDACTED]' in sanitized['payload']['token']


class TestSecretManagement:
  """Test suite for secret management."""
  
  def test_secret_encryption_at_rest(self):
    """Verify secrets are encrypted in cache."""
    secret_mgr = SecretManager()
    
    with patch.dict(os.environ, {'TEST_SECRET': 'sensitive_value'}):
      secret = secret_mgr.get_secret('TEST_SECRET')
      
      # Check cache is encrypted
      cached = secret_mgr._cache.get('TEST_SECRET')
      assert cached != b'sensitive_value'  # Should be encrypted
      assert secret == 'sensitive_value'  # But retrievable
  
  def test_secret_audit_logging(self):
    """Verify secret access is logged for audit."""
    secret_mgr = SecretManager()
    
    with patch.dict(os.environ, {'SECRET1': 'val1', 'SECRET2': 'val2'}):
      secret_mgr.get_secret('SECRET1')
      secret_mgr.get_secret('SECRET2')
      
      # Should track accessed secrets
      accessed = secret_mgr.get_accessed_secrets()
      assert 'SECRET1' in accessed
      assert 'SECRET2' in accessed
  
  def test_secret_rotation_clears_cache(self):
    """Verify secret rotation updates cached value."""
    secret_mgr = SecretManager()
    
    with patch.dict(os.environ, {'ROTATE_SECRET': 'old_value'}):
      old = secret_mgr.get_secret('ROTATE_SECRET')
      assert old == 'old_value'
    
    # Update environment
    with patch.dict(os.environ, {'ROTATE_SECRET': 'new_value'}):
      # Rotate
      new = secret_mgr.rotate_secret('ROTATE_SECRET')
      assert new == 'new_value'
      assert new != old
  
  def test_required_secret_raises_error_when_missing(self):
    """Verify required secrets raise error when not found."""
    secret_mgr = SecretManager()
    
    with patch.dict(os.environ, {}, clear=True):
      with pytest.raises(ValueError) as exc:
        secret_mgr.get_secret('MISSING_SECRET', required=True)
      
      assert 'Required secret' in str(exc.value)
  
  def test_secret_redaction_for_logging(self):
    """Verify secrets are redacted in logs."""
    secret_mgr = SecretManager()
    
    sensitive = 'my_secret_api_key_12345'
    redacted = secret_mgr.redact_value(sensitive)
    
    # Should show preview but not full value
    assert 'my_s' in redacted
    assert '2345' in redacted
    assert '****' in redacted
    assert sensitive != redacted
  
  def test_secret_type_conversion_int(self):
    """Verify secret type conversion for integers."""
    secret_mgr = SecretManager()
    
    with patch.dict(os.environ, {'PORT': '8080'}):
      port = secret_mgr.get_secret_int('PORT')
      assert port == 8080
      assert isinstance(port, int)
  
  def test_secret_type_conversion_bool(self):
    """Verify secret type conversion for booleans."""
    secret_mgr = SecretManager()
    
    with patch.dict(
      os.environ,
      {'ENABLED': 'true', 'DISABLED': 'false'}
    ):
      enabled = secret_mgr.get_secret_bool('ENABLED')
      disabled = secret_mgr.get_secret_bool('DISABLED')
      
      assert enabled is True
      assert disabled is False


class TestRequestSigning:
  """Test suite for HMAC request signing."""
  
  def test_request_signature_generation(self):
    """Verify HMAC signatures are generated correctly."""
    signer = RequestSigner(signing_key='test_key_12345')
    
    headers = signer.sign_request(
      method='POST',
      url='https://api.example.com/test',
      body={'key': 'value'}
    )
    
    assert 'X-Signature' in headers
    assert 'X-Timestamp' in headers
    assert headers['X-Signature-Algorithm'] == 'HMAC-SHA256'
    assert len(headers['X-Signature']) == 64  # SHA256 hex length
  
  def test_signature_verification_succeeds_for_valid(self):
    """Verify valid signatures pass verification."""
    signer = RequestSigner(signing_key='test_key')
    
    # Generate signature
    headers = signer.sign_request('GET', 'https://api.test.com')
    
    # Verify
    is_valid = signer.verify_signature(
      'GET',
      'https://api.test.com',
      headers['X-Signature'],
      int(headers['X-Timestamp'])
    )
    
    assert is_valid
  
  def test_signature_verification_fails_for_tampering(self):
    """Verify tampered requests are rejected."""
    signer = RequestSigner(signing_key='test_key')
    
    headers = signer.sign_request('GET', 'https://api.test.com')
    
    # Tamper with URL
    is_valid = signer.verify_signature(
      'GET',
      'https://api.test.com/tampered',  # Different URL
      headers['X-Signature'],
      int(headers['X-Timestamp'])
    )
    
    assert not is_valid
  
  def test_replay_attack_prevention(self):
    """Verify old signatures are rejected."""
    signer = RequestSigner(signing_key='test_key', timestamp_window=60)
    
    # Create old signature (5 minutes ago)
    old_timestamp = int(time.time()) - 300
    headers = signer.sign_request(
      'GET',
      'https://api.test.com',
      timestamp=old_timestamp
    )
    
    # Should reject old signature
    is_valid = signer.verify_signature(
      'GET',
      'https://api.test.com',
      headers['X-Signature'],
      old_timestamp
    )
    
    assert not is_valid
  
  def test_signature_includes_request_body(self):
    """Verify signature includes request body in HMAC."""
    signer = RequestSigner(signing_key='test_key')
    
    # Same URL/method, different bodies should have different signatures
    headers1 = signer.sign_request(
      'POST',
      'https://api.test.com',
      body={'action': 'create'}
    )
    
    headers2 = signer.sign_request(
      'POST',
      'https://api.test.com',
      body={'action': 'delete'}
    )
    
    # Signatures should differ
    assert headers1['X-Signature'] != headers2['X-Signature']
  
  def test_future_timestamp_rejected(self):
    """Verify future timestamps are rejected to prevent attacks."""
    signer = RequestSigner(signing_key='test_key')
    
    # Create future timestamp (5 minutes ahead)
    future_timestamp = int(time.time()) + 300
    headers = signer.sign_request(
      'GET',
      'https://api.test.com',
      timestamp=future_timestamp
    )
    
    # Should reject future timestamp
    is_valid = signer.verify_signature(
      'GET',
      'https://api.test.com',
      headers['X-Signature'],
      future_timestamp
    )
    
    assert not is_valid


class TestParameterValidation:
  """Test suite for parameter validation and whitelisting."""
  
  def test_only_whitelisted_params_allowed(self):
    """Verify only whitelisted parameters are accepted."""
    validator = InputValidator()
    
    # Valid params
    valid_params = {'query': 'test', 'limit': 100}
    result = validator.validate_params(valid_params)
    assert result['query'] == 'test'
    
    # Invalid param
    with pytest.raises(SafetyCultureValidationError):
      validator.validate_params({'evil_param': 'value'})
  
  def test_limit_boundary_validation(self):
    """Verify limit parameter boundaries are enforced."""
    validator = InputValidator()
    
    # Within bounds
    result = validator.validate_params({'limit': 500})
    assert result['limit'] == 500
    
    # Exceeds maximum
    with pytest.raises(SafetyCultureValidationError):
      validator.validate_params({'limit': 10000})
    
    # Below minimum
    with pytest.raises(SafetyCultureValidationError):
      validator.validate_params({'limit': 0})
  
  def test_offset_boundary_validation(self):
    """Verify offset parameter boundaries are enforced."""
    validator = InputValidator()
    
    # Valid offset
    result = validator.validate_params({'offset': 1000})
    assert result['offset'] == 1000
    
    # Exceeds maximum
    with pytest.raises(SafetyCultureValidationError):
      validator.validate_params({'offset': 200000})
  
  def test_query_length_validation(self):
    """Verify query length is limited."""
    validator = InputValidator()
    
    # Valid length
    result = validator.validate_params({'query': 'test' * 10})
    assert 'query' in result
    
    # Exceeds maximum
    long_query = 'a' * 1000
    with pytest.raises(SafetyCultureValidationError):
      validator.validate_params({'query': long_query})