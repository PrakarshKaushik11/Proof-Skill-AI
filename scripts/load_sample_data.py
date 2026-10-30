#!/usr/bin/env python
"""
Load sample data for development/testing.
Run with: python scripts/load_sample_data.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.session import init_db, db_session
from sqlalchemy import text


def create_sample_resumes():
    """Create sample resume text files for testing."""
    resumes_dir = Path("data/resumes")
    resumes_dir.mkdir(parents=True, exist_ok=True)
    
    sample_resumes = {
        "CAND-0042.txt": """
JOHN DOE
Software Developer
john.doe@email.com | github.com/johndoe | linkedin.com/in/johndoe

EDUCATION
B.Tech Computer Science, Tier 1 Institute, 2024
CGPA: 8.5/10

SKILLS
Programming Languages: Python (Advanced), JavaScript (Intermediate), TypeScript (Intermediate), SQL (Advanced)
Frameworks: FastAPI, Django, React, Express.js
Databases: PostgreSQL, MongoDB, Redis
Tools: Docker, Kubernetes, Git, GitHub Actions, AWS (EC2, S3, RDS)
Testing: Pytest, Jest, React Testing Library

PROJECTS
1. E-commerce API (github.com/johndoe/ecommerce-api)
   - Built RESTful API with FastAPI, PostgreSQL, Redis caching
   - Implemented JWT authentication, role-based access control
   - Added rate limiting, request validation, comprehensive tests (85% coverage)
   - Deployed on AWS ECS with CI/CD pipeline

2. Real-time Chat App (github.com/johndoe/chat-app)
   - Full-stack React/TypeScript frontend with Node.js/Express backend
   - WebSocket connections for real-time messaging
   - PostgreSQL for persistence, Redis for session management

3. Task Manager (github.com/johndoe/task-manager)
   - Django REST Framework backend with React frontend
   - Celery for async tasks, PostgreSQL database

EXPERIENCE
Software Engineering Intern, TechCorp (Jan 2024 - Jun 2024)
- Developed microservices using FastAPI and PostgreSQL
- Improved API response time by 40% through query optimization
- Wrote unit/integration tests, maintained 80%+ coverage
""",
        "CAND-0117.txt": """
JANE SMITH
Data Analyst
jane.smith@email.com | linkedin.com/in/janesmith

EDUCATION
M.Sc Data Science, Tier 2 University, 2024
CGPA: 8.2/10

SKILLS
Programming Languages: Python (Advanced), SQL (Advanced), R (Intermediate)
Libraries: Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn, Plotly
Databases: PostgreSQL, MySQL, BigQuery
Tools: Jupyter, Git, Tableau, Power BI, Airflow
Statistics: Hypothesis Testing, Regression, A/B Testing, Time Series

PROJECTS
1. Customer Churn Prediction
   - Analyzed 500K+ customer records using Pandas/SQL
   - Built classification models (XGBoost, LightGBM) - 92% AUC
   - Created interactive dashboard in Tableau for stakeholders

2. Sales Forecasting Dashboard
   - Time series analysis with Prophet and ARIMA
   - Automated ETL pipeline with Airflow
   - Power BI dashboard for weekly executive reviews

3. A/B Test Framework
   - Designed statistical framework for product experiments
   - Implemented in Python with SciPy/StatsModels
   - Reduced false positive rate by 60%

EXPERIENCE
Data Science Intern, DataDriven Inc (Jun 2023 - Dec 2023)
- Built automated reporting pipelines reducing manual work by 15 hrs/week
- Conducted deep-dive analyses for product team decisions
""",
        "CAND-0293.txt": """
ALEX JOHNSON
Business Analyst
alex.johnson@email.com | linkedin.com/in/alexjohnson

EDUCATION
BBA Business Administration, Tier 3 College, 2024
CGPA: 7.8/10

SKILLS
Business Analysis: Requirements Gathering, Process Modeling, Gap Analysis, User Stories
Tools: Jira, Confluence, Lucidchart, Miro, Excel (Advanced), PowerPoint
Data: SQL (Beginner), Tableau (Intermediate), Excel Pivot Tables
Methodologies: Agile/Scrum, Waterfall, BPMN, UML

PROJECTS
1. Digital Transformation Case Study
   - Analyzed legacy processes for retail client
   - Mapped 50+ business processes using BPMN
   - Identified 15 automation opportunities with ROI analysis

2. Requirements Documentation for CRM Migration
   - Elicited requirements from 20+ stakeholders
   - Created 200+ user stories with acceptance criteria
   - Managed traceability matrix for compliance

3. Market Research Dashboard
   - Built interactive dashboard in Tableau
   - Integrated data from CRM, marketing tools, surveys
   - Enabled self-service analytics for sales team

