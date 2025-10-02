# OpenTelemetry Monitoring for SafetyCulture Agent

This directory contains the OpenTelemetry integration for comprehensive monitoring and observability of the SafetyCulture agent.

## Overview

The telemetry system provides:

- **Distributed Tracing**: Track API calls and database operations across the system
- **Metrics Collection**: Monitor performance, throughput, and error rates
- **OTLP Export**: Send traces to Jaeger, Zipkin, or other OTLP-compatible backends
- **Prometheus Integration**: Expose metrics for Prometheus scraping
- **Low Overhead**: Minimal performance impact (<5% overhead when enabled)

## Architecture

```
telemetry/
├── __init__.py              # Public API exports
├── telemetry_config.py      # Configuration dataclass and constants
├── telemetry_manager.py     # Singleton manager for OpenTelemetry SDK
├── decorators.py            # Tracing decorators for instrumentation
├── prometheus_metrics.py    # Prometheus metrics helpers
└── README.md               # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r safetyculture_agent/requirements.txt
```

### 2. Enable Telemetry

Telemetry is **enabled by default**. To disable it:

```bash
export TELEMETRY_ENABLED=false
```

### 3. Configure Exporters

#### Prometheus Metrics (Default: Enabled)

Metrics are automatically exposed at `http://localhost:8889/metrics`

```bash
# Change Prometheus port (default: 8889)
export TELEMETRY_PROMETHEUS_PORT=9090

# Disable Prometheus
export TELEMETRY_PROMETHEUS_ENABLED=false
```

#### OTLP Traces (Default: Disabled)

To send traces to a collector (e.g., Jaeger):

```bash
# Local Jaeger (via docker)
export TELEMETRY_OTLP_ENDPOINT=localhost:4317

# Cloud provider
export TELEMETRY_OTLP_ENDPOINT=https://otlp.example.com:4317
export TELEMETRY_OTLP_INSECURE=false
```

### 4. Run the Agent

```bash
python -m safetyculture_agent.agent
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEMETRY_ENABLED` | `true` | Enable/disable telemetry |
| `TELEMETRY_SERVICE_NAME` | `safetyculture-agent` | Service name |
| `TELEMETRY_SERVICE_VERSION` | `1.0.0` | Service version |
| `TELEMETRY_OTLP_ENDPOINT` | `null` | OTLP endpoint (e.g., `localhost:4317`) |
| `TELEMETRY_OTLP_INSECURE` | `true` | Use insecure OTLP connection |
| `TELEMETRY_PROMETHEUS_PORT` | `8889` | Prometheus metrics port |
| `TELEMETRY_PROMETHEUS_ENABLED` | `true` | Enable Prometheus metrics |
| `TELEMETRY_SAMPLING_RATE` | `1.0` | Trace sampling rate (0.0-1.0) |

### Configuration File

You can also use [`config/telemetry.yaml`](../config/telemetry.yaml) for configuration (environment variables take precedence).

## Viewing Telemetry Data

### Prometheus Metrics

1. **Access metrics endpoint**:
   ```bash
   curl http://localhost:8889/metrics
   ```

2. **Configure Prometheus** (`prometheus.yml`):
   ```yaml
   scrape_configs:
     - job_name: 'safetyculture-agent'
       static_configs:
         - targets: ['localhost:8889']
   ```

3. **Common queries**:
   ```promql
   # API request rate
   rate(safetyculture_api_requests[5m])
   
   # API latency (p95)
   histogram_quantile(0.95, rate(safetyculture_api_latency_bucket[5m]))
   
   # Database query rate by operation
   rate(safetyculture_db_queries[5m])
   
   # Circuit breaker state
   safetyculture_circuit_breaker_state
   ```

### Distributed Traces (Jaeger)

1. **Start Jaeger** (via Docker):
   ```bash
   docker run -d --name jaeger \
     -p 16686:16686 \
     -p 4317:4317 \
     jaegertracing/all-in-one:latest
   ```

2. **Configure agent**:
   ```bash
   export TELEMETRY_OTLP_ENDPOINT=localhost:4317
   ```

3. **View traces**: Navigate to `http://localhost:16686`

### Distributed Traces (Zipkin)

1. **Start Zipkin**:
   ```bash
   docker run -d -p 9411:9411 openzipkin/zipkin
   ```

