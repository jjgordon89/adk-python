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

"""Tools for managing API credentials and authentication."""

from __future__ import annotations

import json
import logging
from typing import Any
from typing import Dict
from typing import Optional

from ..config.api_config import SafetyCultureConfig
from ..exceptions import SafetyCultureCredentialError

logger = logging.getLogger(__name__)

# Global config instance (should be initialized by agent)
_api_config: Optional[SafetyCultureConfig] = None


def set_api_config(config: SafetyCultureConfig) -> None:
  """Set the global API configuration instance.
  
  Args:
      config: APIConfig instance to use
  """
  global _api_config
  _api_config = config


async def revoke_safetyculture_credentials() -> str:
  """Revoke SafetyCulture API credentials.
  
  This tool revokes cached credentials, requiring re-authentication
  for subsequent API calls. Use this on logout or when credentials
  are compromised.
  
  Returns:
      JSON string with revocation status
      
  Raises:
      SafetyCultureCredentialError: If revocation fails
  """
  if not _api_config:
    raise SafetyCultureCredentialError(
      "API configuration not initialized"
    )
  
  try:
    await _api_config.revoke_credentials()
    
    result = {
      'success': True,
      'message': 'Credentials revoked successfully'
    }
    
    logger.info("Credentials revoked via tool")
    return json.dumps(result)
    
  except Exception as e:
    logger.error(f"Failed to revoke credentials: {e}")
    raise SafetyCultureCredentialError(
      f"Credential revocation failed: {e}"
    ) from e


async def test_safetyculture_credentials() -> str:
  """Test if SafetyCulture API credentials are valid.
  
  Makes a lightweight API call to verify credentials are working.
  
  Returns:
      JSON string with validation status
  """
  if not _api_config:
    return json.dumps({
      'valid': False,
      'error': 'API configuration not initialized'
    })
  
  try:
    is_valid = await _api_config.test_credentials()
    
    result = {
      'valid': is_valid,
      'message': (
        'Credentials are valid' if is_valid else 'Credentials are invalid'
      )
    }
    
    return json.dumps(result)
    
  except Exception as e:
    logger.error(f"Credential validation failed: {e}")
    return json.dumps({
      'valid': False,
      'error': str(e)
    })


async def get_credential_status() -> str:
  """Get status of current API credentials.
  
  Returns:
      JSON string with credential status information
  """
  if not _api_config:
    return json.dumps({
      'status': 'not_initialized',
      'message': 'API configuration not set up'
    })
  
  try:
    status = await _api_config.get_credential_status()
    return json.dumps(status)
    
  except Exception as e:
    logger.error(f"Failed to get credential status: {e}")
    return json.dumps({
      'status': 'error',
      'error': str(e)
    })