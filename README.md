# 🎓 AI-Adaptive Onboarding Engine Backend

A production-ready FastAPI backend that generates personalized learning roadmaps based on resume analysis and job description matching.

## 🎯 Features

- **Resume Parsing**: Extract technical skills with proficiency levels using OpenAI or keyword matching
- **Job Description Analysis**: Identify required skills and importance levels
- **Semantic Gap Analysis**: Use sentence-transformers for intelligent skill matching across different naming conventions
- **Dependency Resolution**: Build learning paths respecting skill prerequisites using NetworkX
- **Adaptive Roadmap Generation**: Create personalized, ordered learning modules
- **Readiness Scoring**: Calculate current readiness percentage and expected outcome
- **Production-Ready**: Error handling, logging, CORS, environment configuration

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip or Poetry

### Installation

1. **Clone and navigate to project**
```bash
cd onboarding-engine-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment** (optional)
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key (optional - works without it)
```

### Running the Server

```bash
uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`

**Interactive API docs**: `http://localhost:8000/docs`

## 📡 API Endpoints

### POST `/api/generate-roadmap`

Generate a personalized learning roadmap.

**Request:**
```json
{
  "resume_text": "I have 5 years of Python and JavaScript experience...",
  "jd_text": "We're looking for a Full Stack Engineer with React, Node.js, and PostgreSQL experience..."
}
```

**Response:**
```json
{
  "extracted_skills": {
    "Python": 0.8,
    "JavaScript": 0.7
  },
  "jd_skills": {
    "React": 0.9,
    "Node.js": 0.8,
    "PostgreSQL": 0.7
  },
  "gap_analysis": {
    "known_skills": ["JavaScript"],
    "partial_skills": [],
    "missing_skills": ["React", "PostgreSQL"],
    "total_required_skills": 3
  },
  "roadmap": [
    {
      "module_name": "JavaScript Essentials",
      "duration_weeks": 4,
      "reason": "Partial knowledge - strengthen capability",
      "skill_covered": "JavaScript",
      "prerequisites": [],
      "order": 1
    },
    {
      "module_name": "React Development",
      "duration_weeks": 6,
      "reason": "Missing skill - required for role",
      "skill_covered": "React",
      "prerequisites": ["JavaScript"],
      "order": 2
    }
  ],
  "readiness_score": 0.33,
  "total_weeks_required": 10
}
```

### GET `/api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "onboarding-engine"
}
```

## 🏗️ Architecture

```
app/
├── main.py                  # FastAPI app setup
├── routes/
│   └── roadmap.py          # API endpoints
├── services/
│   ├── parser.py           # Skill extraction (OpenAI or keywords)
│   ├── gap_analysis.py     # Semantic similarity analysis
│   ├── path_generator.py   # Topological sorting + roadmap
│   └── reasoning.py        # Explanation generation
├── models/
│   └── schemas.py          # Pydantic request/response models
└── data/
    ├── skill_graph.json    # Skill dependency graph
    └── course_catalog.json # Course information
```

### Service Layer Details

#### 1. **Parser Service** (`parser.py`)
- Extracts skills from text using OpenAI GPT-3.5-turbo
- Falls back to keyword matching if API key missing
- Returns normalized skill-to-proficiency mapping

#### 2. **Gap Analysis Service** (`gap_analysis.py`)
- Uses sentence-transformers (all-MiniLM-L6-v2) for embeddings
- Computes cosine similarity between candidate and JD skills
- Classifies skills as: known (>0.75), partial (0.4-0.75), missing (<0.4)
- Robust to skill naming variations (e.g., "Node.js" vs "NodeJS")

#### 3. **Path Generator Service** (`path_generator.py`)
- Loads skill dependency DAG from `skill_graph.json`
- Performs topological sort using NetworkX
- Respects prerequisites while ordering modules
- Maps skills to courses from `course_catalog.json`
- Only includes courses that exist in catalog (no hallucination)

#### 4. **Reasoning Service** (`reasoning.py`)
- Generates detailed explanations for each module
- Shows why skills are needed based on JD requirements
- Lists prerequisites and duration
- Produces executive summary with readiness metrics

## 🧠 How It Works

```
Resume + JD
    ↓
