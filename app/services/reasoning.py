"""
Reasoning service.
Generates explanations for learning recommendations.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def generate_reasoning_trace(
    modules: List[Dict],
    missing_skills: List[str],
    partial_skills: List[str],
    jd_skills: Dict[str, float]
) -> List[str]:
    """
    Generate detailed reasoning for each module in the roadmap.

    Args:
        modules: Learning modules
        missing_skills: Skills completely missing
        partial_skills: Skills with partial knowledge
        jd_skills: Skills required in JD with proficiency

    Returns:
        List of reasoning explanations
    """
    reasons = []

    for module in modules:
        skill = module["skill_covered"]
        prereqs = module.get("prerequisites", [])

        # Build explanation
        explanation = f"Module: {module['module_name']}\n"

        # Why is this skill needed?
        if skill in missing_skills:
            jd_prof = jd_skills.get(skill, 0.5)
            explanation += (
                f"  → {skill} is completely missing from your resume\n"
                f"  → Job description requires {skill} (importance: {jd_prof:.0%})\n"
            )
        elif skill in partial_skills:
            jd_prof = jd_skills.get(skill, 0.5)
            explanation += (
                f"  → {skill} has partial knowledge\n"
                f"  → Job description requires {skill} (importance: {jd_prof:.0%})\n"
            )

        # Prerequisites
        if prereqs:
            explanation += f"  → Prerequisites: {', '.join(prereqs)}\n"

        # Duration
        explanation += (
            f"  → Estimated duration: {module['duration_weeks']} weeks\n"
            f"  → Reason: {module['reason']}"
        )

        reasons.append(explanation)

    return reasons


def generate_summary(
    readiness_score: float,
    total_weeks: int,
    missing_count: int,
    partial_count: int,
    known_count: int
) -> str:
    """Generate executive summary of the roadmap."""
    summary = f"""
📊 READINESS ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Readiness Score: {readiness_score:.0%}

Skill Breakdown:
  ✅ Known Skills:     {known_count}
  ⚠️  Partial Skills:   {partial_count}
  ❌ Missing Skills:    {missing_count}

Learning Plan:
  📚 Total Modules:     {len([m for m in [missing_count, partial_count] if m > 0])}
  ⏱️  Total Duration:    {total_weeks} weeks
  📈 Expected Outcome: {min(100, readiness_score * 100 + 35):.0%} readiness

Strategy:
  1. Start with prerequisite foundations
  2. Build core competencies
  3. Progress to advanced topics
  4. Apply knowledge through projects
    """
    return summary
