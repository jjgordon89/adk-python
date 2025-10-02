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

import logging
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Optional
from urllib.parse import urlparse

from .credential_manager import SecureCredentialManager
from ..exceptions import SafetyCultureCredentialError

logger = logging.getLogger(__name__)

# API Configuration constants
DEFAULT_REQUESTS_PER_SECOND = 10  # Default rate limit for API requests
DEFAULT_MAX_RETRIES = 3  # Maximum retry attempts for failed requests
DEFAULT_RETRY_DELAY_SECONDS = 1.0  # Initial delay between retries in seconds
DEFAULT_BATCH_SIZE = 50  # Default batch size for operations
DEFAULT_MAX_CONCURRENT_REQUESTS = 5  # Maximum concurrent API requests
DEFAULT_REQUEST_TIMEOUT_SECONDS = 30  # Default timeout for API requests


@dataclass
class SafetyCultureConfig:
  """Configuration for SafetyCulture API integration."""
  
  # API Configuration
  base_url: str = "https://api.safetyculture.io"
  
  # Rate limiting
  requests_per_second: int = DEFAULT_REQUESTS_PER_SECOND
  max_retries: int = DEFAULT_MAX_RETRIES
  retry_delay: float = DEFAULT_RETRY_DELAY_SECONDS
  
  # Batch processing
  batch_size: int = DEFAULT_BATCH_SIZE
  max_concurrent_requests: int = DEFAULT_MAX_CONCURRENT_REQUESTS
  
  # Timeouts
  request_timeout: int = DEFAULT_REQUEST_TIMEOUT_SECONDS
  
  # Private credential manager
  _credential_manager: Optional[SecureCredentialManager] = None
  
  def __post_init__(self):
    """Initialize configuration with secure credential management and validation."""
    if not self._credential_manager:
      self._credential_manager = SecureCredentialManager()
    
    # Strict HTTPS validation
    if not self.base_url.startswith('https://'):
      raise ValueError(
        f"API URL must use HTTPS protocol (got: {self.base_url}). "
        "HTTP is not allowed for security reasons."
      )
    
    # Additional URL validation
    try:
      parsed = urlparse(self.base_url)
      if not parsed.netloc:
        raise ValueError(
          f"Invalid API URL (missing hostname): {self.base_url}"
        )
      if parsed.path and parsed.path != '/':
        logger.warning(
          f"Base URL contains path: {parsed.path}. "
          "This may cause issues with endpoint construction."
        )
    except Exception as e:
      raise ValueError(
        f"Invalid API URL format: {self.base_url}"
      ) from e
  
  async def get_api_token(self) -> str:
    """Retrieve API token securely.
    
    Returns:
        Decrypted API token
        
    Raises:
        SafetyCultureCredentialError: If token retrieval fails
    """
    if not self._credential_manager:
      self._credential_manager = SecureCredentialManager()
    
    return await self._credential_manager.get_api_token()
  
  async def get_headers(self) -> Dict[str, str]:
    """Get HTTP headers for API requests.
    
    Returns:
        Dictionary of HTTP headers with authentication
        
    Raises:
        SafetyCultureCredentialError: If token retrieval fails
    """
    token = await self.get_api_token()
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

  
  async def revoke_credentials(self) -> None:
    """Revoke all cached credentials.
    
    This should be called on logout or when credentials are compromised.
    After revocation, new API calls will fail until new credentials
    are provided.
    """
    if hasattr(self, '_credential_manager') and self._credential_manager:
      await self._credential_manager.revoke_token()
      logger.info("Credentials revoked successfully")

  async def test_credentials(self) -> bool:
    """Test if current credentials are valid.
    
    Returns:
        True if credentials are valid, False otherwise
    """
    if not hasattr(self, '_credential_manager') or not self._credential_manager:
      return False
    
    return await self._credential_manager.test_token_validity(self.base_url)

  async def get_credential_status(self) -> Dict[str, Any]:
    """Get status of current credentials.
    
    Returns:
        Dictionary with credential status information
    """
    if not hasattr(self, '_credential_manager') or not self._credential_manager:
      return {'status': 'not_initialized'}
    
    token_info = await self._credential_manager.get_token_info()
    
    if not token_info['has_token']:
      return {'status': 'no_token'}
    
    is_valid = await self._credential_manager.test_token_validity(self.base_url)
    
    return {
      'status': 'valid' if is_valid else 'invalid',
      'token_info': token_info
    }

# Default configuration instance
DEFAULT_CONFIG = SafetyCultureConfig()
