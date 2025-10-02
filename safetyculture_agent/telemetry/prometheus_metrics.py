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

"""Prometheus metrics collection for SafetyCulture agent.

This module provides helper functions to record various metrics including
API requests, database queries, circuit breaker states, and rate limiting.
"""

from __future__ import annotations

import logging
from typing import Any

from .telemetry_config import (
  METRIC_API_LATENCY,
  METRIC_API_REQUESTS,
  METRIC_CIRCUIT_BREAKER_STATE,
  METRIC_DB_QUERIES,
  METRIC_DB_QUERY_DURATION,
  METRIC_RATE_LIMIT_HITS,
)
from .telemetry_manager import get_telemetry_manager

logger = logging.getLogger(__name__)

# Module-level metric instruments (lazily initialized)
_api_request_counter: Any = None
_api_latency_histogram: Any = None
_db_query_counter: Any = None
_db_query_duration_histogram: Any = None
_circuit_breaker_gauge: Any = None
_rate_limit_counter: Any = None


def _get_api_request_counter() -> Any:
  """Get or create the API request counter."""
  global _api_request_counter
  if _api_request_counter is None:
    try:
      manager = get_telemetry_manager()
      if manager.is_enabled:
        meter = manager.get_meter(__name__)
        _api_request_counter = meter.create_counter(
          name=METRIC_API_REQUESTS,
          unit='1',
          description='Count of API requests by endpoint and status',
        )
    except Exception as e:  # pylint: disable=broad-except
      logger.error('Failed to create API request counter: %s', e)
  return _api_request_counter


def _get_api_latency_histogram() -> Any:
  """Get or create the API latency histogram."""
  global _api_latency_histogram
  if _api_latency_histogram is None:
    try:
      manager = get_telemetry_manager()
      if manager.is_enabled:
        meter = manager.get_meter(__name__)
        _api_latency_histogram = meter.create_histogram(
          name=METRIC_API_LATENCY,
          unit='s',
          description='API request latency in seconds',
        )
    except Exception as e:  # pylint: disable=broad-except
      logger.error('Failed to create API latency histogram: %s', e)
  return _api_latency_histogram


def _get_db_query_counter() -> Any:
  """Get or create the database query counter."""
  global _db_query_counter
  if _db_query_counter is None:
    try:
      manager = get_telemetry_manager()
      if manager.is_enabled:
        meter = manager.get_meter(__name__)
        _db_query_counter = meter.create_counter(
          name=METRIC_DB_QUERIES,
          unit='1',
          description='Count of database queries by operation type',
        )
    except Exception as e:  # pylint: disable=broad-except
      logger.error('Failed to create DB query counter: %s', e)
  return _db_query_counter


def _get_db_query_duration_histogram() -> Any:
  """Get or create the database query duration histogram."""
  global _db_query_duration_histogram
  if _db_query_duration_histogram is None:
    try:
      manager = get_telemetry_manager()
      if manager.is_enabled:
        meter = manager.get_meter(__name__)
        _db_query_duration_histogram = meter.create_histogram(
          name=METRIC_DB_QUERY_DURATION,
          unit='s',
          description='Database query duration in seconds',
        )
    except Exception as e:  # pylint: disable=broad-except
      logger.error('Failed to create DB query duration histogram: %s', e)
  return _db_query_duration_histogram


def _get_circuit_breaker_gauge() -> Any:
  """Get or create the circuit breaker state gauge."""
  global _circuit_breaker_gauge
  if _circuit_breaker_gauge is None:
    try:
      manager = get_telemetry_manager()
      if manager.is_enabled:
        meter = manager.get_meter(__name__)
        _circuit_breaker_gauge = meter.create_up_down_counter(
          name=METRIC_CIRCUIT_BREAKER_STATE,
          unit='1',
          description='Circuit breaker state (0=closed, 1=open, 2=half_open)',
        )
    except Exception as e:  # pylint: disable=broad-except
      logger.error('Failed to create circuit breaker gauge: %s', e)
  return _circuit_breaker_gauge


def _get_rate_limit_counter() -> Any:
  """Get or create the rate limit hits counter."""
  global _rate_limit_counter
  if _rate_limit_counter is None:
    try:
      manager = get_telemetry_manager()
      if manager.is_enabled:
        meter = manager.get_meter(__name__)
        _rate_limit_counter = meter.create_counter(
          name=METRIC_RATE_LIMIT_HITS,
          unit='1',
          description='Count of rate limit hits',
        )
    except Exception as e:  # pylint: disable=broad-except
      logger.error('Failed to create rate limit counter: %s', e)
  return _rate_limit_counter


