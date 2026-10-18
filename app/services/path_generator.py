"""
Learning path generation service.
Builds adaptive learning path using skill dependency graph.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Set
import networkx as nx

logger = logging.getLogger(__name__)


def load_skill_graph() -> Dict[str, List[str]]:
    """Load skill dependency graph from JSON."""
    graph_path = Path(__file__).parent.parent / "data" / "skill_graph.json"
    with open(graph_path) as f:
        data = json.load(f)
    return data.get("dependencies", {})


def load_course_catalog() -> Dict[str, Dict]:
    """Load course catalog from JSON."""
    catalog_path = Path(__file__).parent.parent / "data" / "course_catalog.json"
    with open(catalog_path) as f:
        data = json.load(f)
    return data.get("courses", {})


def resolve_prerequisites(skills: List[str]) -> List[str]:
    """
    Resolve prerequisites for given skills using topological sort.

    Args:
        skills: List of skills to learn

    Returns:
        Ordered list of skills including all prerequisites
    """
    graph = load_skill_graph()

    # Build directed graph (skill -> prerequisites)
    G = nx.DiGraph()

    # Add all requested skills
    for skill in skills:
        G.add_node(skill)

    # Recursively add prerequisites
    visited = set()

    def add_prerequisites_recursive(skill: str):
        if skill in visited:
            return
        visited.add(skill)

        if skill in graph:
            for prereq in graph.get(skill, []):
                G.add_edge(prereq, skill)  # prereq must come before skill
                add_prerequisites_recursive(prereq)

    for skill in skills:
        add_prerequisites_recursive(skill)

    # Topological sort gives us the correct order
    try:
        ordered = list(nx.topological_sort(G))
    except nx.NetworkXError:
        logger.warning("Circular dependency detected. Using original order.")
        ordered = skills

    return ordered


def generate_roadmap(
    missing_skills: List[str],
    partial_skills: List[str],
    known_skills: List[str]
) -> tuple[List[Dict], int]:
    """
    Generate complete learning roadmap.

    Args:
        missing_skills: Skills not yet learned
        partial_skills: Skills with partial knowledge
        known_skills: Skills already mastered

    Returns:
        Tuple of (modules list, total weeks)
    """
    catalog = load_course_catalog()

    # Combine missing and partial skills, prioritize missing
    to_learn = missing_skills + partial_skills

    if not to_learn:
        return [], 0

    # Resolve prerequisites
    ordered_skills = resolve_prerequisites(to_learn)

    # Filter out skills not in catalog
    ordered_skills = [s for s in ordered_skills if s in catalog]

    if not ordered_skills:
        logger.warning(f"No courses found for skills: {to_learn}")
        return [], 0

    modules = []
    total_weeks = 0

    for order, skill in enumerate(ordered_skills, start=1):
        course = catalog[skill]
        duration = course.get("duration_weeks", 4)
        total_weeks += duration

        # Determine reason
        if skill in missing_skills:
            reason = f"Missing skill - required for role"
        else:
            reason = f"Partial knowledge - strengthen capability"

        # Get prerequisites from skill graph
        graph = load_skill_graph()
        prerequisites = [p for p in graph.get(skill, []) if p in ordered_skills]

        module = {
            "module_name": course["name"],
            "duration_weeks": duration,
            "reason": reason,
            "skill_covered": skill,
            "prerequisites": prerequisites,
            "order": order,
        }

        modules.append(module)

    return modules, total_weeks
