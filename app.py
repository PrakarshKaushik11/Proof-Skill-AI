# app.py
"""
ProofSkill AI — Streamlit Application Entry Point
"""
import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import settings

# Page configuration
st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #f9fafb;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #d1d5db;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #151922;
        border: 1px solid #374151;
        border-radius: 0.75rem;
        padding: 1.5rem;
    }
    .confidence-bar {
        height: 8px;
        border-radius: 4px;
        background: #e5e7eb;
        overflow: hidden;
    }
    .confidence-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-pending { background: #fef3c7; color: #92400e; }
    .status-running { background: #dbeafe; color: #1e40af; }
    .status-done { background: #d1fae5; color: #065f46; }
    .status-failed { background: #fee2e2; color: #991b1b; }
    .clone-warning {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 0.5rem;
        padding: 1rem;
        color: #991b1b;
        margin: 0.5rem 0;
    }
    .evidence-item {
        background: #f0fdf4;
        border-left: 3px solid #22c55e;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
        color: #166534;
    }
    .evidence-item strong {
        color: #14532d;
    }
    .proof-card-muted {
        color: #374151;
    }
    [data-testid="stExpander"] summary p {
        font-weight: 600;
    }
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: 500;
    }
    .stButton > button[kind="primary"] {
        background: #2563eb;
        border-color: #2563eb;
    }
    .ai-speaking, .ai-listening {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.8rem 1rem;
        margin: 1rem 0;
        border: 1px solid #374151;
        border-radius: 0.75rem;
        background: #151922;
        color: #e5e7eb;
    }
    .ai-speaking {
        border-color: #2563eb;
        animation: ai-glow 2s ease-in-out infinite;
    }
    .ai-listening {
        border-color: #ef4444;
        animation: ai-listen 1.5s ease-in-out infinite;
    }
    .ai-orb {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2.25rem;
        height: 2.25rem;
        border-radius: 50%;
        background: #2563eb;
        font-size: 1.25rem;
    }
    .ai-listening .ai-orb {
        background: #dc2626;
    }
    @keyframes ai-glow {
        50% { box-shadow: 0 0 18px rgba(37, 99, 235, 0.55); }
    }
    @keyframes ai-listen {
        50% { box-shadow: 0 0 18px rgba(239, 68, 68, 0.55); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
if "recruiter_authenticated" not in st.session_state:
    st.session_state.recruiter_authenticated = False
if "db_initialized" not in st.session_state:
    from src.db.session import init_db
    init_db()
    st.session_state.db_initialized = True
if "page" not in st.session_state:
    st.session_state.page = "login"

# Navigation function
def navigate(page: str):
    st.session_state.page = page
    st.rerun()

def logout():
    st.session_state.user = None
    st.session_state.recruiter_authenticated = False
    st.session_state.page = "login"
    st.rerun()

# Sidebar (only show when logged in)
if st.session_state.user or st.session_state.recruiter_authenticated:
    with st.sidebar:
        if st.session_state.recruiter_authenticated:
            st.markdown("### 🏢 Recruiter")
        else:
            st.markdown(f"### 👤 {st.session_state.user.user_id}")
            st.caption(f"Resume: {st.session_state.user.resume_path}")
        
        st.divider()
        
        # Navigation
        if st.session_state.recruiter_authenticated:
            if st.button("🏢 Recruiter Dashboard", use_container_width=True,
                         type="primary" if st.session_state.page == "recruiter" else "secondary"):
                navigate("recruiter")
        else:
            if st.button("📊 Dashboard", use_container_width=True,
                         type="primary" if st.session_state.page == "dashboard" else "secondary"):
                navigate("dashboard")
            
            if st.button("🎤 Viva Session", use_container_width=True,
                         type="primary" if st.session_state.page == "viva" else "secondary"):
                navigate("viva")
            
            if st.button("📈 Results", use_container_width=True,
                         type="primary" if st.session_state.page == "results" else "secondary"):
                navigate("results")
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
        
        st.divider()
        st.caption(f"{settings.APP_NAME} v1.0")
        st.caption("IM-105 Hackathon")

# Page routing
if st.session_state.page == "login":
    from pages.Login import show_login
    show_login(navigate)

elif st.session_state.page == "dashboard":
    from pages.Candidate_Dashboard import show_dashboard
    show_dashboard()

elif st.session_state.page == "viva":
    from pages.Viva_Session import show_viva
    show_viva()

elif st.session_state.page == "results":
    from pages.Results import show_results
    show_results()

elif st.session_state.page == "recruiter":
    if not st.session_state.recruiter_authenticated:
        st.session_state.page = "login"
        st.rerun()
    else:
        from pages.Recruiter_View import show_recruiter
        show_recruiter()

else:
    st.error(f"Unknown page: {st.session_state.page}")
    if st.button("Go to Login"):
        navigate("login")