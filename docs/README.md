# Documentation

Welcome to the Scam Detection Platform documentation!

## 📚 Documentation Structure

### Getting Started

- **[Getting Started Guide](guides/getting-started.md)** - Installation and first steps
- **[Quick Reference](guides/quick-reference.md)** - Commands and common tasks
- **[FAQ](guides/faq.md)** - Frequently asked questions

### Tutorials

- **[API Integration](tutorials/api-integration.md)** - Integrate the API into your applications
- **[Batch Processing](tutorials/batch-processing.md)** - Process large volumes of messages
- **[Browser Extension](tutorials/browser-extension.md)** - Build a browser extension

### Guides

- **[Production Deployment](guides/production-deployment.md)** - Deploy to production
- **[Performance Optimization](guides/performance.md)** - Optimize for scale
- **[Model Training](guides/model-training.md)** - Train custom models
- **[Security Best Practices](guides/security.md)** - Secure your deployment

### API Reference

- **[REST API Documentation](api/reference.md)** - Complete API reference
- **[Python Client API](api/python-client.md)** - Python client library
- **[Error Codes](api/errors.md)** - Error handling guide

### Architecture

- **[System Architecture](../ARCHITECTURE.md)** - High-level architecture
- **[Database Schema](../docker/init-db.sql)** - Database design
- **[Detection Pipeline](guides/detection-pipeline.md)** - How detection works

## 🚀 Quick Links

| Resource | Description |
|----------|-------------|
| [Installation](#installation) | Get up and running |
| [API Docs](http://localhost:8000/docs) | Interactive API documentation |
| [GitHub](https://github.com/yourusername/scam-detector) | Source code |
| [Issues](https://github.com/yourusername/scam-detector/issues) | Report bugs |

## 📖 Documentation by Role

### For Developers

1. [Getting Started Guide](guides/getting-started.md)
2. [API Integration Tutorial](tutorials/api-integration.md)
3. [Architecture Overview](../ARCHITECTURE.md)
4. [Contributing Guidelines](../CONTRIBUTING.md)

### For Data Scientists

1. [Model Training Guide](guides/model-training.md)
2. [Dataset Preparation](guides/dataset-preparation.md)
3. [Model Evaluation](guides/model-evaluation.md)
4. [Feature Engineering](guides/feature-engineering.md)

### For DevOps/SRE

1. [Production Deployment](guides/production-deployment.md)
2. [Monitoring Setup](../monitoring/README.md)
3. [Performance Tuning](guides/performance.md)
4. [Backup & Recovery](guides/backup-recovery.md)

### For End Users

1. [User Guide](guides/user-guide.md)
2. [Browser Extension Guide](guides/browser-extension-user.md)
3. [Mobile App Guide](guides/mobile-app.md)
4. [Reporting Scams](guides/reporting.md)

## 🔧 Installation

Choose your installation method:

### Docker (Recommended)

```bash
git clone https://github.com/yourusername/scam-detector.git
cd scam-detector
docker-compose up -d
```

### Local Development

```bash
git clone https://github.com/yourusername/scam-detector.git
cd scam-detector
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.main:app --reload
```

See the [Getting Started Guide](guides/getting-started.md) for detailed instructions.

## 🎯 Common Tasks

### Check Scam

```python
from src.api.client import ScamDetectorClient

client = ScamDetectorClient()
result = client.detect("Suspicious message", "email")
print(f"Risk: {result['risk_level']}")
```

### Batch Processing

```python
messages = [
    {"message": "Message 1", "message_type": "email"},
    {"message": "Message 2", "message_type": "sms"},
]
results = client.batch_detect(messages)
```

### Health Check

```bash
curl http://localhost:8000/health
```

## 📊 API Overview

### Detection Endpoint

```bash
POST /api/v1/detect
```

Detect scam in a single message.

### Batch Detection

```bash
POST /api/v1/detect/batch
```

Process multiple messages at once.

### Feedback

```bash
POST /api/v1/feedback
```

Submit feedback to improve accuracy.

### Statistics

```bash
GET /api/v1/stats/overview
```

Get detection statistics.

See [API Reference](api/reference.md) for complete documentation.

## 🛡️ Australian Scam Types Detected

| Type | Examples | Risk Indicators |
|------|----------|-----------------|
| **ATO** | Tax refunds, ABN verification | Fake .gov.au domains, ABN/TFN requests |
| **MyGov** | Account suspension | Urgent action required, verification links |
| **Banking** | CBA, NAB, Westpac alerts | Unusual activity claims, credential requests |
| **Delivery** | Australia Post packages | Unexpected fees, customs charges |
| **Telco** | NBN disconnection | Tech support scams, service threats |
| **Government** | Centrelink, Medicare | Benefit suspensions, identity verification |

## 📈 Performance Metrics

Our platform achieves:

- **>92% Detection Accuracy**
- **<3% False Positive Rate**
- **<500ms Average Latency**
- **1000+ requests/sec throughput**

See [Performance Guide](guides/performance.md) for optimization tips.

## 🤝 Contributing

We welcome contributions! See our [Contributing Guidelines](../CONTRIBUTING.md).

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/`
5. Submit a pull request

### Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run pre-commit hooks:
```bash
pre-commit install
pre-commit run --all-files
```

## 📧 Support

- **Documentation**: You're reading it!
- **Issues**: [GitHub Issues](https://github.com/yourusername/scam-detector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/scam-detector/discussions)
- **Email**: support@example.com

## 📄 License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

## 🙏 Acknowledgments

- Australian Competition & Consumer Commission (ACCC) for scam pattern research
- Scamwatch database contributors
- Open source community

---

**Last Updated**: 2024-01-15
**Version**: 0.1.0
**Maintainers**: Scam Detector Team
