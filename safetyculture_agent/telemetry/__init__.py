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

"""OpenTelemetry monitoring and observability for SafetyCulture agent.

This module provides comprehensive telemetry capabilities including:
- Distributed tracing for API calls and database operations
- Metrics collection (counters, histograms, gauges)
- Integration with OTLP exporters and Prometheus
- Performance monitoring with minimal overhead

The telemetry system is optional and can be disabled via configuration.
"""

from __future__ import annotations

from .decorators import measure_duration
from .decorators import trace_async
from .decorators import trace_sync
from .prometheus_metrics import record_api_latency
from .prometheus_metrics import record_api_request
from .prometheus_metrics import record_circuit_breaker_state
from .prometheus_metrics import record_database_query
from .prometheus_metrics import record_query_duration
from .prometheus_metrics import record_rate_limit_hit
from .telemetry_config import SERVICE_NAME
from .telemetry_config import SERVICE_VERSION
from .telemetry_config import TelemetryConfig
from .telemetry_manager import TelemetryManager

__all__ = [
  'TelemetryConfig',
  'TelemetryManager',
  'SERVICE_NAME',
  'SERVICE_VERSION',
  'trace_async',
  'trace_sync',
  'measure_duration',
  'record_api_request',
  'record_api_latency',
  'record_database_query',
  'record_query_duration',
  'record_circuit_breaker_state',
  'record_rate_limit_hit',
]