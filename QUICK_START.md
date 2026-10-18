# ⚡ Quick Start (5 Minutes)

## 1. Install Dependencies

```bash
cd onboarding-engine-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Time: 2-3 minutes** (first-time only)

## 2. Start Server

```bash
uvicorn app.main:app --reload
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Time: 10 seconds**

## 3. Test API

Open in browser or use cURL:

```bash
curl -X POST "http://localhost:8000/api/generate-roadmap" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "I have 5 years of Python experience with Django and PostgreSQL.",
    "jd_text": "Senior Full Stack Engineer - requires React, Node.js, Docker, Kubernetes"
  }'
```

**Time: 1-3 seconds** (first request slower due to model loading)

## 4. View Documentation

Visit: http://localhost:8000/docs

Click "Try it out" on the `/api/generate-roadmap` endpoint

**Time: 1 minute**

---

## That's It! 🎉

You now have a working AI-Adaptive Onboarding Engine running locally.

### Next Steps:

- **Read API docs**: http://localhost:8000/docs
- **Customize skills**: Edit `app/data/skill_graph.json`
- **Add courses**: Edit `app/data/course_catalog.json`
- **Add OpenAI key**: Set `OPENAI_API_KEY` in `.env` for better extraction
- **Run tests**: `pytest tests/`

### What It Does:

1. **Input**: Resume text + Job Description
2. **Process**: Extracts skills → Analyzes gaps → Generates learning path
3. **Output**: Personalized roadmap with modules, duration, and reasoning

### Example Response:

```json
{
  "readiness_score": 0.33,
  "gap_analysis": {
    "known_skills": ["Python", "PostgreSQL"],
    "missing_skills": ["React", "Kubernetes"],
    "partial_skills": ["Docker"]
  },
  "roadmap": [
    {
      "module_name": "JavaScript Essentials",
      "duration_weeks": 4,
      "order": 1
    },
    {
      "module_name": "React Development",
      "duration_weeks": 6,
      "order": 2
    }
  ],
  "total_weeks_required": 10
}
```

---

### Useful Commands:

```bash
# Stop server
Ctrl+C

# Run tests
pytest

# Format code
black app tests

# Check code quality
flake8 app tests

# View OpenAPI schema
curl http://localhost:8000/openapi.json | jq
```

---

### Troubleshooting:

| Issue | Solution |
|-------|----------|
| Port 8000 already in use | `uvicorn app.main:app --port 8001` |
| Module not found error | Ensure venv is activated: `source venv/bin/activate` |
| Slow first request (5+ sec) | Normal - embedding model loads on first run |
| OpenAI API errors | API key not set in `.env` (optional - uses keywords fallback) |

---

### Want to Use Docker?

```bash
# Build and run
docker-compose up

# Will be available at http://localhost:8000
```

---

### Production Deployment?

```bash
# See DEPLOYMENT.md for:
# - Railway
# - Heroku
# - Docker
# - Kubernetes
# - AWS Lambda
```

---

## Questions?

📚 **Full Guides:**
- API endpoints: `API_REFERENCE.md`
- Architecture: `ARCHITECTURE.md`
- Deployment: `DEPLOYMENT.md`
- Development: `DEVELOPMENT.md`

📖 **Code Documentation:**
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Happy learning! 🚀
