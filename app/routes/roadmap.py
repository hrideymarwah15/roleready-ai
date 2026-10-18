"""
Roadmap endpoint - main orchestrator.
"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import RoadmapRequest, RoadmapResponse, GapAnalysisResult
from app.services.parser import extract_skills
from app.services.gap_analysis import analyze_gaps
from app.services.path_generator import generate_roadmap
from app.services.reasoning import generate_reasoning_trace, generate_summary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["roadmap"])


@router.post("/generate-roadmap", response_model=RoadmapResponse)
async def generate_learning_roadmap(request: RoadmapRequest) -> RoadmapResponse:
    """
    Generate personalized learning roadmap based on resume and job description.

    Steps:
    1. Extract skills from resume
    2. Extract skills from job description
    3. Analyze gaps using semantic similarity
    4. Generate ordered learning path
    5. Calculate readiness score
    """
    try:
        logger.info("Starting roadmap generation...")

        # Step 1: Extract skills from resume
        logger.info("Extracting resume skills...")
        resume_skills = extract_skills(request.resume_text)
        logger.info(f"Found {len(resume_skills)} skills in resume")

        # Step 2: Extract skills from JD
        logger.info("Extracting JD skills...")
        jd_skills = extract_skills(request.jd_text)
        logger.info(f"Found {len(jd_skills)} skills in JD")

        # Step 3: Gap analysis
        logger.info("Analyzing skill gaps...")
        known_skills, partial_skills, missing_skills = analyze_gaps(
            resume_skills, jd_skills
        )
        logger.info(
            f"Gap analysis: {len(known_skills)} known, "
            f"{len(partial_skills)} partial, {len(missing_skills)} missing"
        )

        # Step 4: Generate learning path
        logger.info("Generating learning path...")
        modules, total_weeks = generate_roadmap(
            missing_skills, partial_skills, known_skills
        )
        logger.info(f"Generated {len(modules)} learning modules ({total_weeks} weeks)")

        # Step 5: Calculate readiness score
        total_required = len(jd_skills) if jd_skills else 1
        readiness_score = len(known_skills) / total_required if total_required > 0 else 0
        logger.info(f"Readiness score: {readiness_score:.2%}")

        # Generate reasoning
        reasoning_trace = generate_reasoning_trace(
            modules, missing_skills, partial_skills, jd_skills
        )
        summary = generate_summary(
            readiness_score,
            total_weeks,
            len(missing_skills),
            len(partial_skills),
            len(known_skills),
        )

        logger.info(f"Roadmap generation complete")

        # Return response
        response = RoadmapResponse(
            extracted_skills=resume_skills,
            jd_skills=jd_skills,
            gap_analysis=GapAnalysisResult(
                known_skills=known_skills,
                partial_skills=partial_skills,
                missing_skills=missing_skills,
                total_required_skills=total_required,
            ),
            roadmap=modules,
            readiness_score=readiness_score,
            total_weeks_required=total_weeks,
        )

        # Log to console for debugging
        logger.info(f"\n{summary}")
        for reason in reasoning_trace:
            logger.debug(f"\n{reason}")

        return response

    except Exception as e:
        logger.error(f"Error generating roadmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate roadmap: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "onboarding-engine"}
