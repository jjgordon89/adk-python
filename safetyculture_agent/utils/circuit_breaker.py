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

"""Circuit breaker pattern for API failure protection.

This module implements a three-state circuit breaker to protect against
cascading failures when making API calls. The circuit breaker transitions
between CLOSED (normal operation), OPEN (failing fast), and HALF_OPEN
(testing recovery).
"""

from __future__ import annotations

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, TypeVar

logger = logging.getLogger(__name__)

# Circuit breaker exponential backoff constants
EXPONENTIAL_BACKOFF_BASE = 2  # Base for exponential backoff calculation

T = TypeVar('T')


class CircuitState(Enum):
  """Circuit breaker states."""
  CLOSED = "closed"  # Normal operation, requests flow through
  OPEN = "open"  # Failures detected, requests fail immediately
  HALF_OPEN = "half_open"  # Testing if service has recovered


class CircuitBreakerOpenError(Exception):
  """Raised when circuit breaker is open and rejects requests."""
  pass


class CircuitBreaker:
  """Three-state circuit breaker with exponential backoff.
  
  Protects API calls from cascading failures by tracking failures and
  opening the circuit when a threshold is exceeded. Uses exponential
  backoff for recovery attempts.
  
  Attributes:
      failure_threshold: Number of failures before opening circuit
      success_threshold: Number of successes needed to close from half-open
      base_timeout: Initial timeout in seconds when circuit opens
      max_timeout: Maximum timeout in seconds (caps exponential growth)
  """
  
  def __init__(
      self,
      failure_threshold: int = 5,
      success_threshold: int = 2,
      base_timeout: float = 60.0,
      max_timeout: float = 600.0
  ):
    """Initialize circuit breaker with configurable thresholds.
    
    Args:
        failure_threshold: Failures before opening (default: 5)
        success_threshold: Successes to close from half-open (default: 2)
        base_timeout: Initial timeout in seconds (default: 60.0)
        max_timeout: Maximum timeout in seconds (default: 600.0)
    """
    self.failure_threshold = failure_threshold
    self.success_threshold = success_threshold
    self.base_timeout = base_timeout
    self.max_timeout = max_timeout
    
    # State tracking
    self._state = CircuitState.CLOSED
    self._failure_count = 0
    self._success_count = 0
    self._last_failure_time: float = 0.0
    self._open_count = 0  # Track how many times circuit has opened
    
    # Metrics
    self._total_calls = 0
    self._total_failures = 0
    self._total_successes = 0
    
    self._lock = asyncio.Lock()
  
  @property
  def state(self) -> CircuitState:
    """Get current circuit state."""
    return self._state
  
  def _calculate_timeout(self) -> float:
    """Calculate timeout using exponential backoff.
    
    Returns:
        Timeout in seconds, capped at max_timeout
    """
    timeout = self.base_timeout * (EXPONENTIAL_BACKOFF_BASE ** self._open_count)
    return min(timeout, self.max_timeout)
  
  def _should_attempt_reset(self) -> bool:
    """Check if enough time has passed to try recovery.
    
    Returns:
        True if circuit should transition to HALF_OPEN
    """
    if self._state != CircuitState.OPEN:
      return False
    
    timeout = self._calculate_timeout()
    time_since_failure = time.time() - self._last_failure_time
    return time_since_failure >= timeout
  
  def _transition_to_open(self) -> None:
    """Transition circuit to OPEN state."""
    self._state = CircuitState.OPEN
    self._last_failure_time = time.time()
    self._open_count += 1
    self._success_count = 0
    
    timeout = self._calculate_timeout()
    logger.warning(
      f"Circuit breaker OPENED after {self._failure_count} failures. "
      f"Timeout: {timeout}s (attempt #{self._open_count})"
    )
  
  def _transition_to_half_open(self) -> None:
    """Transition circuit to HALF_OPEN state for testing."""
    self._state = CircuitState.HALF_OPEN
    self._success_count = 0
    logger.info("Circuit breaker transitioning to HALF_OPEN for testing")
  
  def _transition_to_closed(self) -> None:
    """Transition circuit to CLOSED state (normal operation)."""
    self._state = CircuitState.CLOSED
    self._failure_count = 0
    self._success_count = 0
    self._open_count = 0  # Reset open count on successful recovery
    logger.info("Circuit breaker CLOSED - service recovered")
  
  def _record_success(self) -> None:
    """Record successful call and update state accordingly."""
    self._total_successes += 1
    
    if self._state == CircuitState.HALF_OPEN:
      self._success_count += 1
      logger.debug(
        f"Circuit breaker success in HALF_OPEN: "
        f"{self._success_count}/{self.success_threshold}"
      )
      
      if self._success_count >= self.success_threshold:
        self._transition_to_closed()
    elif self._state == CircuitState.CLOSED:
      # Reset failure count on success in closed state
      self._failure_count = 0
  
  def _record_failure(self) -> None:
    """Record failed call and update state accordingly."""
    self._total_failures += 1
    
    if self._state == CircuitState.HALF_OPEN:
      # Any failure in half-open immediately reopens circuit
      logger.warning(
        "Circuit breaker failure in HALF_OPEN - reopening circuit"
      )
      self._transition_to_open()
    elif self._state == CircuitState.CLOSED:
      self._failure_count += 1
      logger.debug(
        f"Circuit breaker failure count: "
        f"{self._failure_count}/{self.failure_threshold}"
      )
      
      if self._failure_count >= self.failure_threshold:
        self._transition_to_open()
  
  async def call(
      self,
      func: Callable[..., Any],
      *args: Any,
      **kwargs: Any
  ) -> Any:
    """Execute function call through circuit breaker.
    
    Args:
        func: Async function to execute
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func
    
    Returns:
        Result from func execution
    
    Raises:
        CircuitBreakerOpenError: If circuit is open
        Exception: Any exception raised by func
    """
    async with self._lock:
      self._total_calls += 1
      
      # Check if we should attempt reset from OPEN to HALF_OPEN
      if self._should_attempt_reset():
        self._transition_to_half_open()
      
      # Reject calls if circuit is open
      if self._state == CircuitState.OPEN:
        timeout = self._calculate_timeout()
        time_remaining = (
          timeout - (time.time() - self._last_failure_time)
        )
        raise CircuitBreakerOpenError(
          f"Circuit breaker is OPEN. Retry in {time_remaining:.1f}s "
          f"(attempt #{self._open_count})"
        )
    
    # Execute the function call (outside lock to allow concurrency)
    try:
      result = await func(*args, **kwargs)
      
      # Record success
      async with self._lock:
        self._record_success()
      
      return result
    
    except Exception as e:
      # Record failure
      async with self._lock:
        self._record_failure()
      
      # Re-raise the original exception
      raise
  
  def get_metrics(self) -> Dict[str, Any]:
    """Get circuit breaker metrics.
    
    Returns:
        Dictionary containing current metrics:
        - state: Current circuit state
        - total_calls: Total number of calls attempted
        - total_failures: Total number of failures
        - total_successes: Total number of successes
        - failure_rate: Current failure rate (0.0-1.0)
        - open_count: Number of times circuit has opened
        - current_timeout: Current timeout value in seconds
    """
    failure_rate = (
      self._total_failures / self._total_calls
      if self._total_calls > 0
      else 0.0
    )
    
    return {
      'state': self._state.value,
      'total_calls': self._total_calls,
      'total_failures': self._total_failures,
      'total_successes': self._total_successes,
      'failure_rate': failure_rate,
      'open_count': self._open_count,
      'current_timeout': self._calculate_timeout()
    }
  
  def reset(self) -> None:
    """Manually reset circuit breaker to CLOSED state.
    
    This should be used with caution, typically only for testing or
    administrative intervention.
    """
    self._state = CircuitState.CLOSED
    self._failure_count = 0
    self._success_count = 0
    self._open_count = 0
    self._last_failure_time = 0.0
    logger.info("Circuit breaker manually reset to CLOSED")