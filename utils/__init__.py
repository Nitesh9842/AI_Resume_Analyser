"""
Utils Package
"""

from .text_extractor import extract_text_from_file, clean_text
from .skill_extractor import SkillExtractor
from .resume_parser import ResumeParser
from .jd_processor import JobDescriptionProcessor

# Import similarity with error handling
try:
    from .similarity import calculate_similarity, get_embeddings
    SIMILARITY_AVAILABLE = True
except Exception as e:
    print(f"Warning: Similarity calculation may use fallback method: {e}")
    from .similarity import calculate_similarity, get_embeddings
    SIMILARITY_AVAILABLE = False

__all__ = [
    'extract_text_from_file',
    'clean_text',
    'SkillExtractor',
    'ResumeParser',
    'JobDescriptionProcessor',
    'calculate_similarity',
    'get_embeddings'
]