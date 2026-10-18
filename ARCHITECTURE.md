# 🏗️ Architecture & Design

## System Design

### High-Level Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/generate-roadmap
       │ {resume_text, jd_text}
       ↓
┌──────────────────────────────────────┐
│        FastAPI Application           │
├──────────────────────────────────────┤
│  Routes (roadmap.py)                 │
│    ↓                                 │
│  Service Layer                       │
│    ├─ parser.py       (Extract skills)
│    ├─ gap_analysis.py (Semantic similarity)
│    ├─ path_generator.py (Topological sort)
│    └─ reasoning.py    (Generate explanations)
│    ↓                                 │
│  Data Layer                          │
│    ├─ skill_graph.json   (Dependencies)
│    └─ course_catalog.json (Courses)
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────┐
│   OpenAI API (Optional)           │
│   (GPT-3.5-turbo for extraction) │
└──────────────────────────────────┘
       ↓
┌──────────────────────────────────┐
│   Sentence Transformers (Local)   │
│   (all-MiniLM-L6-v2)             │
│   (Semantic embeddings)          │
└──────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│  Response                               │
│  {                                      │
│    extracted_skills,                    │
│    jd_skills,                           │
│    gap_analysis,                        │
│    roadmap,                             │
│    readiness_score,                     │
│    total_weeks_required                 │
│  }                                      │
└─────────────────────────────────────────┘
```

## Design Patterns

### 1. Service Layer Pattern

Separation of concerns: each service handles one responsibility.

```python
# Business logic isolated in services
from app.services.parser import extract_skills
from app.services.gap_analysis import analyze_gaps
from app.services.path_generator import generate_roadmap

# Routes orchestrate services
@router.post("/generate-roadmap")
async def generate_learning_roadmap(request: RoadmapRequest):
    resume_skills = extract_skills(request.resume_text)
    jd_skills = extract_skills(request.jd_text)
    gaps = analyze_gaps(resume_skills, jd_skills)
    roadmap = generate_roadmap(...)
    return RoadmapResponse(...)
```

### 2. Dependency Injection

```python
# Loose coupling through dependency injection
def analyze_gaps(
    candidate_skills: Dict[str, float],
    jd_skills: Dict[str, float]
) -> tuple[List[str], List[str], List[str]]:
    """Pure function - no global state"""
    ...
```

### 3. Data Validation with Pydantic

```python
# Strong typing and validation
class RoadmapRequest(BaseModel):
    resume_text: str = Field(..., min_length=50)
    jd_text: str = Field(..., min_length=50)

# Automatic OpenAPI documentation
```

### 4. Graceful Fallbacks

```python
# Multiple strategies with fallback
def extract_skills(text: str) -> Dict[str, float]:
    if has_openai_key():
        return _extract_skills_openai(text)
    else:
        return _extract_skills_keywords(text)
```

### 5. Error Handling

```python
# Structured error messages
try:
    result = client.chat.completions.create(...)
except APIError as e:
    logger.error(f"OpenAI failed: {e}")
    return fallback_result()
```

## Skill Graph & Dependencies

### Directed Acyclic Graph (DAG)

The skill_graph.json represents prerequisites:

```json
{
  "dependencies": {
    "React": ["JavaScript"],
    "Django": ["Python", "SQL"],
    "Deep Learning": ["Machine Learning", "NumPy"]
  }
}
```

Visualized:
```
JavaScript ──→ React
Python ──→ Django ←── SQL

Python ──→ Machine Learning ──→ Deep Learning
NumPy ────────────────────────↗
```

### Topological Sorting

NetworkX topological sort ensures correct ordering:

```python
import networkx as nx

# Build graph: edges point from prerequisite → skill
G = nx.DiGraph()
G.add_edge("Python", "Django")

# Topological sort: prerequisites first
ordered = list(nx.topological_sort(G))
# Output: ["Python", "SQL", "Django"]
```

Algorithm complexity: **O(V + E)** where V=skills, E=dependencies

## Semantic Similarity

### Embedding Model: all-MiniLM-L6-v2

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode skill names to 384-dimensional vectors
embeddings = model.encode([
    "React",
    "Node.js",
    "JavaScript",
    "Python",
])

# Cosine similarity matrix
from sentence_transformers import util
similarities = util.pytorch_cos_sim(embeddings, embeddings)
```

Similarity thresholds:
- **Exact match**: > 0.75 → "Known"
- **Partial match**: 0.4 - 0.75 → "Partial"
- **No match**: < 0.4 → "Missing"

### Why Semantic Similarity?

Handles skill naming variations:
- "Node.js" ↔ "NodeJS" ↔ "Node"
- "PostgreSQL" ↔ "Postgres" ↔ "PG"
- "Machine Learning" ↔ "ML"

## Scalability Architecture

