# Architecture Documentation

## System Overview

The AI-Powered Scam Detection Platform is a production-grade, microservices-ready application designed to detect scam messages in real-time with a focus on Australian-specific threats.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                       │
│  (Web UI, Browser Extension, Mobile App, API Clients)          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Load Balancer (Nginx)                      │
│               SSL Termination, Rate Limiting                     │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Detection   │  │   Health     │  │  Statistics  │         │
│  │   Routes     │  │   Routes     │  │   Routes     │         │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘         │
│         │                                     │                  │
│         ▼                                     ▼                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │           Scam Detection Service                 │          │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────┐ │          │
│  │  │   Text     │  │   Feature   │  │Australian│ │          │
│  │  │  Cleaner   │  │  Extractor  │  │ Patterns │ │          │
│  │  └────┬───────┘  └──────┬──────┘  └────┬─────┘ │          │
│  │       └──────────────────┴──────────────┘       │          │
│  │                    ▼                             │          │
│  │         ┌──────────────────────┐                │          │
│  │         │   Ensemble Model     │                │          │
│  │         │  (XGBoost + BERT)    │                │          │
│  │         └──────────────────────┘                │          │
│  └──────────────────────────────────────────────────┘          │
└────────────────┬────────────────┬───────────────────────────────┘
                 │                │
        ┌────────┴────────┐      └──────────┐
        ▼                 ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │  Prometheus  │
│   Database   │  │    Cache     │  │   Metrics    │
│              │  │              │  │              │
│ - Reports    │  │ - Sessions   │  │ - Counters   │
│ - Patterns   │  │ - Results    │  │ - Gauges     │
│ - Feedback   │  │ - Rate Limit │  │ - Histograms │
│ - Metrics    │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Component Details

### 1. API Layer (FastAPI)

**Purpose:** RESTful API for scam detection services

**Key Components:**
- **Routes:** Endpoint definitions for detection, health, statistics
- **Schemas:** Pydantic models for request/response validation
- **Dependencies:** Shared dependencies (DB sessions, authentication)
- **Middleware:** CORS, rate limiting, logging

**Endpoints:**
```
POST   /api/v1/detect              - Single message detection
POST   /api/v1/detect/batch        - Batch message detection
POST   /api/v1/feedback            - User feedback submission
GET    /api/v1/report/{id}         - Retrieve detection report
GET    /api/v1/stats/overview      - Comprehensive statistics
GET    /api/v1/stats/summary       - Quick metrics summary
GET    /api/v1/stats/reports/recent - Recent detection reports
GET    /health                      - Basic health check
GET    /health/detailed            - Detailed health with metrics
GET    /ready                       - Readiness probe
GET    /liveness                    - Liveness probe
```

**Performance:**
- Async/await for non-blocking I/O
- Connection pooling for database
- Request timeout: 30s default
- Rate limiting: 100 req/min per API key

### 2. Detection Engine

#### 2.1 Text Preprocessing (`src/preprocessing/`)

**TextCleaner:**
- Normalizes text (lowercase, remove special chars)
- Replaces URLs, emails, phone numbers with tokens
- Tokenization using spaCy
- Lemmatization and stopword removal
- Named entity extraction

**FeatureExtractor:**
- TF-IDF vectorization (max 5000 features, 1-3 n-grams)
- Basic text statistics (length, word count, ratios)
- Urgency keyword detection (15+ patterns)
- Australian-specific features (ATO, MyGov, banks, etc.)
- Character distribution analysis

#### 2.2 Australian Pattern Detection (`src/preprocessing/australian_patterns.py`)

**Detected Patterns:**

1. **ATO Impersonation** (Severity: 1.0)
   - Keywords: "ato", "tax office", "tax refund"
   - ABN pattern: `\d{2}\s?\d{3}\s?\d{3}\s?\d{3}`
   - TFN pattern: `\d{3}\s?\d{3}\s?\d{3}`
   - Urgency indicators

2. **MyGov Impersonation** (Severity: 0.95)
   - Keywords: "mygov", "centrelink", "medicare"
   - Account suspension tactics
   - Credential requests

3. **Banking Scams** (Severity: 0.9)
   - Banks: CBA, NAB, Westpac, ANZ
   - BSB pattern: `\d{3}[-\s]?\d{3}`
   - Account verification requests

4. **Delivery Scams** (Severity: 0.7)
   - Carriers: Australia Post, Toll, StarTrack
   - Failed delivery tactics
   - Payment requests

