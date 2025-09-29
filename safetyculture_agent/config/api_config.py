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

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SafetyCultureConfig:
  """Configuration for SafetyCulture API integration."""
  
  # API Configuration
  base_url: str = "https://api.safetyculture.io"
  api_token: Optional[str] = None
  
  # Rate limiting
  requests_per_second: int = 10
  max_retries: int = 3
  retry_delay: float = 1.0
  
  # Batch processing
  batch_size: int = 50
  max_concurrent_requests: int = 5
  
  # Timeouts
  request_timeout: int = 30
  
  def __post_init__(self):
    """Load API token from environment if not provided."""
    if not self.api_token:
      self.api_token = os.getenv('SAFETYCULTURE_API_TOKEN')
      if not self.api_token:
        raise ValueError(
            "SafetyCulture API token must be provided either directly or "
            "via SAFETYCULTURE_API_TOKEN environment variable"
        )
  
  @property
  def headers(self) -> dict[str, str]:
    """Get HTTP headers for API requests."""
    return {
        'Authorization': f'Bearer {self.api_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


# Default configuration instance
DEFAULT_CONFIG = SafetyCultureConfig()
