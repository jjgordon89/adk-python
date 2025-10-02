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

import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlencode

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from ..config.api_config import SafetyCultureConfig, DEFAULT_CONFIG
from ..telemetry.decorators import trace_async
from ..telemetry.prometheus_metrics import (
  record_api_latency,
  record_api_request,
  record_circuit_breaker_state,
  record_rate_limit_hit,
)
from ..telemetry.telemetry_config import (
  SPAN_ATTR_API_ENDPOINT,
  SPAN_ATTR_API_METHOD,
  SPAN_ATTR_API_STATUS_CODE,
  SPAN_ATTR_CIRCUIT_BREAKER_STATE,
)
from ..exceptions import (
  SafetyCultureAPIError,
  SafetyCultureAuthError,
  SafetyCultureRateLimitError,
  SafetyCultureValidationError
)
from ..utils.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from ..utils.input_validator import InputValidator
from ..utils.rate_limiter import ExponentialBackoffRateLimiter
from ..utils.request_signer import RequestSigner, RequestSigningError
from ..utils.secure_header_manager import SecureHeaderManager

logger = logging.getLogger(__name__)

# Rate limiting constants
RATE_LIMIT_BURST_MULTIPLIER = 2  # Burst capacity as multiple of base rate
INITIAL_BACKOFF_SECONDS = 1.0  # Initial backoff delay in seconds
MAX_BACKOFF_SECONDS = 30.0  # Maximum backoff delay in seconds

# Circuit breaker constants
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5  # Failures before opening circuit
CIRCUIT_BREAKER_SUCCESS_THRESHOLD = 2  # Successes to close circuit
CIRCUIT_BREAKER_BASE_TIMEOUT_SECONDS = 60.0  # Initial circuit timeout
CIRCUIT_BREAKER_MAX_TIMEOUT_SECONDS = 600.0  # Maximum circuit timeout

# Request signing constants
REQUEST_SIGNING_WINDOW_SECONDS = 300  # Request signature validity window

# HTTP/API related constants
DEFAULT_RETRY_AFTER_SECONDS = 60  # Default retry-after value
EXPONENTIAL_BACKOFF_BASE = 2  # Base multiplier for exponential backoff
DEFAULT_ASSET_SEARCH_LIMIT = 100  # Default asset search page size
DEFAULT_ASSET_SEARCH_OFFSET = 0  # Default asset search offset
DEFAULT_INSPECTION_SEARCH_LIMIT = 1000  # Default inspection search limit
DEFAULT_SITE_SEARCH_LIMIT = 100  # Default site search limit