2. **Configure agent**:
   ```bash
   export TELEMETRY_OTLP_ENDPOINT=localhost:9411/api/v2/spans
   ```

3. **View traces**: Navigate to `http://localhost:9411`

## Available Metrics

### API Metrics

- **`safetyculture.api.requests`** (Counter): API request count
  - Labels: `endpoint`, `method`, `status_code`

- **`safetyculture.api.latency`** (Histogram): API request duration (seconds)
  - Labels: `endpoint`, `method`

- **`safetyculture.rate_limit.hits`** (Counter): Rate limit hits
  - Labels: `endpoint`

### Database Metrics

- **`safetyculture.db.queries`** (Counter): Database query count
  - Labels: `operation`, `table`

- **`safetyculture.db.query_duration`** (Histogram): Query duration (seconds)
  - Labels: `operation`, `table`

### System Metrics

- **`safetyculture.circuit_breaker.state`** (Gauge): Circuit breaker state
  - Labels: `name`, `state`
  - Values: `0=closed`, `1=open`, `2=half_open`

## Instrumented Components

### API Client

All SafetyCulture API methods in [`tools/safetyculture_api_client.py`](../tools/safetyculture_api_client.py) are instrumented:

- `search_assets()`
- `get_asset()`
- `search_templates()`
- `get_template()`
- `search_inspections()`
- `create_inspection()`
- `update_inspection()`
- `get_inspection()`
- `share_inspection()`
- `search_sites()`
- `search_users()`

### Database Operations

Key database methods are instrumented:

- **AssetRepository** ([`database/asset_repository.py`](../database/asset_repository.py)):
  - `initialize()`
  - `check_asset_completed_this_month()`
  - `register_asset()`
  - `register_asset_for_inspection()`
  - `update_inspection_status()`

- **MonthlySummaryService** ([`database/monthly_summary_service.py`](../database/monthly_summary_service.py)):
  - `get_monthly_summary()`
  - `get_completed_assets()`
  - `get_pending_assets()`
  - `export_monthly_report()`

- **AssetQueries** ([`database/asset_queries.py`](../database/asset_queries.py)):
  - `cleanup_old_records()`
  - `get_retention_stats()`

## Adding Custom Instrumentation

### Tracing Async Functions

```python
from safetyculture_agent.telemetry import trace_async

@trace_async('my_operation', {'custom_attr': 'value'})
async def my_async_function(param: str) -> dict:
    # Your code here
    return result
```

### Tracing Sync Functions

```python
from safetyculture_agent.telemetry import trace_sync

@trace_sync('my_sync_operation')
def my_sync_function(param: str) -> dict:
    # Your code here
    return result
```

### Recording Custom Metrics

```python
from safetyculture_agent.telemetry import (
    record_api_request,
    record_api_latency,
    record_database_query,
    record_query_duration
)

# Record API metrics
record_api_request('/custom/endpoint', 'GET', 200)
record_api_latency('/custom/endpoint', 'GET', 0.125)

# Record database metrics
record_database_query('INSERT', 'custom_table')
record_query_duration('INSERT', 0.05, 'custom_table')
```

## Performance Impact

The telemetry system is designed for minimal overhead:

- **Tracing overhead**: ~1-2% when enabled with 100% sampling
- **Metrics overhead**: ~0.5-1% for metric recording
- **Total overhead**: <5% in typical usage
- **Disabled overhead**: ~0.01% (negligible no-op checks)

### Performance Tuning

1. **Reduce sampling** for high-traffic endpoints:
   ```bash
   export TELEMETRY_SAMPLING_RATE=0.1  # Sample 10% of traces
   ```

2. **Disable tracing**, keep metrics:
   ```bash
   export TELEMETRY_OTLP_ENDPOINT=  # Empty to disable
   export TELEMETRY_PROMETHEUS_ENABLED=true
   ```

3. **Disable telemetry completely**:
   ```bash
   export TELEMETRY_ENABLED=false
   ```

## Troubleshooting

### Metrics Not Showing Up

1. **Check if telemetry is enabled**:
   ```bash
   curl http://localhost:8889/metrics | grep safetyculture
   ```

2. **Verify environment variables**:
   ```bash
   echo $TELEMETRY_ENABLED
   echo $TELEMETRY_PROMETHEUS_PORT
   ```

3. **Check logs** for initialization errors:
   ```bash
   grep -i telemetry logs/agent.log
   ```

### Traces Not Appearing in Jaeger/Zipkin

