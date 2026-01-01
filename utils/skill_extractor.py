"""
Skill Extraction Module
Extracts technical and soft skills from text
"""

import json
import re
from typing import List, Set, Dict
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class SkillExtractor:
    """Extract skills from resume and job description text"""
    
    def __init__(self, skills_json_path: str = "assets/skills.json"):
        """Initialize with skills database"""
        self.skills_db = self._load_skills(skills_json_path)
        self.all_skills = self._flatten_skills()
        
    def _load_skills(self, path: str) -> Dict:
        """Load skills from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default skills if file not found
            return {
                "programming_languages": ["Python", "Java", "JavaScript", "C++"],
                "web_frameworks": ["React", "Django", "Flask", "Node.js"],
                "databases": ["MySQL", "PostgreSQL", "MongoDB"],
                "ai_ml": ["Machine Learning", "Deep Learning", "TensorFlow", "PyTorch"],
                "cloud_devops": ["AWS", "Docker", "Kubernetes", "CI/CD"],
            }
    
    def _flatten_skills(self) -> Set[str]:
        """Flatten all skills into a single set"""
        all_skills = set()
        for category, skills in self.skills_db.items():
            all_skills.update([skill.lower() for skill in skills])
        return all_skills
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from text using multiple methods:
        1. Direct matching from skills database
        2. N-gram matching for multi-word skills
        3. Case-insensitive matching
        """
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = set()
        
        # Method 1: Direct word matching
        for skill in self.all_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill.title())
        
        # Method 2: Check for variations and abbreviations
        skill_variations = {
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'react.js': 'React',
            'vue.js': 'Vue.js',
            'node.js': 'Node.js',
            'ml': 'Machine Learning',
            'dl': 'Deep Learning',
            'nlp': 'NLP',
            'cv': 'Computer Vision',
            'aws': 'AWS',
            'gcp': 'Google Cloud',
            'k8s': 'Kubernetes',
        }
        
        for abbrev, full_name in skill_variations.items():
            if re.search(r'\b' + abbrev + r'\b', text_lower):
                found_skills.add(full_name)
        
        return sorted(list(found_skills))
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize extracted skills"""
        categorized = {}
        
        for skill in skills:
            skill_lower = skill.lower()
            for category, category_skills in self.skills_db.items():
                category_skills_lower = [s.lower() for s in category_skills]
                if skill_lower in category_skills_lower:
                    if category not in categorized:
                        categorized[category] = []
                    categorized[category].append(skill)
                    break
        
        return categorized
    
    def find_missing_skills(self, resume_skills: List[str], jd_skills: List[str]) -> List[str]:
        """Find skills in JD but not in resume"""
        resume_skills_lower = [s.lower() for s in resume_skills]
        missing = [skill for skill in jd_skills if skill.lower() not in resume_skills_lower]
        return sorted(missing)
    
    def find_matching_skills(self, resume_skills: List[str], jd_skills: List[str]) -> List[str]:
        """Find skills present in both resume and JD"""
        resume_skills_lower = [s.lower() for s in resume_skills]
        matching = [skill for skill in jd_skills if skill.lower() in resume_skills_lower]
        return sorted(matching)
    
    def suggest_related_skills(self, current_skills: List[str]) -> List[str]:
        """Suggest related skills to learn"""
        suggestions = set()
        
        # Skill relationship mapping
        skill_relations = {
            'python': ['Django', 'Flask', 'FastAPI', 'Pandas', 'NumPy'],
            'javascript': ['React', 'Node.js', 'TypeScript', 'Vue.js'],
            'machine learning': ['TensorFlow', 'PyTorch', 'Scikit-learn', 'Deep Learning'],
            'react': ['Next.js', 'Redux', 'TypeScript', 'Node.js'],
            'aws': ['Docker', 'Kubernetes', 'Terraform', 'CI/CD'],
        }
        
        for skill in current_skills:
            skill_lower = skill.lower()
            if skill_lower in skill_relations:
                suggestions.update(skill_relations[skill_lower])
        
        # Remove already known skills
        current_skills_lower = [s.lower() for s in current_skills]
        suggestions = [s for s in suggestions if s.lower() not in current_skills_lower]
        
        return sorted(list(suggestions))[:5]  # Return top 5 suggestions