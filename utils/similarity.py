"""
Similarity Calculation Module
Uses sentence transformers to calculate semantic similarity
Falls back to TF-IDF if sentence-transformers is unavailable
"""

from __future__ import annotations
from typing import Dict, List
import numpy as np

# Try to import ML dependencies
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: sentence-transformers not available: {e}")
    print("Falling back to TF-IDF based similarity")
    DEPENDENCIES_AVAILABLE = False
    
# Fallback imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine


# Global model instance
_model_instance = None


class SimilarityCalculator:
    """Calculate similarity between resume and job description"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """Initialize with sentence transformer model or fallback to TF-IDF"""
        self.use_transformers = DEPENDENCIES_AVAILABLE
        if self.use_transformers:
            self.model = self._load_model(model_name)
        else:
            self.vectorizer = TfidfVectorizer(max_features=1000)
            print("Using TF-IDF vectorizer as fallback")
    
    def _load_model(self, model_name: str):
        """Load sentence transformer model"""
        global _model_instance
        if _model_instance is None:
            try:
                print(f"Loading model: {model_name}")
                _model_instance = SentenceTransformer(model_name)
                print("Model loaded successfully")
            except Exception as e:
                print(f"Error loading model {model_name}: {e}")
                print("Trying default model...")
                _model_instance = SentenceTransformer('all-MiniLM-L6-v2')
        return _model_instance
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for given texts"""
        if not texts:
            return np.array([], dtype=np.float32)
        
        if self.use_transformers:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return np.asarray(embeddings, dtype=np.float32)
        else:
            # Fallback to TF-IDF
            try:
                tfidf_matrix = self.vectorizer.fit_transform(texts)
                # Convert sparse matrix to dense array
                dense_matrix = np.array(tfidf_matrix.todense())
                return dense_matrix.astype(np.float32)
            except:
                # Return zero embeddings if error
                return np.zeros((len(texts), 100), dtype=np.float32)
    
    def calculate_cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        if self.use_transformers:
            embeddings = self.get_embeddings([text1, text2])
            if embeddings.shape[0] < 2:
                return 0.0
            similarity = cosine_similarity(embeddings[0:1], embeddings[1:2])[0][0]
        else:
            # TF-IDF fallback
            try:
                tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
                dense_matrix = np.asarray(tfidf_matrix.todense())
                similarity_matrix = sklearn_cosine(dense_matrix[0:1], dense_matrix[1:2])
                similarity = float(similarity_matrix[0, 0])
            except:
                similarity = 0.0
        
        return float(similarity)
    
    def calculate_skill_match_score(self, resume_skills: List[str], jd_skills: List[str]) -> float:
        """
        Calculate skill match score
        Returns percentage (0-100)
        """
        if not jd_skills:
            return 0.0

        resume_skills_lower = [s.lower() for s in resume_skills]
        jd_skills_lower = [s.lower() for s in jd_skills]

        matched_skills = sum(1 for skill in jd_skills_lower if skill in resume_skills_lower)

        score = (matched_skills / len(jd_skills_lower)) * 100
        return round(score, 2)

    def calculate_overall_match_score(
        self,
        resume_text: str,
        jd_text: str,
        resume_skills: List[str],
        jd_skills: List[str],
    ) -> Dict:
        """
        Calculate overall match score combining:
        1. Semantic similarity (40%)
        2. Skill match (60%)
        """
        # Semantic similarity
        semantic_score = self.calculate_cosine_similarity(resume_text, jd_text) * 100

        # Skill match score
        skill_score = self.calculate_skill_match_score(resume_skills, jd_skills)

        # Weighted average
        overall_score = (semantic_score * 0.4) + (skill_score * 0.6)

        return {
            "overall_score": round(overall_score, 2),
            "semantic_similarity": round(semantic_score, 2),
            "skill_match": round(skill_score, 2),
        }


# Global calculator instance
_calculator_instance = None


def get_similarity_calculator():
    """Get cached similarity calculator instance"""
    global _calculator_instance
    if _calculator_instance is None:
        _calculator_instance = SimilarityCalculator()
    return _calculator_instance


def get_embeddings(texts: List[str]) -> np.ndarray:
    """Get embeddings for texts"""
    calc = get_similarity_calculator()
    return calc.get_embeddings(texts)


def calculate_similarity(
    resume_text: str, jd_text: str, resume_skills: List[str], jd_skills: List[str]
) -> Dict:
    """Calculate similarity between resume and JD"""
    calc = get_similarity_calculator()
    return calc.calculate_overall_match_score(resume_text, jd_text, resume_skills, jd_skills)