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

"""Rate limiting implementation using token bucket algorithm."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional

from ..exceptions import SafetyCultureRateLimitError

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
  """Rate limiter using token bucket algorithm with burst support.
  
  The token bucket algorithm allows for burst traffic while maintaining
  an average rate limit. Tokens are added to the bucket at a fixed rate,
  and each request consumes one token.
  
  Attributes:
      rate: Maximum requests per second
      burst: Maximum burst size (tokens in bucket)
      tokens: Current available tokens
      last_update: Last time tokens were added
  """
  
  def __init__(
      self,
      rate: float,
      burst: Optional[int] = None,
      max_wait: float = 30.0
  ):
    """Initialize rate limiter.
    
    Args:
        rate: Maximum requests per second (e.g., 10.0)
        burst: Maximum burst size. Defaults to rate if not specified.
        max_wait: Maximum time to wait for a token (seconds)
    """
    self.rate = rate
    self.burst = burst or int(rate)
    self.max_wait = max_wait
    
    # Current available tokens (starts at burst capacity)
    self.tokens = float(self.burst)
    self.last_update = time.monotonic()
    
    # Lock for thread safety
    self._lock = asyncio.Lock()
    
    logger.info(
      f"Initialized rate limiter: {rate} req/s, burst={self.burst}"
    )
  
  def _refill_tokens(self) -> None:
    """Refill tokens based on elapsed time since last update."""
    now = time.monotonic()
    elapsed = now - self.last_update
    
    # Add tokens based on elapsed time and rate
    tokens_to_add = elapsed * self.rate
    self.tokens = min(self.burst, self.tokens + tokens_to_add)
    self.last_update = now
  
  async def acquire(self, tokens: int = 1) -> None:
    """Acquire tokens for making requests.
    
    This method will block until enough tokens are available or max_wait
    is exceeded. Tokens are refilled at the configured rate.
    
    Args:
        tokens: Number of tokens to acquire (default: 1)
        
    Raises:
        SafetyCultureRateLimitError: If max_wait exceeded
        ValueError: If requesting more tokens than burst capacity
    """
    if tokens > self.burst:
      raise ValueError(
        f"Cannot request {tokens} tokens (burst capacity: {self.burst})"
      )
    
    async with self._lock:
      wait_start = time.monotonic()
      
      while True:
        # Refill tokens based on elapsed time
        self._refill_tokens()
        
        # Check if we have enough tokens
        if self.tokens >= tokens:
          self.tokens -= tokens
          logger.debug(
            f"Acquired {tokens} token(s), "
            f"{self.tokens:.2f} remaining"
          )
          return
        
        # Check if we've been waiting too long
        wait_time = time.monotonic() - wait_start
        if wait_time >= self.max_wait:
          raise SafetyCultureRateLimitError(
            f"Rate limit exceeded. Waited {wait_time:.1f}s for tokens. "
            f"Current rate: {self.rate} req/s"
          )
        
        # Calculate how long to wait for next token
        tokens_needed = tokens - self.tokens
        wait_seconds = tokens_needed / self.rate
        
        # Wait a bit and try again
        await asyncio.sleep(min(wait_seconds, 0.1))
  
  async def try_acquire(self, tokens: int = 1) -> bool:
    """Try to acquire tokens without blocking.
    
    Args:
        tokens: Number of tokens to acquire (default: 1)
        
    Returns:
        True if tokens were acquired, False otherwise
    """
    async with self._lock:
      self._refill_tokens()
      
      if self.tokens >= tokens:
        self.tokens -= tokens
        logger.debug(
          f"Acquired {tokens} token(s), "
          f"{self.tokens:.2f} remaining"
        )
        return True
      
      logger.debug(
        f"Insufficient tokens: need {tokens}, have {self.tokens:.2f}"
      )
      return False
  
  def get_wait_time(self, tokens: int = 1) -> float:
    """Calculate estimated wait time for tokens.
    
    Args:
        tokens: Number of tokens needed
        
    Returns:
        Estimated wait time in seconds
    """
    tokens_needed = max(0, tokens - self.tokens)
    return tokens_needed / self.rate
  
  async def reset(self) -> None:
    """Reset the rate limiter to full capacity."""
    async with self._lock:
      self.tokens = float(self.burst)
      self.last_update = time.monotonic()
      logger.info("Rate limiter reset to full capacity")


class ExponentialBackoffRateLimiter:
  """Rate limiter with exponential backoff for failed requests.
  
  This rate limiter wraps a TokenBucketRateLimiter and adds exponential
  backoff when rate limit errors are encountered.
  """
  
  def __init__(
      self,
      rate: float,
      burst: Optional[int] = None,
      initial_backoff: float = 1.0,
      max_backoff: float = 60.0,
      backoff_multiplier: float = 2.0
  ):
    """Initialize exponential backoff rate limiter.
    
    Args:
        rate: Maximum requests per second
        burst: Maximum burst size
        initial_backoff: Initial backoff delay (seconds)
        max_backoff: Maximum backoff delay (seconds)
        backoff_multiplier: Backoff multiplier on each failure
    """
    self.bucket = TokenBucketRateLimiter(rate, burst)
    self.initial_backoff = initial_backoff
    self.max_backoff = max_backoff
    self.backoff_multiplier = backoff_multiplier
    
    # Current backoff state
    self.current_backoff = initial_backoff
    self.consecutive_failures = 0
  
  async def acquire(self, tokens: int = 1) -> None:
    """Acquire tokens with exponential backoff on rate limit errors.
    
    Args:
        tokens: Number of tokens to acquire
        
    Raises:
        SafetyCultureRateLimitError: If rate limit cannot be satisfied
    """
    try:
      await self.bucket.acquire(tokens)
      # Success - reset backoff
      self.current_backoff = self.initial_backoff
      self.consecutive_failures = 0
      
    except SafetyCultureRateLimitError:
      # Rate limit hit - apply exponential backoff
      self.consecutive_failures += 1
      
      logger.warning(
        f"Rate limit exceeded (failure #{self.consecutive_failures}). "
        f"Backing off for {self.current_backoff:.1f}s"
      )
      
      await asyncio.sleep(self.current_backoff)
      
      # Increase backoff for next failure
      self.current_backoff = min(
        self.max_backoff,
        self.current_backoff * self.backoff_multiplier
      )
      
      # Retry after backoff
      await self.bucket.acquire(tokens)
  
  async def reset(self) -> None:
    """Reset both bucket and backoff state."""
    await self.bucket.reset()
    self.current_backoff = self.initial_backoff
    self.consecutive_failures = 0