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

"""Input validation and sanitization for SafetyCulture agent."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Set
from urllib.parse import urlparse

from ..exceptions import SafetyCultureValidationError

logger = logging.getLogger(__name__)


class InputValidator:
  """Validates and sanitizes user inputs to prevent injection attacks."""
  
  # Allowed URL parameters for API calls
  ALLOWED_PARAMS: Set[str] = {
    'query',
    'limit',
    'offset',
    'fields',
    'field',
    'sort',
    'filter',
    'page',
    'per_page',
    'order',
    'include',
    'exclude',
    'archived',
    'modified_after',
    'template',
    'asset_type',
    'site_id',
    'name',
    'email',
  }
  
  # Parameter value constraints
  MAX_LIMIT = 1000
  MAX_OFFSET = 100000
  MAX_QUERY_LENGTH = 500
  MAX_STRING_LENGTH = 1000
  
  # Safe field name pattern (alphanumeric + underscore only)
  FIELD_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')
  
  # Safe string pattern (no control characters)
  SAFE_STRING_PATTERN = re.compile(r'^[\w\s\-\.@,]+$')
  
  @classmethod
  def validate_params(
      cls,
      params: Dict[str, Any]
  ) -> Dict[str, Any]:
    """Validate URL parameters against whitelist.
    
    Args:
        params: Dictionary of URL parameters to validate
        
    Returns:
        Dictionary of validated and sanitized parameters
        
    Raises:
        SafetyCultureValidationError: If validation fails
    """
    if not isinstance(params, dict):
      raise SafetyCultureValidationError(
        f"Parameters must be a dictionary, got {type(params).__name__}"
      )
    
    validated = {}
    
    for key, value in params.items():
      # Check parameter name against whitelist
      if key not in cls.ALLOWED_PARAMS:
        raise SafetyCultureValidationError(
          f"Invalid parameter: '{key}'. "
          f"Allowed: {', '.join(sorted(cls.ALLOWED_PARAMS))}"
        )
      
      # Validate based on parameter type
      if key == 'query':
        validated[key] = cls._validate_query(value)
      elif key == 'limit':
        validated[key] = cls._validate_limit(value)
      elif key == 'offset':
        validated[key] = cls._validate_offset(value)
      elif key in ('fields', 'field'):
        validated[key] = cls._validate_fields(value)
      elif key in ('sort', 'order'):
        validated[key] = cls._validate_sort(value)
      elif key == 'archived':
        validated[key] = cls._validate_boolean(value)
      elif key in ('asset_type', 'site_id', 'email'):
        # These can be lists
        validated[key] = value if isinstance(value, list) else [value]
      else:
        validated[key] = cls._sanitize_string(value)
    
    return validated
  
  @classmethod
  def _validate_query(cls, query: Any) -> str:
    """Validate search query string.
    
    Args:
        query: Query value to validate
        
    Returns:
        Sanitized query string
        
    Raises:
        SafetyCultureValidationError: If validation fails
    """
    if not isinstance(query, str):
      raise SafetyCultureValidationError(
        f"Query must be a string, got {type(query).__name__}"
      )
    
    if len(query) > cls.MAX_QUERY_LENGTH:
      raise SafetyCultureValidationError(
        f"Query too long ({len(query)} chars). "
        f"Maximum: {cls.MAX_QUERY_LENGTH}"
      )
    
    # Remove control characters but allow spaces and common punctuation
    sanitized = ''.join(
      char for char in query
      if char.isprintable() or char.isspace()
    )
    
    return sanitized.strip()
  
  @classmethod
  def _validate_limit(cls, limit: Any) -> int:
    """Validate limit parameter.
    
    Args:
        limit: Limit value to validate
        
    Returns:
        Validated limit as integer
        
    Raises:
        SafetyCultureValidationError: If validation fails
    """
    try:
      limit_int = int(limit)
    except (ValueError, TypeError) as e:
      raise SafetyCultureValidationError(
        f"Limit must be an integer, got {type(limit).__name__}"
      ) from e
    
    if limit_int < 1 or limit_int > cls.MAX_LIMIT:
      raise SafetyCultureValidationError(
        f"Limit must be between 1 and {cls.MAX_LIMIT}, got {limit_int}"
      )
    
    return limit_int
  
  @classmethod
  def _validate_offset(cls, offset: Any) -> int:
    """Validate offset parameter.
    
    Args:
        offset: Offset value to validate
        
    Returns:
        Validated offset as integer
        
    Raises:
        SafetyCultureValidationError: If validation fails
    """
    try:
      offset_int = int(offset)
    except (ValueError, TypeError) as e:
      raise SafetyCultureValidationError(
        f"Offset must be an integer, got {type(offset).__name__}"
      ) from e
    
    if offset_int < 0 or offset_int > cls.MAX_OFFSET:
      raise SafetyCultureValidationError(
        f"Offset must be between 0 and {cls.MAX_OFFSET}, got {offset_int}"
      )
    
    return offset_int
  
  @classmethod
  def _validate_fields(cls, fields: Any) -> Any:
    """Validate fields parameter.
    
    Args:
        fields: Fields value to validate (string, list, or single value)
        
    Returns:
        Validated fields (preserves input type for API compatibility)
        
    Raises:
        SafetyCultureValidationError: If validation fails
    """
    # Handle list of fields
    if isinstance(fields, list):
      validated_fields = []
      for field in fields:
        field_str = str(field).strip()
        if not cls.FIELD_NAME_PATTERN.match(field_str):
          raise SafetyCultureValidationError(
            f"Invalid field name: '{field_str}'. "
            "Field names must contain only letters, numbers, and underscores."
          )
        validated_fields.append(field_str)
      
      if not validated_fields:
        raise SafetyCultureValidationError(
          "Fields parameter cannot be empty"
        )
      
      return validated_fields
    
    # Handle comma-separated string
    if isinstance(fields, str):
      field_list = [f.strip() for f in fields.split(',') if f.strip()]
      validated_fields = []
      
      for field in field_list:
        if not cls.FIELD_NAME_PATTERN.match(field):
          raise SafetyCultureValidationError(
            f"Invalid field name: '{field}'. "
            "Field names must contain only letters, numbers, and underscores."
          )
        validated_fields.append(field)
      
      if not validated_fields:
        raise SafetyCultureValidationError(
          "Fields parameter cannot be empty"
        )
      
      return ','.join(validated_fields)
    
    # Handle single field value
    field_str = str(fields).strip()
    if not cls.FIELD_NAME_PATTERN.match(field_str):
      raise SafetyCultureValidationError(
        f"Invalid field name: '{field_str}'. "
        "Field names must contain only letters, numbers, and underscores."
      )
    
    return field_str
  
  @classmethod
  def _validate_sort(cls, sort: Any) -> str:
    """Validate sort parameter.
    
    Args:
        sort: Sort value to validate
        
    Returns:
        Validated sort string
        
    Raises:
        SafetyCultureValidationError: If validation fails
    """
    if not isinstance(sort, str):
      raise SafetyCultureValidationError(
        f"Sort must be a string, got {type(sort).__name__}"
      )
    
    # Allow field_name or -field_name for descending
    sort = sort.strip()
    if sort.startswith('-'):
      field = sort[1:]
    else:
      field = sort
    
    if not cls.FIELD_NAME_PATTERN.match(field):
      raise SafetyCultureValidationError(
        f"Invalid sort field: '{field}'. "
        "Must contain only letters, numbers, and underscores."
      )
    
    return sort
  
  @classmethod
  def _validate_boolean(cls, value: Any) -> str:
    """Validate boolean parameter.
    
    Args:
        value: Boolean value to validate
        
    Returns:
        Validated boolean as lowercase string
        
    Raises:
        SafetyCultureValidationError: If validation fails
    """
    if isinstance(value, bool):
      return str(value).lower()
    
    if isinstance(value, str):
      if value.lower() in ('true', 'false'):
        return value.lower()
    
    raise SafetyCultureValidationError(
      f"Boolean parameter must be true/false, got: {value}"
    )
  
  @classmethod
  def _sanitize_string(cls, value: Any) -> str:
    """Sanitize generic string value.
    
    Args:
        value: Value to sanitize
        
    Returns:
        Sanitized string
        
    Raises:
        SafetyCultureValidationError: If value is too long
    """
    str_value = str(value)
    
    if len(str_value) > cls.MAX_STRING_LENGTH:
      raise SafetyCultureValidationError(
        f"String too long ({len(str_value)} chars). "
        f"Maximum: {cls.MAX_STRING_LENGTH}"
      )
    
    # Remove control characters
    sanitized = ''.join(
      char for char in str_value
      if char.isprintable() or char.isspace()
    )
    
    return sanitized.strip()
  
  @classmethod
  def validate_url(cls, url: str) -> str:
    """Validate URL is properly formatted and uses HTTPS.
    
    Args:
        url: URL to validate
        
    Returns:
        Validated URL
        
    Raises:
        SafetyCultureValidationError: If URL is invalid
    """
    if not isinstance(url, str):
      raise SafetyCultureValidationError(
        f"URL must be a string, got {type(url).__name__}"
      )
    
    try:
      parsed = urlparse(url)
    except Exception as e:
      raise SafetyCultureValidationError(
        f"Invalid URL format: {url}"
      ) from e
    
    if parsed.scheme != 'https':
      raise SafetyCultureValidationError(
        f"URL must use HTTPS protocol, got: {parsed.scheme}"
      )
    
    if not parsed.netloc:
      raise SafetyCultureValidationError(
        f"URL missing hostname: {url}"
      )
    
    return url
  
  @classmethod
  def validate_and_enforce_https(
      cls,
      url: str,
      allow_localhost: bool = False
  ) -> str:
    """Validate URL with strict HTTPS enforcement.
    
    This method is used for runtime URL validation to ensure no
    HTTP URLs are accidentally used in production.
    
    Args:
        url: URL to validate and enforce HTTPS
        allow_localhost: If True, allow http://localhost for development
        
    Returns:
        Validated HTTPS URL
        
    Raises:
        SafetyCultureValidationError: If URL is not HTTPS or invalid
    """
    if not isinstance(url, str) or not url.strip():
      raise SafetyCultureValidationError(
        "URL cannot be empty"
      )
    
    url = url.strip()
    
    try:
      parsed = urlparse(url)
    except Exception as e:
      raise SafetyCultureValidationError(
        f"Invalid URL format: {url}"
      ) from e
    
    # Allow localhost for development/testing
    if allow_localhost and parsed.netloc in ('localhost', '127.0.0.1'):
      if parsed.scheme not in ('http', 'https'):
        raise SafetyCultureValidationError(
          f"Localhost URL must use http or https: {url}"
        )
      return url
    
    # Enforce HTTPS for all other URLs
    if parsed.scheme != 'https':
      raise SafetyCultureValidationError(
        f"All external URLs must use HTTPS protocol. "
        f"Got '{parsed.scheme}' in: {url}"
      )
    
    if not parsed.netloc:
      raise SafetyCultureValidationError(
        f"URL missing hostname: {url}"
      )
    
    # Warn about suspicious URLs
    suspicious_tlds = {'.local', '.internal', '.test'}
    if any(parsed.netloc.endswith(tld) for tld in suspicious_tlds):
      logger.warning(
        f"Suspicious TLD in URL: {parsed.netloc}. "
        "Ensure this is intentional."
      )
    
    return url
  
  @classmethod
  def validate_endpoint(cls, endpoint: str) -> str:
    """Validate API endpoint path.
    
    Args:
        endpoint: Endpoint path (e.g., '/api/v1/assets')
        
    Returns:
        Validated endpoint path
        
    Raises:
        SafetyCultureValidationError: If endpoint is invalid
    """
    if not isinstance(endpoint, str):
      raise SafetyCultureValidationError(
        f"Endpoint must be a string, got {type(endpoint).__name__}"
      )
    
    endpoint = endpoint.strip()
    
    # Must start with /
    if not endpoint.startswith('/'):
      raise SafetyCultureValidationError(
        f"Endpoint must start with '/': {endpoint}"
      )
    
    # Check for suspicious patterns
    suspicious_patterns = ['..', '//', '\\', '<', '>', '{', '}']
    for pattern in suspicious_patterns:
      if pattern in endpoint:
        raise SafetyCultureValidationError(
          f"Endpoint contains suspicious pattern '{pattern}': {endpoint}"
        )
    
    return endpoint
  
  @classmethod
  def validate_asset_id(cls, asset_id: str) -> str:
    """Validate asset ID format.
    
    Args:
        asset_id: Asset ID to validate
        
    Returns:
        Validated asset ID
        
    Raises:
        SafetyCultureValidationError: If asset ID is invalid
    """
    if not isinstance(asset_id, str):
      raise SafetyCultureValidationError(
        f"Asset ID must be a string, got {type(asset_id).__name__}"
      )
    
    if not asset_id or not asset_id.strip():
      raise SafetyCultureValidationError(
        "Asset ID cannot be empty"
      )
    
    # Allow alphanumeric, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9\-_]+$', asset_id):
      raise SafetyCultureValidationError(
        f"Invalid asset ID format: '{asset_id}'. "
        "Must contain only letters, numbers, hyphens, and underscores."
      )
    
    if len(asset_id) > 100:
      raise SafetyCultureValidationError(
        f"Asset ID too long: {len(asset_id)} chars (max 100)"
      )
    
    return asset_id.strip()
  
  @classmethod
  def validate_template_id(cls, template_id: str) -> str:
    """Validate template ID format.
    
    Args:
        template_id: Template ID to validate
        
    Returns:
        Validated template ID
        
    Raises:
        SafetyCultureValidationError: If template ID is invalid
    """
    # Template IDs follow same rules as asset IDs
    return cls.validate_asset_id(template_id)
  
  @classmethod
  def validate_audit_id(cls, audit_id: str) -> str:
    """Validate audit/inspection ID format.
    
    Args:
        audit_id: Audit ID to validate
        
    Returns:
        Validated audit ID
        
    Raises:
        SafetyCultureValidationError: If audit ID is invalid
    """
    # Audit IDs follow same rules as asset IDs
    return cls.validate_asset_id(audit_id)