class SafetyCultureAPIClient:
  """Async client for SafetyCulture API interactions."""
  
  def __init__(self, config: SafetyCultureConfig = DEFAULT_CONFIG):
    """Initialize API client with rate limiting, security, and validation.
    
    Args:
        config: SafetyCultureConfig instance with credentials and rate limits
    """
    self.config = config
    self.header_manager = SecureHeaderManager()
    self.validator = InputValidator()
    self._session: Optional[ClientSession] = None
    
    # Initialize rate limiter with config values
    self.rate_limiter = ExponentialBackoffRateLimiter(
      rate=config.requests_per_second,
      burst=config.requests_per_second * RATE_LIMIT_BURST_MULTIPLIER,
      initial_backoff=INITIAL_BACKOFF_SECONDS,
      max_backoff=MAX_BACKOFF_SECONDS
    )
    
    # Initialize circuit breaker with default settings
    self.circuit_breaker = CircuitBreaker(
      failure_threshold=CIRCUIT_BREAKER_FAILURE_THRESHOLD,
      success_threshold=CIRCUIT_BREAKER_SUCCESS_THRESHOLD,
      base_timeout=CIRCUIT_BREAKER_BASE_TIMEOUT_SECONDS,
      max_timeout=CIRCUIT_BREAKER_MAX_TIMEOUT_SECONDS
    )
    
    # Initialize request signing (optional - only if signing key provided)
    self.request_signer: Optional[RequestSigner] = None
    signing_key = os.getenv('SAFETYCULTURE_SIGNING_KEY')
    if signing_key:
      self.request_signer = RequestSigner(
        signing_key=signing_key,
        timestamp_window=REQUEST_SIGNING_WINDOW_SECONDS
      )
      logger.info("Request signing enabled")
    else:
      logger.debug(
        "Request signing disabled (no signing key provided)"
      )
  
  async def __aenter__(self):
    """Async context manager entry."""
    await self._ensure_session()
    return self
  
  async def __aexit__(self, exc_type, exc_val, exc_tb):
    """Async context manager exit."""
    if self._session:
      await self._session.close()
      self._session = None
  
  async def _ensure_session(self):
    """Ensure HTTP session is created without credentials in session."""
    if not self._session:
      timeout = ClientTimeout(total=self.config.request_timeout)
      # Create session without default headers (tokens added per-request)
      self._session = ClientSession(timeout=timeout)
  
  async def _make_request(
      self,
      method: str,
      endpoint: str,
      params: Optional[Dict[str, Any]] = None,
      data: Optional[Dict[str, Any]] = None,
      retry_count: int = 0
  ) -> Dict[str, Any]:
    """Make HTTP request with circuit breaker, rate limiting, and security.
    
    Wraps the internal request implementation with a circuit breaker to
    protect against cascading failures when the API is unavailable.
    
    Args:
        method: HTTP method (GET, POST, etc)
        endpoint: API endpoint path
        params: Query parameters
        data: Request body data
        retry_count: Current retry attempt number
        
    Returns:
        Response data as dictionary
        
    Raises:
        CircuitBreakerOpenError: If circuit breaker is open
        SafetyCultureAPIError: If request fails
        SafetyCultureAuthError: If authentication fails
        SafetyCultureRateLimitError: If rate limit exceeded
        SafetyCultureValidationError: If URL validation fails
    """
    # Wrap the internal implementation with circuit breaker
    return await self.circuit_breaker.call(
      self._make_request_internal,
      method,
      endpoint,
      params,
      data,
      retry_count
    )
  
  async def _make_request_internal(
      self,
      method: str,
      endpoint: str,
      params: Optional[Dict[str, Any]] = None,
      data: Optional[Dict[str, Any]] = None,
      retry_count: int = 0
  ) -> Dict[str, Any]:
    """Internal HTTP request implementation with retries.
    
    This is the actual implementation that performs the HTTP request.
    It's wrapped by _make_request which adds circuit breaker protection.
    
    Args:
        method: HTTP method (GET, POST, etc)
        endpoint: API endpoint path
        params: Query parameters
        data: Request body data
        retry_count: Current retry attempt number
        
    Returns:
        Response data as dictionary
        
    Raises:
        SafetyCultureAPIError: If request fails
        SafetyCultureAuthError: If authentication fails
        SafetyCultureRateLimitError: If rate limit exceeded
        SafetyCultureValidationError: If URL validation fails
    """
    await self._ensure_session()
    
    # Acquire rate limit token before making request
    await self.rate_limiter.acquire()
    
    # Start timing for metrics
    start_time = time.perf_counter()
    
    # Validate endpoint path
    safe_endpoint = self.validator.validate_endpoint(endpoint)
    
    # Construct and validate full URL
    full_url = f"{self.config.base_url}{safe_endpoint}"
    validated_url = self.validator.validate_and_enforce_https(
      full_url,
      allow_localhost=False  # Strict HTTPS in production
    )
    
    # Validate and sanitize parameters
    if params:
      params = self.validator.validate_params(params)
    
    # Get API token securely
    api_token = await self.config.get_api_token()
    
    # Generate secure headers
    headers = await self.header_manager.get_secure_headers(api_token)
    
    # Add request signing if enabled
    if self.request_signer:
      try:
        signing_headers = self.request_signer.sign_request(
          method=method,
          url=validated_url,
          body=data
        )
        headers.update(signing_headers)
        logger.debug(f"Added signature headers to {method} {endpoint}")
      except Exception as e:
        sanitized_error = self.header_manager.sanitize_error(e)
        logger.error(f"Failed to sign request: {sanitized_error}")
        raise RequestSigningError(
          f"Request signing failed: {sanitized_error}"
        ) from e
    
    # Use validated URL instead of urljoin
    url = validated_url
    if params:
      # Handle multiple values for same parameter
      url_params = []
      for key, value in params.items():
        if isinstance(value, list):
          for item in value:
            url_params.append(f"{key}={item}")
        else:
          url_params.append(f"{key}={value}")
      if url_params:
        url += '?' + '&'.join(url_params)
    
    # Sanitize request data for logging
    safe_params = self.header_manager.sanitize_for_logging(params)
    safe_data = self.header_manager.sanitize_for_logging(data)
    logger.info(
      f"Making {method} request to {endpoint}",
      extra={'params': safe_params, 'data': safe_data}
    )
    
    try:
      if self._session is None:
        raise SafetyCultureAPIError("Session not initialized")
      
      async with self._session.request(
          method,
          url,
          headers=headers,
          json=data if data else None
      ) as response:
        # Record metrics
        duration = time.perf_counter() - start_time
        record_api_request(endpoint, method, response.status)
        record_api_latency(endpoint, method, duration)
        
        # Check for rate limit response from server
        if response.status == 429:
          retry_after = response.headers.get(
            'Retry-After',
            str(DEFAULT_RETRY_AFTER_SECONDS)
          )
          record_rate_limit_hit(endpoint)
          raise SafetyCultureRateLimitError(
            f"API rate limit exceeded. Retry after {retry_after}s"
          )
        
        if response.status == 401:
          raise SafetyCultureAuthError(
            "Authentication failed. Check API token."
          )
        
        response.raise_for_status()
        return await response.json()
    
    except aiohttp.ClientResponseError as e:
      safe_error = self.header_manager.sanitize_error(e)
      logger.error(f"HTTP error: {safe_error}")
      
      if retry_count < self.config.max_retries:
        await asyncio.sleep(
          self.config.retry_delay * (EXPONENTIAL_BACKOFF_BASE ** retry_count)
        )
        return await self._make_request_internal(
            method, endpoint, params, data, retry_count + 1
        )
      
      raise SafetyCultureAPIError(
        f"API request failed: {safe_error}",
        status_code=e.status
      ) from e
    
    except aiohttp.ClientError as e:
      safe_error = self.header_manager.sanitize_error(e)
      logger.error(f"Network error: {safe_error}")
      
      if retry_count < self.config.max_retries:
        await asyncio.sleep(
          self.config.retry_delay * (EXPONENTIAL_BACKOFF_BASE ** retry_count)
        )
        return await self._make_request_internal(
            method, endpoint, params, data, retry_count + 1
        )
      
      raise SafetyCultureAPIError(
        f"Network error: {safe_error}"
      ) from e
  
  def get_circuit_breaker_metrics(self) -> Dict[str, Any]:
    """Get circuit breaker metrics for monitoring.
    
    Returns:
        Dictionary containing circuit breaker metrics including:
        - state: Current circuit state (closed/open/half_open)
        - total_calls: Total number of calls attempted
        - total_failures: Total number of failures
        - total_successes: Total number of successes
        - failure_rate: Current failure rate (0.0-1.0)
        - open_count: Number of times circuit has opened
        - current_timeout: Current timeout value in seconds
    """
    return self.circuit_breaker.get_metrics()
  
  # Asset API methods
  @trace_async('search_assets', {'operation': 'search_assets'})
  async def search_assets(
      self,
      asset_types: Optional[List[str]] = None,
      site_ids: Optional[List[str]] = None,
      limit: int = DEFAULT_ASSET_SEARCH_LIMIT,
      offset: int = DEFAULT_ASSET_SEARCH_OFFSET
  ) -> Dict[str, Any]:
    """Search for assets with validated filters.
    
    Args:
        asset_types: List of asset types to filter by
        site_ids: List of site IDs to filter by
        limit: Maximum results to return (1-1000)
        offset: Pagination offset (0-100000)
        
    Returns:
        Dictionary containing search results
        
    Raises:
        SafetyCultureValidationError: If inputs are invalid
    """
    params: Dict[str, Any] = {
        'limit': limit,
        'offset': offset
    }
    
    if asset_types:
      params['asset_type'] = asset_types
    if site_ids:
      params['site_id'] = site_ids
    
    return await self._make_request('GET', '/assets/search', params=params)
  
  @trace_async('get_asset', {'operation': 'get_asset'})
  async def get_asset(self, asset_id: str) -> Dict[str, Any]:
    """Get a specific asset by ID.
    
    Args:
        asset_id: Validated asset identifier
        
    Returns:
        Dictionary containing asset details
        
    Raises:
        SafetyCultureValidationError: If asset_id is invalid
    """
    validated_id = self.validator.validate_asset_id(asset_id)
    return await self._make_request('GET', f'/assets/{validated_id}')
  
  # Template API methods
  @trace_async('search_templates', {'operation': 'search_templates'})
  async def search_templates(
      self,
      fields: Optional[List[str]] = None,
      archived: bool = False,
      modified_after: Optional[str] = None
  ) -> Dict[str, Any]:
    """Search for inspection templates."""
    params: Dict[str, Any] = {
        'archived': str(archived).lower()
    }
    
    if fields:
      params['field'] = fields
    else:
      params['field'] = ['template_id', 'name', 'modified_at']
    
    if modified_after:
      params['modified_after'] = modified_after
    
    return await self._make_request('GET', '/templates/search', params=params)
  
  @trace_async('get_template', {'operation': 'get_template'})
  async def get_template(self, template_id: str) -> Dict[str, Any]:
    """Get a specific template by ID.
    
    Args:
        template_id: Validated template identifier
        
    Returns:
        Dictionary containing template details
        
    Raises:
        SafetyCultureValidationError: If template_id is invalid
    """
    validated_id = self.validator.validate_template_id(template_id)
    return await self._make_request('GET', f'/templates/{validated_id}')
  
  # Inspection API methods
  @trace_async('search_inspections', {'operation': 'search_inspections'})
  async def search_inspections(
      self,
      fields: Optional[List[str]] = None,
      template_id: Optional[str] = None,
      modified_after: Optional[str] = None,
      limit: int = DEFAULT_INSPECTION_SEARCH_LIMIT
  ) -> Dict[str, Any]:
    """Search for inspections."""
    params: Dict[str, Any] = {
        'limit': limit
    }
    
    if fields:
      params['field'] = fields
    else:
      params['field'] = ['audit_id', 'modified_at', 'template_id']
    
    if template_id:
      params['template'] = template_id
    if modified_after:
      params['modified_after'] = modified_after
    
    return await self._make_request('GET', '/audits/search', params=params)
  
  @trace_async('create_inspection', {'operation': 'create_inspection'})
  async def create_inspection(
      self,
      template_id: str,
      header_items: Optional[List[Dict[str, Any]]] = None
  ) -> Dict[str, Any]:
    """Create a new inspection from template.
    
    Args:
        template_id: Validated template identifier
        header_items: Optional header data for inspection
        
    Returns:
        Dictionary containing created inspection details
        
    Raises:
        SafetyCultureValidationError: If template_id is invalid
    """
    validated_id = self.validator.validate_template_id(template_id)
    data: Dict[str, Any] = {
        'template_id': validated_id
    }
    
    if header_items:
      data['header_items'] = header_items
    
    return await self._make_request('POST', '/audits', data=data)
  
  @trace_async('update_inspection', {'operation': 'update_inspection'})
  async def update_inspection(
      self,
      audit_id: str,
      items: List[Dict[str, Any]]
  ) -> Dict[str, Any]:
    """Update inspection responses.
    
    Args:
        audit_id: Validated audit/inspection identifier
        items: List of inspection items to update
        
    Returns:
        Dictionary containing update results
        
    Raises:
        SafetyCultureValidationError: If audit_id is invalid
    """
    validated_id = self.validator.validate_audit_id(audit_id)
    data = {
        'items': items
    }
    
    return await self._make_request('PUT', f'/audits/{validated_id}', data=data)
  
  @trace_async('get_inspection', {'operation': 'get_inspection'})
  async def get_inspection(self, audit_id: str) -> Dict[str, Any]:
    """Get a specific inspection by ID.
    
    Args:
        audit_id: Validated audit/inspection identifier
        
    Returns:
        Dictionary containing inspection details
        
    Raises:
        SafetyCultureValidationError: If audit_id is invalid
    """
    validated_id = self.validator.validate_audit_id(audit_id)
    return await self._make_request('GET', f'/audits/{validated_id}')
  
  @trace_async('share_inspection', {'operation': 'share_inspection'})
  async def share_inspection(
      self,
      audit_id: str,
      shares: List[Dict[str, str]]
  ) -> Dict[str, Any]:
    """Share inspection with users or groups.
    
    Args:
        audit_id: Validated audit/inspection identifier
        shares: List of share configurations
        
    Returns:
        Dictionary containing share operation results
        
    Raises:
        SafetyCultureValidationError: If audit_id is invalid
    """
    validated_id = self.validator.validate_audit_id(audit_id)
    data = {
        'shares': shares
    }
    
    return await self._make_request(
      'POST',
      f'/audits/{validated_id}/share',
      data=data
    )
  
  # Site API methods
  @trace_async('search_sites', {'operation': 'search_sites'})
  async def search_sites(
      self,
      name_filter: Optional[str] = None,
      limit: int = DEFAULT_SITE_SEARCH_LIMIT
  ) -> Dict[str, Any]:
    """Search for sites/locations."""
    params: Dict[str, Any] = {
        'limit': limit
    }
    
    if name_filter:
      params['name'] = name_filter
    
    return await self._make_request('GET', '/directories/sites', params=params)
  
  # User API methods
  @trace_async('search_users', {'operation': 'search_users'})
  async def search_users(
      self,
      email: Optional[str] = None
  ) -> Dict[str, Any]:
    """Search for users."""
    data = {}
    if email:
      data['email'] = [email]
    
    return await self._make_request('POST', '/users/search', data=data)
