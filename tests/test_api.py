"""
Integration tests for the onboarding engine.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()
    assert "endpoints" in response.json()


def test_generate_roadmap_basic():
    """Test basic roadmap generation."""
    response = client.post(
        "/api/generate-roadmap",
        json={
            "resume_text": "I have 5 years of Python and Django experience. "
                          "Familiar with SQL, Git, Linux, and REST APIs.",
            "jd_text": "Senior Full Stack Engineer. Required: React, Node.js, "
                      "PostgreSQL, Docker, Kubernetes, AWS. Preferred: System Design",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Validate response structure
    assert "extracted_skills" in data
    assert "jd_skills" in data
    assert "gap_analysis" in data
    assert "roadmap" in data
    assert "readiness_score" in data
    assert "total_weeks_required" in data

    # Validate gap analysis
    gap = data["gap_analysis"]
    assert "known_skills" in gap
    assert "partial_skills" in gap
    assert "missing_skills" in gap
    assert "total_required_skills" in gap

    # Validate roadmap modules
    assert isinstance(data["roadmap"], list)
    for module in data["roadmap"]:
        assert "module_name" in module
        assert "duration_weeks" in module
        assert "reason" in module
        assert "skill_covered" in module
        assert "prerequisites" in module
        assert "order" in module

    # Validate scores
    assert 0 <= data["readiness_score"] <= 1
    assert data["total_weeks_required"] >= 0


def test_generate_roadmap_empty_input():
    """Test with invalid input."""
    response = client.post(
        "/api/generate-roadmap",
        json={
            "resume_text": "Short",  # Too short
            "jd_text": "Text",       # Too short
        },
    )
    assert response.status_code == 422  # Validation error


def test_generate_roadmap_missing_expert():
    """Test when candidate has all required skills."""
    response = client.post(
        "/api/generate-roadmap",
        json={
            "resume_text": "Python, JavaScript, SQL, React, Node.js, PostgreSQL, "
                          "Docker, Kubernetes, AWS, System Design",
            "jd_text": "Python, JavaScript, SQL, React, Node.js, PostgreSQL, "
                      "Docker, Kubernetes, AWS, System Design",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Should have high readiness
    assert data["readiness_score"] > 0.8
    # May have roadmap for optimization/specialization


def test_generate_roadmap_complete_beginner():
    """Test with beginner candidate."""
    response = client.post(
        "/api/generate-roadmap",
        json={
            "resume_text": "I have a degree in Computer Science. "
                          "I'm learning Python and JavaScript.",
            "jd_text": "Senior Engineer with 5+ years in Python, Node.js, React, "
                      "PostgreSQL, Docker, Kubernetes, AWS, System Design, "
                      "Microservices, GraphQL",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Should have low readiness
    assert data["readiness_score"] < 0.5
    # Should have substantial roadmap
    assert len(data["roadmap"]) > 0
    # Should take weeks to complete
    assert data["total_weeks_required"] > 10


def test_prerequisite_ordering():
    """
    Test that prerequisites are ordered correctly.
    E.g., Python before Django, JavaScript before React.
    """
    response = client.post(
        "/api/generate-roadmap",
        json={
            "resume_text": "Beginner programmer",
            "jd_text": "Expert in Python, Django, JavaScript, React, Node.js, "
                      "PostgreSQL, Kubernetes",
        },
    )

    assert response.status_code == 200
    data = response.json()

    roadmap = data["roadmap"]
    skill_order = {module["skill_covered"]: module["order"] for module in roadmap}

    # Python should come before Django
    if "Python" in skill_order and "Django" in skill_order:
        assert skill_order["Python"] < skill_order["Django"]

    # JavaScript should come before React
    if "JavaScript" in skill_order and "React" in skill_order:
        assert skill_order["JavaScript"] < skill_order["React"]

    # Linux should come before Docker
    if "Linux" in skill_order and "Docker" in skill_order:
        assert skill_order["Linux"] < skill_order["Docker"]


@pytest.mark.parametrize("resume,jd,expected_skills", [
    (
        "Python expert with 10 years experience",
        "We need Python",
        ["Python"],
    ),
    (
        "JavaScript and TypeScript developer",
        "TypeScript required",
        ["TypeScript"],
    ),
])
def test_skill_extraction_variations(resume, jd, expected_skills):
    """Test skill extraction with various inputs."""
    response = client.post(
        "/api/generate-roadmap",
        json={"resume_text": resume, "jd_text": jd},
    )

    assert response.status_code == 200
    data = response.json()

    extracted = data["extracted_skills"]
    assert any(skill in extracted for skill in expected_skills)
