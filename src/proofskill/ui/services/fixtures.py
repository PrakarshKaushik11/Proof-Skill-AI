"""Synthetic demo fixtures for ProofSkill AI.

Everything in this module is invented for demonstration and testing. It is
**not** real candidate data, and nothing here represents a real person,
organisation, GitHub account or assessment result.

The fixtures exist so the Streamlit UI can run the complete candidate and
recruiter journeys without external API credentials (demo mode).
"""

from __future__ import annotations

import re

from proofskill.ui.services.contracts import (
    DiscoveredRepository,
    GithubLink,
    JobSummary,
    SkillRequirement,
)

DEMO_NOTICE = (
    "Synthetic demo data — not a real candidate, repository or assessment result."
)

# --------------------------------------------------------------------------
# Resume
# --------------------------------------------------------------------------

DEMO_RESUME_FILENAME = "synthetic-demo-resume.txt"

DEMO_RESUME_TEXT = """DEMO CANDIDATE (synthetic profile used only for the ProofSkill AI demo)
Contact: demo.candidate@example.invalid

SKILLS
Python, SQL, Flask, Git, REST APIs, pandas, pytest, Problem solving

PROJECTS
Project: Task Tracker API - A Flask REST API for tracking tasks with SQLite storage,
pagination and simple token checks. Includes pytest unit tests.
Project: Expense Dashboard - A pandas dashboard that categorises monthly expenses
and plots monthly totals.

LINKS
Portfolio GitHub: https://github.com/proofskill-demo
Task tracker repository: https://github.com/proofskill-demo/task-tracker

EDUCATION
B.Tech Computer Science (synthetic institution name; never used for ranking)
"""

#: Canonical skill vocabulary used for demo extraction and job matching.
SKILL_VOCABULARY: tuple[str, ...] = (
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "SQL",
    "Flask",
    "Django",
    "FastAPI",
    "React",
    "Node.js",
    "HTML",
    "CSS",
    "Git",
    "GitHub",
    "Docker",
    "Kubernetes",
    "AWS",
    "pandas",
    "NumPy",
    "scikit-learn",
    "Machine learning",
    "Data analysis",
    "REST APIs",
    "pytest",
    "Unit testing",
    "CI/CD",
    "MongoDB",
    "Linux",
    "C++",
    "Go",
    "Vue.js",
    "GraphQL",
    "Selenium",
    "Tableau",
    "Power BI",
    "Problem solving",
    "Data structures",
    "Testing",
    "Debugging",
    "API design",
)

#: Skills that also count as "technologies/tools" in the profile view.
TECH_SKILLS: frozenset[str] = frozenset(
    {
        "Python",
        "Java",
        "JavaScript",
        "TypeScript",
        "SQL",
        "Flask",
        "Django",
        "FastAPI",
        "React",
        "Node.js",
        "HTML",
        "CSS",
        "Git",
        "GitHub",
        "Docker",
        "Kubernetes",
        "AWS",
        "pandas",
        "NumPy",
        "scikit-learn",
        "MongoDB",
        "Linux",
        "C++",
        "Go",
        "Vue.js",
        "GraphQL",
        "Selenium",
        "Tableau",
        "Power BI",
    }
)

# --------------------------------------------------------------------------
# Interview question bank (demo mode only)
# --------------------------------------------------------------------------