EXPERIENCE
Business Analyst Intern, ConsultingFirm (Jan 2024 - Jun 2024)
- Supported senior BAs in requirements workshops
- Created process maps and functional specifications
- Assisted in UAT planning and execution
"""
    }
    
    for filename, content in sample_resumes.items():
        (resumes_dir / filename).write_text(content)
        print(f"Created {filename}")
    
    return list(sample_resumes.keys())


def create_sample_assessments():
    """Create sample assessment scores."""
    assessments = {
        "CAND-0042": {"Python": 88, "FastAPI": 82, "PostgreSQL": 85, "Docker": 75, "React": 70, "JavaScript": 75},
        "CAND-0117": {"Python": 92, "SQL": 88, "Pandas": 85, "Statistics": 90, "Tableau": 78},
        "CAND-0293": {"Business Analysis": 80, "SQL": 55, "Tableau": 72, "Requirements Engineering": 85},
    }
    
    assessments_dir = Path("data/assessments")
    assessments_dir.mkdir(parents=True, exist_ok=True)
    
    for cand_id, scores in assessments.items():
        (assessments_dir / f"{cand_id}.json").write_text(json.dumps(scores, indent=2))
        print(f"Created assessment for {cand_id}")
    
    return assessments


def setup_database():
    """Initialize database and load job descriptions only."""
    print("Initializing database...")
    init_db()
    
    # Load sample JDs
    load_sample_jds()
    
    print("\n✅ Database and sample JDs loaded successfully!")
    print("Recruiter uploads create candidate accounts and credentials.")


def load_sample_jds():
    """Load sample job descriptions."""
    sample_jds = [
        {
            "jd_id": "JD-001",
            "title": "Backend Engineer - Python",
            "company": "TechCorp",
            "description": "We are looking for a Backend Engineer with strong Python skills to build scalable APIs and services. You will work with FastAPI, PostgreSQL, Redis, and Docker in a Kubernetes environment. Experience with microservices, event-driven architecture, and CI/CD pipelines is a plus.",
            "required_skills": json.dumps([
                {"skill": "Python", "level": "advanced", "weight": 1.0, "required": True},
                {"skill": "FastAPI", "level": "intermediate", "weight": 0.8, "required": True},
                {"skill": "PostgreSQL", "level": "intermediate", "weight": 0.7, "required": True},
                {"skill": "Docker", "level": "beginner", "weight": 0.5, "required": False}
            ]),
            "preferred_skills": json.dumps([
                {"skill": "AWS", "level": "beginner", "weight": 0.4, "required": False},
                {"skill": "Kubernetes", "level": "beginner", "weight": 0.3, "required": False},
                {"skill": "Redis", "level": "intermediate", "weight": 0.4, "required": False}
            ])
        },
        {
            "jd_id": "JD-002",
            "title": "Frontend Developer - React",
            "company": "StartupXYZ",
            "description": "Frontend Developer role focusing on React and TypeScript. You will build modern, responsive UIs with React, TypeScript, and modern CSS. Experience with Next.js, testing libraries, and state management is valued.",
            "required_skills": json.dumps([
                {"skill": "React", "level": "advanced", "weight": 1.0, "required": True},
                {"skill": "TypeScript", "level": "intermediate", "weight": 0.9, "required": True},
                {"skill": "CSS", "level": "intermediate", "weight": 0.6, "required": True}
            ]),
            "preferred_skills": json.dumps([
                {"skill": "Next.js", "level": "intermediate", "weight": 0.5, "required": False},
                {"skill": "Testing", "level": "beginner", "weight": 0.4, "required": False},
                {"skill": "Tailwind CSS", "level": "beginner", "weight": 0.3, "required": False}
            ])
        },
        {
            "jd_id": "JD-003",
            "title": "Data Analyst",
            "company": "DataDriven Inc",
            "description": "Data Analyst position requiring strong SQL, Python, and visualization skills. You will analyze large datasets, build predictive models, and create dashboards for business stakeholders. Experience with A/B testing and statistical analysis is required.",
            "required_skills": json.dumps([
                {"skill": "SQL", "level": "advanced", "weight": 1.0, "required": True},
                {"skill": "Python", "level": "intermediate", "weight": 0.8, "required": True},
                {"skill": "Tableau", "level": "intermediate", "weight": 0.7, "required": True}
            ]),
            "preferred_skills": json.dumps([
                {"skill": "Pandas", "level": "intermediate", "weight": 0.5, "required": False},
                {"skill": "Statistics", "level": "intermediate", "weight": 0.5, "required": False},
                {"skill": "A/B Testing", "level": "intermediate", "weight": 0.4, "required": False}
            ])
        }
    ]
    
    with db_session() as db:
        for jd in sample_jds:
            db.execute(text("""
                INSERT OR IGNORE INTO recruiter_jds (jd_id, title, company, description, required_skills_json, preferred_skills_json)
                VALUES (:jd_id, :title, :company, :desc, :req, :pref)
            """), {
                "jd_id": jd["jd_id"],
                "title": jd["title"],
                "company": jd["company"],
                "desc": jd["description"],
                "req": jd["required_skills"],
                "pref": jd["preferred_skills"],
            })
        db.commit()
    
    print(f"Loaded {len(sample_jds)} sample JDs")


if __name__ == "__main__":
    setup_database()