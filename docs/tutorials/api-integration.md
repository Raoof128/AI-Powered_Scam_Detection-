# API Integration Tutorial

Learn how to integrate the Scam Detection API into your applications.

## Table of Contents

- [Authentication](#authentication)
- [Python Integration](#python-integration)
- [JavaScript Integration](#javascript-integration)
- [REST API](#rest-api)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Authentication

### API Key Setup

For production use, obtain an API key:

```bash
# Generate API key (requires admin access)
docker-compose exec api python -c "
from src.database.models import APIKey
from src.database.connection import SessionLocal
import secrets

db = SessionLocal()
api_key = APIKey(
    name='My Application',
    key=secrets.token_urlsafe(32),
    is_active=True
)
db.add(api_key)
db.commit()
print(f'API Key: {api_key.key}')
"
```

### Using API Keys

Include the API key in request headers:

```bash
curl -X POST "http://localhost:8000/api/v1/detect" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test", "message_type": "email"}'
```

## Python Integration

### Installation

```bash
pip install requests
# Or use the built-in client
from src.api.client import ScamDetectorClient
```

### Basic Usage

```python
from src.api.client import ScamDetectorClient

# Initialize client
client = ScamDetectorClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"  # Optional
)

# Single detection
result = client.detect(
    message="URGENT: Click here to claim your tax refund",
    message_type="email"
)

print(f"Risk: {result['risk_level']}")
print(f"Confidence: {result['confidence_score']:.2%}")
```

### Batch Processing

```python
messages = [
    {"message": "Message 1", "message_type": "email"},
    {"message": "Message 2", "message_type": "sms"},
    {"message": "Message 3", "message_type": "email"},
]

results = client.batch_detect(messages)

for i, result in enumerate(results['results']):
    print(f"Message {i+1}: {result['risk_level']}")
```

### Async Usage

```python
import asyncio
import aiohttp

async def detect_async(message: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/api/v1/detect",
            json={
                "message": message,
                "message_type": "email"
            }
        ) as response:
            return await response.json()

# Use in async function
result = await detect_async("Test message")
```

### Context Manager

```python
with ScamDetectorClient() as client:
    result = client.detect("Test message", "email")
    # Client automatically closes connection
```

### Error Handling

```python
from src.api.client import ScamDetectorClient
import requests

client = ScamDetectorClient()

try:
    result = client.detect("Test", "email")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        print("Rate limit exceeded")
    elif e.response.status_code == 500:
        print("Server error")
    else:
        print(f"HTTP error: {e}")
except requests.exceptions.ConnectionError:
    print("Connection failed")
except requests.exceptions.Timeout:
    print("Request timed out")
```

## JavaScript Integration

### Node.js

```javascript
const axios = require('axios');

class ScamDetectorClient {
    constructor(baseURL = 'http://localhost:8000', apiKey = null) {
        this.client = axios.create({
            baseURL: baseURL,
            headers: apiKey ? {'X-API-Key': apiKey} : {},
            timeout: 10000
        });
    }

    async detect(message, messageType) {
        try {
            const response = await this.client.post('/api/v1/detect', {
                message: message,
                message_type: messageType
            });
            return response.data;
        } catch (error) {
            console.error('Detection error:', error.message);
            throw error;
        }
    }

    async batchDetect(messages) {
        const response = await this.client.post('/api/v1/detect/batch', {
            messages: messages
        });
        return response.data;
    }
}

// Usage
const client = new ScamDetectorClient();

(async () => {
    const result = await client.detect(
        'URGENT: Your account has been suspended',
        'email'
    );
    console.log('Risk Level:', result.risk_level);
    console.log('Confidence:', result.confidence_score);
})();
```

### Browser (Fetch API)

```javascript
class ScamDetector {
    constructor(apiUrl = 'http://localhost:8000') {
        this.apiUrl = apiUrl;
        this.apiKey = null;
    }

    setApiKey(key) {
        this.apiKey = key;
    }

    async detect(message, messageType = 'email') {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }

        const response = await fetch(`${this.apiUrl}/api/v1/detect`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                message: message,
                message_type: messageType
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }
}

// Usage
const detector = new ScamDetector();

detector.detect('Test message', 'email')
    .then(result => {
        console.log('Risk:', result.risk_level);
        if (result.risk_level === 'HIGH' || result.risk_level === 'CRITICAL') {
            alert('Warning: This message appears to be a scam!');
        }
    })
    .catch(error => console.error('Error:', error));
```

### React Integration

```jsx
import React, { useState } from 'react';
import axios from 'axios';

function ScamChecker() {
    const [message, setMessage] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const checkMessage = async () => {
        setLoading(true);
        try {
            const response = await axios.post('http://localhost:8000/api/v1/detect', {
                message: message,
                message_type: 'email'
            });
            setResult(response.data);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Paste suspicious message here..."
                rows={5}
                style={{width: '100%'}}
            />
            <button onClick={checkMessage} disabled={loading}>
                {loading ? 'Checking...' : 'Check for Scams'}
            </button>

            {result && (
                <div>
                    <h3>Results:</h3>
                    <p>Risk Level: <strong>{result.risk_level}</strong></p>
                    <p>Confidence: {(result.confidence_score * 100).toFixed(1)}%</p>

                    {result.detected_patterns.length > 0 && (
                        <div>
                            <h4>Detected Patterns:</h4>
                            <ul>
                                {result.detected_patterns.map((pattern, i) => (
                                    <li key={i}>{pattern}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {result.recommendations && (
                        <div>
                            <h4>Recommendations:</h4>
                            <ul>
                                {result.recommendations.map((rec, i) => (
                                    <li key={i}>{rec}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default ScamChecker;
```

## REST API

### Endpoints

#### POST /api/v1/detect

Detect scam in a single message.

**Request:**
```json
{
  "message": "string",
  "message_type": "email|sms|url|phone",
  "metadata": {
    "sender": "optional",
    "subject": "optional"
  }
}
```

**Response:**
```json
{
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "confidence_score": 0.95,
  "detected_patterns": ["pattern1", "pattern2"],
  "recommendations": ["action1", "action2"],
  "metadata": {
    "processing_time_ms": 145
  }
}
```

#### POST /api/v1/detect/batch

Batch detection for multiple messages.

**Request:**
```json
{
  "messages": [
    {"message": "string1", "message_type": "email"},
    {"message": "string2", "message_type": "sms"}
  ]
}
```

**Response:**
```json
{
  "results": [...],
  "summary": {
    "total_processed": 2,
    "high_risk_count": 1,
    "processing_time_ms": 290
  }
}
```

#### POST /api/v1/feedback

Submit feedback on detection accuracy.

**Request:**
```json
{
  "message": "original message",
  "actual_label": "scam|legitimate",
  "predicted_label": "predicted label",
  "feedback_text": "optional comments"
}
```

#### GET /api/v1/stats/overview

Get detection statistics.

**Response:**
```json
{
  "total_detections": 10000,
  "scam_detections": 3500,
  "legitimate_detections": 6500,
  "average_confidence": 0.89,
  "today_stats": {...}
}
```

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process result |
| 400 | Bad Request | Fix request format |
| 401 | Unauthorized | Check API key |
| 422 | Validation Error | Fix input data |
| 429 | Rate Limit | Retry after delay |
| 500 | Server Error | Retry or contact support |

### Python Error Handling

```python
import time
from requests.exceptions import HTTPError

def detect_with_retry(client, message, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.detect(message, "email")
        except HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited - exponential backoff
                wait_time = 2 ** attempt
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            elif e.response.status_code >= 500:
                # Server error - retry
                print(f"Server error. Attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2)
            else:
                # Client error - don't retry
                raise

    raise Exception("Max retries exceeded")
```

### JavaScript Error Handling

```javascript
async function detectWithRetry(message, maxRetries = 3) {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return await detector.detect(message, 'email');
        } catch (error) {
            if (error.response?.status === 429) {
                const waitTime = Math.pow(2, attempt) * 1000;
                console.log(`Rate limited. Waiting ${waitTime}ms...`);
                await new Promise(resolve => setTimeout(resolve, waitTime));
            } else if (error.response?.status >= 500) {
                console.log(`Server error. Attempt ${attempt + 1}/${maxRetries}`);
                if (attempt < maxRetries - 1) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            } else {
                throw error;
            }
        }
    }
    throw new Error('Max retries exceeded');
}
```

## Best Practices

### 1. Use Batch Processing

Process multiple messages in a single request:

```python
# Bad: Individual requests
for message in messages:
    result = client.detect(message, "email")

# Good: Batch request
batch = [{"message": m, "message_type": "email"} for m in messages]
results = client.batch_detect(batch)
```

### 2. Implement Caching

Cache results for duplicate messages:

```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=1000)
def detect_cached(message_hash: str):
    # Actual detection happens only for unique messages
    return client.detect(message, "email")

# Usage
message_hash = hashlib.sha256(message.encode()).hexdigest()
result = detect_cached(message_hash)
```

### 3. Handle Rate Limits

Implement exponential backoff:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def detect_with_backoff(message):
    return client.detect(message, "email")
```

### 4. Use Async for High Throughput

```python
import asyncio

async def process_messages(messages):
    tasks = [detect_async(msg) for msg in messages]
    return await asyncio.gather(*tasks)

# Process 100 messages concurrently
results = asyncio.run(process_messages(messages))
```

### 5. Monitor Performance

Track API performance:

```python
import time

start = time.time()
result = client.detect(message, "email")
elapsed = (time.time() - start) * 1000

if elapsed > 500:
    print(f"Warning: Slow response ({elapsed}ms)")
```

### 6. Validate Input

Always validate before sending:

```python
def validate_message(message, message_type):
    if not message or len(message.strip()) == 0:
        raise ValueError("Message cannot be empty")

    if message_type not in ["email", "sms", "url", "phone"]:
        raise ValueError("Invalid message type")

    if len(message) > 10000:
        raise ValueError("Message too long (max 10000 chars)")
```

---

**Next Steps:**
- [Batch Processing Guide](./batch-processing.md)
- [Browser Extension Tutorial](./browser-extension.md)
- [Performance Optimization](../guides/performance.md)
