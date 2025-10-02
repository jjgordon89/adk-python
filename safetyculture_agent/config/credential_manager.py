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

"""Secure credential management for SafetyCulture API."""

from __future__ import annotations

import logging
from typing import Any
from typing import Dict
from typing import Optional

from .secret_manager import get_secret
from ..exceptions import SafetyCultureCredentialError
from ..exceptions import SafetyCultureValidationError

logger = logging.getLogger(__name__)

# Credential manager constants
TOKEN_VALIDATION_TIMEOUT_SECONDS = 10  # Timeout for token validation API calls
TOKEN_PREVIEW_PREFIX_LENGTH = 4  # Number of characters to show at start
TOKEN_PREVIEW_SUFFIX_LENGTH = 4  # Number of characters to show at end
TOKEN_PREVIEW_MIN_LENGTH = 8  # Minimum length for preview generation


class SecureCredentialManager:
  """Manages secure storage and retrieval of API credentials."""

  def __init__(self) -> None:
    """Initialize credential manager."""
    self._cached_token: Optional[str] = None

  async def get_api_token(self) -> str:
    """Retrieve API token securely.

    Returns:
        API token for SafetyCulture API

    Raises:
        SafetyCultureCredentialError: If token cannot be retrieved
    """
    # First check cache
    if self._cached_token:
      return self._cached_token

    # Try environment variable via SecretManager
    token = get_secret('SAFETYCULTURE_API_TOKEN')
    if not token:
      raise SafetyCultureCredentialError(
        "API token not found. Please set SAFETYCULTURE_API_TOKEN "
        "environment variable or configure secure credential storage. "
        "Get your token from: "
        "https://app.safetyculture.com/account/api-tokens"
      )

    # Cache for this session
    self._cached_token = token
    return token

  async def rotate_token(self, new_token: str) -> None:
    """Rotate API token with new value.

    Args:
        new_token: New API token value

    Raises:
        SafetyCultureValidationError: If token format is invalid
    """
    if not new_token or not isinstance(new_token, str):
      raise SafetyCultureValidationError("Invalid token format")

    self._cached_token = new_token

  async def revoke_token(self) -> None:
    """Revoke the current API token.
    
    This method invalidates the cached token. For full revocation,
    the token should also be revoked at the SafetyCulture API level.
    
    Note:
        SafetyCulture API doesn't provide a standard revocation endpoint.
        This method clears the local cache. For complete security,
        generate a new token in the SafetyCulture dashboard and rotate.
    """
    if self._cached_token:
      logger.info("Revoking cached API token")
      self._cached_token = None
    else:
      logger.debug("No cached token to revoke")

  async def is_token_valid(self) -> bool:
    """Check if a token is currently cached.
    
    Returns:
        True if token is cached, False otherwise
        
    Note:
        This only checks if a token exists in cache, not if it's
        actually valid at the API level. Use test_token_validity()
        for API-level validation.
    """
    return self._cached_token is not None

  async def test_token_validity(
      self,
      api_base_url: str = "https://api.safetyculture.io"
  ) -> bool:
    """Test if the cached token is valid by making an API call.
    
    Args:
        api_base_url: Base URL for SafetyCulture API
        
    Returns:
        True if token is valid, False otherwise
    """
    if not self._cached_token:
      return False
    
    try:
      import aiohttp
      
      headers = {
        'Authorization': f'Bearer {self._cached_token}',
        'Content-Type': 'application/json'
      }
      
      # Make a lightweight API call to test credentials
      async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{api_base_url}/accounts/v1/user",
            headers=headers,
            timeout=aiohttp.ClientTimeout(
                total=TOKEN_VALIDATION_TIMEOUT_SECONDS
            )
        ) as response:
          return response.status == 200
          
    except Exception as e:
      logger.debug(f"Token validation failed: {e}")
      return False

  async def get_token_info(self) -> Dict[str, Any]:
    """Get information about the current token.
    
    Returns:
        Dictionary with token information:
            - has_token: Whether a token is cached
            - token_length: Length of token (for verification)
            - token_preview: First and last 4 chars (for identification)
    """
    if not self._cached_token:
      return {
        'has_token': False,
        'token_length': 0,
        'token_preview': None
      }
    
    token = self._cached_token
    preview = (
        f"{token[:TOKEN_PREVIEW_PREFIX_LENGTH]}..."
        f"{token[-TOKEN_PREVIEW_SUFFIX_LENGTH:]}"
        if len(token) > TOKEN_PREVIEW_MIN_LENGTH
        else "***"
    )
    
    return {
      'has_token': True,
      'token_length': len(token),
      'token_preview': preview
    }

  def clear_cache(self) -> None:
    """Clear cached credentials."""
    self._cached_token = None