### Current (Single Instance)

```
Request → FastAPI Server → Memory (Embeddings Model)
                        → External (OpenAI API)
```

Limitations:
- Embedding model takes ~1GB RAM
- ONE request at a time if sequential
- OpenAI API rate limits

### Scaled (Multiple Instances)

```
Requests → Load Balancer
            ├→ Instance 1
            ├→ Instance 2
            └→ Instance 3

All → Shared Redis Cache (Embeddings)
   → Shared OpenAI API (Rate limit handling)
```

Implementation:

```python
# Use Redis for embeddings cache
import redis

cache = redis.Redis(host='redis-host', port=6379)

def get_cached_embeddings(text: str):
    key = f"embed:{hash(text)}"
    cached = cache.get(key)
    if cached:
        return json.loads(cached)

    embeddings = model.encode(text)
    cache.setex(key, 3600, json.dumps(embeddings))
    return embeddings
```

### Async Processing

For long-running requests:

```python
# Use Celery for background tasks
from celery import Celery

celery_app = Celery('onboarding')

@celery_app.task
def generate_roadmap_async(resume_id: str, jd_id: str):
    # Process in background
    # Store result in database
    pass

# API returns task_id immediately
@router.post("/generate-roadmap-async")
async def generate_async(request: RoadmapRequest):
    task = generate_roadmap_async.delay(...)
    return {"task_id": task.id, "status_url": f"/tasks/{task.id}"}
```

## Database Integration (Optional)

### Schema

```sql
CREATE TABLE candidates (
    id UUID PRIMARY KEY,
    resume_text TEXT,
    extracted_skills JSONB,
    created_at TIMESTAMP
);

CREATE TABLE job_descriptions (
    id UUID PRIMARY KEY,
    jd_text TEXT,
    jd_skills JSONB,
    created_at TIMESTAMP
);

CREATE TABLE roadmaps (
    id UUID PRIMARY KEY,
    candidate_id UUID,
    job_id UUID,
    gap_analysis JSONB,
    modules JSONB,
    readiness_score FLOAT,
    created_at TIMESTAMP
);

CREATE INDEX idx_candidates_created ON candidates(created_at);
CREATE INDEX idx_roadmaps_candidate ON roadmaps(candidate_id);
```

### ORM Integration

```python
# app/models/database.py
from sqlalchemy import Column, String, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CandidateModel(Base):
    __tablename__ = "candidates"

    id: str = Column(String, primary_key=True)
    resume_text: str = Column(Text)
    extracted_skills: dict = Column(JSON)
    created_at: datetime = Column(DateTime)
```

## Cost Analysis

### OpenAI API Costs

```
GPT-3.5-turbo:
- Input:  $0.50 per 1M tokens
- Output: $1.50 per 1M tokens

Average request: ~500 input tokens
Cost per request: ~$0.00025 (~100 requests = $0.025)
```

### Sentence-Transformers (Local)

```
One-time: Download model (~500MB)
Per request: Free (runs locally)
Hardware: 1GB RAM, minimal CPU
```

### Architecture Recommendation

For < 100 requests/day:
- Use OpenAI (simple, accurate)
- Cost: ~$0.025/day

For > 1000 requests/day:
- Use Sentence-Transformers only (free)
- Cost: Infrastructure only

For hybrid:
- Sentence-Transformers locally
- OpenAI for verification (optional)

## Testing Strategy

### Unit Tests
```python
# Test individual services
def test_extract_skills_openai():
    skills = extract_skills("Python expert")
    assert "Python" in skills

def test_topological_sort():
    ordered = resolve_prerequisites(["Django"])
    assert ordered.index("Python") < ordered.index("Django")
```

### Integration Tests
```python
# Test full API flow
def test_generate_roadmap_basic():
    response = client.post("/api/generate-roadmap", json={...})
    assert response.status_code == 200
    assert "roadmap" in response.json()
```

### Load Tests
```bash
k6 run load_test.js
# Verify performance under load
# Target: < 5s response time at 100 concurrent users
```

## Security Considerations

### Input Validation
```python
class RoadmapRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, max_length=50000)
    jd_text: str = Field(..., min_length=50, max_length=50000)
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/api/generate-roadmap")
@limiter.limit("10/minute")  # 10 requests per minute
async def generate_roadmap(...):
    pass
```

### Authentication
```python
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

@router.post("/api/generate-roadmap")
async def generate_roadmap(
    request: RoadmapRequest,
    credentials: HTTPAuthCredentials = Depends(security)
):
    # Validate token
    pass
```

---

**Design Goals Achieved:**
- ✅ Single Responsibility Principle
- ✅ Modular & Testable
- ✅ Scalable architecture
- ✅ Fallback mechanisms
- ✅ Type-safe with Pydantic
- ✅ Production-ready error handling
