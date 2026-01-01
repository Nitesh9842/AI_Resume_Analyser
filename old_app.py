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
from typing import Dict, List
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


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def predict_job_roles(skills: List[str]) -> List[str]:
    """Predict suitable job roles based on skills"""
    roles = []
    skills_lower = [s.lower() for s in skills]
    
    # AI/ML roles
    ai_ml_skills = ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'nlp', 'computer vision']
    if any(skill in skills_lower for skill in ai_ml_skills):
        roles.extend(["Machine Learning Engineer", "AI Engineer"])
        if 'nlp' in skills_lower:
            roles.append("NLP Engineer")
        if 'computer vision' in skills_lower:
            roles.append("Computer Vision Engineer")
    
    # Data Science roles
    ds_skills = ['data analysis', 'pandas', 'numpy', 'statistics', 'data visualization']
    if any(skill in skills_lower for skill in ds_skills):
        roles.extend(["Data Scientist", "Data Analyst"])
    
    # Backend roles
    backend_skills = ['python', 'java', 'node.js', 'django', 'flask', 'fastapi', 'spring boot']
    if any(skill in skills_lower for skill in backend_skills):
        roles.extend(["Backend Developer", "Full Stack Developer"])
    
    # Frontend roles
    frontend_skills = ['react', 'angular', 'vue.js', 'javascript', 'typescript', 'html', 'css']
    if any(skill in skills_lower for skill in frontend_skills):
        roles.extend(["Frontend Developer", "Full Stack Developer"])
    
    # DevOps roles
    devops_skills = ['docker', 'kubernetes', 'aws', 'azure', 'ci/cd', 'jenkins', 'terraform']
    if any(skill in skills_lower for skill in devops_skills):
        roles.extend(["DevOps Engineer", "Cloud Engineer"])
    
    return list(set(roles)) if roles else ["Software Engineer", "Technical Consultant"]


def identify_strengths(resume_skills: List[str], jd_skills: List[str]) -> List[str]:
    """Identify key strengths from resume"""
    strengths = []
    resume_skills_lower = [s.lower() for s in resume_skills]
    jd_skills_lower = [s.lower() for s in jd_skills]
    
    matching_skills = [skill for skill in resume_skills if skill.lower() in jd_skills_lower]
    
    high_value_skills = [
        'machine learning', 'deep learning', 'aws', 'kubernetes', 'docker',
        'tensorflow', 'pytorch', 'react', 'node.js', 'python', 'java'
    ]
    
    for skill in resume_skills:
        if skill.lower() in high_value_skills and skill not in matching_skills:
            strengths.append(skill)
    
    strengths.extend(matching_skills)
    return list(set(strengths))[:10]


@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index_old.html')


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
        
        # Extract text from resume
        with open(filepath, 'rb') as f:
            resume_text = extract_text_from_file(f)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        if not resume_text or len(resume_text) < 100:
            return jsonify({'error': 'Could not extract sufficient text from resume'}), 400
        
        # Clean texts
        clean_resume = clean_text(resume_text)
        clean_jd = clean_text(job_description)
        
        # Parse resume
        resume_data = resume_parser.parse_resume(resume_text)

        # Process job description
        jd_data = jd_processor.process_job_description(job_description)
        
        # Extract skills
        resume_skills = skill_extractor.extract_skills(resume_text)
        jd_skills = jd_data['required_skills']
        
        # Calculate similarity
        similarity_scores = calculate_similarity(clean_resume, clean_jd, resume_skills, jd_skills)
        
        # Find matched and missing skills
        matched_skills = skill_extractor.find_matching_skills(resume_skills, jd_skills)
        missing_skills = skill_extractor.find_missing_skills(resume_skills, jd_skills)
        
        # Identify strengths
        strengths = identify_strengths(resume_skills, jd_skills)
        
        # Predict job roles
        predicted_roles = predict_job_roles(resume_skills)
        
        # Get skill suggestions
        skill_suggestions = skill_extractor.suggest_related_skills(resume_skills)
        
        # Calculate match rate
        match_rate = (len(matched_skills) / len(jd_skills) * 100) if jd_skills else 0
        
        # Generate recommendations
        overall_score = similarity_scores['overall_score']
        if overall_score >= 80:
            recommendation = {
                'level': 'excellent',
                'message': 'Excellent Match! Your resume is highly aligned with this job description.',
                'advice': 'You should definitely apply! Make sure to highlight your matching skills in your cover letter.'
            }
        elif overall_score >= 60:
            recommendation = {
                'level': 'good',
                'message': 'Good Match! Your profile shows good alignment with the job requirements.',
                'advice': 'Consider emphasizing your matched skills and learning the missing skills if possible.'
            }
        else:
            recommendation = {
                'level': 'needs_improvement',
                'message': 'Needs Improvement. There is a significant gap between your profile and job requirements.',
                'advice': 'Focus on building the missing skills through projects, courses, and certifications.'
            }
        
        # Prepare response
        response = {
            'success': True,
            'scores': {
                'overall_score': similarity_scores['overall_score'],
                'semantic_similarity': similarity_scores['semantic_similarity'],
                'skill_match': similarity_scores['skill_match'],
                'match_rate': round(match_rate, 2)
            },
            'skills': {
                'resume_skills': resume_skills,
                'jd_skills': jd_skills,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'strengths': strengths,
                'suggestions': list(set(skill_suggestions + missing_skills[:5]))[:8]
            },
            'resume_data': {
                'name': resume_data.get('name', 'Not found'),
                'email': resume_data.get('email', 'Not found'),
                'phone': resume_data.get('phone', 'Not found'),
                'experience': resume_data.get('years_of_experience', 'Not specified'),
                'education': resume_data.get('education', ['Not specified'])
            },
            'jd_data': {
                'job_title': jd_data.get('job_title', 'Not specified'),
                'seniority_level': jd_data.get('seniority_level', 'Not specified'),
                'experience_required': jd_data.get('experience_required', 'Not specified'),
                'skills_count': len(jd_skills)
            },
            'predicted_roles': predicted_roles[:6],
            'recommendation': recommendation,
            'resume_preview': resume_text[:500],
            'jd_preview': job_description[:500]
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'AI Resume Analyzer API is running'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)