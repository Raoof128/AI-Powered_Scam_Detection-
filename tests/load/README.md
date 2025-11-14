# Load Testing Guide

This directory contains load testing configurations using Locust.

## Quick Start

### Installation

```bash
# Install Locust
pip install locust

# Or with Docker
docker run -p 8089:8089 -v $PWD:/mnt/locust locustio/locust -f /mnt/locust/locustfile.py
```

### Run Load Test

```bash
# Web UI mode
locust --host=http://localhost:8000

# Then open http://localhost:8089 in your browser
```

### Headless Mode

```bash
# Run with 100 users, spawn rate 10/sec, for 5 minutes
locust --host=http://localhost:8000 \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m
```

## Test Scenarios

### 1. Basic Load Test

Test normal load with mixed operations:

```bash
locust -f locustfile.py \
    --host=http://localhost:8000 \
    --users 50 \
    --spawn-rate 5 \
    --run-time 10m
```

**Expected Results:**
- P95 latency < 500ms
- Error rate < 1%
- Throughput > 100 req/sec

### 2. Stress Test

Test maximum capacity:

```bash
locust -f locustfile.py \
    --host=http://localhost:8000 \
    --users 500 \
    --spawn-rate 50 \
    --run-time 10m \
    --stop-timeout 30
```

**Expected Results:**
- System remains stable
- No crashes or OOM errors
- Graceful degradation under load

### 3. Spike Test

Test sudden traffic spikes:

```bash
# Use SpikeLoadShape
locust -f locustfile.py \
    --host=http://localhost:8000 \
    --users 20 \
    --spawn-rate 100 \
    --run-time 5m
```

**Expected Results:**
- Handles sudden spikes
- Rate limiting activates correctly
- Quick recovery after spike

### 4. Endurance Test

Test long-running stability:

```bash
locust -f locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 1h
```

**Expected Results:**
- No memory leaks
- Stable performance over time
- No degradation after 1 hour

## Distributed Load Testing

For high load testing, use distributed mode:

### Master Node

```bash
locust -f locustfile.py \
    --master \
    --host=http://localhost:8000 \
    --expect-workers=4
```

### Worker Nodes

```bash
# On each worker machine
locust -f locustfile.py \
    --worker \
    --master-host=<master-ip>
```

## Custom Load Shapes

### Step Load

Gradually increase load:

```python
# In locustfile.py
class StepLoadShape(LoadTestShape):
    def tick(self):
        run_time = self.get_run_time()
        if run_time < 60:
            return (10, 1)
        elif run_time < 120:
            return (50, 5)
        elif run_time < 180:
            return (100, 10)
        else:
            return None
```

### Spike Load

Test traffic spikes:

```python
class SpikeLoadShape(LoadTestShape):
    def tick(self):
        run_time = self.get_run_time()
        if 60 < run_time < 90:
            return (200, 50)  # Spike
        else:
            return (20, 5)  # Normal
```

## Monitoring During Load Tests

### 1. System Metrics

```bash
# Terminal 1: Monitor system resources
docker stats

# Terminal 2: Watch API logs
docker-compose logs -f api

# Terminal 3: Monitor database
docker-compose exec postgres psql -U scam_detector -c "SELECT * FROM pg_stat_activity;"
```

### 2. Prometheus Metrics

Access during test:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Key metrics to watch:
- Request rate: `rate(http_requests_total[1m])`
- Latency: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- Error rate: `rate(http_requests_total{status=~"5.."}[1m])`

### 3. Application Logs

```bash
# Watch for errors
docker-compose logs api | grep ERROR

# Monitor rate limiting
docker-compose logs api | grep "Rate limit"

# Check detection performance
docker-compose logs api | grep "Detection time"
```

## Performance Targets

### Latency Requirements

| Percentile | Target | Maximum |
|------------|--------|---------|
| P50 | < 200ms | < 300ms |
| P95 | < 500ms | < 800ms |
| P99 | < 1000ms | < 1500ms |

### Throughput Requirements

| Metric | Target | Maximum |
|--------|--------|---------|
| Requests/sec | > 100 | > 1000 |
| Batch/sec | > 10 | > 100 |
| Concurrent users | > 100 | > 1000 |

### Accuracy Under Load