# Each entry: (question_text, question_type, difficulty, expected_concepts)
QUESTION_BANK: dict[str, tuple[tuple[str, str, str, tuple[str, ...]], ...]] = {
    "Python": (
        (
            "Explain how a Python dictionary differs from a list, and give an example "
            "of when you would choose each.",
            "technical",
            "beginner",
            ("key", "lookup", "hash", "order"),
        ),
        (
            "A Python function is slower than you expected. How would you investigate "
            "and improve it?",
            "technical",
            "intermediate",
            ("profile", "measure", "complexity", "optimise"),
        ),
    ),
    "SQL": (
        (
            "Write (describe) a query that returns the total number of orders per "
            "customer, and explain each part of it.",
            "technical",
            "beginner",
            ("group by", "count", "join", "aggregate"),
        ),
        (
            "When would you add an index to a table, and what is the trade-off?",
            "technical",
            "intermediate",
            ("index", "read", "write", "trade-off"),
        ),
    ),
    "Flask": (
        (
            "Describe how a Flask request travels from the URL to your response, "
            "including routing and error handling.",
            "technical",
            "intermediate",
            ("route", "request", "handler", "response"),
        ),
    ),
    "REST APIs": (
        (
            "What makes an API RESTful? Describe the HTTP methods and status codes "
            "you use most often.",
            "technical",
            "beginner",
            ("resource", "get", "post", "status"),
        ),
    ),
    "Git": (
        (
            "Explain the difference between git merge and git rebase, and when you "
            "would use each.",
            "technical",
            "intermediate",
            ("branch", "history", "conflict", "team"),
        ),
    ),
    "pytest": (
        (
            "How do you decide what to test in a small API project, and how do you "
            "handle testing external services?",
            "technical",
            "intermediate",
            ("case", "mock", "edge", "fixture"),
        ),
    ),
    "pandas": (
        (
            "You receive a CSV with missing values and duplicate rows. Describe your "
            "cleaning steps in pandas.",
            "technical",
            "beginner",
            ("missing", "duplicate", "dropna", "column"),
        ),
    ),
    "Testing": (
        (
            "What is the difference between a unit test and an integration test, and "
            "where would you draw the line?",
            "technical",
            "beginner",
            ("unit", "integration", "isolate", "boundary"),
        ),
    ),
    "Problem solving": (
        (
            "Walk me through how you would break down an unfamiliar problem into "
            "smaller steps before writing any code.",
            "scenario",
            "beginner",
            ("decompose", "assumption", "small", "verify"),
        ),
    ),
    "Data structures": (
        (
            "Which data structure would you use to check membership quickly in a "
            "large dataset, and why?",
            "technical",
            "beginner",
            ("set", "hash", "lookup", "complexity"),
        ),
    ),
}

FOLLOW_UP_TEMPLATE = (
    "Thanks. Could you go one level deeper on {skill}: a concrete example of how you "
    "applied it, what could go wrong, and how you would check your work?"
)

GENERIC_QUESTION_TEMPLATE = (
    "This role needs {skill}. Describe a specific situation where you used {skill}, "
    "what you did, and how you verified the result."
)

# --------------------------------------------------------------------------
# GitHub demo discovery (no network access is performed in demo mode)
# --------------------------------------------------------------------------

_TASK_TRACKER = DiscoveredRepository(
    full_name="proofskill-demo/task-tracker",
    html_url="https://github.com/proofskill-demo/task-tracker",
    description="Flask REST API for tracking tasks (synthetic demo repository).",
    language="Python",
    visibility="public",
    updated_at="2026-09-12",
)

_EXPENSE_DASHBOARD = DiscoveredRepository(
    full_name="proofskill-demo/expense-dashboard",
    html_url="https://github.com/proofskill-demo/expense-dashboard",
    description="pandas expense dashboard (synthetic demo repository).",
    language="Python",
    visibility="public",
    updated_at="2026-08-03",
)

_NOTES_APP = DiscoveredRepository(
    full_name="proofskill-demo/notes-app",
    html_url="https://github.com/proofskill-demo/notes-app",
    description="Small markdown notes app (synthetic demo repository).",
    language="JavaScript",
    visibility="public",
    updated_at="2026-06-21",
)

DEMO_ACCOUNTS: dict[str, tuple[DiscoveredRepository, ...]] = {
    "proofskill-demo": (_TASK_TRACKER, _EXPENSE_DASHBOARD, _NOTES_APP),
    "proofskill-empty": (),
}

#: Direct repository links that resolve to nothing the demo can read.
INACCESSIBLE_REPOS: frozenset[str] = frozenset(
    {
        "proofskill-demo/private-project",
        "proofskill-demo/missing-repo",
    }
)

#: Accounts that simulate an exhausted GitHub API quota.
RATE_LIMITED_ACCOUNTS: frozenset[str] = frozenset({"proofskill-ratelimit"})

REPO_FINDINGS: dict[str, tuple[str, tuple[str, ...], str]] = {
    "proofskill-demo/task-tracker": (
        "Flask application exposing task CRUD endpoints with SQLite storage and a "
        "pytest suite.",
        ("app.py", "models.py", "tests/test_tasks.py", "README.md"),
        "Python",
    ),
    "proofskill-demo/expense-dashboard": (
        "pandas scripts that load CSV data, clean it and plot monthly totals.",
        ("dashboard.py", "cleaning.py", "README.md"),
        "Python",
    ),
    "proofskill-demo/notes-app": (
        "Express service rendering markdown notes with a small front-end.",
        ("server.js", "public/app.js", "README.md"),
        "JavaScript",
    ),
}

