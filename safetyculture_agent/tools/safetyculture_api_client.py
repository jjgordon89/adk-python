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
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlencode

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from ..config.api_config import SafetyCultureConfig, DEFAULT_CONFIG


class SafetyCultureAPIClient:
  """Async client for SafetyCulture API interactions."""
  
  def __init__(self, config: SafetyCultureConfig = DEFAULT_CONFIG):
    self.config = config
    self._session: Optional[ClientSession] = None
    self._rate_limiter = asyncio.Semaphore(config.requests_per_second)
    self._last_request_time = 0.0
  
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
    """Ensure HTTP session is created."""
    if not self._session:
      timeout = ClientTimeout(total=self.config.request_timeout)
      self._session = ClientSession(
          headers=self.config.headers,
          timeout=timeout
      )
  
  async def _rate_limit(self):
    """Apply rate limiting."""
    async with self._rate_limiter:
      current_time = time.time()
      time_since_last = current_time - self._last_request_time
      min_interval = 1.0 / self.config.requests_per_second
      
      if time_since_last < min_interval:
        await asyncio.sleep(min_interval - time_since_last)
      
      self._last_request_time = time.time()
  
  async def _make_request(
      self,
      method: str,
      endpoint: str,
      params: Optional[Dict[str, Any]] = None,
      data: Optional[Dict[str, Any]] = None,
      retry_count: int = 0
  ) -> Dict[str, Any]:
    """Make HTTP request with retry logic."""
    await self._ensure_session()
    await self._rate_limit()
    
    url = urljoin(self.config.base_url, endpoint)
    if params:
      # Handle multiple values for same parameter (like multiple 'field' params)
      url_params = []
      for key, value in params.items():
        if isinstance(value, list):
          for item in value:
            url_params.append(f"{key}={item}")
        else:
          url_params.append(f"{key}={value}")
      if url_params:
        url += '?' + '&'.join(url_params)
    
    try:
      if self._session is None:
        raise Exception("Session not initialized")
      
      async with self._session.request(
          method,
          url,
          json=data if data else None
      ) as response:
        if response.status == 429:  # Rate limited
          if retry_count < self.config.max_retries:
            await asyncio.sleep(self.config.retry_delay * (2 ** retry_count))
            return await self._make_request(
                method, endpoint, params, data, retry_count + 1
            )
          else:
            raise Exception(f"Rate limit exceeded after {self.config.max_retries} retries")
        
        response.raise_for_status()
        return await response.json()
    
    except aiohttp.ClientError as e:
      if retry_count < self.config.max_retries:
        await asyncio.sleep(self.config.retry_delay * (2 ** retry_count))
        return await self._make_request(
            method, endpoint, params, data, retry_count + 1
        )
      else:
        raise Exception(f"API request failed after {self.config.max_retries} retries: {e}")
  
  # Asset API methods
  async def search_assets(
      self,
      asset_types: Optional[List[str]] = None,
      site_ids: Optional[List[str]] = None,
      limit: int = 100,
      offset: int = 0
  ) -> Dict[str, Any]:
    """Search for assets with filters."""
    params: Dict[str, Any] = {
        'limit': limit,
        'offset': offset
    }
    
    if asset_types:
      params['asset_type'] = asset_types
    if site_ids:
      params['site_id'] = site_ids
    
    return await self._make_request('GET', '/assets/search', params=params)
  
  async def get_asset(self, asset_id: str) -> Dict[str, Any]:
    """Get a specific asset by ID."""
    return await self._make_request('GET', f'/assets/{asset_id}')
  
  # Template API methods
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
  
  async def get_template(self, template_id: str) -> Dict[str, Any]:
    """Get a specific template by ID."""
    return await self._make_request('GET', f'/templates/{template_id}')
  
  # Inspection API methods
  async def search_inspections(
      self,
      fields: Optional[List[str]] = None,
      template_id: Optional[str] = None,
      modified_after: Optional[str] = None,
      limit: int = 1000
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
  
  async def create_inspection(
      self,
      template_id: str,
      header_items: Optional[List[Dict[str, Any]]] = None
  ) -> Dict[str, Any]:
    """Create a new inspection from template."""
    data: Dict[str, Any] = {
        'template_id': template_id
    }
    
    if header_items:
      data['header_items'] = header_items
    
    return await self._make_request('POST', '/audits', data=data)
  
  async def update_inspection(
      self,
      audit_id: str,
      items: List[Dict[str, Any]]
  ) -> Dict[str, Any]:
    """Update inspection responses."""
    data = {
        'items': items
    }
    
    return await self._make_request('PUT', f'/audits/{audit_id}', data=data)
  
  async def get_inspection(self, audit_id: str) -> Dict[str, Any]:
    """Get a specific inspection by ID."""
    return await self._make_request('GET', f'/audits/{audit_id}')
  
  async def share_inspection(
      self,
      audit_id: str,
      shares: List[Dict[str, str]]
  ) -> Dict[str, Any]:
    """Share inspection with users or groups."""
    data = {
        'shares': shares
    }
    
    return await self._make_request('POST', f'/audits/{audit_id}/share', data=data)
  
  # Site API methods
  async def search_sites(
      self,
      name_filter: Optional[str] = None,
      limit: int = 100
  ) -> Dict[str, Any]:
    """Search for sites/locations."""
    params: Dict[str, Any] = {
        'limit': limit
    }
    
    if name_filter:
      params['name'] = name_filter
    
    return await self._make_request('GET', '/directories/sites', params=params)
  
  # User API methods
  async def search_users(
      self,
      email: Optional[str] = None
  ) -> Dict[str, Any]:
    """Search for users."""
    data = {}
    if email:
      data['email'] = [email]
    
    return await self._make_request('POST', '/users/search', data=data)