5. **Phone Scams** (Severity: 0.65)
   - NBN, Telstra, tech support
   - Refund offers
   - Virus warnings

6. **Suspicious URLs** (Severity: 0.8)
   - Fake .gov.au domains
   - Suspicious TLDs (.tk, .ml, .ga)
   - Shortened URLs (bit.ly, tinyurl)
   - IP-based URLs

**Detection Algorithm:**
```python
for pattern_detector in detectors:
    if matches_keywords:
        score += keyword_weight
    if matches_urgency:
        score += urgency_weight
    if matches_specific_pattern:
        score += pattern_weight

    if score >= threshold:
        return PatternMatch(
            pattern_name,
            confidence=score,
            severity=pattern_severity
        )
```

#### 2.3 ML Models (`src/models/`)

**Ensemble Architecture:**

```
Input Text
    │
    ├─────────────────┬─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
Metadata         TF-IDF           BERT
Features         Features       Embeddings
    │                 │                 │
    ▼                 ▼                 ▼
XGBoost          XGBoost           BERT
Classifier       Classifier      Classifier
    │                 │                 │
    └─────────┬───────┴─────────────────┘
              ▼
      Weighted Voting
       (0.4 + 0.6)
              │
              ▼
      Final Prediction
```

**XGBoost Model:**
- Features: Metadata + extracted features
- Parameters: max_depth=6, n_estimators=100
- Training: 80/20 train/test split
- Handles structured features well

**BERT Model:**
- Base: bert-base-uncased
- Fine-tuning: Australian scam corpus
- Max sequence length: 512 tokens
- Captures semantic meaning

**Ensemble Voting:**
- XGBoost weight: 0.4
- BERT weight: 0.6
- Combines probabilities via weighted average
- Confidence calculated from decision boundary distance

### 3. Data Layer

#### 3.1 Database Schema (PostgreSQL)

**Tables:**

```sql
-- Detection reports
scam_reports (
    id UUID PRIMARY KEY,
    message TEXT,
    message_type VARCHAR(50),
    scam_probability DECIMAL(5,4),
    risk_level VARCHAR(20),
    confidence DECIMAL(5,4),
    detected_patterns JSONB,
    metadata JSONB,
    recommendations JSONB,
    processing_time_ms INTEGER,
    australian_specific BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Configurable patterns
detection_patterns (
    id SERIAL PRIMARY KEY,
    pattern_name VARCHAR(100) UNIQUE,
    pattern_type VARCHAR(50),
    pattern_regex TEXT,
    weight DECIMAL(3,2),
    is_active BOOLEAN,
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- User feedback for improvement
feedback_loop (
    id UUID PRIMARY KEY,
    report_id UUID REFERENCES scam_reports(id),
    user_feedback VARCHAR(20),
    corrected_label VARCHAR(20),
    feedback_text TEXT,
    created_at TIMESTAMP
)

-- Performance metrics
performance_metrics (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    total_requests INTEGER,
    scam_detected INTEGER,
    legitimate_detected INTEGER,
    avg_processing_time_ms DECIMAL(10,2),
    p95_processing_time_ms INTEGER,
    p99_processing_time_ms INTEGER,
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    false_positive_rate DECIMAL(5,4),
    created_at TIMESTAMP
)

-- API authentication
api_keys (
    id UUID PRIMARY KEY,
    key_hash VARCHAR(255) UNIQUE,
    name VARCHAR(100),
    is_active BOOLEAN,
    rate_limit INTEGER,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP
)
```

**Indexes:**
- `idx_scam_reports_created_at` on `scam_reports(created_at)`
- `idx_scam_reports_risk_level` on `scam_reports(risk_level)`
- `idx_scam_reports_message_type` on `scam_reports(message_type)`
- `idx_feedback_loop_report_id` on `feedback_loop(report_id)`
- `idx_api_keys_key_hash` on `api_keys(key_hash)`

#### 3.2 Repository Pattern

**Design:**
- Abstraction layer over database operations
- Encapsulates query logic
- Facilitates testing with mocks
- Type-safe with SQLAlchemy models

**Repositories:**
- `ScamReportRepository`: CRUD + statistics
- `FeedbackRepository`: Feedback management
- `DetectionPatternRepository`: Pattern configuration
- `PerformanceMetricRepository`: Metrics tracking

