"""
AI Resume Analyzer & Job Fit Scorer - Flask Backend
A production-ready AI application for resume analysis
Author: Nitesh - AI Engineer

Run this command to install dependencies: 
pip install -r requirements.txt
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
from typing import Dict, List, Any, Union
import json
from werkzeug.utils import secure_filename

# Import utilities
from utils.text_extractor import extract_text_from_file, clean_text
from utils.resume_parser import ResumeParser
from utils.jd_processor import JobDescriptionProcessor
from utils.skill_extractor import SkillExtractor
from utils.similarity import calculate_similarity

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize components
resume_parser = ResumeParser()
jd_processor = JobDescriptionProcessor()
skill_extractor = SkillExtractor()


# ============================================
# UTILITY FUNCTIONS
# ============================================

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def format_education(education_list: List[Any]) -> List[str]:
    """
    Format education list to readable strings
    Handles both string and dictionary formats
    """
    formatted = []
    
    if not education_list:
        return ['Not specified']
    
    for edu in education_list:
        if isinstance(edu, str):
            # Already a string, just append
            formatted.append(edu)
        elif isinstance(edu, dict):
            # Build education string from dictionary
            parts = []
            
            # Degree/Qualification
            degree = edu.get('degree') or edu.get('qualification') or edu.get('title') or ''
            if degree:
                parts.append(str(degree))
            
            # Field of study
            field = edu.get('field') or edu.get('major') or edu.get('specialization') or ''
            if field:
                parts.append(f"in {field}")
            
            # Institution
            institution = edu.get('institution') or edu.get('university') or edu.get('college') or edu.get('school') or ''
            if institution:
                parts.append(f"from {institution}")
            
            # Year/Duration
            year = edu.get('year') or edu.get('graduation_year') or edu.get('end_date') or ''
            start_year = edu.get('start_year') or edu.get('start_date') or ''
            
            if start_year and year:
                parts.append(f"({start_year} - {year})")
            elif year:
                parts.append(f"({year})")
            
            # GPA/Grade
            gpa = edu.get('gpa') or edu.get('grade') or edu.get('cgpa') or ''
            if gpa:
                parts.append(f"- GPA: {gpa}")
            
            if parts:
                formatted.append(' '.join(parts))
            else:
                # If no known keys, try to convert the whole dict to readable format
                edu_str = ', '.join([f"{k}: {v}" for k, v in edu.items() if v])
                if edu_str:
                    formatted.append(edu_str)
        else:
            formatted.append(str(edu))
    
    return formatted if formatted else ['Not specified']


def format_projects(projects_list: List[Any]) -> List[Dict[str, str]]:
    """
    Format projects list to readable format
    Returns list of dictionaries with name, description, technologies, duration, and link
    """
    formatted = []
    
    if not projects_list:
        return []
    
    for project in projects_list:
        if isinstance(project, str):
            # If it's a string, create a basic project dict
            formatted.append({
                'name': project,
                'description': '',
                'technologies': '',
                'duration': '',
                'link': ''
            })
        elif isinstance(project, dict):
            # Extract project information from dictionary
            name = (project.get('name') or 
                   project.get('title') or 
                   project.get('project_name') or 
                   project.get('project') or
                   'Unnamed Project')
            
            description = (project.get('description') or 
                          project.get('details') or 
                          project.get('summary') or 
                          project.get('about') or
                          '')
            
            # Handle technologies - could be list or string
            technologies = (project.get('technologies') or 
                           project.get('tech_stack') or 
                           project.get('tools') or 
                           project.get('tech') or
                           project.get('skills') or
                           '')
            if isinstance(technologies, list):
                technologies = ', '.join(str(t) for t in technologies)
            
            # Handle duration/date
            duration = (project.get('duration') or 
                       project.get('date') or 
                       project.get('period') or 
                       project.get('timeline') or
                       '')
            
            # Handle link/URL
            link = (project.get('link') or 
                   project.get('url') or 
                   project.get('github') or 
                   project.get('demo') or
                   project.get('repository') or
                   '')
            
            formatted.append({
                'name': str(name),
                'description': str(description),
                'technologies': str(technologies),
                'duration': str(duration),
                'link': str(link)
            })
        else:
            formatted.append({
                'name': str(project),
                'description': '',
                'technologies': '',
                'duration': '',
                'link': ''
            })
    
    return formatted


def format_experience(experience_list: List[Any]) -> List[Dict[str, str]]:
    """
    Format experience list to readable format
    Returns list of dictionaries with company, role, duration, description, and location
    """
    formatted = []
    
    if not experience_list:
        return []
    
    for exp in experience_list:
        if isinstance(exp, str):
            # If it's a string, create a basic experience dict
            formatted.append({
                'company': '',
                'role': exp,
                'duration': '',
                'description': '',
                'location': ''
            })
        elif isinstance(exp, dict):
            # Extract experience information from dictionary
            company = (exp.get('company') or 
                      exp.get('organization') or 
                      exp.get('employer') or 
                      exp.get('company_name') or
                      '')
            
            role = (exp.get('role') or 
                   exp.get('title') or 
                   exp.get('position') or 
                   exp.get('designation') or 
                   exp.get('job_title') or
                   '')
            
            # Handle duration
            duration = exp.get('duration') or ''
            start_date = exp.get('start_date') or exp.get('from') or exp.get('start') or ''
            end_date = exp.get('end_date') or exp.get('to') or exp.get('end') or 'Present'
            
            if not duration and start_date:
                duration = f"{start_date} - {end_date}"
            
            description = (exp.get('description') or 
                          exp.get('responsibilities') or 
                          exp.get('details') or 
                          exp.get('summary') or
                          '')
            
            # Handle responsibilities list
            if isinstance(description, list):
                description = ' | '.join(str(d) for d in description)
            
            location = (exp.get('location') or 
                       exp.get('city') or 
                       exp.get('place') or
                       '')
            
            formatted.append({
                'company': str(company),
                'role': str(role),
                'duration': str(duration),
                'description': str(description),
                'location': str(location)
            })
        else:
            formatted.append({
                'company': '',
                'role': str(exp),
                'duration': '',
                'description': '',
                'location': ''
            })
    
    return formatted


def format_certifications(cert_list: List[Any]) -> List[str]:
    """
    Format certifications list to readable strings
    Handles both string and dictionary formats
    """
    formatted = []
    
    if not cert_list:
        return []
    
    for cert in cert_list:
        if isinstance(cert, str):
            # Already a string, just append
            formatted.append(cert)
        elif isinstance(cert, dict):
            # Build certification string from dictionary
            parts = []
            
            # Certificate name/title
            name = (cert.get('name') or 
                   cert.get('title') or 
                   cert.get('certification') or 
                   cert.get('certificate') or
                   cert.get('course') or
                   '')
            if name:
                parts.append(str(name))
            
            # Issuing organization
            issuer = (cert.get('issuer') or 
                     cert.get('organization') or 
                     cert.get('provider') or 
                     cert.get('issued_by') or
                     cert.get('platform') or
                     '')
            if issuer:
                parts.append(f"by {issuer}")
            
            # Year/Date
            year = (cert.get('year') or 
                   cert.get('date') or 
                   cert.get('issued_date') or
                   cert.get('completion_date') or
                   '')
            if year:
                parts.append(f"({year})")
            
            # Credential ID (if available)
            credential_id = cert.get('credential_id') or cert.get('id') or ''
            if credential_id:
                parts.append(f"[ID: {credential_id}]")
            
            if parts:
                formatted.append(' '.join(parts))
            else:
                # Convert dict to readable string
                cert_str = ', '.join([f"{k}: {v}" for k, v in cert.items() if v])
                if cert_str:
                    formatted.append(cert_str)
        else:
            formatted.append(str(cert))
    
    return formatted


def predict_job_roles(skills: List[str]) -> List[str]:
    """Predict suitable job roles based on skills"""
    roles = []
    skills_lower = [s.lower() for s in skills]
    
    # AI/ML roles
    ai_ml_skills = ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'nlp', 
                    'computer vision', 'artificial intelligence', 'neural networks', 'keras',
                    'scikit-learn', 'opencv', 'transformers', 'huggingface']
    if any(skill in skills_lower for skill in ai_ml_skills):
        roles.extend(["Machine Learning Engineer", "AI Engineer"])
        if 'nlp' in skills_lower or 'natural language processing' in skills_lower:
            roles.append("NLP Engineer")
        if 'computer vision' in skills_lower or 'opencv' in skills_lower:
            roles.append("Computer Vision Engineer")
    
    # Data Science roles
    ds_skills = ['data analysis', 'pandas', 'numpy', 'statistics', 'data visualization', 
                 'tableau', 'power bi', 'matplotlib', 'seaborn', 'data science', 'r programming']
    if any(skill in skills_lower for skill in ds_skills):
        roles.extend(["Data Scientist", "Data Analyst"])
    
    # Data Engineering roles
    de_skills = ['apache spark', 'hadoop', 'airflow', 'etl', 'data pipeline', 
                 'kafka', 'data warehouse', 'bigquery', 'snowflake', 'databricks']
    if any(skill in skills_lower for skill in de_skills):
        roles.append("Data Engineer")
    
    # Backend roles
    backend_skills = ['python', 'java', 'node.js', 'django', 'flask', 'fastapi', 
                      'spring boot', 'express.js', 'ruby on rails', 'golang', 'rust',
                      '.net', 'c#', 'php', 'laravel']
    if any(skill in skills_lower for skill in backend_skills):
        roles.extend(["Backend Developer", "Software Engineer"])
    
    # Frontend roles
    frontend_skills = ['react', 'angular', 'vue.js', 'javascript', 'typescript', 
                       'html', 'css', 'next.js', 'svelte', 'tailwind', 'bootstrap',
                       'sass', 'redux', 'webpack']
    if any(skill in skills_lower for skill in frontend_skills):
        roles.extend(["Frontend Developer", "UI Developer"])
    
    # Full Stack
    backend_match = any(skill in skills_lower for skill in backend_skills)
    frontend_match = any(skill in skills_lower for skill in frontend_skills)
    if backend_match and frontend_match:
        roles.append("Full Stack Developer")
    
    # DevOps roles
    devops_skills = ['docker', 'kubernetes', 'aws', 'azure', 'ci/cd', 'jenkins', 
                     'terraform', 'ansible', 'gcp', 'linux', 'devops', 'helm',
                     'prometheus', 'grafana', 'nginx']
    if any(skill in skills_lower for skill in devops_skills):
        roles.extend(["DevOps Engineer", "Cloud Engineer", "SRE"])
    
    # Mobile Development
    mobile_skills = ['android', 'ios', 'flutter', 'react native', 'swift', 'kotlin',
                     'xamarin', 'ionic', 'mobile development']
    if any(skill in skills_lower for skill in mobile_skills):
        roles.append("Mobile Developer")
    
    # Security roles
    security_skills = ['cybersecurity', 'penetration testing', 'security', 'ethical hacking', 
                       'siem', 'soc', 'vulnerability assessment', 'network security']
    if any(skill in skills_lower for skill in security_skills):
        roles.append("Security Engineer")
    
    # Database roles
    db_skills = ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'database', 'oracle',
                 'cassandra', 'elasticsearch', 'dynamodb']
    if any(skill in skills_lower for skill in db_skills) and len(roles) == 0:
        roles.append("Database Administrator")
    
    # QA/Testing roles
    qa_skills = ['selenium', 'testing', 'qa', 'automation testing', 'cypress', 'jest',
                 'junit', 'test automation', 'quality assurance']
    if any(skill in skills_lower for skill in qa_skills):
        roles.append("QA Engineer")
    
    # Product/Project Management
    pm_skills = ['agile', 'scrum', 'jira', 'product management', 'project management']
    if any(skill in skills_lower for skill in pm_skills):
        roles.append("Technical Project Manager")
    
    return list(set(roles))[:8] if roles else ["Software Engineer", "Technical Consultant"]


def identify_strengths(resume_skills: List[str], jd_skills: List[str]) -> List[str]:
    """Identify key strengths from resume"""
    strengths = []
    resume_skills_lower = [s.lower() for s in resume_skills]
    jd_skills_lower = [s.lower() for s in jd_skills]
    
    matching_skills = [skill for skill in resume_skills if skill.lower() in jd_skills_lower]
    
    high_value_skills = [
        'machine learning', 'deep learning', 'aws', 'kubernetes', 'docker',
        'tensorflow', 'pytorch', 'react', 'node.js', 'python', 'java',
        'sql', 'mongodb', 'azure', 'gcp', 'javascript', 'typescript',
        'data analysis', 'nlp', 'computer vision', 'api development',
        'microservices', 'system design', 'agile', 'ci/cd'
    ]
    
    for skill in resume_skills:
        if skill.lower() in high_value_skills and skill not in matching_skills:
            strengths.append(skill)
    
    strengths.extend(matching_skills)
    return list(set(strengths))[:10]


def generate_improvement_suggestions(missing_skills: List[str], matched_skills: List[str], 
                                     overall_score: float) -> List[str]:
    """Generate personalized improvement suggestions"""
    suggestions = []
    
    if overall_score < 60:
        suggestions.append("Consider taking online courses to build missing technical skills")
        suggestions.append("Work on personal projects that demonstrate the required skills")
    
    if missing_skills:
        top_missing = missing_skills[:3]
        suggestions.append(f"Focus on learning: {', '.join(top_missing)}")
    
    if len(matched_skills) < 5:
        suggestions.append("Add more relevant keywords from the job description to your resume")
    
    suggestions.append("Quantify your achievements with metrics where possible")
    suggestions.append("Tailor your resume summary to match the job requirements")
    
    return suggestions[:5]


# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index_old.html')


@app.route('/old')
def index_old():
    """Serve the old HTML page"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    """Main API endpoint for resume analysis"""
    try:
        # Check if file is present
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        file = request.files['resume']
        job_description = request.form.get('job_description', '')
        
        # Validate inputs
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not job_description or len(job_description) < 50:
            return jsonify({'error': 'Job description must be at least 50 characters'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Allowed: PDF, DOCX, DOC, TXT'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text from resume
            with open(filepath, 'rb') as f:
                resume_text = extract_text_from_file(f)
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
        
        if not resume_text or len(resume_text) < 100:
            return jsonify({'error': 'Could not extract sufficient text from resume'}), 400
        
        # Clean texts
        clean_resume = clean_text(resume_text)
        clean_jd = clean_text(job_description)
        
        # ============================================
        # USE RESUME PARSER WITH CORRECT API
        # ============================================
        
        # Parse full resume (returns complete parsed data)
        resume_data = resume_parser.parse_resume(resume_text)
        
        # Individual extractions using the correct parser methods
        name = resume_parser.extract_name(resume_text)
        email = resume_parser.extract_email(resume_text)
        phone = resume_parser.extract_phone(resume_text)
        resume_skills = resume_parser.extract_skills(resume_text)
        education_raw = resume_parser.extract_education(resume_text)
        experience_raw = resume_parser.extract_experience(resume_text)
        years_of_experience = resume_parser.extract_years_of_experience(resume_text)
        certifications_raw = resume_parser.extract_certifications(resume_text)
        projects_raw = resume_parser.extract_projects(resume_text)
        summary = resume_parser.extract_summary(resume_text)
        
        # Format complex data structures to readable formats
        education_formatted = format_education(education_raw)
        experience_formatted = format_experience(experience_raw)
        projects_formatted = format_projects(projects_raw)
        certifications_formatted = format_certifications(certifications_raw)
        
        # Match against job description using parser's built-in method
        job_match = resume_parser.match_job(resume_text, job_description)
        
        # ============================================
        # Process job description
        # ============================================
        jd_data = jd_processor.process_job_description(job_description)
        jd_skills = jd_data.get('required_skills', [])
        
        # Also use skill_extractor for additional analysis
        additional_resume_skills = skill_extractor.extract_skills(resume_text)
        
        # Combine skills from both sources (remove duplicates)
        all_resume_skills = list(set(resume_skills + additional_resume_skills))
        
        # Calculate similarity
        similarity_scores = calculate_similarity(clean_resume, clean_jd, all_resume_skills, jd_skills)
        
        # Find matched and missing skills
        matched_skills = skill_extractor.find_matching_skills(all_resume_skills, jd_skills)
        missing_skills = skill_extractor.find_missing_skills(all_resume_skills, jd_skills)
        
        # Identify strengths
        strengths = identify_strengths(all_resume_skills, jd_skills)
        
        # Predict job roles
        predicted_roles = predict_job_roles(all_resume_skills)
        
        # Get skill suggestions
        skill_suggestions = skill_extractor.suggest_related_skills(all_resume_skills)
        
        # Calculate match rate
        match_rate = (len(matched_skills) / len(jd_skills) * 100) if jd_skills else 0
        
        # Use job_match score if available, otherwise use calculated score
        if isinstance(job_match, dict) and 'score' in job_match:
            overall_score = job_match['score']
        else:
            overall_score = similarity_scores['overall_score']
        
        # Ensure overall_score is a number
        if not isinstance(overall_score, (int, float)):
            overall_score = similarity_scores['overall_score']
        
        # Generate recommendations
        if overall_score >= 80:
            recommendation = {
                'level': 'excellent',
                'message': 'Excellent Match! Your resume is highly aligned with this job description.',
                'advice': 'You should definitely apply! Make sure to highlight your matching skills in your cover letter.',
                'color': '#28a745'
            }
        elif overall_score >= 60:
            recommendation = {
                'level': 'good',
                'message': 'Good Match! Your profile shows good alignment with the job requirements.',
                'advice': 'Consider emphasizing your matched skills and learning the missing skills if possible.',
                'color': '#ffc107'
            }
        elif overall_score >= 40:
            recommendation = {
                'level': 'moderate',
                'message': 'Moderate Match. There are some gaps between your profile and job requirements.',
                'advice': 'Focus on building the missing skills through projects, courses, and certifications.',
                'color': '#fd7e14'
            }
        else:
            recommendation = {
                'level': 'needs_improvement',
                'message': 'Needs Improvement. There is a significant gap between your profile and job requirements.',
                'advice': 'Consider gaining more experience in the required skills before applying.',
                'color': '#dc3545'
            }
        
        # Generate improvement suggestions
        improvement_suggestions = generate_improvement_suggestions(
            missing_skills, matched_skills, overall_score
        )
        
        # Prepare response with properly formatted data
        response = {
            'success': True,
            'scores': {
                'overall_score': round(overall_score, 2),
                'semantic_similarity': round(similarity_scores.get('semantic_similarity', 0), 2),
                'skill_match': round(similarity_scores.get('skill_match', 0), 2),
                'keyword_match': round(similarity_scores.get('keyword_match', 0), 2) if 'keyword_match' in similarity_scores else None,
                'match_rate': round(match_rate, 2)
            },
            'skills': {
                'resume_skills': all_resume_skills,
                'jd_skills': jd_skills,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'strengths': strengths,
                'suggestions': list(set(skill_suggestions + missing_skills[:5]))[:8]
            },
            'resume_data': {
                'name': name if name else 'Not found',
                'email': email if email else 'Not found',
                'phone': phone if phone else 'Not found',
                'years_of_experience': years_of_experience if years_of_experience else 'Not specified',
                'experience': experience_formatted,
                'education': education_formatted,
                'certifications': certifications_formatted,
                'projects': projects_formatted,
                'summary': summary if summary else 'Not available'
            },
            'jd_data': {
                'job_title': jd_data.get('job_title', 'Not specified'),
                'company': jd_data.get('company', 'Not specified'),
                'seniority_level': jd_data.get('seniority_level', 'Not specified'),
                'experience_required': jd_data.get('experience_required', 'Not specified'),
                'skills_count': len(jd_skills),
                'location': jd_data.get('location', 'Not specified')
            },
            'job_match': job_match if isinstance(job_match, dict) else {'score': overall_score},
            'predicted_roles': predicted_roles[:6],
            'recommendation': recommendation,
            'improvement_suggestions': improvement_suggestions,
            'resume_preview': resume_text[:500] + '...' if len(resume_text) > 500 else resume_text,
            'jd_preview': job_description[:500] + '...' if len(job_description) > 500 else job_description
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500


@app.route('/api/parse-resume', methods=['POST'])
def parse_resume_only():
    """API endpoint for parsing resume without job matching"""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        file = request.files['resume']
        
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Allowed: PDF, DOCX, DOC, TXT'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text from resume
            with open(filepath, 'rb') as f:
                resume_text = extract_text_from_file(f)
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
        
        if not resume_text or len(resume_text) < 100:
            return jsonify({'error': 'Could not extract sufficient text from resume'}), 400
        
        # Extract all data using parser methods
        name = resume_parser.extract_name(resume_text)
        email = resume_parser.extract_email(resume_text)
        phone = resume_parser.extract_phone(resume_text)
        skills = resume_parser.extract_skills(resume_text)
        education_raw = resume_parser.extract_education(resume_text)
        experience_raw = resume_parser.extract_experience(resume_text)
        years_of_experience = resume_parser.extract_years_of_experience(resume_text)
        certifications_raw = resume_parser.extract_certifications(resume_text)
        projects_raw = resume_parser.extract_projects(resume_text)
        summary = resume_parser.extract_summary(resume_text)
        
        # Format the data
        education_formatted = format_education(education_raw)
        experience_formatted = format_experience(experience_raw)
        projects_formatted = format_projects(projects_raw)
        certifications_formatted = format_certifications(certifications_raw)
        
        # Parse resume using all available methods with proper formatting
        response = {
            'success': True,
            'parsed_data': resume_parser.parse_resume(resume_text),
            'extracted_fields': {
                'name': name if name else 'Not found',
                'email': email if email else 'Not found',
                'phone': phone if phone else 'Not found',
                'skills': skills,
                'education': education_formatted,
                'experience': experience_formatted,
                'years_of_experience': years_of_experience if years_of_experience else 'Not specified',
                'certifications': certifications_formatted,
                'projects': projects_formatted,
                'summary': summary if summary else 'Not available'
            },
            'predicted_roles': predict_job_roles(skills),
            'resume_preview': resume_text[:500] + '...' if len(resume_text) > 500 else resume_text
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500


@app.route('/api/match-job', methods=['POST'])
def match_job_only():
    """API endpoint for matching resume against job description"""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        file = request.files['resume']
        job_description = request.form.get('job_description', '')
        
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not job_description or len(job_description) < 50:
            return jsonify({'error': 'Job description must be at least 50 characters'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Allowed: PDF, DOCX, DOC, TXT'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text from resume
            with open(filepath, 'rb') as f:
                resume_text = extract_text_from_file(f)
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
        
        if not resume_text or len(resume_text) < 100:
            return jsonify({'error': 'Could not extract sufficient text from resume'}), 400
        
        # Use parser's match_job method directly
        job_match = resume_parser.match_job(resume_text, job_description)
        
        # Also get skills comparison
        resume_skills = resume_parser.extract_skills(resume_text)
        jd_data = jd_processor.process_job_description(job_description)
        jd_skills = jd_data.get('required_skills', [])
        
        matched_skills = skill_extractor.find_matching_skills(resume_skills, jd_skills)
        missing_skills = skill_extractor.find_missing_skills(resume_skills, jd_skills)
        
        response = {
            'success': True,
            'match_result': job_match,
            'skills_comparison': {
                'resume_skills': resume_skills,
                'jd_skills': jd_skills,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'match_rate': round((len(matched_skills) / len(jd_skills) * 100), 2) if jd_skills else 0
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500


@app.route('/api/extract-skills', methods=['POST'])
def extract_skills_only():
    """API endpoint for extracting skills from text"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        
        if len(text) < 20:
            return jsonify({'error': 'Text too short'}), 400
        
        # Extract skills using both methods
        parser_skills = resume_parser.extract_skills(text)
        extractor_skills = skill_extractor.extract_skills(text)
        
        # Combine and deduplicate
        all_skills = list(set(parser_skills + extractor_skills))
        
        response = {
            'success': True,
            'skills': all_skills,
            'count': len(all_skills),
            'predicted_roles': predict_job_roles(all_skills)
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500


@app.route('/api/compare-resumes', methods=['POST'])
def compare_resumes():
    """API endpoint for comparing multiple resumes against a job description"""
    try:
        if 'resumes' not in request.files:
            return jsonify({'error': 'No resume files uploaded'}), 400
        
        files = request.files.getlist('resumes')
        job_description = request.form.get('job_description', '')
        
        if not job_description or len(job_description) < 50:
            return jsonify({'error': 'Job description must be at least 50 characters'}), 400
        
        if len(files) < 2:
            return jsonify({'error': 'Please upload at least 2 resumes to compare'}), 400
        
        if len(files) > 10:
            return jsonify({'error': 'Maximum 10 resumes allowed'}), 400
        
        results = []
        
        for file in files:
            if not file.filename:
                continue
            
            if not allowed_file(file.filename):
                continue
            
            # Save file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Extract text from resume
                with open(filepath, 'rb') as f:
                    resume_text = extract_text_from_file(f)
                
                if not resume_text or len(resume_text) < 100:
                    continue
                
                # Get basic info and match
                name = resume_parser.extract_name(resume_text)
                email = resume_parser.extract_email(resume_text)
                phone = resume_parser.extract_phone(resume_text)
                skills = resume_parser.extract_skills(resume_text)
                experience = resume_parser.extract_years_of_experience(resume_text)
                certifications_raw = resume_parser.extract_certifications(resume_text)
                projects_raw = resume_parser.extract_projects(resume_text)
                job_match = resume_parser.match_job(resume_text, job_description)
                
                score = job_match.get('score', 0) if isinstance(job_match, dict) else 0
                
                # Format certifications and projects
                certifications_formatted = format_certifications(certifications_raw)
                projects_formatted = format_projects(projects_raw)
                
                results.append({
                    'filename': file.filename,
                    'name': name if name else 'Unknown',
                    'email': email if email else 'Not found',
                    'phone': phone if phone else 'Not found',
                    'years_of_experience': experience if experience else 'Not specified',
                    'skills_count': len(skills),
                    'score': round(score, 2),
                    'skills': skills[:10],
                    'certifications_count': len(certifications_formatted),
                    'projects_count': len(projects_formatted)
                })
                
            finally:
                # Clean up
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Add ranking
        for i, result in enumerate(results):
            result['rank'] = i + 1
        
        response = {
            'success': True,
            'results': results,
            'total_resumes': len(results),
            'job_description_preview': job_description[:200] + '...' if len(job_description) > 200 else job_description
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Resume Analyzer API is running',
        'version': '1.0.0',
        'author': 'Nitesh - AI Engineer',
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'Main application'},
            {'path': '/api/analyze', 'method': 'POST', 'description': 'Analyze resume against job description'},
            {'path': '/api/parse-resume', 'method': 'POST', 'description': 'Parse resume only'},
            {'path': '/api/match-job', 'method': 'POST', 'description': 'Match resume with job description'},
            {'path': '/api/extract-skills', 'method': 'POST', 'description': 'Extract skills from text'},
            {'path': '/api/compare-resumes', 'method': 'POST', 'description': 'Compare multiple resumes'},
            {'path': '/api/health', 'method': 'GET', 'description': 'Health check'},
            {'path': '/api/supported-formats', 'method': 'GET', 'description': 'List supported formats'}
        ]
    }), 200


@app.route('/api/supported-formats', methods=['GET'])
def supported_formats():
    """Return supported file formats"""
    return jsonify({
        'success': True,
        'formats': list(ALLOWED_EXTENSIONS),
        'max_file_size': '5MB',
        'max_file_size_bytes': MAX_FILE_SIZE
    }), 200


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad Request',
        'message': str(error),
        'success': False
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'success': False
    }), 404


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'error': 'File Too Large',
        'message': 'The uploaded file exceeds the maximum size of 5MB',
        'success': False
    }), 413


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'success': False
    }), 500


# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("\n🚀 Starting server...")
    
    app.run(debug=True, host='0.0.0.0', port=5000)