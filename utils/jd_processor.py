"""
Job Description Processor Module
Processes job descriptions to extract requirements
"""

import re
from typing import Dict, List

# Handle both relative and absolute imports
try:
    from .skill_extractor import SkillExtractor
except ImportError:
    from skill_extractor import SkillExtractor


class JobDescriptionProcessor:
    """Process job descriptions and extract key requirements"""
    
    def __init__(self):
        self.skill_extractor = SkillExtractor()
        
        self.seniority_keywords = {
            'entry': ['junior', 'entry level', 'graduate', 'fresher', '0-2 years'],
            'mid': ['mid level', 'intermediate', '2-5 years', '3-5 years'],
            'senior': ['senior', 'lead', 'principal', '5+ years', '7+ years'],
            'expert': ['expert', 'architect', 'director', 'head', '10+ years']
        }
        
    def extract_required_skills(self, jd_text: str) -> List[str]:
        """Extract required skills from job description"""
        return self.skill_extractor.extract_skills(jd_text)
    
    def extract_experience_required(self, jd_text: str) -> str:
        """Extract required years of experience"""
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, jd_text.lower())
            if match:
                return match.group(0)
        
        return "Not specified"
    
    def extract_education_required(self, jd_text: str) -> List[str]:
        """Extract required education"""
        education_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'b.tech', 'm.tech',
            'graduate', 'diploma'
        ]
        
        found_education = []
        jd_lower = jd_text.lower()
        
        for keyword in education_keywords:
            if keyword in jd_lower:
                found_education.append(keyword.title())
        
        return found_education if found_education else ['Not specified']
    
    def extract_job_title(self, jd_text: str) -> str:
        """Extract job title from JD (usually in first few lines)"""
        lines = jd_text.strip().split('\n')
        
        # Common job title keywords
        title_keywords = [
            'engineer', 'developer', 'scientist', 'analyst', 'manager',
            'architect', 'consultant', 'specialist', 'lead'
        ]
        
        for line in lines[:5]:  # Check first 5 lines
            for keyword in title_keywords:
                if keyword in line.lower():
                    return line.strip()
        
        return "Not specified"
    
    def determine_seniority_level(self, jd_text: str) -> str:
        """Determine seniority level from JD"""
        jd_lower = jd_text.lower()
        
        for level, keywords in self.seniority_keywords.items():
            for keyword in keywords:
                if keyword in jd_lower:
                    return level.title()
        
        return "Mid"  # Default to mid-level
    
    def extract_responsibilities(self, jd_text: str) -> List[str]:
        """Extract key responsibilities from JD"""
        responsibilities = []
        
        # Look for responsibility section
        resp_keywords = ['responsibilities', 'what you will do', 'role', 'duties']
        
        jd_lower = jd_text.lower()
        for keyword in resp_keywords:
            if keyword in jd_lower:
                # Find the section
                pattern = rf'\b{keyword}\b.*?(?=\n\n|\Z|requirements|qualifications)'
                match = re.search(pattern, jd_lower, re.DOTALL)
                if match:
                    section = match.group()
                    # Split by bullet points or newlines
                    items = re.split(r'[•\-\*]|\n', section)
                    responsibilities.extend([item.strip() for item in items if item.strip() and len(item.strip()) > 20])
                    break
        
        return responsibilities[:5] if responsibilities else []
    
    def process_job_description(self, jd_text: str) -> Dict:
        """
        Main function to process job description
        Returns structured data
        """
        return {
            'job_title': self.extract_job_title(jd_text),
            'required_skills': self.extract_required_skills(jd_text),
            'experience_required': self.extract_experience_required(jd_text),
            'education_required': self.extract_education_required(jd_text),
            'seniority_level': self.determine_seniority_level(jd_text),
            'responsibilities': self.extract_responsibilities(jd_text)
        }


# Test code - only runs when executed directly
if __name__ == "__main__":
    # Sample job description for testing
    sample_jd = """
    Senior Machine Learning Engineer
    
    We are looking for a Senior ML Engineer with 5+ years of experience.
    
    Requirements:
    - Bachelor's degree in Computer Science
    - Strong skills in Python, TensorFlow, PyTorch
    - Experience with Docker, Kubernetes
    - Knowledge of AWS cloud services
    
    Responsibilities:
    - Design and implement ML models
    - Collaborate with cross-functional teams
    - Optimize model performance
    """
    
    processor = JobDescriptionProcessor()
    result = processor.process_job_description(sample_jd)
    
    print("Job Description Analysis Results:")
    print("=" * 50)
    for key, value in result.items():
        print(f"\n{key.replace('_', ' ').title()}:")
        if isinstance(value, list):
            for item in value:
                print(f"  - {item}")
        else:
            print(f"  {value}")