def record_api_request(
  endpoint: str,
  method: str,
  status_code: int,
  additional_attrs: dict[str, Any] | None = None
) -> None:
  """Record an API request metric.

  Args:
    endpoint: The API endpoint (e.g., '/assets', '/inspections').
    method: HTTP method (e.g., 'GET', 'POST').
    status_code: HTTP status code (e.g., 200, 404, 500).
    additional_attrs: Additional attributes to include.
  """
  counter = _get_api_request_counter()
  if counter is None:
    return

  try:
    attrs = {
      'endpoint': endpoint,
      'method': method,
      'status_code': str(status_code),
    }
    if additional_attrs:
      attrs.update(additional_attrs)

    counter.add(1, attrs)
  except Exception as e:  # pylint: disable=broad-except
    logger.error('Failed to record API request metric: %s', e)


def record_api_latency(
  endpoint: str,
  method: str,
  duration_seconds: float,
  additional_attrs: dict[str, Any] | None = None
) -> None:
  """Record API request latency metric.

  Args:
    endpoint: The API endpoint (e.g., '/assets', '/inspections').
    method: HTTP method (e.g., 'GET', 'POST').
    duration_seconds: Request duration in seconds.
    additional_attrs: Additional attributes to include.
  """
  histogram = _get_api_latency_histogram()
  if histogram is None:
    return

  try:
    attrs = {
      'endpoint': endpoint,
      'method': method,
    }
    if additional_attrs:
      attrs.update(additional_attrs)

    histogram.record(duration_seconds, attrs)
  except Exception as e:  # pylint: disable=broad-except
    logger.error('Failed to record API latency metric: %s', e)


def record_database_query(
  operation: str,
  table: str | None = None,
  additional_attrs: dict[str, Any] | None = None
) -> None:
  """Record a database query metric.

  Args:
    operation: Type of operation (e.g., 'SELECT', 'INSERT', 'UPDATE').
    table: Database table name.
    additional_attrs: Additional attributes to include.
  """
  counter = _get_db_query_counter()
  if counter is None:
    return

  try:
    attrs = {'operation': operation}
    if table:
      attrs['table'] = table
    if additional_attrs:
      attrs.update(additional_attrs)

    counter.add(1, attrs)
  except Exception as e:  # pylint: disable=broad-except
    logger.error('Failed to record database query metric: %s', e)


def record_query_duration(
  operation: str,
  duration_seconds: float,
  table: str | None = None,
  additional_attrs: dict[str, Any] | None = None
) -> None:
  """Record database query duration metric.

  Args:
    operation: Type of operation (e.g., 'SELECT', 'INSERT', 'UPDATE').
    duration_seconds: Query duration in seconds.
    table: Database table name.
    additional_attrs: Additional attributes to include.
  """
  histogram = _get_db_query_duration_histogram()
  if histogram is None:
    return

  try:
    attrs = {'operation': operation}
    if table:
      attrs['table'] = table
    if additional_attrs:
      attrs.update(additional_attrs)

    histogram.record(duration_seconds, attrs)
  except Exception as e:  # pylint: disable=broad-except
    logger.error('Failed to record query duration metric: %s', e)


def record_circuit_breaker_state(
  name: str,
  state: str,
  additional_attrs: dict[str, Any] | None = None
) -> None:
  """Record circuit breaker state change.

  Args:
    name: Name/identifier of the circuit breaker.
    state: State of the circuit breaker ('closed', 'open', 'half_open').
    additional_attrs: Additional attributes to include.
  """
  gauge = _get_circuit_breaker_gauge()
  if gauge is None:
    return

  try:
    # Map state to numeric value
    state_value = {'closed': 0, 'open': 1, 'half_open': 2}.get(
      state.lower(), -1
    )

    attrs = {'name': name, 'state': state}
    if additional_attrs:
      attrs.update(additional_attrs)

    gauge.add(state_value, attrs)
  except Exception as e:  # pylint: disable=broad-except
    logger.error('Failed to record circuit breaker state: %s', e)


def record_rate_limit_hit(
  endpoint: str | None = None,
  additional_attrs: dict[str, Any] | None = None
) -> None:
  """Record a rate limit hit metric.

  Args:
    endpoint: The API endpoint that hit the rate limit.
    additional_attrs: Additional attributes to include.
  """
  counter = _get_rate_limit_counter()
  if counter is None:
    return

  try:
    attrs = {}
    if endpoint:
      attrs['endpoint'] = endpoint
    if additional_attrs:
      attrs.update(additional_attrs)

    counter.add(1, attrs)
  except Exception as e:  # pylint: disable=broad-except
    logger.error('Failed to record rate limit hit: %s', e)