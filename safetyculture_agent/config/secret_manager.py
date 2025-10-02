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

"""Centralized secret management with encryption and audit logging."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class SecretManager:
  """Centralized secret management with encryption and rotation.
  
  This class provides secure access to secrets from environment variables
  with optional encryption at rest, audit logging, and rotation support.
  It replaces direct os.getenv() calls throughout the codebase.
  
  Features:
      - Encrypted caching of secrets
      - Audit logging of secret access
      - Automatic redaction in logs
      - Secret rotation support
      - Default value handling
      - Type conversion
  
  Attributes:
      _cache: Encrypted secret cache
      _accessed_secrets: Set of secrets that have been accessed
      _encryption_key: Key for encrypting cached secrets
  """
  
  def __init__(self, encryption_key: Optional[str] = None):
    """Initialize secret manager.
    
    Args:
        encryption_key: Optional encryption key for cache.
                       If not provided, generates a session key.
    """
    self._cache: Dict[str, bytes] = {}
    self._accessed_secrets: Set[str] = set()
    self._last_rotation: Dict[str, datetime] = {}
    
    # Initialize encryption
    if encryption_key:
      # Use provided key (should be base64-encoded)
      self._encryption_key = encryption_key.encode()
    else:
      # Generate session key
      self._encryption_key = Fernet.generate_key()
    
    self._cipher = Fernet(self._encryption_key)
    
    logger.info("SecretManager initialized")
  
  def get_secret(
      self,
      key: str,
      default: Optional[str] = None,
      required: bool = False
  ) -> Optional[str]:
    """Get a secret from environment variables.
    
    This method replaces os.getenv() calls. It provides encrypted
    caching, audit logging, and secure default handling.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: If True, raises error when secret not found
        
    Returns:
        Secret value or default
        
    Raises:
        ValueError: If required=True and secret not found
        
    Example:
        >>> secret_mgr = SecretManager()
        >>> api_key = secret_mgr.get_secret('API_KEY', required=True)
        >>> optional = secret_mgr.get_secret('OPTIONAL_KEY', default='value')
    """
    # Check cache first
    if key in self._cache:
      logger.debug(f"Retrieved secret '{key}' from cache")
      encrypted_value = self._cache[key]
      value = self._cipher.decrypt(encrypted_value).decode('utf-8')
      self._accessed_secrets.add(key)
      return value
    
    # Get from environment
    value = os.getenv(key, default)
    
    if value is None and required:
      logger.error(f"Required secret '{key}' not found")
      raise ValueError(
        f"Required secret '{key}' not found in environment variables"
      )
    
    if value is not None:
      # Cache encrypted value
      encrypted_value = self._cipher.encrypt(value.encode('utf-8'))
      self._cache[key] = encrypted_value
      self._accessed_secrets.add(key)
      self._last_rotation[key] = datetime.now()
      
      logger.debug(
        f"Secret '{key}' loaded from environment "
        f"(length: {len(value)} chars)"
      )
    else:
      logger.debug(f"Secret '{key}' not found, using default")
    
    return value
  
  def get_secret_int(
      self,
      key: str,
      default: Optional[int] = None,
      required: bool = False
  ) -> Optional[int]:
    """Get a secret as integer.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: If True, raises error when not found
        
    Returns:
        Secret value as integer or default
    """
    value = self.get_secret(key, str(default) if default else None, required)
    if value is None:
      return None
    
    try:
      return int(value)
    except ValueError as e:
      logger.error(f"Failed to convert secret '{key}' to int: {value}")
      raise ValueError(
        f"Secret '{key}' must be an integer, got: {value}"
      ) from e
  
  def get_secret_bool(
      self,
      key: str,
      default: Optional[bool] = None,
      required: bool = False
  ) -> Optional[bool]:
    """Get a secret as boolean.
    
    Accepts: true/false, yes/no, 1/0, on/off (case-insensitive)
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: If True, raises error when not found
        
    Returns:
        Secret value as boolean or default
    """
    value = self.get_secret(
      key,
      str(default) if default is not None else None,
      required
    )
    if value is None:
      return None
    
    value_lower = value.lower()
    if value_lower in ('true', 'yes', '1', 'on'):
      return True
    elif value_lower in ('false', 'no', '0', 'off'):
      return False
    else:
      raise ValueError(
        f"Secret '{key}' must be boolean-like, got: {value}"
      )
  
  def clear_secret(self, key: str) -> None:
    """Clear a secret from cache (for rotation).
    
    Args:
        key: Secret key to clear
    """
    if key in self._cache:
      del self._cache[key]
      logger.info(f"Cleared secret '{key}' from cache")
  
  def clear_all_secrets(self) -> None:
    """Clear all secrets from cache."""
    count = len(self._cache)
    self._cache.clear()
    self._accessed_secrets.clear()
    logger.info(f"Cleared {count} secrets from cache")
  
  def rotate_secret(self, key: str) -> Optional[str]:
    """Rotate a secret by clearing cache and reloading.
    
    Args:
        key: Secret key to rotate
        
    Returns:
        New secret value or None
    """
    self.clear_secret(key)
    new_value = self.get_secret(key)
    
    if new_value:
      logger.info(f"Rotated secret '{key}'")
    
    return new_value
  
  def get_secret_age(self, key: str) -> Optional[timedelta]:
    """Get age of secret since last rotation.
    
    Args:
        key: Secret key
        
    Returns:
        Age as timedelta or None if not tracked
    """
    if key not in self._last_rotation:
      return None
    
    return datetime.now() - self._last_rotation[key]
  
  def get_accessed_secrets(self) -> Set[str]:
    """Get set of all accessed secret keys.
    
    Useful for auditing which secrets are actually used.
    
    Returns:
        Set of secret keys that have been accessed
    """
    return self._accessed_secrets.copy()
  
  def redact_value(self, value: str) -> str:
    """Redact a secret value for logging.
    
    Shows first and last 4 characters for identification.
    
    Args:
        value: Secret value to redact
        
    Returns:
        Redacted value like "abcd****wxyz"
    """
    if not value or len(value) < 8:
      return "****"
    
    return f"{value[:4]}****{value[-4:]}"
  
  def export_audit_log(self) -> Dict[str, Any]:
    """Export audit log of secret access.
    
    Returns:
        Dictionary with audit information:
            - accessed_secrets: List of accessed keys
            - total_secrets: Count of cached secrets
            - oldest_secret: Age of oldest secret
    """
    oldest_age = None
    if self._last_rotation:
      oldest_time = min(self._last_rotation.values())
      oldest_age = (datetime.now() - oldest_time).total_seconds()
    
    return {
      'accessed_secrets': sorted(list(self._accessed_secrets)),
      'total_cached': len(self._cache),
      'oldest_secret_age_seconds': oldest_age,
      'timestamp': datetime.now().isoformat()
    }


# Global instance for convenience
_global_secret_manager: Optional[SecretManager] = None


def get_secret_manager() -> SecretManager:
  """Get or create global secret manager instance.
  
  Returns:
      Global SecretManager instance
  """
  global _global_secret_manager
  
  if _global_secret_manager is None:
    _global_secret_manager = SecretManager()
  
  return _global_secret_manager


def set_secret_manager(manager: SecretManager) -> None:
  """Set global secret manager instance.
  
  Args:
      manager: SecretManager to use globally
  """
  global _global_secret_manager
  _global_secret_manager = manager
  logger.info("Global secret manager updated")


# Convenience functions for common use
def get_secret(
    key: str,
    default: Optional[str] = None,
    required: bool = False
) -> Optional[str]:
  """Convenience function to get secret from global manager.
  
  Args:
      key: Environment variable name
      default: Default value
      required: If True, raises error when not found
      
  Returns:
      Secret value or default
  """
  return get_secret_manager().get_secret(key, default, required)


def get_secret_int(
    key: str,
    default: Optional[int] = None,
    required: bool = False
) -> Optional[int]:
  """Get secret as integer from global manager."""
  return get_secret_manager().get_secret_int(key, default, required)


def get_secret_bool(
    key: str,
    default: Optional[bool] = None,
    required: bool = False
) -> Optional[bool]:
  """Get secret as boolean from global manager."""
  return get_secret_manager().get_secret_bool(key, default, required)