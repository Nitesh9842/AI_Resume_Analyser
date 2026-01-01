# 📄 AI Resume Analyzer & Job Fit Scorer

An intelligent AI-powered resume analysis tool that helps candidates understand how well their resume matches a job description. Built with Flask and powered by state-of-the-art NLP models.

## ✨ Features

- 📊 **Job Match Scoring**: Get an overall compatibility score
- 🎯 **Skill Analysis**: Identify matched and missing skills
- 📈 **Visual Analytics**: Interactive charts and visualizations
- 💼 **Job Role Predictions**: Get recommendations for suitable roles
- 📚 **Learning Recommendations**: Personalized skill development suggestions
- 📄 **Multi-format Support**: Upload PDF, DOCX, DOC, or TXT files

## 🚀 Quick Start

### Step 1: Clean Install (Recommended)

```bash
# Deactivate current environment if active
deactivate

# Remove old virtual environment
Remove-Item -Recurse -Force venv

# Create fresh virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

### Step 2: Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Step 3: Install Dependencies

```bash
pip install --no-cache-dir -r requirements.txt
```

If you encounter errors, install packages individually:

```bash
# Core packages first
pip install Flask==2.3.3
pip install Flask-CORS==4.0.0
pip install Werkzeug==2.3.7

# Text extraction
pip install pdfplumber PyMuPDF python-docx docx2txt

# ML packages
pip install sentence-transformers scikit-learn nltk

# Data processing
pip install pandas numpy plotly
```

### Step 4: Setup Project Structure

```bash
python setup_project.py
```

### Step 5: Test Flask Installation

```bash
python test_app.py
```

Open browser at `http://localhost:5000` - you should see "Flask is Working!"

### Step 6: Run Main Application

```bash
python app.py
```

Open browser at `http://localhost:5000`

## 🛠️ Troubleshooting

### Issue: ModuleNotFoundError: No module named 'flask'

**Solution:**
```bash
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall Flask
pip install Flask==2.3.3
```

### Issue: Werkzeug import errors

**Solution:**
```bash
# Uninstall and reinstall with specific version
pip uninstall Werkzeug
pip install Werkzeug==2.3.7
```

### Issue: KeyboardInterrupt during import

**Solution:**
This usually indicates a corrupted package installation.

```bash
# Clear pip cache
pip cache purge

# Reinstall all packages
pip uninstall -y -r requirements.txt
pip install --no-cache-dir -r requirements.txt
```

### Issue: No module named 'utils'

**Solution:**
Make sure you're running the app from the project root directory:

```bash
cd "C:\Users\DELL\OneDrive\Desktop\Resume Analiser ai"
python app.py
```

### Issue: Templates not found

**Solution:**
```bash
# Run setup script
python setup_project.py

# Verify templates/index.html exists
# Verify static/css/style.css exists
# Verify static/js/main.js exists
```

## 📁 Project Structure

```
ai_resume_analyzer/
│
├── app.py                      # Main Flask application
├── test_app.py                 # Flask test script
├── setup_project.py            # Project setup script
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation
│
├── templates/                  # HTML templates
│   └── index.html             # Main page
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css          # Styles
│   └── js/
│       └── main.js            # JavaScript
│
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── text_extractor.py      # Text extraction
│   ├── resume_parser.py       # Resume parsing
│   ├── jd_processor.py        # JD processing
│   ├── skill_extractor.py     # Skill extraction
│   ├── similarity.py          # Similarity calculation
│   └── visuals.py             # Visualizations
│
├── assets/
│   └── skills.json            # Skills database
│
└── uploads/                    # Temporary file uploads
```

## 🔧 Environment Setup

### Windows PowerShell

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows CMD

```cmd
venv\Scripts\activate.bat
```

### Linux/Mac

```bash
source venv/bin/activate
```

## 📊 How It Works

1. **Upload Resume**: User uploads resume (PDF/DOCX/TXT)
2. **Enter Job Description**: User pastes job description
3. **Text Extraction**: Extract text from resume file
4. **Skill Analysis**: Identify skills using NLP
5. **Similarity Calculation**: Use sentence transformers for semantic matching
6. **Generate Report**: Create detailed analysis with visualizations
7. **Recommendations**: Provide personalized suggestions

## 🎯 API Endpoints

### `POST /api/analyze`
Analyze resume against job description

**Request:**
- `resume`: File (multipart/form-data)
- `job_description`: Text

**Response:**
```json
{
  "success": true,
  "scores": {
    "overall_score": 75.5,
    "semantic_similarity": 68.2,
    "skill_match": 80.0,
    "match_rate": 75.0
  },
  "skills": {
    "matched_skills": [...],
    "missing_skills": [...],
    "strengths": [...]
  },
  ...
}
```

### `GET /api/health`
Health check endpoint

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Add more skill categories
- Improve parsing accuracy
- Add export functionality
- Implement user authentication

## 👨‍💻 Author

**Nitesh - AI Engineer**

Built with ❤️ using Flask, Sentence Transformers, and modern web technologies.

## 📝 License

Open source - available for personal and commercial use.

---

## 🚨 Common Commands

```bash
# Setup
python setup_project.py

# Test Flask
python test_app.py

# Run app
python app.py

# Install dependencies
pip install -r requirements.txt

# Create fresh environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Happy Analyzing! 🎉