| Metric | Requirement |
|--------|-------------|
| Detection accuracy | > 90% |
| False positive rate | < 5% |
| No degradation | Under high load |

## Analyzing Results

### Locust Web UI

Access at http://localhost:8089:

1. **Statistics Tab**: Request counts, failure rates, response times
2. **Charts Tab**: Real-time performance graphs
3. **Failures Tab**: Detailed error information
4. **Download Data**: Export results to CSV

### Command Line Results

```bash
# Example output
Name                            # reqs      # fails  |     Avg     Min     Max  Median  |   req/s failures/s
------------------------------------------------------------------------------------------
POST /api/v1/detect              10000           0  |     234      45     890     210  |   100.0    0.00
POST /api/v1/detect/batch         2000           0  |     567     123    1234     520  |    20.0    0.00
GET  /api/v1/stats/overview       1000           0  |      89      23     234      78  |    10.0    0.00
------------------------------------------------------------------------------------------
Aggregated                       13000           0  |     267      23    1234     215  |   130.0    0.00

Response time percentiles (approximated)
Type            Name                50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
------------------------------------------------------------------------
POST   /api/v1/detect                210    245    280    310    390    480    650    780   890    890    890  10000
POST   /api/v1/detect/batch          520    610    690    750    890   1050   1180   1230  1234   1234   1234   2000
GET    /api/v1/stats/overview         78     89    101    112    145    178    210    223   234    234    234   1000
```

### Performance Analysis

```bash
# Calculate average latency
awk -F, 'NR>1 {sum+=$8; count++} END {print "Avg latency:", sum/count, "ms"}' stats.csv

# Calculate error rate
awk -F, 'NR>1 {fails+=$3; total+=$2} END {print "Error rate:", (fails/total)*100, "%"}' stats.csv

# Find slowest requests
awk -F, 'NR>1 {if($10>max) {max=$10; line=$0}} END {print "Slowest:", line}' stats.csv
```

## Troubleshooting

### High Latency

**Symptoms:**
- P95 latency > 500ms
- Increasing response times

**Solutions:**
1. Increase API workers: `API_WORKERS=8`
2. Add database connection pooling
3. Enable Redis caching
4. Optimize database queries

### High Error Rate

**Symptoms:**
- Error rate > 1%
- 500 errors in logs

**Solutions:**
1. Check database connections
2. Review error logs
3. Increase timeout settings
4. Scale resources

### Rate Limiting

**Symptoms:**
- 429 Too Many Requests
- Requests rejected

**Solutions:**
1. Increase rate limits in .env
2. Use API keys for higher limits
3. Implement client-side backoff
4. Use batch endpoints

### Memory Issues

**Symptoms:**
- OOM errors
- Container restarts

**Solutions:**
1. Increase container memory limits
2. Check for memory leaks
3. Reduce batch sizes
4. Clear caches periodically

## Best Practices

### 1. Gradual Ramp-Up

Always ramp up users gradually:

```bash
# Good: Gradual ramp
locust --users 100 --spawn-rate 5

# Bad: Instant ramp
locust --users 100 --spawn-rate 100
```

### 2. Realistic Workload

Use production-like patterns:

```python
@task(10)  # Common operation
def single_detection(self):
    pass

@task(1)  # Rare operation
def submit_feedback(self):
    pass
```

### 3. Monitor During Tests

Always monitor:
- System resources (CPU, memory, disk)
- Application metrics (latency, errors)
- Database performance (connections, queries)

### 4. Test Incrementally

Build up complexity:

1. Single endpoint
2. Multiple endpoints
3. Full workflow
4. Production-like load

### 5. Document Results

Track performance over time:

```bash
# Save results
locust --csv=results_$(date +%Y%m%d)

# Compare with baseline
diff results_baseline.csv results_$(date +%Y%m%d).csv
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Load Test

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start services
        run: docker-compose up -d
      - name: Run load test
        run: |
          pip install locust
          locust -f locustfile.py \
            --headless \
            --users 100 \
            --spawn-rate 10 \
            --run-time 5m \
            --host http://localhost:8000
```

## Resources

- [Locust Documentation](https://docs.locust.io/)
- [Load Testing Best Practices](https://docs.locust.io/en/stable/writing-a-locustfile.html)
- [Performance Testing Guide](https://martinfowler.com/articles/performance-testing.html)