┌─────────────────────────────┐
│ Extract Skills (OpenAI/KW)  │
└─────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Semantic Gap Analysis (Embeddings)  │
└─────────────────────────────────────┘
    ↓
┌──────────────────────────────────┐
│ Resolve Dependencies (TopoSort)  │
└──────────────────────────────────┘
    ↓
┌──────────────────────────┐
│ Generate Learning Path   │
└──────────────────────────┘
    ↓
Readiness Score + Roadmap
```

## 📊 Readiness Score Formula

```
Readiness Score = Known Skills / Total Required Skills
```

- **Score 0.0-0.2**: Entry level - significant learning required
- **Score 0.2-0.5**: Intermediate - focused upskilling needed
- **Score 0.5-0.8**: Advanced - refinement and specialization
- **Score 0.8-1.0**: Expert - ready for role with minor updates

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key (optional) |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `SERVER_HOST` | `0.0.0.0` | Server host |
| `SERVER_PORT` | `8000` | Server port |

### Skill Graph

Edit `app/data/skill_graph.json` to customize skill dependencies:

```json
{
  "dependencies": {
    "SkillName": ["Prerequisite1", "Prerequisite2"],
    "React": ["JavaScript"],
    "Django": ["Python", "SQL"]
  }
}
```

### Course Catalog

Edit `app/data/course_catalog.json` to add/modify courses:

```json
{
  "courses": {
    "Python": {
      "name": "Python Fundamentals",
      "duration_weeks": 4,
      "description": "..."
    }
  }
}
```

## 🧪 Testing

### Example curl request:

```bash
curl -X POST "http://localhost:8000/api/generate-roadmap" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "I have 3 years of Python experience with Django. Familiar with SQL and Git.",
    "jd_text": "Senior Full Stack Engineer - Required: React, Node.js, PostgreSQL, Docker, Kubernetes. Preferred: System Design, AWS"
  }'
```

### Using Python requests:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/generate-roadmap",
    json={
        "resume_text": "Python, Django, SQL, Git",
        "jd_text": "React, Node.js, PostgreSQL, Docker, Kubernetes, AWS"
    }
)

print(response.json())
```

## 📈 Performance

- **Skill Extraction**: ~1-2 seconds (OpenAI) or ~100ms (keywords)
- **Semantic Similarity**: ~200ms for 50+ skills
- **Roadmap Generation**: ~100ms
- **Total Response Time**: ~2-3 seconds (with OpenAI)

Model caching and lazy loading ensure efficient memory usage.

## 🔒 Production Considerations

1. **API Rate Limiting**: Add FastAPI-Limiter for production
2. **Authentication**: Implement OAuth2 or JWT
3. **Async Database**: Use async PostgreSQL for skill/user storage
4. **Caching**: Redis for embedding cache
5. **Monitoring**: Add Sentry or similar error tracking
6. **Logging**: Structured logging with JSON format
7. **Load Testing**: Use locust or k6 for capacity planning

## 🐛 Error Handling

The API gracefully handles:
- Missing OpenAI API key → Falls back to keywords
- Circular dependencies → Uses original skill order
- Unknown skills → Filters to catalog only
- Embedding model failures → Returns error with context
- Malformed input → Pydantic validation errors

## 📚 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.111.0 | Web framework |
| uvicorn | 0.28.0 | ASGI server |
| pydantic | 2.7.1 | Data validation |
| openai | 1.32.0 | OpenAI API client |
| sentence-transformers | 3.0.1 | Semantic embeddings |
| networkx | 3.3 | Graph algorithms |
| python-dotenv | 1.0.1 | Environment loading |

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Railway / Heroku / Render

Set environment variable:
```
OPENAI_API_KEY=sk-...
```

Deploy with:
```bash
git push railway main
```

## 📄 License

MIT

## 🤝 Contributing

PRs welcome! Please ensure:
1. Code follows PEP 8
2. Type hints for all functions
3. Docstrings for modules and public functions
4. Tests pass locally

---

Built with ❤️ for learning and productivity.
