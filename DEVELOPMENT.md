# 🔧 Development Guide

## Prerequisites

- Python 3.10 or higher
- pip or Poetry for package management
- Git for version control
- Visual Studio Code or PyCharm (recommended)

## Setup Steps

### 1. Clone Repository

```bash
cd /path/to/projects
git clone <repository-url>
cd onboarding-engine-backend
```

### 2. Create Virtual Environment

```bash
# Using venv (built-in)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify activation
which python  # Should show path to venv/bin/python
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print(fastapi.__version__)"
```

### 4. Configure Environment

```bash
# Copy example .env
cp .env.example .env

# Edit .env to add OpenAI API key (optional)
# OPENAI_API_KEY=sk-your-key-here
```

### 5. Run Development Server

```bash
# Start with auto-reload
uvicorn app.main:app --reload

# Or using make
make dev

# Or using python module
python -m uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

### 6. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI**: http://localhost:8000/openapi.json

---

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v tests/

# Run specific test
pytest tests/test_api.py::test_health_check -v
```

### Code Quality

```bash
# Lint code (flake8)
flake8 app tests --max-line-length=100

# Format code (black)
black app tests

# Type checking (mypy)
mypy app

# All at once
make lint
```

### Creating a New Service

1. Create file in `app/services/`

```python
# app/services/my_service.py
"""
My service description.
"""

import logging

logger = logging.getLogger(__name__)


def my_function(param: str) -> dict:
    """
    Function description.

    Args:
        param: Input parameter

    Returns:
        Result dictionary
    """
    logger.info(f"Processing: {param}")
    return {"result": param}
```

2. Add tests in `tests/test_my_service.py`

```python
# tests/test_my_service.py
import pytest
from app.services.my_service import my_function


def test_my_function():
    result = my_function("input")
    assert result == {"result": "input"}
```

3. Integrate into routes

```python
# app/routes/roadmap.py
from app.services.my_service import my_function

@router.post("/api/my-endpoint")
async def my_endpoint(request: MyRequest):
    result = my_function(request.param)
    return result
```

### Adding a New Endpoint

1. Create route handler

```python
# app/routes/roadmap.py
@router.get("/api/endpoint", response_model=ResponseSchema)
async def my_endpoint(param: str):
    """Endpoint description."""
    result = some_service.process(param)
    return result
```

2. Define request/response schemas

```python
# app/models/schemas.py
class MyRequest(BaseModel):
    param: str = Field(..., description="Parameter description")

class MyResponse(BaseModel):
    result: str = Field(..., description="Result")
```

3. Add tests

```python
# tests/test_api.py
def test_my_endpoint():
    response = client.get("/api/endpoint?param=value")
    assert response.status_code == 200
```

---

## Debugging

### Print Debugging

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Using PyCharm Debugger

1. Set breakpoint (click line number)
2. Right-click on `app/main.py` → "Debug 'main'"
3. Use debug panel to step through code

### Using VS Code Debugger

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

Press F5 to start debugging.

### Interactive Python Shell (iPython)

```bash
# Install ipython
pip install ipython

# Start interactive shell
ipython

# Import and test
>>> from app.services.parser import extract_skills
>>> skills = extract_skills("I'm a Python developer")
>>> print(skills)
```

---

## Project Structure Deep-Dive

```
app/
├── main.py                    # FastAPI app setup, middleware, startup/shutdown
├── config.py                  # Settings & configuration management
│
├── routes/
│   ├── __init__.py
│   └── roadmap.py            # API endpoints and orchestration logic
│
├── services/                  # Business logic layer
│   ├── __init__.py
│   ├── parser.py             # Skill extraction (OpenAI or keyword fallback)
│   ├── gap_analysis.py       # Semantic similarity & gap analysis
│   ├── path_generator.py     # Dependency resolution & path generation
│   └── reasoning.py          # Explanation generation
│
├── models/                    # Pydantic schemas & data models
│   ├── __init__.py
│   └── schemas.py            # Request/response validation
│
├── data/                      # Static data files
│   ├── skill_graph.json      # Skill dependencies DAG
│   └── course_catalog.json   # Course information

tests/
├── __init__.py
└── test_api.py               # Integration tests
```

### main.py

Responsibility: FastAPI setup, middleware, lifecycle events

```python
# What happens here:
- Create FastAPI app
- Add CORS middleware
- Add error handlers
- Include routes
- Setup startup/shutdown events
```

### routes/roadmap.py

