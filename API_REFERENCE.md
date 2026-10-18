# 📚 API Reference

## Base URL

```
http://localhost:8000
https://your-api-domain.com
```

## Authentication

Currently, no authentication required. For production, add:

```bash
Authorization: Bearer <your-api-key>
```

## Content Type

All requests use `application/json`:

```bash
Content-Type: application/json
```

---

## Endpoints

### 1. Generate Learning Roadmap

**Endpoint:** `POST /api/generate-roadmap`

Generate a personalized learning roadmap based on resume and job description.

#### Request

```json
{
  "resume_text": "string (min: 50 chars)",
  "jd_text": "string (min: 50 chars)"
}
```

#### Request Example

```bash
curl -X POST "http://localhost:8000/api/generate-roadmap" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Senior Python Developer with 5 years experience. Expert in Django, Flask, PostgreSQL, and Redis. Familiar with Docker, Kubernetes, and AWS EC2. Strong in REST APIs, system design, and microservices architecture.",
    "jd_text": "Full Stack Engineer - Required: React, Node.js, PostgreSQL, Docker, Kubernetes, System Design, AWS. Preferred: TypeScript, GraphQL, CI/CD pipelines, Microservices. 3+ years experience required."
  }'
```

#### Response

```json
{
  "extracted_skills": {
    "Python": 0.8,
    "Django": 0.85,
    "Flask": 0.75,
    "PostgreSQL": 0.7,
    "Redis": 0.65,
    "Docker": 0.6,
    "Kubernetes": 0.5,
    "AWS": 0.6,
    "System Design": 0.7,
    "REST APIs": 0.8
  },
  "jd_skills": {
    "React": 0.9,
    "Node.js": 0.85,
    "PostgreSQL": 0.8,
    "Docker": 0.8,
    "Kubernetes": 0.75,
    "System Design": 0.7,
    "AWS": 0.7,
    "TypeScript": 0.65,
    "GraphQL": 0.6,
    "CI/CD": 0.6
  },
  "gap_analysis": {
    "known_skills": ["PostgreSQL", "Docker", "System Design", "AWS"],
    "partial_skills": ["Node.js", "Kubernetes"],
    "missing_skills": ["React", "TypeScript", "GraphQL", "CI/CD"],
    "total_required_skills": 10
  },
  "roadmap": [
    {
      "module_name": "JavaScript Essentials",
      "duration_weeks": 4,
      "reason": "Missing skill - required for role",
      "skill_covered": "JavaScript",
      "prerequisites": [],
      "order": 1
    },
    {
      "module_name": "TypeScript Advanced",
      "duration_weeks": 3,
      "reason": "Missing skill - required for role",
      "skill_covered": "TypeScript",
      "prerequisites": ["JavaScript"],
      "order": 2
    },
    {
      "module_name": "React Development",
      "duration_weeks": 6,
      "reason": "Missing skill - required for role",
      "skill_covered": "React",
      "prerequisites": ["JavaScript"],
      "order": 3
    },
    {
      "module_name": "Node.js Backend Development",
      "duration_weeks": 5,
      "reason": "Partial knowledge - strengthen capability",
      "skill_covered": "Node.js",
      "prerequisites": ["JavaScript"],
      "order": 4
    },
    {
      "module_name": "GraphQL API Development",
      "duration_weeks": 4,
      "reason": "Missing skill - required for role",
      "skill_covered": "GraphQL",
      "prerequisites": ["JavaScript"],
      "order": 5
    },
    {
      "module_name": "CI/CD Pipelines",
      "duration_weeks": 3,
      "reason": "Missing skill - required for role",
      "skill_covered": "CI/CD",
      "prerequisites": ["Git"],
      "order": 6
    },
    {
      "module_name": "Kubernetes Orchestration",
      "duration_weeks": 4,
      "reason": "Partial knowledge - strengthen capability",
      "skill_covered": "Kubernetes",
      "prerequisites": ["Docker"],
      "order": 7
    }
  ],
  "readiness_score": 0.4,
  "total_weeks_required": 29
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| extracted_skills | object | Skills found in resume with proficiency (0-1) |
| jd_skills | object | Skills required in JD with importance level |
| gap_analysis | object | Categorized skill gaps |
| gap_analysis.known_skills | array | Skills already mastered |
| gap_analysis.partial_skills | array | Skills with partial knowledge |
| gap_analysis.missing_skills | array | Skills completely missing |
| gap_analysis.total_required_skills | number | Total skills needed for role |
| roadmap | array | Ordered learning modules |
| roadmap[].module_name | string | Name of learning course |
| roadmap[].duration_weeks | number | Weeks to complete module |
| roadmap[].reason | string | Why this module is needed |
| roadmap[].skill_covered | string | Primary skill this teaches |
| roadmap[].prerequisites | array | Required modules before this |
| roadmap[].order | number | Sequence in learning path (1-indexed) |
| readiness_score | number | Current readiness 0.0-1.0 |
| total_weeks_required | number | Total weeks to complete all modules |

#### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success - roadmap generated |
| 422 | Validation error - input too short or invalid |
| 500 | Server error - processing failed |

#### Error Response

```json
{
  "detail": "Failed to generate roadmap: OpenAI API error"
}
```

---

### 2. Health Check

**Endpoint:** `GET /api/health`

Simple health check endpoint for monitoring.

#### Response

```json
{
  "status": "healthy",
  "service": "onboarding-engine"
}
```

#### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Service is healthy |

---

### 3. Root Endpoint

**Endpoint:** `GET /`

Returns API metadata and available endpoints.

#### Response

```json
{
  "service": "AI-Adaptive Onboarding Engine",
  "version": "1.0.0",
  "endpoints": {
    "POST /api/generate-roadmap": "Generate learning roadmap",
    "GET /api/health": "Health check",
    "GET /docs": "Interactive API documentation"
  }
}
```

---

## Language Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

def generate_roadmap(resume_text: str, jd_text: str):
    response = requests.post(
        f"{BASE_URL}/api/generate-roadmap",
        json={
            "resume_text": resume_text,
            "jd_text": jd_text
        }
    )
    return response.json()

# Usage
roadmap = generate_roadmap(
    resume_text="Python, Django, PostgreSQL",
    jd_text="React, Node.js, Docker, Kubernetes"
)

print(f"Readiness: {roadmap['readiness_score']:.0%}")
print(f"Learning path: {roadmap['total_weeks_required']} weeks")

for module in roadmap['roadmap']:
    print(f"  {module['order']}. {module['module_name']} ({module['duration_weeks']}w)")
```

