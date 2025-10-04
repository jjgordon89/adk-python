# Circuit Breaker and API Monitoring

This document describes the monitoring capabilities for circuit breaker and API
metrics tracking in the SafetyCulture agent.

## Overview

The SafetyCulture agent includes comprehensive monitoring for:
- Circuit breaker state transitions and health
- API request metrics (latency, errors, timeouts)
- Rate limiter events
- Database query performance

All metrics are exposed via Prometheus and can be collected by standard
monitoring tools.

## Circuit Breaker Metrics

### State Tracking

The circuit breaker tracks its state through three phases:
- **CLOSED** (0): Normal operation, requests flow through
- **OPEN** (1): Failures detected, requests fail immediately
- **HALF_OPEN** (2): Testing if service has recovered

**Metric**: `safetyculture.circuit_breaker.state`
**Type**: Gauge (UpDownCounter)
**Labels**: `name`, `state`

### Circuit Breaker Events

The following event counters are tracked:

#### Trips (Circuit Opens)
**Metric**: `safetyculture.circuit_breaker.trips`
**Type**: Counter
**Labels**: `name`
**Description**: Incremented when circuit breaker opens due to failures

#### Recoveries (Circuit Closes)
**Metric**: `safetyculture.circuit_breaker.recoveries`
**Type**: Counter
**Labels**: `name`
**Description**: Incremented when circuit breaker closes after recovery

#### Rejections
**Metric**: `safetyculture.circuit_breaker.rejections`
**Type**: Counter
**Labels**: `name`
**Description**: Count of calls rejected due to open circuit

#### Successes
**Metric**: `safetyculture.circuit_breaker.successes`
**Type**: Counter
**Labels**: `name`
**Description**: Count of successful calls through circuit breaker

#### Failures
**Metric**: `safetyculture.circuit_breaker.failures`
**Type**: Counter
**Labels**: `name`
**Description**: Count of failed calls through circuit breaker

## API Metrics

### Request Tracking

**Metric**: `safetyculture.api.requests`
**Type**: Counter
**Labels**: `endpoint`, `method`, `status_code`
**Description**: Count of API requests by endpoint and HTTP status code

### Latency Tracking

**Metric**: `safetyculture.api.latency`
**Type**: Histogram
**Labels**: `endpoint`, `method`
**Unit**: seconds
**Description**: API request duration in seconds

### Error Tracking

**Metric**: `safetyculture.api.errors`
**Type**: Counter
**Labels**: `endpoint`, `method`, `error_type`
**Description**: Count of API errors by type

Error types include:
- `timeout`: Request timeout
- `http_XXX`: HTTP error with status code (e.g., `http_401`, `http_500`)
- `json_decode`: JSON decoding error
- `network`: Network connectivity error

### Timeout Tracking

**Metric**: `safetyculture.api.timeouts`
**Type**: Counter
**Labels**: `endpoint`, `method`
**Description**: Count of API request timeouts

## Usage Examples

### Viewing Metrics

Metrics are exposed at `http://localhost:8889/metrics` when Prometheus is
enabled (default).

```bash
# View all metrics
curl http://localhost:8889/metrics

# Filter circuit breaker metrics
curl http://localhost:8889/metrics | grep circuit_breaker

# Filter API metrics
curl http://localhost:8889/metrics | grep api
```

### Prometheus Queries

#### Circuit Breaker Health
```promql
# Current circuit breaker state
safetyculture_circuit_breaker_state{name="safetyculture_api"}

# Circuit breaker trip rate (last 5 minutes)
rate(safetyculture_circuit_breaker_trips_total[5m])

# Circuit breaker failure rate
rate(safetyculture_circuit_breaker_failures_total[5m]) /
rate(safetyculture_circuit_breaker_successes_total[5m])
```

#### API Performance
```promql
# API request rate by endpoint
rate(safetyculture_api_requests_total[5m])

# 95th percentile API latency
histogram_quantile(0.95, safetyculture_api_latency_bucket)

# API error rate
rate(safetyculture_api_errors_total[5m])

# API timeout rate
rate(safetyculture_api_timeouts_total[5m])
```

### Grafana Dashboard

Example dashboard queries:

```json
{
  "panels": [
    {
      "title": "Circuit Breaker State",
      "targets": [
        {
          "expr": "safetyculture_circuit_breaker_state"
        }
      ]
    },
    {
      "title": "API Request Rate",
      "targets": [
        {
          "expr": "sum(rate(safetyculture_api_requests_total[5m])) by (endpoint)"
        }
      ]
    },
    {
      "title": "API Error Rate",
      "targets": [
        {
          "expr": "sum(rate(safetyculture_api_errors_total[5m])) by (error_type)"
        }
      ]
    }
  ]
}
```