1. **Verify OTLP endpoint**:
   ```bash
   echo $TELEMETRY_OTLP_ENDPOINT
   ```

2. **Test connectivity**:
   ```bash
   nc -zv localhost 4317  # For local Jaeger
   ```

3. **Check collector logs** for errors

4. **Verify sampling rate** (not set too low):
   ```bash
   echo $TELEMETRY_SAMPLING_RATE
   ```

### High Memory Usage

1. **Reduce span attributes**:
   ```python
   # In telemetry_config.py or via env var
   max_attributes_per_span: 64  # Default: 128
   ```

2. **Reduce sampling rate**:
   ```bash
   export TELEMETRY_SAMPLING_RATE=0.1
   ```

3. **Disable tracing** if only metrics are needed:
   ```bash
   export TELEMETRY_OTLP_ENDPOINT=
   ```

### Import Errors

If you see import errors for OpenTelemetry packages:

```bash
pip install -r safetyculture_agent/requirements.txt --upgrade
```

The agent gracefully handles missing dependencies and continues without telemetry.

## Production Best Practices

### 1. Use Sampling

For production workloads, use sampling to reduce overhead:

```bash
export TELEMETRY_SAMPLING_RATE=0.1  # 10% sampling
```

### 2. Secure OTLP Connections

Always use TLS for production OTLP endpoints:

```bash
export TELEMETRY_OTLP_ENDPOINT=https://otlp.example.com:4317
export TELEMETRY_OTLP_INSECURE=false
```

### 3. Add Resource Attributes

Tag telemetry with environment information:

```bash
# In config/telemetry.yaml
resource_attributes:
  environment: production
  deployment.type: kubernetes
  region: us-west-2
  team: platform
```

### 4. Monitor Prometheus Metrics

Set up alerts for key metrics:

```yaml
# prometheus/alerts.yml
groups:
  - name: safetyculture-agent
    rules:
      - alert: HighAPILatency
        expr: |
          histogram_quantile(0.95,
            rate(safetyculture_api_latency_bucket[5m])
          ) > 2.0
        annotations:
          summary: "High API latency detected"
      
      - alert: CircuitBreakerOpen
        expr: safetyculture_circuit_breaker_state == 1
        annotations:
          summary: "Circuit breaker is open"
```

### 5. Regular Maintenance

- Monitor telemetry data volume
- Adjust sampling rates based on traffic
- Review and optimize instrumented code paths
- Update retention policies for trace data

## Example Dashboards

### Grafana Dashboard Queries

**API Performance Panel**:
```promql
# Request rate by endpoint
sum(rate(safetyculture_api_requests[5m])) by (endpoint)

# P95 latency by endpoint
histogram_quantile(0.95,
  sum(rate(safetyculture_api_latency_bucket[5m])) by (le, endpoint)
)

# Error rate
sum(rate(safetyculture_api_requests{status_code=~"5.."}[5m]))
  / sum(rate(safetyculture_api_requests[5m]))
```

**Database Performance Panel**:
```promql
# Query rate by operation
sum(rate(safetyculture_db_queries[5m])) by (operation)

# P95 query duration
histogram_quantile(0.95,
  rate(safetyculture_db_query_duration_bucket[5m])
)
```

**System Health Panel**:
```promql
# Circuit breaker status
safetyculture_circuit_breaker_state

# Rate limit hits
rate(safetyculture_rate_limit_hits[5m])
```

## Advanced Usage

### Custom Span Attributes

Add custom attributes to spans:

```python
from opentelemetry import trace

# Get current span
span = trace.get_current_span()
span.set_attribute('custom.attribute', 'value')
span.set_attribute('user.id', user_id)
```

### Manual Span Creation

Create custom spans manually:

```python
from safetyculture_agent.telemetry import TelemetryManager

manager = TelemetryManager()
tracer = manager.get_tracer(__name__)

with tracer.start_as_current_span('custom_operation') as span:
    span.set_attribute('operation.type', 'custom')
    # Your code here
    span.add_event('Processing started')
    result = process_data()
    span.add_event('Processing completed')
```

### Custom Metrics

Create and record custom metrics:

