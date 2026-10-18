"""
Gap analysis service.
Compares candidate skills vs JD requirements using semantic similarity.
"""

import logging
from typing import Dict, List
from sentence_transformers import util
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Load embeddings model once (cache)
_model = None


def get_embeddings_model():
    """Get or load the sentence-transformers model."""
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def analyze_gaps(
    candidate_skills: Dict[str, float],
    jd_skills: Dict[str, float]
) -> tuple[List[str], List[str], List[str]]:
    """
    Compare candidate skills vs JD requirements.
    Uses semantic similarity to match skills across different naming.

    Args:
        candidate_skills: Skills from resume with proficiency
        jd_skills: Skills from job description with proficiency

    Returns:
        Tuple of (known, partial, missing) skill lists
    """
    model = get_embeddings_model()

    candidate_skill_names = list(candidate_skills.keys())
    jd_skill_names = list(jd_skills.keys())

    if not candidate_skill_names or not jd_skill_names:
        return [], [], jd_skill_names

    # Encode all skill names
    candidate_embeddings = model.encode(candidate_skill_names)
    jd_embeddings = model.encode(jd_skill_names)

    # Calculate similarity matrix
    similarity_matrix = util.pytorch_cos_sim(candidate_embeddings, jd_embeddings)

    known_skills = []
    partial_skills = []
    missing_skills = list(jd_skill_names)  # Start with all as missing

    # For each JD skill, find best match in candidate skills
    for jd_idx, jd_skill in enumerate(jd_skill_names):
        if candidate_skill_names:
            # Get similarity scores for this JD skill
            similarities = similarity_matrix[:, jd_idx].cpu().numpy()
            max_similarity = float(similarities.max())
            best_candidate_idx = int(similarities.argmax())
            best_candidate_skill = candidate_skill_names[best_candidate_idx]

            logger.debug(
                f"JD skill '{jd_skill}' matched to '{best_candidate_skill}' "
                f"with similarity {max_similarity:.2f}"
            )

            if max_similarity > 0.75:
                known_skills.append(jd_skill)
                if jd_skill in missing_skills:
                    missing_skills.remove(jd_skill)
            elif max_similarity > 0.4:
                partial_skills.append(jd_skill)
                if jd_skill in missing_skills:
                    missing_skills.remove(jd_skill)

    return known_skills, partial_skills, missing_skills
