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

"""Telemetry manager for OpenTelemetry initialization and configuration.

This module provides a singleton manager that handles the initialization
and lifecycle of OpenTelemetry tracing and metrics components.
"""

from __future__ import annotations

import logging
from typing import Any

from .telemetry_config import TelemetryConfig

logger = logging.getLogger(__name__)


class TelemetryManager:
  """Singleton manager for OpenTelemetry telemetry.

  This class manages the initialization and lifecycle of OpenTelemetry
  components including TracerProvider, MeterProvider, and exporters.
  It uses a singleton pattern to ensure only one instance exists.
  """

  _instance: TelemetryManager | None = None
  _initialized: bool = False

  def __new__(cls) -> TelemetryManager:
    """Create or return the singleton instance."""
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  def __init__(self) -> None:
    """Initialize the telemetry manager (only once)."""
    # Prevent reinitialization
    if TelemetryManager._initialized:
      return

    self._config: TelemetryConfig | None = None
    self._tracer_provider: Any = None
    self._meter_provider: Any = None
    self._prometheus_exporter: Any = None
    TelemetryManager._initialized = True

  def initialize(self, config: TelemetryConfig) -> None:
    """Initialize OpenTelemetry with the provided configuration.

    This method sets up the TracerProvider with OTLP exporter and the
    MeterProvider with Prometheus exporter based on the configuration.

    Args:
      config: Telemetry configuration.
    """
    if not config.enabled:
      logger.info('Telemetry is disabled')
      return

    try:
      self._config = config
      self._setup_tracing()
      self._setup_metrics()
      self._setup_auto_instrumentation()
      logger.info(
        'Telemetry initialized successfully for service %s v%s',
        config.service_name,
        config.service_version,
      )
    except ImportError as e:
      logger.warning(
        'OpenTelemetry dependencies not installed, telemetry disabled: %s', e
      )
      self._config = None
    except Exception as e:  # pylint: disable=broad-except
      logger.error('Failed to initialize telemetry: %s', e)
      self._config = None

  def _setup_tracing(self) -> None:
    """Set up OpenTelemetry tracing with OTLP exporter."""
    if not self._config:
      return

    try:
      from opentelemetry import trace
      from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter,
      )
      from opentelemetry.sdk.resources import Resource
      from opentelemetry.sdk.trace import TracerProvider
      from opentelemetry.sdk.trace.export import BatchSpanProcessor
      from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

      # Create resource with service information
      resource_attrs = {
        'service.name': self._config.service_name,
        'service.version': self._config.service_version,
      }
      resource_attrs.update(self._config.resource_attributes)
      resource = Resource.create(resource_attrs)

      # Create tracer provider with sampling
      sampler = TraceIdRatioBased(self._config.sampling_rate)
      self._tracer_provider = TracerProvider(
        resource=resource,
        sampler=sampler,
      )

      # Add OTLP exporter if endpoint is configured
      if self._config.otlp_endpoint:
        otlp_exporter = OTLPSpanExporter(
          endpoint=self._config.otlp_endpoint,
          insecure=self._config.otlp_insecure,
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        self._tracer_provider.add_span_processor(span_processor)
        logger.info('OTLP trace exporter configured: %s',
                    self._config.otlp_endpoint)

      # Set as global tracer provider
      trace.set_tracer_provider(self._tracer_provider)

    except ImportError as e:
      logger.warning('Tracing dependencies not available: %s', e)
      raise

  def _setup_metrics(self) -> None:
    """Set up OpenTelemetry metrics with Prometheus exporter."""
    if not self._config or not self._config.prometheus_enabled:
      return

    try:
      from opentelemetry import metrics
      from opentelemetry.exporter.prometheus import PrometheusMetricReader
      from opentelemetry.sdk.metrics import MeterProvider
      from opentelemetry.sdk.resources import Resource

      # Create resource with service information
      resource_attrs = {
        'service.name': self._config.service_name,
        'service.version': self._config.service_version,
      }
      resource_attrs.update(self._config.resource_attributes)
      resource = Resource.create(resource_attrs)

      # Create Prometheus exporter
      self._prometheus_exporter = PrometheusMetricReader()

      # Create meter provider with Prometheus exporter
      self._meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[self._prometheus_exporter],
      )

      # Set as global meter provider
      metrics.set_meter_provider(self._meter_provider)

      logger.info(
        'Prometheus metrics exporter configured on port %d',
        self._config.prometheus_port,
      )

    except ImportError as e:
      logger.warning('Metrics dependencies not available: %s', e)
      raise

  def _setup_auto_instrumentation(self) -> None:
    """Set up automatic instrumentation for libraries."""
    if not self._config:
      return

    try:
      # Instrument aiohttp client
      try:
        from opentelemetry.instrumentation.aiohttp_client import (
          AioHttpClientInstrumentor,
        )
        AioHttpClientInstrumentor().instrument()
        logger.debug('aiohttp client instrumentation enabled')
      except ImportError:
        logger.debug('aiohttp instrumentation not available')

      # Instrument SQLite
      try:
        from opentelemetry.instrumentation.sqlite3 import (
          SQLite3Instrumentor,
        )
        SQLite3Instrumentor().instrument()
        logger.debug('SQLite instrumentation enabled')
      except ImportError:
        logger.debug('SQLite instrumentation not available')

    except Exception as e:  # pylint: disable=broad-except
      logger.warning('Auto-instrumentation setup failed: %s', e)

  def get_tracer(self, name: str) -> Any:
    """Get a tracer instance.

    Args:
      name: Name of the tracer (typically module name).

    Returns:
      Tracer instance or no-op tracer if telemetry is disabled.
    """
    if not self._config or not self._config.enabled:
      from opentelemetry import trace
      return trace.get_tracer(name)

    try:
      from opentelemetry import trace
      return trace.get_tracer(name)
    except Exception as e:  # pylint: disable=broad-except
      logger.error('Failed to get tracer: %s', e)
      from opentelemetry import trace
      return trace.get_tracer(name)

  def get_meter(self, name: str) -> Any:
    """Get a meter instance.

    Args:
      name: Name of the meter (typically module name).

    Returns:
      Meter instance or no-op meter if telemetry is disabled.
    """
    if not self._config or not self._config.enabled:
      from opentelemetry import metrics
      return metrics.get_meter(name)

    try:
      from opentelemetry import metrics
      return metrics.get_meter(name)
    except Exception as e:  # pylint: disable=broad-except
      logger.error('Failed to get meter: %s', e)
      from opentelemetry import metrics
      return metrics.get_meter(name)

  def shutdown(self) -> None:
    """Gracefully shutdown telemetry and flush any pending data."""
    if not self._config:
      return

    try:
      if self._tracer_provider:
        self._tracer_provider.shutdown()
        logger.info('Tracer provider shut down')

      if self._meter_provider:
        self._meter_provider.shutdown()
        logger.info('Meter provider shut down')

    except Exception as e:  # pylint: disable=broad-except
      logger.error('Error during telemetry shutdown: %s', e)

  @property
  def is_enabled(self) -> bool:
    """Check if telemetry is enabled.

    Returns:
      True if telemetry is enabled, False otherwise.
    """
    return self._config is not None and self._config.enabled


# Global instance
_telemetry_manager = TelemetryManager()


def get_telemetry_manager() -> TelemetryManager:
  """Get the global telemetry manager instance.

  Returns:
    Global TelemetryManager instance.
  """
  return _telemetry_manager