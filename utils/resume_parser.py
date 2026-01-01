"""
Minimal AI Resume Parser using Groq API
"""

import re
import json
import os
from typing import Dict, List, Optional


class ResumeParser:
    """
    AI-Powered Resume Parser using Groq API
    
    Usage:
        parser = ResumeParser(api_key="your-groq-api-key")
        result = parser.parse_resume(resume_text)
    """
    
    def __init__(self, api_key: Optional[str] = "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", model: str = "llama-3.1-8b-instant"):
        """
        Initialize parser with Groq API
        
        Args:
            api_key: Groq API key (or set GROQ_API_KEY env var)
            model: Model name (llama-3.1-8b-instant, mixtral-8x7b-32768, gemma2-9b-it)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("Groq API key required. Get free key at https://console.groq.com")
        
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            raise ImportError("Install groq: pip install groq")
    
    def _query(self, prompt: str, text: str) -> str:
        """Send query to Groq API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Extract information from resumes. Return valid JSON only."},
                {"role": "user", "content": f"{prompt}\n\nResume:\n{text}"}
            ],
            temperature=0.1,
            max_tokens=1024
        )
        return response.choices[0].message.content # type: ignore
    
    def _parse_json(self, response: str) -> Dict:
        """Parse JSON from response"""
        try:
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                return json.loads(match.group())
        except json.JSONDecodeError:
            pass
        return {}
    
    def parse_resume(self, text: str) -> Dict:
        """
        Parse complete resume
        
        Returns dict with: name, email, phone, location, summary, skills,
        education, experience, total_years_experience, certifications, projects
        """
        prompt = """Extract from this resume and return JSON:
{
    "name": "string",
    "email": "string", 
    "phone": "string",
    "location": "string",
    "summary": "1-2 sentence summary",
    "skills": ["skill1", "skill2"],
    "education": [{"degree": "", "institution": "", "year": ""}],
    "experience": [{"title": "", "company": "", "duration": "", "years": 0, "responsibilities": []}],
    "total_years_experience": 0,
    "certifications": ["cert1"],
    "projects": [{"name": "", "description": "", "technologies": []}]
}
Return JSON only. Use null for missing fields."""

        result = self._parse_json(self._query(prompt, text))
        
        # Ensure all fields exist with defaults
        defaults = {
            "name": None, "email": None, "phone": None, "location": None,
            "summary": None, "skills": [], "education": [], "experience": [],
            "total_years_experience": None, "certifications": [], "projects": []
        }
        
        return {**defaults, **result}
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name"""
        prompt = 'Extract the person\'s full name. Return: {"name": "Full Name"}'
        return self._parse_json(self._query(prompt, text)).get("name")
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        prompt = 'Extract email address. Return: {"email": "email@example.com"}'
        return self._parse_json(self._query(prompt, text)).get("email")
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        prompt = 'Extract phone number. Return: {"phone": "number"}'
        return self._parse_json(self._query(prompt, text)).get("phone")
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract all skills"""
        prompt = 'Extract all technical and professional skills. Return: {"skills": ["skill1", "skill2"]}'
        return self._parse_json(self._query(prompt, text)).get("skills", [])
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education history"""
        prompt = '''Extract education. Return: {"education": [{"degree": "", "institution": "", "year": "", "gpa": ""}]}'''
        return self._parse_json(self._query(prompt, text)).get("education", [])
    
    def extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        prompt = '''Extract work experience. Return: {"experience": [{"title": "", "company": "", "duration": "", "years": 0, "responsibilities": []}]}'''
        return self._parse_json(self._query(prompt, text)).get("experience", [])
    
    def extract_years_of_experience(self, text: str) -> Optional[float]:
        """Extract total years of experience"""
        prompt = 'Calculate total years of professional experience. Return: {"years": 0}'
        result = self._parse_json(self._query(prompt, text)).get("years")
        try:
            return float(result) if result else None
        except (ValueError, TypeError):
            return None
    
    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        prompt = 'Extract all certifications. Return: {"certifications": ["cert1", "cert2"]}'
        return self._parse_json(self._query(prompt, text)).get("certifications", [])
    
    def extract_projects(self, text: str) -> List[Dict]:
        """Extract projects"""
        prompt = '''Extract projects. Return: {"projects": [{"name": "", "description": "", "technologies": []}]}'''
        return self._parse_json(self._query(prompt, text)).get("projects", [])
    
    def extract_summary(self, text: str) -> Optional[str]:
        """Extract or generate professional summary"""
        prompt = 'Extract or generate a 2-sentence professional summary. Return: {"summary": "text"}'
        return self._parse_json(self._query(prompt, text)).get("summary")
    
    def match_job(self, resume_text: str, job_description: str) -> Dict:
        """
        Match resume against job description
        
        Returns: match_score, matching_skills, missing_skills, recommendation
        """
        prompt = f"""Compare this resume to the job description and return:
{{
    "match_score": 0-100,
    "matching_skills": ["matched skills"],
    "missing_skills": ["missing required skills"],
    "recommendation": "brief hiring recommendation"
}}

Job Description:
{job_description}

Return JSON only."""
        
        result = self._parse_json(self._query(prompt, resume_text))
        defaults = {"match_score": 0, "matching_skills": [], "missing_skills": [], "recommendation": ""}
        return {**defaults, **result}


# Example usage
if __name__ == "__main__":
    sample_resume = """
    John Smith
    Software Engineer | john.smith@email.com | (555) 123-4567 | San Francisco, CA
    
    SUMMARY
    Senior software engineer with 5+ years building scalable web applications.
    
    SKILLS
    Python, JavaScript, React, Node.js, PostgreSQL, AWS, Docker, Kubernetes
    
    EXPERIENCE
    Senior Software Engineer | Tech Corp | 2021 - Present
    - Led microservices development for 1M+ users
    - Mentored 5 junior developers
    
    Software Engineer | StartupXYZ | 2019 - 2021
    - Built React frontend for e-commerce platform
    - Implemented CI/CD with GitHub Actions
    
    EDUCATION
    BS Computer Science | UC Berkeley | 2018 | GPA: 3.7
    
    CERTIFICATIONS
    AWS Certified Solutions Architect, Google Cloud Developer
    
    PROJECTS
    - E-commerce Platform: Full-stack app with React/Node.js
    """
    
    # Initialize parser
    parser = ResumeParser()  # Uses GROQ_API_KEY env var
    
    # Parse full resume
    print("=== Full Parse ===")
    result = parser.parse_resume(sample_resume)
    print(json.dumps(result, indent=2))
    
    # Individual extractions
    print("\n=== Individual Extractions ===")
    print(f"Name: {parser.extract_name(sample_resume)}")
    print(f"Email: {parser.extract_email(sample_resume)}")
    print(f"Skills: {parser.extract_skills(sample_resume)}")
    print(f"Years: {parser.extract_years_of_experience(sample_resume)}")
    
    # Job matching
    print("\n=== Job Match ===")
    job_desc = "Looking for Python developer with 3+ years experience, AWS knowledge, and React skills."
    match = parser.match_job(sample_resume, job_desc)
    print(json.dumps(match, indent=2))