```python
from safetyculture_agent.telemetry import TelemetryManager

manager = TelemetryManager()
meter = manager.get_meter(__name__)

# Create a counter
custom_counter = meter.create_counter(
    name='custom.operations',
    unit='1',
    description='Count of custom operations'
)
custom_counter.add(1, {'operation_type': 'special'})

# Create a histogram
custom_histogram = meter.create_histogram(
    name='custom.duration',
    unit='s',
    description='Duration of custom operations'
)
custom_histogram.record(0.125, {'operation_type': 'special'})
```

## Disabling Telemetry

### Completely Disable

```bash
export TELEMETRY_ENABLED=false
```

### Disable Only Tracing

```bash
export TELEMETRY_OTLP_ENDPOINT=
```

### Disable Only Metrics

```bash
export TELEMETRY_PROMETHEUS_ENABLED=false
```

## Integration Examples

### With Docker Compose

```yaml
version: '3.8'
services:
  safetyculture-agent:
    image: safetyculture-agent:latest
    environment:
      - TELEMETRY_ENABLED=true
      - TELEMETRY_OTLP_ENDPOINT=jaeger:4317
      - TELEMETRY_PROMETHEUS_PORT=8889
    ports:
      - "8889:8889"  # Prometheus metrics
  
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC
  
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### With Kubernetes

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: telemetry-config
data:
  TELEMETRY_ENABLED: "true"
  TELEMETRY_OTLP_ENDPOINT: "otel-collector.monitoring:4317"
  TELEMETRY_PROMETHEUS_PORT: "8889"
  TELEMETRY_SAMPLING_RATE: "0.1"
---
apiVersion: v1
kind: Service
metadata:
  name: safetyculture-agent-metrics
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8889"
    prometheus.io/path: "/metrics"
spec:
  selector:
    app: safetyculture-agent
  ports:
    - name: metrics
      port: 8889
```

## Span Attributes

### API Spans

- `safetyculture.api.endpoint`: API endpoint path
- `safetyculture.api.method`: HTTP method
- `safetyculture.api.status_code`: HTTP status code
- `safetyculture.rate_limit.remaining`: Remaining rate limit quota
- `safetyculture.circuit_breaker.state`: Circuit breaker state

### Database Spans

- `safetyculture.db.operation`: SQL operation type (SELECT, INSERT, etc.)
- `safetyculture.db.table`: Database table name
- `safetyculture.db.query_type`: Query classification

### Asset/Inspection Spans

- `safetyculture.asset.id`: Asset identifier
- `safetyculture.template.id`: Template identifier

### Error Spans

- `safetyculture.error.type`: Error type/exception name
- `exception.type`: Standard exception type
- `exception.message`: Exception message

## Testing Telemetry

### Unit Tests

```python
from safetyculture_agent.telemetry import (
    TelemetryConfig,
    TelemetryManager
)

def test_telemetry_disabled():
    """Test that telemetry can be disabled."""
    config = TelemetryConfig(enabled=False)
    manager = TelemetryManager()
    manager.initialize(config)
    assert not manager.is_enabled

def test_telemetry_enabled():
    """Test that telemetry initializes correctly."""
    config = TelemetryConfig(
        enabled=True,
        prometheus_enabled=True,
        prometheus_port=9999
    )
    manager = TelemetryManager()
    manager.initialize(config)
    assert manager.is_enabled
```

### Manual Testing

```bash
# Start the agent with telemetry
export TELEMETRY_ENABLED=true
export TELEMETRY_PROMETHEUS_PORT=8889
python -m safetyculture_agent.agent

# In another terminal, check metrics
curl http://localhost:8889/metrics | grep safetyculture

# Make some API calls, then check metrics again
curl http://localhost:8889/metrics | grep safetyculture_api_requests
```

## Security Considerations

1. **Sensitive Data**: The telemetry system automatically excludes sensitive headers (API tokens, passwords) from spans and metrics.

2. **Network Security**: Use TLS for OTLP endpoints in production:
   ```bash
   export TELEMETRY_OTLP_INSECURE=false
   ```

3. **Metrics Endpoint**: Consider securing the Prometheus endpoint with authentication in production environments.

4. **Data Retention**: Configure appropriate retention policies in your monitoring backend to comply with data policies.

## Support and Resources

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [ADK Telemetry Sample](../../contributing/samples/telemetry/)

## Changelog

### Version 1.0.0 (2025-01)
- Initial OpenTelemetry integration
- Distributed tracing for API and database operations
- Prometheus metrics export
- OTLP trace export support
- Comprehensive instrumentation of SafetyCulture agent