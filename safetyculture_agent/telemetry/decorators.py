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

"""Decorators for instrumenting functions with OpenTelemetry tracing.

This module provides convenient decorators for adding distributed tracing
to both synchronous and asynchronous functions with minimal code changes.
"""

from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable, TypeVar

from .telemetry_manager import get_telemetry_manager

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def trace_async(
  span_name: str | None = None,
  attributes: dict[str, Any] | None = None
) -> Callable[[F], F]:
  """Decorator to add OpenTelemetry tracing to async functions.

  This decorator wraps an async function with a span, recording the function
  execution and any errors that occur. The span will automatically capture
  the function duration and set the status based on success/failure.

  Args:
    span_name: Name for the span. If None, uses the function name.
    attributes: Additional attributes to add to the span.

  Returns:
    Decorated function with tracing instrumentation.

  Example:
    @trace_async('fetch_asset', {'asset_type': 'inspection'})
    async def fetch_asset(asset_id: str) -> dict:
      # Function implementation
      pass
  """
  def decorator(func: F) -> F:
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
      manager = get_telemetry_manager()
      if not manager.is_enabled:
        return await func(*args, **kwargs)

      try:
        from opentelemetry import trace
        from opentelemetry.trace import Status, StatusCode

        tracer = manager.get_tracer(__name__)
        name = span_name or func.__name__

        with tracer.start_as_current_span(name) as span:
          # Add custom attributes
          if attributes:
            for key, value in attributes.items():
              span.set_attribute(key, value)

          # Add function metadata
          span.set_attribute('function.name', func.__name__)
          span.set_attribute('function.module', func.__module__)

          try:
            result = await func(*args, **kwargs)
            span.set_status(Status(StatusCode.OK))
            return result
          except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.set_attribute('exception.type', type(e).__name__)
            span.set_attribute('exception.message', str(e))
            span.record_exception(e)
            raise

      except ImportError:
        # OpenTelemetry not installed, run function without tracing
        return await func(*args, **kwargs)
      except Exception as e:  # pylint: disable=broad-except
        # Telemetry failures should not prevent function execution or mask
        # errors. Log the telemetry error but let the original exception
        # propagate.
        logger.error('Error in tracing decorator: %s', e)
        raise

    return wrapper  # type: ignore

  return decorator


def trace_sync(
  span_name: str | None = None,
  attributes: dict[str, Any] | None = None
) -> Callable[[F], F]:
  """Decorator to add OpenTelemetry tracing to synchronous functions.

  This decorator wraps a synchronous function with a span, recording the
  function execution and any errors that occur. The span will automatically
  capture the function duration and set the status based on success/failure.

  Args:
    span_name: Name for the span. If None, uses the function name.
    attributes: Additional attributes to add to the span.

  Returns:
    Decorated function with tracing instrumentation.

  Example:
    @trace_sync('validate_data', {'validator': 'schema'})
    def validate_data(data: dict) -> bool:
      # Function implementation
      pass
  """
  def decorator(func: F) -> F:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      manager = get_telemetry_manager()
      if not manager.is_enabled:
        return func(*args, **kwargs)

      try:
        from opentelemetry import trace
        from opentelemetry.trace import Status, StatusCode

        tracer = manager.get_tracer(__name__)
        name = span_name or func.__name__

        with tracer.start_as_current_span(name) as span:
          # Add custom attributes
          if attributes:
            for key, value in attributes.items():
              span.set_attribute(key, value)

          # Add function metadata
          span.set_attribute('function.name', func.__name__)
          span.set_attribute('function.module', func.__module__)

          try:
            result = func(*args, **kwargs)
            span.set_status(Status(StatusCode.OK))
            return result
          except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.set_attribute('exception.type', type(e).__name__)
            span.set_attribute('exception.message', str(e))
            span.record_exception(e)
            raise

      except ImportError:
        # OpenTelemetry not installed, run function without tracing
        return func(*args, **kwargs)
      except Exception as e:  # pylint: disable=broad-except
        # Telemetry failures should not prevent function execution or mask
        # errors. Log the telemetry error but let the original exception
        # propagate.
        logger.error('Error in tracing decorator: %s', e)
        raise

    return wrapper  # type: ignore

  return decorator


def measure_duration(
  metric_name: str,
  attributes: dict[str, Any] | None = None
) -> Callable[[F], F]:
  """Decorator to measure and record function execution duration.

  This decorator measures the time taken to execute a function and records
  it as a histogram metric. It works with both sync and async functions.

  Args:
    metric_name: Name of the metric to record.
    attributes: Additional attributes to add to the metric.

  Returns:
    Decorated function with duration measurement.

  Example:
    @measure_duration('api.request.duration', {'endpoint': '/assets'})
    async def fetch_assets() -> list:
      # Function implementation
      pass
  """
  def decorator(func: F) -> F:
    if functools.iscoroutinefunction(func):
      @functools.wraps(func)
      async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        manager = get_telemetry_manager()
        if not manager.is_enabled:
          return await func(*args, **kwargs)

        start_time = time.perf_counter()
        try:
          result = await func(*args, **kwargs)
          return result
        finally:
          duration = time.perf_counter() - start_time
          try:
            meter = manager.get_meter(__name__)
            histogram = meter.create_histogram(
              name=metric_name,
              unit='s',
              description=f'Duration of {func.__name__}',
            )
            attrs = attributes or {}
            attrs['function.name'] = func.__name__
            histogram.record(duration, attrs)
          except Exception as e:  # pylint: disable=broad-except
            logger.error('Error recording metric: %s', e)

      return async_wrapper  # type: ignore
    else:
      @functools.wraps(func)
      def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        manager = get_telemetry_manager()
        if not manager.is_enabled:
          return func(*args, **kwargs)

        start_time = time.perf_counter()
        try:
          result = func(*args, **kwargs)
          return result
        finally:
          duration = time.perf_counter() - start_time
          try:
            meter = manager.get_meter(__name__)
            histogram = meter.create_histogram(
              name=metric_name,
              unit='s',
              description=f'Duration of {func.__name__}',
            )
            attrs = attributes or {}
            attrs['function.name'] = func.__name__
            histogram.record(duration, attrs)
          except Exception as e:  # pylint: disable=broad-except
            logger.error('Error recording metric: %s', e)

      return sync_wrapper  # type: ignore

  return decorator