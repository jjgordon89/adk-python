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

"""Secure header management with automatic token redaction."""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Secure header constants
MIN_TOKEN_LENGTH_FOR_REDACTION = 8  # Minimum token length to trigger redaction


class SecureHeaderManager:
  """Manages secure header injection with automatic token redaction."""

  SENSITIVE_HEADERS = {'authorization', 'x-api-key', 'api-token'}
  SENSITIVE_PATTERNS = [
    r'(authorization["\']?\s*[:=]\s*["\']?)bearer\s+\S+',
    r'(api[_-]?key["\']?\s*[:=]\s*["\']?)\S+',
    r'(token["\']?\s*[:=]\s*["\']?)\S+',
  ]

  def __init__(self):
    """Initialize secure header manager."""
    self._setup_redacting_logger()

  def _setup_redacting_logger(self) -> None:
    """Configure logger to redact sensitive information."""

    class RedactingFilter(logging.Filter):
      """Filter that redacts sensitive information from logs."""

      def filter(self, record):
        """Redact sensitive data from log records."""
        if hasattr(record, 'msg') and record.msg:
          message = str(record.msg)

          # Redact authorization headers
          message = re.sub(
            r'(authorization["\']?\s*[:=]\s*["\']?)bearer\s+\S+',
            r'\1Bearer [REDACTED]',
            message,
            flags=re.IGNORECASE
          )

          # Redact API keys
          message = re.sub(
            r'(api[_-]?key["\']?\s*[:=]\s*["\']?)\S+',
            r'\1[REDACTED]',
            message,
            flags=re.IGNORECASE
          )

          # Redact tokens
          message = re.sub(
            rf'(token["\']?\s*[:=]\s*["\']?)\S{{{MIN_TOKEN_LENGTH_FOR_REDACTION},}}',
            r'\1[REDACTED]',
            message,
            flags=re.IGNORECASE
          )

          record.msg = message

        return True

    logger = logging.getLogger('safetyculture_agent')
    logger.addFilter(RedactingFilter())

  async def get_secure_headers(
      self,
      api_token: str,
      extra_headers: Optional[Dict[str, str]] = None
  ) -> Dict[str, str]:
    """Generate headers with secure token injection.

    Args:
        api_token: API authentication token
        extra_headers: Additional headers to include

    Returns:
        Dictionary of HTTP headers with token securely injected
    """
    headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'ADK-SafetyCulture/1.0',
      'X-Request-ID': str(uuid.uuid4()),
      'X-Request-Time': datetime.now(timezone.utc).isoformat(),
    }

    # Add extra headers if provided
    if extra_headers:
      headers.update(extra_headers)

    # Inject token securely (not logged)
    headers['Authorization'] = f'Bearer {api_token}'

    return headers

  def sanitize_for_logging(self, data: Any) -> Any:
    """Recursively sanitize data structure for safe logging.

    Args:
        data: Data structure to sanitize

    Returns:
        Sanitized copy safe for logging
    """
    if isinstance(data, dict):
      return {
        k: '[REDACTED]' if k.lower() in self.SENSITIVE_HEADERS
        else self.sanitize_for_logging(v)
        for k, v in data.items()
      }
    elif isinstance(data, (list, tuple)):
      return [self.sanitize_for_logging(item) for item in data]
    elif isinstance(data, str):
      # Check if string contains sensitive patterns
      sanitized = data
      for pattern in self.SENSITIVE_PATTERNS:
        sanitized = re.sub(
          pattern,
          r'\1[REDACTED]',
          sanitized,
          flags=re.IGNORECASE
        )
      return sanitized
    return data

  def sanitize_error(self, error: Exception) -> str:
    """Remove sensitive data from error messages.

    Args:
        error: Exception to sanitize

    Returns:
        Sanitized error message
    """
    message = str(error)
    for pattern in self.SENSITIVE_PATTERNS:
      message = re.sub(
        pattern,
        r'\1[REDACTED]',
        message,
        flags=re.IGNORECASE
      )
    return message