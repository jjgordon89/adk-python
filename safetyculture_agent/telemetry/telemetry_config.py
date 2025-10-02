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

"""Configuration for OpenTelemetry monitoring and observability.

This module defines constants and configuration classes for the telemetry
system, including service identification, span attributes, and metric names.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


# Service identification constants
SERVICE_NAME = 'safetyculture-agent'
SERVICE_VERSION = '1.0.0'

# Span attribute keys for SafetyCulture-specific attributes
SPAN_ATTR_API_ENDPOINT = 'safetyculture.api.endpoint'
SPAN_ATTR_API_METHOD = 'safetyculture.api.method'
SPAN_ATTR_API_STATUS_CODE = 'safetyculture.api.status_code'
SPAN_ATTR_RATE_LIMIT_REMAINING = 'safetyculture.rate_limit.remaining'
SPAN_ATTR_CIRCUIT_BREAKER_STATE = 'safetyculture.circuit_breaker.state'
SPAN_ATTR_DB_OPERATION = 'safetyculture.db.operation'
SPAN_ATTR_DB_TABLE = 'safetyculture.db.table'
SPAN_ATTR_QUERY_TYPE = 'safetyculture.db.query_type'
SPAN_ATTR_ASSET_ID = 'safetyculture.asset.id'
SPAN_ATTR_TEMPLATE_ID = 'safetyculture.template.id'
SPAN_ATTR_ERROR_TYPE = 'safetyculture.error.type'

# Metric name constants
METRIC_API_REQUESTS = 'safetyculture.api.requests'
METRIC_API_LATENCY = 'safetyculture.api.latency'
METRIC_DB_QUERIES = 'safetyculture.db.queries'
METRIC_DB_QUERY_DURATION = 'safetyculture.db.query_duration'
METRIC_CIRCUIT_BREAKER_STATE = 'safetyculture.circuit_breaker.state'
METRIC_RATE_LIMIT_HITS = 'safetyculture.rate_limit.hits'


@dataclass
class TelemetryConfig:
  """Configuration for OpenTelemetry telemetry system.

  Attributes:
    enabled: Whether telemetry is enabled. If False, no-op implementations
      are used to minimize overhead.
    service_name: Name of the service for telemetry identification.
    service_version: Version of the service for telemetry identification.
    otlp_endpoint: OTLP endpoint for traces and metrics (e.g., Jaeger).
    otlp_insecure: Whether to use insecure connection for OTLP.
    prometheus_port: Port for Prometheus metrics exporter.
    prometheus_enabled: Whether Prometheus metrics are enabled.
    sampling_rate: Trace sampling rate (0.0 to 1.0). 1.0 means all traces.
    max_attributes_per_span: Maximum number of attributes per span.
    max_events_per_span: Maximum number of events per span.
    resource_attributes: Additional resource attributes for telemetry.
  """

  enabled: bool = True
  service_name: str = SERVICE_NAME
  service_version: str = SERVICE_VERSION
  otlp_endpoint: str | None = None
  otlp_insecure: bool = True
  prometheus_port: int = 8889
  prometheus_enabled: bool = True
  sampling_rate: float = 1.0
  max_attributes_per_span: int = 128
  max_events_per_span: int = 128
  resource_attributes: dict[str, str] = field(default_factory=dict)

  def __post_init__(self) -> None:
    """Validate configuration values after initialization."""
    if not 0.0 <= self.sampling_rate <= 1.0:
      raise ValueError(
        f'sampling_rate must be between 0.0 and 1.0, got {self.sampling_rate}'
      )
    if self.prometheus_port < 1 or self.prometheus_port > 65535:
      raise ValueError(
        f'prometheus_port must be between 1 and 65535, '
        f'got {self.prometheus_port}'
      )
    if self.max_attributes_per_span < 1:
      raise ValueError(
        f'max_attributes_per_span must be at least 1, '
        f'got {self.max_attributes_per_span}'
      )
    if self.max_events_per_span < 1:
      raise ValueError(
        f'max_events_per_span must be at least 1, '
        f'got {self.max_events_per_span}'
      )

  @classmethod
  def from_env(cls) -> TelemetryConfig:
    """Create configuration from environment variables.

    Environment variables:
      TELEMETRY_ENABLED: Enable/disable telemetry (default: true)
      TELEMETRY_SERVICE_NAME: Service name (default: safetyculture-agent)
      TELEMETRY_SERVICE_VERSION: Service version (default: 1.0.0)
      TELEMETRY_OTLP_ENDPOINT: OTLP endpoint (default: None)
      TELEMETRY_OTLP_INSECURE: Use insecure OTLP (default: true)
      TELEMETRY_PROMETHEUS_PORT: Prometheus port (default: 8889)
      TELEMETRY_PROMETHEUS_ENABLED: Enable Prometheus (default: true)
      TELEMETRY_SAMPLING_RATE: Trace sampling rate (default: 1.0)

    Returns:
      TelemetryConfig instance with values from environment variables.
    """
    import os

    def parse_bool(value: str | None, default: bool) -> bool:
      """Parse boolean from environment variable."""
      if value is None:
        return default
      return value.lower() in ('true', '1', 'yes', 'on')

    def parse_float(value: str | None, default: float) -> float:
      """Parse float from environment variable."""
      if value is None:
        return default
      try:
        return float(value)
      except ValueError:
        return default

    def parse_int(value: str | None, default: int) -> int:
      """Parse integer from environment variable."""
      if value is None:
        return default
      try:
        return int(value)
      except ValueError:
        return default

    return cls(
      enabled=parse_bool(os.getenv('TELEMETRY_ENABLED'), True),
      service_name=os.getenv('TELEMETRY_SERVICE_NAME', SERVICE_NAME),
      service_version=os.getenv('TELEMETRY_SERVICE_VERSION', SERVICE_VERSION),
      otlp_endpoint=os.getenv('TELEMETRY_OTLP_ENDPOINT'),
      otlp_insecure=parse_bool(os.getenv('TELEMETRY_OTLP_INSECURE'), True),
      prometheus_port=parse_int(os.getenv('TELEMETRY_PROMETHEUS_PORT'), 8889),
      prometheus_enabled=parse_bool(
        os.getenv('TELEMETRY_PROMETHEUS_ENABLED'), True
      ),
      sampling_rate=parse_float(os.getenv('TELEMETRY_SAMPLING_RATE'), 1.0),
    )