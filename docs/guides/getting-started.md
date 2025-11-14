# Getting Started Guide

Welcome to the AI-Powered Scam Detection Platform! This guide will help you get up and running quickly.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Your First Detection](#your-first-detection)
- [Understanding Results](#understanding-results)
- [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Python** (3.11+) for local development
- **Git** for cloning the repository
- **8GB RAM** minimum (16GB recommended)
- **10GB free disk space**

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 8GB | 16GB |
| Disk | 10GB | 50GB (with data storage) |
| OS | Linux, macOS, Windows (WSL2) | Linux |

## Installation

### Option 1: Docker (Recommended)

**Step 1: Clone the repository**

```bash
git clone https://github.com/yourusername/scam-detector.git
cd scam-detector
```

**Step 2: Configure environment**

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration (optional)
nano .env
```

**Step 3: Start the services**

```bash
# Start all services (API, database, Redis, Jupyter)
docker-compose up -d

# Check status
docker-compose ps
```

**Step 4: Verify installation**

```bash
# Check API health
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","version":"0.1.0","environment":"development"}
```

### Option 2: Local Development

**Step 1: Clone and setup virtual environment**

```bash
git clone https://github.com/yourusername/scam-detector.git
cd scam-detector

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Step 2: Setup database**

```bash
# Start PostgreSQL with Docker
docker-compose up -d postgres

# Run migrations
alembic upgrade head
```

**Step 3: Download ML models**

```bash
# Download spaCy model
python -m spacy download en_core_web_sm
```

**Step 4: Start the API**

```bash
# Development mode with hot reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Quick Start

### Access the API Documentation

Once the services are running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Basic API Usage

**Example 1: Detect scam in a single message**

```bash
curl -X POST "http://localhost:8000/api/v1/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "URGENT: Your ATO tax refund of $2,450 is ready. Click here to claim.",
    "message_type": "email"
  }'
```

**Example 2: Using Python client**

```python
from src.api.client import ScamDetectorClient

# Initialize client
client = ScamDetectorClient(base_url="http://localhost:8000")

# Detect scam
result = client.detect(
    message="URGENT: Your ATO tax refund of $2,450 is ready.",
    message_type="email"
)

print(f"Risk Level: {result['risk_level']}")
print(f"Confidence: {result['confidence_score']:.2%}")
print(f"Patterns: {', '.join(result['detected_patterns'])}")
```

## Your First Detection

Let's walk through a complete detection workflow:

### Step 1: Prepare Your Message

```python
suspicious_message = """
Dear Customer,

Your MyGov account has been temporarily suspended due to unusual activity.

To restore access, please verify your identity immediately:
https://mygov-verify.net/restore

If you don't verify within 24 hours, your account will be permanently deleted.

MyGov Security Team
"""
```

### Step 2: Send Detection Request

```python
result = client.detect(
    message=suspicious_message,
    message_type="email"
)
```

### Step 3: Analyze Results

```python
# Risk level assessment
if result['risk_level'] == 'CRITICAL':
    print("⚠️ HIGH RISK SCAM DETECTED!")
elif result['risk_level'] == 'HIGH':
    print("⚠️ Likely scam - proceed with caution")
elif result['risk_level'] == 'MEDIUM':
    print("⚠️ Suspicious - verify sender")
else:
    print("✓ Appears legitimate")

# Detected patterns
for pattern in result['detected_patterns']:
    print(f"  - {pattern}")

# Recommendations
for rec in result.get('recommendations', []):
    print(f"  ✓ {rec}")
```

## Understanding Results

### Risk Levels

| Level | Description | Action |
|-------|-------------|--------|
| **CRITICAL** | Confirmed scam with high confidence | Block immediately, report |
| **HIGH** | Very likely scam | Block, warn user |
| **MEDIUM** | Suspicious indicators present | Flag for review |
| **LOW** | Appears legitimate | Allow with logging |

### Confidence Scores

- **> 0.90**: Very high confidence
- **0.70 - 0.90**: High confidence
- **0.50 - 0.70**: Medium confidence
- **< 0.50**: Low confidence

### Australian-Specific Patterns

The system detects these Australian scam types:

1. **ATO Scams**: Fake tax refunds, ABN/TFN requests
2. **MyGov Scams**: Account suspension threats
3. **Banking**: CBA, NAB, Westpac, ANZ impersonation
4. **Delivery**: Australia Post package scams
5. **Telco**: NBN, Telstra tech support scams
6. **Government**: Centrelink, Medicare fraud

### Response Fields

```json
{
  "risk_level": "HIGH",
  "confidence_score": 0.87,
  "detected_patterns": [
    "mygov_impersonation",
    "account_suspension_threat",
    "suspicious_url",
    "urgency_tactics"
  ],
  "recommendations": [
    "Do not click any links in this message",
    "Verify sender through official MyGov website",
    "Report to ACCC Scamwatch"
  ],
  "metadata": {
    "processing_time_ms": 234,
    "model_version": "0.1.0",
    "australian_patterns_detected": 2
  }
}
```

## Next Steps

Now that you're up and running, explore these topics:

### Tutorials

- [API Integration Tutorial](../tutorials/api-integration.md)
- [Batch Processing Guide](../tutorials/batch-processing.md)
- [Building a Browser Extension](../tutorials/browser-extension.md)

### Advanced Topics

- [Model Training Guide](../guides/model-training.md)
- [Performance Optimization](../guides/performance.md)
- [Production Deployment](../guides/production-deployment.md)

### Development

- [Contributing Guidelines](../../CONTRIBUTING.md)
- [Architecture Overview](../../ARCHITECTURE.md)
- [API Reference](../api/reference.md)

## Common Issues

### Docker Issues

**Error: Port already in use**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
```

**Error: Permission denied**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Database Issues

**Error: Connection refused**
```bash
# Check database status
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### API Issues

**Error: 500 Internal Server Error**
```bash
# Check API logs
docker-compose logs api

# Restart API
docker-compose restart api
```

## Getting Help

- **Documentation**: Check the [docs](../) folder
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/scam-detector/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/yourusername/scam-detector/discussions)
- **Email**: Contact support@example.com

## Quick Reference

### Essential Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f api

# Run tests
docker-compose run --rm api pytest

# Access database
docker-compose exec postgres psql -U scam_detector

# Backup database
./scripts/backup.sh

# Health check
./scripts/health_check.sh
```

### Environment Variables

Key configuration options in `.env`:

```bash
# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/scam_detector

# Logging
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

---

**Congratulations!** 🎉 You're now ready to use the Scam Detection Platform. Continue to the [API Integration Tutorial](../tutorials/api-integration.md) to learn more.
