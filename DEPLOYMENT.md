# 🚀 Deployment Guide

## Local Development

### Using Virtual Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add OPENAI_API_KEY if available

# Run server
python -m uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000
API docs: http://localhost:8000/docs

### Using Docker Compose

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop
docker-compose down
```

## Production Deployment

### Environment Variables

Set these in production:

```bash
OPENAI_API_KEY=sk-...
CORS_ORIGINS=https://yourdomain.com
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
```

### Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Deploy
railway up
```

Set `OPENAI_API_KEY` in Railway dashboard.

### Heroku Deployment

```bash
# Install Heroku CLI
brew install heroku

# Login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set OPENAI_API_KEY=sk-...

# Deploy
git push heroku main
```

### AWS Lambda + API Gateway

Create `lambda_handler.py`:

```python
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

Install: `pip install mangum`

Deploy using Zappa or AWS SAM.

### Docker Container

```bash
# Build image
docker build -t onboarding-engine .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  onboarding-engine

# Push to registry
docker tag onboarding-engine yourregistry/onboarding-engine:latest
docker push yourregistry/onboarding-engine:latest
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: onboarding-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: onboarding-engine
  template:
    metadata:
      labels:
        app: onboarding-engine
    spec:
      containers:
      - name: api
        image: your-registry/onboarding-engine:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: onboarding-engine-service
spec:
  selector:
    app: onboarding-engine
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f deployment.yaml
```

## Performance Optimization

### 1. Caching Layers

Add Redis for embedding cache:

```python
# services/cache.py
import redis
from functools import wraps

cache = redis.Redis(host='localhost', port=6379)

def cache_embeddings(ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(text, *args, **kwargs):
            key = f"embedding:{hash(text)}"
            result = cache.get(key)
            if result:
                return json.loads(result)
            result = func(text, *args, **kwargs)
            cache.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### 2. Async Database Queries

Add PostgreSQL for persistence:

```python
# services/database.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:password@host/db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)
```

### 3. Load Balancing

```bash
# Use Nginx as reverse proxy
upstream api {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://api;
    }
}
```

### 4. CDN for Static Assets

Serve skill_graph.json and course_catalog.json via CloudFront or Cloudflare.

## Monitoring & Logging

### Sentry Error Tracking

```bash
pip install sentry-sdk
```

```python
# app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="https://<key>@sentry.io/<project>",
    traces_sample_rate=1.0
)
```

### Structured Logging

```python
# app/logging_config.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
        }
        return json.dumps(log_data)
```

### Health Checks

```bash
# Simple health check
curl http://localhost:8000/api/health

# In K8s:
# livenessProbe and readinessProbe configured above
```

## Scaling Strategy

### Vertical Scaling
- Increase memory to cache more embeddings
- Increase CPU for parallel requests

### Horizontal Scaling
- Run 3-5 instances behind load balancer
- Share Redis cache across instances
- Use managed OpenAI API (scales automatically)

### Auto-Scaling

```yaml
# K8s HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: onboarding-engine-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: onboarding-engine
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Backup & Disaster Recovery

1. **Version Control**: Keep skill_graph.json and course_catalog.json in git
2. **Database Backups**: If using PostgreSQL, enable automated backups
3. **Config Backups**: Version all environment configurations
4. **Disaster Recovery Plan**:
   - RTO (Recovery Time Objective): < 1 hour
   - RPO (Recovery Point Objective): < 30 minutes

## Security Checklist

- [ ] HTTPS enabled in production
- [ ] API key rotation enabled
- [ ] CORS origins restricted
- [ ] Rate limiting configured
- [ ] Input validation (Pydantic)
- [ ] Error messages sanitized (no stack traces)
- [ ] Dependencies updated regularly
- [ ] Security headers configured
- [ ] DDoS protection enabled (CloudFlare)
- [ ] Access logs monitored

## Testing in Production

### Synthetic Monitoring

```python
# tests/synthetic.py
import requests
import schedule
import time

def health_check():
    response = requests.get("https://api.yourdomain.com/api/health")
    assert response.status_code == 200

def roadmap_test():
    response = requests.post(
        "https://api.yourdomain.com/api/generate-roadmap",
        json={...}
    )
    assert response.status_code == 200

schedule.every(5).minutes.do(health_check)
schedule.every(10).minutes.do(roadmap_test)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### Load Testing

```bash
# Using k6
npm install -g k6

# Create load test
cat > load_test.js << 'EOF'
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 0 },
  ],
};

export default function () {
  let res = http.post('http://localhost:8000/api/generate-roadmap', {
    resume_text: 'Python, JavaScript, SQL',
    jd_text: 'React, Node.js, PostgreSQL, Docker',
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 5s': (r) => r.timings.duration < 5000,
  });
}
EOF

# Run test
k6 run load_test.js
```

## Rollback Plan

If deployment fails:

```bash
# Using Docker
docker stop onboarding-engine
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  onboarding-engine:previous-tag

# Using Kubernetes
kubectl rollout undo deployment/onboarding-engine

# Using Heroku
heroku releases
heroku rollback v42

# Using Railway
# Redeploy from previous commit
```

---

For questions or issues, check `/docs` endpoint or open an issue on GitHub.