### JavaScript/TypeScript

```typescript
const BASE_URL = "http://localhost:8000";

async function generateRoadmap(
  resumeText: string,
  jdText: string
): Promise<RoadmapResponse> {
  const response = await fetch(`${BASE_URL}/api/generate-roadmap`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_text: resumeText,
      jd_text: jdText,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

// Usage
const roadmap = await generateRoadmap(
  "Python, Django, PostgreSQL",
  "React, Node.js, Docker, Kubernetes"
);

console.log(`Readiness: ${Math.round(roadmap.readiness_score * 100)}%`);
console.log(`Total weeks: ${roadmap.total_weeks_required}`);

roadmap.roadmap.forEach((module) => {
  console.log(
    `${module.order}. ${module.module_name} (${module.duration_weeks}w)`
  );
});
```

### cURL

```bash
# Basic roadmap generation
curl -X POST "http://localhost:8000/api/generate-roadmap" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "5 years Python, Django, PostgreSQL experience",
    "jd_text": "Senior Full Stack: React, Node.js, TypeScript, Kubernetes"
  }' \
  | jq .

# Pretty print
curl -X POST "http://localhost:8000/api/generate-roadmap" \
  -H "Content-Type: application/json" \
  -d @request.json \
  | jq '.roadmap[] | {module: .module_name, weeks: .duration_weeks}'
```

### Postman

1. Create new request
2. Method: `POST`
3. URL: `http://localhost:8000/api/generate-roadmap`
4. Headers: `Content-Type: application/json`
5. Body (raw JSON):
```json
{
  "resume_text": "Your resume text here...",
  "jd_text": "Job description text here..."
}
```

---

## SDK Clients

### Python SDK (unofficial example)

```python
from onboarding_engine import Client

client = Client(api_url="http://localhost:8000")

roadmap = client.generate_roadmap(
    resume="Python, Django, PostgreSQL...",
    job_description="React, Node.js, Docker..."
)

print(roadmap.readiness_score)  # 0.4
for module in roadmap.modules:
    print(module.name, module.duration_weeks)
```

### Generate OpenAPI Client

```bash
# Install generator
pip install openapi-generator-cli

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./python-client
```

---

## Rate Limiting (Production)

Rate limits may be enforced:

```
10 requests / minute per IP
```

Response header with limit info:

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1234567890
```

---

## Pagination (Future)

Future versions may support pagination for batch processing:

```json
{
  "resume_text": "...",
  "jd_text": "...",
  "detailed": true,
  "include_reasoning": true
}
```

---

## Webhooks (Future)

For async processing:

```bash
POST /api/roadmaps/subscribe

{
  "callback_url": "https://yourapp.com/webhooks/roadmap",
  "events": ["roadmap.completed", "roadmap.failed"]
}
```

Webhook payload:
```json
{
  "event": "roadmap.completed",
  "task_id": "uuid",
  "roadmap": {...}
}
```

---

## OpenAPI/Swagger

Interactive documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Best Practices

### 1. Resume Text
- Include job titles, technologies, frameworks
- List skills with context (e.g., "5 years Python")
- Include certifications and achievements

### 2. Job Description Text
- Copy from job posting
- Include technical stack
- Include seniority level

### 3. Error Handling
```python
try:
    roadmap = generate_roadmap(resume, jd)
except ValueError as e:
    print(f"Input error: {e}")
except requests.Timeout:
    print("Request timed out - try again")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 4. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_roadmap_cached(resume: str, jd: str):
    return generate_roadmap(resume, jd)
```

---

## Troubleshooting

### Timeout (> 5 seconds)

- First request loads embedding model (slower)
- Subsequent requests faster
- Consider caching on client side

### 422 Validation Error

- Resume text must be ≥ 50 characters
- JD text must be ≥ 50 characters
- Check for special characters

### 500 Server Error

- Check logs: `docker logs onboarding-engine`
- Verify OpenAI key if using API
- Ensure sufficient memory (1GB+)

---

For more help, visit `/docs` or check DEPLOYMENT.md and ARCHITECTURE.md.
