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

"""Exception hierarchy for SafetyCulture agent operations."""

from __future__ import annotations

from typing import Optional


class SafetyCultureAgentError(Exception):
  """Base exception for all SafetyCulture agent operations."""
  pass


class SafetyCultureAPIError(SafetyCultureAgentError):
  """Raised when API communication fails."""

  def __init__(self, message: str, status_code: Optional[int] = None):
    """Initialize API error with optional status code.

    Args:
        message: Error description
        status_code: HTTP status code if applicable
    """
    super().__init__(message)
    self.status_code = status_code


class SafetyCultureAuthError(SafetyCultureAPIError):
  """Raised when authentication or authorization fails."""
  pass


class SafetyCultureValidationError(SafetyCultureAgentError):
  """Raised when input validation fails."""
  pass


class SafetyCultureDatabaseError(SafetyCultureAgentError):
  """Raised when database operations fail."""
  pass


class SafetyCultureRateLimitError(SafetyCultureAPIError):
  """Raised when API rate limit is exceeded."""
  pass


class SafetyCultureCredentialError(SafetyCultureAgentError):
  """Raised when credential management operations fail."""
  pass


class RequestSigningError(SafetyCultureAgentError):
  """Raised when request signing fails."""
  pass


class SignatureVerificationError(SafetyCultureAgentError):
  """Raised when signature verification fails."""

class CircuitBreakerOpenError(SafetyCultureAgentError):
  """Raised when circuit breaker is open and rejects requests."""
  pass
  pass