Responsibility: API endpoints and service orchestration

```python
# What happens here:
- Define POST /api/generate-roadmap
- Call parser.extract_skills()
- Call gap_analysis.analyze_gaps()
- Call path_generator.generate_roadmap()
- Return RoadmapResponse
```

### services/parser.py

Responsibility: Extract skills from text

```python
# What happens here:
- Try OpenAI extraction if API key exists
- Fallback to keyword matching
- Normalize skill names
- Return {skill: proficiency}
```

### services/gap_analysis.py

Responsibility: Compare candidate vs JD skills

```python
# What happens here:
- Load sentence-transformers model
- Encode skill names to embeddings
- Calculate cosine similarity
- Classify as known/partial/missing
```

### services/path_generator.py

Responsibility: Generate learning path

```python
# What happens here:
- Load skill graph dependencies
- Load course catalog
- Resolve prerequisites using topological sort
- Map skills to courses
- Return ordered modules
```

### services/reasoning.py

Responsibility: Generate explanations

```python
# What happens here:
- Create human-readable explanations
- Generate executive summary
- Calculate readiness metrics
```

---

## Common Tasks

### Add a New Skill to the Graph

Edit `app/data/skill_graph.json`:

```json
{
  "dependencies": {
    "Rust": ["Linux"],  // New skill
    "WebAssembly": ["JavaScript", "Rust"]  // New skill
  }
}
```

### Add a New Course

Edit `app/data/course_catalog.json`:

```json
{
  "courses": {
    "Rust": {
      "name": "Rust Systems Programming",
      "duration_weeks": 8,
      "description": "Learn Rust for systems-level programming"
    }
  }
}
```

### Update Skill Keywords

Edit `app/services/parser.py`:

```python
SKILL_KEYWORDS = {
    "Rust": ["rust", "cargo", "async-await"],
    # ... more skills
}
```

---

## Performance Tips

### 1. Cache Embeddings

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embeddings(text: str):
    """Cache transformers embeddings"""
    return model.encode(text)
```

### 2. Async Database

If adding database support:

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/db"
)
```

### 3. Lazy Load Models

```python
_model = None

def get_embeddings_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model
```

### 4. Request Validation

Pydantic validates on entry:

```python
class RoadmapRequest(BaseModel):
    resume_text: str = Field(..., min_length=50)  # Early validation
```

---

## IDE Setup

### VS Code

Install extensions:
1. Python
2. Pylance
3. FastAPI
4. REST Client
5. Thunder Client

settings.json:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  }
}
```

### PyCharm

1. Mark `app` directory as Sources Root
2. Enable code inspections
3. Set formatter to Black
4. Configure run configuration for FastAPI

---

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-endpoint

# Make changes
git add app/routes/roadmap.py app/models/schemas.py

# Commit with clear message
git commit -m "feat: Add new-endpoint with semantic similarity"

# Push to remote
git push origin feature/new-endpoint

# Create PR for review
# After approval, merge to main
```

Commit message format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Add tests
- `chore:` Maintenance

---

## Deployment Checklist

Before deploying to production:

- [ ] All tests pass locally
- [ ] Code formatted with black
- [ ] No linting errors (flake8)
- [ ] Environment variables configured
- [ ] Dependencies updated to latest
- [ ] Documentation updated
- [ ] API endpoints tested manually
- [ ] Performance benchmarked
- [ ] Security review completed

```bash
# Pre-deployment check
make test && make lint && make format && python -m pytest --cov=app
```

---

## Troubleshooting

### Module Import Errors

```python
# Problem: ModuleNotFoundError: No module named 'app'
# Solution: Ensure working directory is project root
cd /path/to/onboarding-engine-backend
```

### CORS Errors

```python
# Problem: CORS error in browser
# Solution: Check .env CORS_ORIGINS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Slow First Request

```
# Problem: First request takes 5+ seconds
# Reason: Embedding model loading (~1GB)
# Solution: Model is cached for subsequent requests
```

### OpenAI Connection Errors

```python
# Problem: OpenAI API timeouts
# Solution: Check API key validity
# Fallback: System uses keywords if OpenAI is down
```

---

## Next Steps

1. Read ARCHITECTURE.md for system design
2. Read API_REFERENCE.md for endpoint details
3. Explore test cases in tests/test_api.py
4. Modify skill_graph.json for your domain
5. Deploy using DEPLOYMENT.md

For questions, check inline code comments or docstrings.