## Alerting

### Recommended Alerts

#### Circuit Breaker Open
```yaml
- alert: CircuitBreakerOpen
  expr: safetyculture_circuit_breaker_state{name="safetyculture_api"} == 1
  for: 5m
  annotations:
    summary: "Circuit breaker is open for SafetyCulture API"
    description: "The circuit breaker has been open for 5 minutes"
```

#### High API Error Rate
```yaml
- alert: HighAPIErrorRate
  expr: |
    rate(safetyculture_api_errors_total[5m]) /
    rate(safetyculture_api_requests_total[5m]) > 0.1
  for: 5m
  annotations:
    summary: "High API error rate detected"
    description: "API error rate is above 10% for 5 minutes"
```

#### High API Latency
```yaml
- alert: HighAPILatency
  expr: |
    histogram_quantile(0.95,
      safetyculture_api_latency_bucket) > 2
  for: 5m
  annotations:
    summary: "High API latency detected"
    description: "95th percentile API latency is above 2 seconds"
```

## Programmatic Access

### Getting Circuit Breaker Metrics

```python
from safetyculture_agent.tools.safetyculture_api_client import (
  SafetyCultureAPIClient
)

async with SafetyCultureAPIClient() as client:
  metrics = client.get_circuit_breaker_metrics()
  print(f"State: {metrics['state']}")
  print(f"Total calls: {metrics['total_calls']}")
  print(f"Failure rate: {metrics['failure_rate']:.2%}")
  print(f"Open count: {metrics['open_count']}")
  print(f"Rejected calls: {metrics['rejected_calls']}")
```

### Custom Metrics Recording

```python
from safetyculture_agent.telemetry.prometheus_metrics import (
  record_circuit_breaker_state,
  record_api_error,
  record_api_timeout
)

# Record custom circuit breaker state
record_circuit_breaker_state('my_circuit', 'open')

# Record custom API error
record_api_error('/custom/endpoint', 'GET', 'custom_error')

# Record custom timeout
record_api_timeout('/custom/endpoint', 'POST')
```

## Configuration

Monitoring is configured in `safetyculture_agent/config/telemetry.yaml`:

```yaml
# Enable telemetry
enabled: true

# Enable Prometheus metrics
prometheus_enabled: true
prometheus_port: 8889

# Sampling rate (1.0 = 100%)
sampling_rate: 1.0
```

Environment variables override YAML configuration:

```bash
export TELEMETRY_ENABLED=true
export TELEMETRY_PROMETHEUS_ENABLED=true
export TELEMETRY_PROMETHEUS_PORT=8889
export TELEMETRY_SAMPLING_RATE=1.0
```

## Troubleshooting

### Metrics Not Appearing

1. Check telemetry is enabled:
   ```python
   from safetyculture_agent.telemetry.telemetry_manager import (
     get_telemetry_manager
   )
   manager = get_telemetry_manager()
   print(f"Telemetry enabled: {manager.is_enabled}")
   ```

2. Verify Prometheus endpoint is accessible:
   ```bash
   curl http://localhost:8889/metrics
   ```

3. Check for initialization errors in logs:
   ```bash
   grep "telemetry" safetyculture_agent.log
   ```

### Missing Dependencies

If OpenTelemetry dependencies are not installed:

```bash
pip install opentelemetry-api opentelemetry-sdk
pip install opentelemetry-exporter-prometheus
pip install opentelemetry-instrumentation-aiohttp
```

### High Memory Usage

If metrics collection causes high memory usage:

1. Reduce sampling rate in `telemetry.yaml`:
   ```yaml
   sampling_rate: 0.1  # Sample 10% of requests
   ```

2. Limit attributes per span:
   ```yaml
   max_attributes_per_span: 64
   max_events_per_span: 64
   ```

## Best Practices

1. **Monitor circuit breaker state**: Set up alerts for when circuit breakers
   open

2. **Track error patterns**: Use error type labels to identify common failure
   modes

3. **Set latency baselines**: Establish normal latency ranges and alert on
   deviations

4. **Use sampling in production**: For high-traffic environments, use sampling
   to reduce overhead

5. **Correlate metrics**: Use circuit breaker state with API error rates to
   understand failure patterns

6. **Regular review**: Periodically review metrics to identify optimization
   opportunities