"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class SkillEntry(BaseModel):
    """Extracted skill with proficiency level."""
    skill_name: str = Field(..., description="Name of the skill")
    proficiency: float = Field(..., ge=0, le=1, description="Proficiency level 0-1")


class ExtractedSkills(BaseModel):
    """Skills extracted from resume."""
    skills: List[SkillEntry] = Field(..., description="List of extracted skills")


class GapAnalysisResult(BaseModel):
    """Gap analysis between candidate and JD."""
    known_skills: List[str] = Field(..., description="Skills >0.75 similarity")
    partial_skills: List[str] = Field(..., description="Skills 0.4-0.75 similarity")
    missing_skills: List[str] = Field(..., description="Skills <0.4 similarity")
    total_required_skills: int = Field(..., description="Total skills required in JD")


class LearningModule(BaseModel):
    """Single module in the learning roadmap."""
    module_name: str = Field(..., description="Name of the learning module")
    duration_weeks: int = Field(..., description="Estimated duration in weeks")
    reason: str = Field(..., description="Why this module is needed")
    skill_covered: str = Field(..., description="Primary skill this module covers")
    prerequisites: List[str] = Field(default_factory=list, description="Required modules before this")
    order: int = Field(..., description="Sequence in learning path")


class RoadmapRequest(BaseModel):
    """Request to generate learning roadmap."""
    resume_text: str = Field(..., min_length=50, description="Candidate's resume")
    jd_text: str = Field(..., min_length=50, description="Job description text")


class RoadmapResponse(BaseModel):
    """Complete learning roadmap response."""
    extracted_skills: Dict[str, float] = Field(..., description="Skills extracted from resume")
    jd_skills: Dict[str, float] = Field(..., description="Skills from job description")
    gap_analysis: GapAnalysisResult = Field(..., description="Gap analysis")
    roadmap: List[LearningModule] = Field(..., description="Ordered learning modules")
    readiness_score: float = Field(..., ge=0, le=1, description="Current readiness (0-1)")
    total_weeks_required: int = Field(..., description="Total weeks to complete roadmap")
