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

"""HMAC-based request signing for API integrity verification."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Request signing constants
CLOCK_SKEW_TOLERANCE_SECONDS = 60  # Allow 60s clock skew for future timestamps


class RequestSigner:
  """Signs API requests using HMAC-SHA256 for integrity verification.
  
  This class implements request signing to prevent tampering and replay
  attacks. Each request is signed with a secret key and includes a
  timestamp to prevent replay attacks.
  
  Attributes:
      signing_key: Secret key used for HMAC signing
      timestamp_window: Maximum age of request in seconds (default: 300)
  """
  
  def __init__(
      self,
      signing_key: str,
      timestamp_window: int = 300
  ):
    """Initialize request signer.
    
    Args:
        signing_key: Secret key for HMAC signing
        timestamp_window: Maximum request age in seconds (default: 5 minutes)
    """
    self.signing_key = signing_key.encode('utf-8')
    self.timestamp_window = timestamp_window
  
  def sign_request(
      self,
      method: str,
      url: str,
      body: Optional[Dict[str, Any]] = None,
      timestamp: Optional[int] = None
  ) -> Dict[str, str]:
    """Sign an API request using HMAC-SHA256.
    
    Creates a signature for the request that includes method, URL, body,
    and timestamp. This signature can be verified by the server to ensure
    request integrity and prevent tampering.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: Full request URL
        body: Request body as dictionary (optional)
        timestamp: Unix timestamp (optional, defaults to current time)
        
    Returns:
        Dictionary with signature headers:
            - X-Signature: HMAC signature
            - X-Timestamp: Request timestamp
            - X-Signature-Algorithm: Algorithm used (HMAC-SHA256)
    """
    if timestamp is None:
      timestamp = int(time.time())
    
    # Serialize body to JSON string for signing
    body_str = json.dumps(body, sort_keys=True) if body else ''
    
    # Create message to sign: METHOD|URL|BODY|TIMESTAMP
    message = f"{method.upper()}|{url}|{body_str}|{timestamp}"
    
    # Generate HMAC signature
    signature = hmac.new(
      self.signing_key,
      message.encode('utf-8'),
      hashlib.sha256
    ).hexdigest()
    
    logger.debug(
      f"Signed {method} request to {url} with timestamp {timestamp}"
    )
    
    return {
      'X-Signature': signature,
      'X-Timestamp': str(timestamp),
      'X-Signature-Algorithm': 'HMAC-SHA256'
    }
  
  def verify_signature(
      self,
      method: str,
      url: str,
      signature: str,
      timestamp: int,
      body: Optional[Dict[str, Any]] = None
  ) -> bool:
    """Verify an API request signature.
    
    Verifies that the signature matches the request and that the
    timestamp is within the allowed window.
    
    Args:
        method: HTTP method
        url: Full request URL
        signature: Signature to verify
        timestamp: Request timestamp
        body: Request body (optional)
        
    Returns:
        True if signature is valid, False otherwise
    """
    # Check timestamp is within window
    current_time = int(time.time())
    age = current_time - timestamp
    
    if age > self.timestamp_window:
      logger.warning(
        f"Request timestamp too old: {age}s > {self.timestamp_window}s"
      )
      return False
    
    if age < -CLOCK_SKEW_TOLERANCE_SECONDS:
      logger.warning(f"Request timestamp in future: {age}s")
      return False
    
    # Regenerate signature
    expected_headers = self.sign_request(method, url, body, timestamp)
    expected_signature = expected_headers['X-Signature']
    
    # Compare signatures using constant-time comparison
    return hmac.compare_digest(signature, expected_signature)
  
  def get_max_request_age(self) -> int:
    """Get maximum allowed request age in seconds.
    
    Returns:
        Maximum request age in seconds
    """
    return self.timestamp_window


class RequestSigningError(Exception):
  """Raised when request signing fails."""
  pass


class SignatureVerificationError(Exception):
  """Raised when signature verification fails."""
  pass