# Monitoring Setup

This directory contains monitoring and observability configuration for the Scam Detection Platform.

## Components

### Prometheus
- **Purpose**: Metrics collection and alerting
- **URL**: http://localhost:9090
- **Configuration**: `prometheus/prometheus.yml`
- **Alert Rules**: `prometheus/rules/alerts.yml`

### Grafana
- **Purpose**: Metrics visualization and dashboards
- **URL**: http://localhost:3000
- **Default Credentials**: admin/admin (change on first login)
- **Dashboards**: `grafana/dashboards/`

## Metrics Collected

### API Metrics
- Request rate (requests/second)
- Response time (P50, P95, P99)
- Error rate (4xx, 5xx)
- Active requests
- Endpoint-specific metrics

### Detection Metrics
- Total detections
- Scam vs legitimate ratio
- Detection accuracy
- False positive/negative rates
- Pattern detection distribution

### System Metrics
- CPU usage
- Memory usage
- Disk I/O
- Network traffic
- Database connections
- Cache hit rate

## Alert Rules

### Critical Alerts
- **APIDown**: API is unreachable
- **DatabaseDown**: Database is unreachable
- **LowDetectionAccuracy**: Accuracy dropped below 90%

### Warning Alerts
- **HighErrorRate**: Error rate > 5%
- **HighLatency**: P95 latency > 500ms
- **HighCPUUsage**: CPU > 80%
- **HighMemoryUsage**: Memory > 85%
- **LowDiskSpace**: Disk space < 15%
- **HighFalsePositiveRate**: FP rate > 5%

## Quick Start

### 1. Start Monitoring Stack

```bash
# With Docker Compose
docker-compose -f docker-compose.prod.yml up -d prometheus grafana

# Or standalone
docker run -d -p 9090:9090 -v $(pwd)/monitoring/prometheus:/etc/prometheus prom/prometheus
docker run -d -p 3000:3000 -v $(pwd)/monitoring/grafana:/etc/grafana grafana/grafana
```

### 2. Access Dashboards

```bash
# Prometheus
open http://localhost:9090

# Grafana
open http://localhost:3000
```

### 3. Import Dashboards

Grafana dashboards are auto-provisioned from `grafana/dashboards/`.

Manual import:
1. Go to Grafana → Dashboards → Import
2. Upload JSON from `grafana/dashboards/`
3. Select Prometheus datasource

## Custom Metrics

### Adding New Metrics

In your Python code:

```python
from prometheus_client import Counter, Histogram, Gauge

# Counter for total detections
detection_counter = Counter(
    'scam_detection_total',
    'Total number of scam detections',
    ['result']  # labels
)

# Histogram for latency
detection_latency = Histogram(
    'scam_detection_duration_seconds',
    'Time spent on detection'
)

# Gauge for accuracy
detection_accuracy = Gauge(
    'scam_detection_accuracy',
    'Current detection accuracy'
)

# Usage
detection_counter.labels(result='scam').inc()
with detection_latency.time():
    # ... detection logic
detection_accuracy.set(0.95)
```

### Exposing Metrics

Add to FastAPI application:

```python
from prometheus_client import make_asgi_app

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

## Alert Configuration

### Email Alerts

1. Install Alertmanager:
```bash
docker run -d -p 9093:9093 prom/alertmanager
```

2. Configure `alertmanager.yml`:
```yaml
route:
  receiver: 'email'

receivers:
  - name: 'email'
    email_configs:
      - to: 'alerts@example.com'
        from: 'prometheus@example.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'your-email@gmail.com'
        auth_password: 'your-app-password'
```

### Slack Alerts

```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'
```

## Troubleshooting

### Prometheus Not Scraping

1. Check targets: http://localhost:9090/targets
2. Verify network connectivity
3. Check application metrics endpoint: http://localhost:8000/metrics

### Grafana No Data

1. Verify Prometheus datasource: Configuration → Data Sources
2. Test connection
3. Check query syntax in dashboard panels

### High Memory Usage

Prometheus retains metrics for 15 days by default. To reduce:

```yaml
global:
  retention: 7d
  retention.size: 10GB
```

## Production Considerations

### Security

1. **Enable Authentication**
```yaml
# prometheus.yml
basic_auth:
  username: admin
  password: secure_password
```

2. **Use HTTPS**
```yaml
# prometheus.yml
tls_config:
  cert_file: /path/to/cert.pem
  key_file: /path/to/key.pem
```

3. **Restrict Access**
- Use firewall rules to limit access
- Configure CORS properly
- Use API keys for Grafana

### Performance

1. **Adjust Scrape Intervals**
```yaml
scrape_interval: 30s  # Reduce for lower load
```

2. **Use Recording Rules**
```yaml
groups:
  - name: performance
    interval: 30s
    rules:
      - record: api:request_rate:5m
        expr: rate(http_requests_total[5m])
```

3. **Enable Compression**
```yaml
scrape_configs:
  - job_name: 'api'
    compression: gzip
```

### High Availability

1. **Prometheus HA**
- Run multiple Prometheus instances
- Use Thanos for long-term storage
- Configure remote write

2. **Grafana HA**
- Use external database (PostgreSQL)
- Configure session storage (Redis)
- Load balance multiple instances

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Dashboard Best Practices](https://grafana.com/docs/grafana/latest/best-practices/best-practices-for-creating-dashboards/)