#: Bounded excerpts only. The UI must never receive full repository contents.
FILE_EXCERPTS: dict[str, str] = {
    "proofskill-demo/task-tracker/app.py": (
        "from flask import Flask, request, jsonify\n"
        "from models import Task\n\n"
        "app = Flask(__name__)\n\n"
        "@app.get('/tasks')\n"
        "def list_tasks():\n"
        "    page = request.args.get('page', 1, type=int)\n"
        "    tasks = Task.query.paginate(page=page, per_page=20)\n"
        "    return jsonify([t.to_dict() for t in tasks.items])\n\n"
        "@app.post('/tasks')\n"
        "def create_task():\n"
        "    data = request.get_json(silent=True) or {}\n"
        "    if not data.get('title'):\n"
        "        return jsonify({'error': 'title is required'}), 400\n"
        "    task = Task(title=data['title'], done=False)\n"
        "    task.save()\n"
        "    return jsonify(task.to_dict()), 201"
    ),
    "proofskill-demo/task-tracker/tests/test_tasks.py": (
        "import pytest\n"
        "from app import app\n\n"
        "@pytest.fixture()\n"
        "def client():\n"
        "    app.config['TESTING'] = True\n"
        "    with app.test_client() as client:\n"
        "        yield client\n\n"
        "def test_create_task_requires_title(client):\n"
        "    response = client.post('/tasks', json={})\n"
        "    assert response.status_code == 400"
    ),
    "proofskill-demo/expense-dashboard/dashboard.py": (
        "import pandas as pd\n\n"
        "def load_expenses(path):\n"
        "    df = pd.read_csv(path)\n"
        "    df = df.drop_duplicates()\n"
        "    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')\n"
        "    return df.dropna(subset=['amount'])\n\n"
        "def monthly_totals(df):\n"
        "    return df.groupby(df['date'].dt.to_period('M'))['amount'].sum()"
    ),
}

# --------------------------------------------------------------------------
# Jobs and recruiter demo data
# --------------------------------------------------------------------------


def _requirements(*items: tuple[str, float, bool]) -> tuple[SkillRequirement, ...]:
    return tuple(
        SkillRequirement(skill_name=name, weight=weight, required=required)
        for name, weight, required in items
    )


DEMO_JOBS: tuple[JobSummary, ...] = (
    JobSummary(
        job_id="demo-job-python-001",
        title="Junior Python Developer",
        skills=("Python", "Problem solving", "Data structures", "SQL", "Testing"),
        description=(
            "Entry-level Python role. Requires Python, problem solving and data "
            "structures. SQL and testing are strongly preferred."
        ),
    ),
    JobSummary(
        job_id="demo-job-web-001",
        title="Junior Web Developer",
        skills=("JavaScript", "React", "HTML", "Testing", "Git"),
        description=(
            "Frontend-focused role requiring JavaScript and React, with HTML, "
            "testing and Git."
        ),
    ),
)

DEMO_JOB_REQUIREMENTS: dict[str, tuple[SkillRequirement, ...]] = {
    "demo-job-python-001": _requirements(
        ("Python", 30.0, True),
        ("Problem solving", 25.0, True),
        ("Data structures", 20.0, True),
        ("SQL", 15.0, False),
        ("Testing", 10.0, False),
    ),
    "demo-job-web-001": _requirements(
        ("JavaScript", 30.0, True),
        ("React", 25.0, True),
        ("HTML", 15.0, False),
        ("Testing", 15.0, False),
        ("Git", 15.0, False),
    ),
}

#: Recruiters only ever see pseudonymous references, never personal details.
DEMO_CANDIDATE_REFERENCES: dict[str, str] = {
    "demo-candidate-001": "DEMO-001",
    "demo-candidate-002": "DEMO-002",
    "demo-candidate-003": "DEMO-003",
    "demo-candidate-004": "DEMO-004",
    "demo-candidate-005": "DEMO-005",
}

DEMO_GITHUB_LINKS: tuple[GithubLink, ...] = (
    GithubLink(
        url="https://github.com/proofskill-demo",
        link_type="profile",
        account="proofskill-demo",
    ),
    GithubLink(
        url="https://github.com/proofskill-demo/task-tracker",
        link_type="repository",
        account="proofskill-demo",
        repo="task-tracker",
    ),
)

GITHUB_URL_PATTERN = re.compile(
    r"https?://(?:www\.)?github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]{0,38}[A-Za-z0-9])?)"
    r"(?:/([A-Za-z0-9_.-]+))?",
    re.IGNORECASE,
)
