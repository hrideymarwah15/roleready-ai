"""
Skill extraction service.
Extracts skills from resume/JD using OpenAI or fallback keyword matching.
"""

import logging
import os
from typing import Dict
import re

from openai import OpenAI, APIError, APIConnectionError

logger = logging.getLogger(__name__)


SKILL_KEYWORDS = {
    "Python": ["python", "py", "django", "flask", "fastapi", "pandas", "numpy"],
    "JavaScript": ["javascript", "js", "nodejs", "node.js", "typescript", "ts"],
    "SQL": ["sql", "postgres", "postgresql", "mysql", "oracle", "query"],
    "Git": ["git", "github", "gitlab", "version control"],
    "Linux": ["linux", "unix", "bash", "shell", "command line"],
    "Docker": ["docker", "containerization", "container"],
    "Kubernetes": ["kubernetes", "k8s", "orchestration"],
    "React": ["react", "react.js", "jsx"],
    "Vue.js": ["vue", "vue.js"],
    "Angular": ["angular"],
    "Node.js": ["node.js", "nodejs"],
    "Express": ["express", "express.js"],
    "Flask": ["flask"],
    "Django": ["django"],
    "FastAPI": ["fastapi"],
    "PostgreSQL": ["postgresql", "postgres", "pg"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "Machine Learning": ["machine learning", "ml", "sklearn", "scikit-learn"],
    "Deep Learning": ["deep learning", "tensorflow", "pytorch", "keras"],
    "AWS": ["aws", "amazon web services", "ec2", "s3"],
    "GCP": ["gcp", "google cloud"],
    "Azure": ["azure", "microsoft azure"],
    "Testing": ["pytest", "jest", "mocha", "unit test", "integration test"],
    "Docker": ["docker"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous deployment"],
    "REST APIs": ["rest api", "api", "http", "endpoint"],
    "GraphQL": ["graphql"],
    "System Design": ["system design", "architecture", "scalability"],
    "Agile": ["agile", "scrum", "sprint", "kanban"],
}


def extract_skills(text: str) -> Dict[str, float]:
    """
    Extract skills from text with proficiency levels.
    Uses OpenAI if API key exists, falls back to keyword matching.

    Args:
        text: Resume or JD text

    Returns:
        Dict mapping skill names to proficiency (0-1)
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        try:
            return _extract_skills_openai(text, api_key)
        except (APIError, APIConnectionError) as e:
            logger.warning(f"OpenAI extraction failed: {e}. Falling back to keywords.")
            return _extract_skills_keywords(text)
    else:
        logger.info("No OpenAI API key. Using keyword matching.")
        return _extract_skills_keywords(text)


def _extract_skills_openai(text: str, api_key: str) -> Dict[str, float]:
    """
    Use OpenAI to extract skills with confidence scores.
    """
    client = OpenAI(api_key=api_key)

    prompt = f"""
    Extract technical skills from the following text and return as JSON.
    For each skill, provide a proficiency level from 0.0 to 1.0.
    Only return valid JSON without markdown formatting.

    Example output:
    {{"Python": 0.8, "JavaScript": 0.5, "Docker": 0.3}}

    Text:
    {text}

    Return only the JSON object with skills as keys and proficiency (0-1) as values.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        result_text = response.choices[0].message.content.strip()

        # Clean up markdown if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        import json
        skills = json.loads(result_text)

        # Validate proficiency levels
        for skill, prof in skills.items():
            if not isinstance(prof, (int, float)) or prof < 0 or prof > 1:
                skills[skill] = 0.5

        return skills

    except Exception as e:
        logger.error(f"OpenAI extraction error: {e}")
        raise


def _extract_skills_keywords(text: str) -> Dict[str, float]:
    """
    Fallback: Extract skills using keyword matching.
    Proficiency is estimated based on frequency and context.
    """
    text_lower = text.lower()
    skills = {}

    for skill, keywords in SKILL_KEYWORDS.items():
        count = sum(text_lower.count(kw) for kw in keywords)

        if count > 0:
            # Calculate proficiency based on frequency
            # More mentions = higher proficiency (capped at 1.0)
            proficiency = min(0.3 + (count * 0.1), 1.0)
            skills[skill] = round(proficiency, 2)

    return skills or {"General Skills": 0.5}