### 4. Caching Strategy (Redis)

**Purpose:**
- Reduce database load
- Improve response time
- Session management
- Rate limiting

**Cache Keys:**
```
detection:{message_hash}        - Cached detection results (24h TTL)
session:{session_id}            - User sessions (1h TTL)
rate_limit:{api_key}:{minute}   - Rate limit counters (1min TTL)
model:{model_version}           - Model metadata (permanent)
```

**Cache Invalidation:**
- Time-based expiration (TTL)
- Event-based invalidation on feedback
- LRU eviction policy

### 5. Monitoring & Observability

#### 5.1 Logging (Loguru)

**Log Levels:**
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages for recoverable errors
- ERROR: Error messages for failures
- CRITICAL: Critical errors requiring immediate attention

**Log Destinations:**
- Console: Colored output for development
- File: Rotated logs (10MB rotation, 30-day retention)
- Format: JSON for production, human-readable for dev

#### 5.2 Metrics (Prometheus)

**Metric Types:**

```python
# Counters
detection_requests_total{status, risk_level}
detection_errors_total{error_type}
api_requests_total{endpoint, method, status_code}

# Gauges
active_connections
database_pool_size
cache_hit_ratio

# Histograms
detection_latency_seconds{quantile}
api_response_time_seconds{endpoint}
model_inference_time_seconds{model}
```

**Dashboards:**
- Request rate and latency
- Error rates by endpoint
- Detection accuracy over time
- Resource utilization (CPU, memory)

#### 5.3 Health Checks

**Endpoints:**
- `/health`: Basic liveness check
- `/health/detailed`: Comprehensive health with metrics
- `/ready`: Readiness probe (checks dependencies)
- `/liveness`: Simple alive check for K8s

**Health Criteria:**
- Database connectivity
- Redis connectivity
- Model loading status
- Memory usage < 80%
- CPU usage < 90%

## Security

### Authentication
- API key authentication via `X-API-Key` header
- Hashed storage in database (bcrypt)
- Rate limiting per API key
- Expiration dates for keys

### Input Validation
- Pydantic schemas for all inputs
- SQL injection prevention (parameterized queries)
- XSS prevention (sanitized outputs)
- File upload restrictions

### Data Privacy
- No PII storage without consent
- Encrypted database connections (SSL)
- Secure password hashing (bcrypt)
- GDPR-compliant data retention

## Scalability

### Horizontal Scaling
- Stateless API design
- Session storage in Redis
- Load balancing with Nginx
- Database connection pooling

### Performance Optimizations
- Async I/O with FastAPI
- Batch processing support
- Model quantization for faster inference
- Result caching

### Resource Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 10GB
- Database: PostgreSQL 13+

**Recommended:**
- CPU: 4+ cores
- RAM: 16GB
- Storage: 50GB SSD
- Database: PostgreSQL 15+
- Redis: 2GB memory

## Deployment

### Docker Compose (Development)
```yaml
services:
  - api: FastAPI application
  - postgres: Database
  - redis: Cache
  - notebook: Jupyter for development
```

### Production (Kubernetes)
```yaml
Deployments:
  - api: 3+ replicas with HPA
  - postgres: StatefulSet with persistence
  - redis: StatefulSet with AOF persistence
  - nginx: Ingress controller

Scaling:
  - HPA based on CPU (target: 70%)
  - HPA based on memory (target: 80%)
  - HPA based on custom metrics (request latency)
```

## CI/CD Pipeline

### Stages:
1. **Lint:** Black, isort, flake8, mypy
2. **Test:** pytest with coverage
3. **Build:** Docker image
4. **Integration Test:** Full stack testing
5. **Security Scan:** safety, bandit
6. **Deploy:** Automated deployment on success

### Quality Gates:
- Test coverage > 80%
- No critical security issues
- All linters passing
- Docker build successful

## Future Enhancements

1. **ML Improvements:**
   - Active learning from feedback
   - Model retraining pipeline
   - A/B testing framework
   - Multi-language support

2. **Features:**
   - Browser extension
   - Mobile apps (React Native)
   - Email plugin (Gmail, Outlook)
   - Slack/Teams integration

3. **Infrastructure:**
   - Kubernetes deployment
   - Multi-region setup
   - CDN for static assets
   - Elasticsearch for log aggregation

4. **Analytics:**
   - Real-time dashboard
   - Trend analysis
   - Anomaly detection
   - Custom reporting
