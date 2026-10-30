# pages/Login.py
"""
Login Page — Candidate authentication with random credentials.
"""
import streamlit as st
from src.services.auth import AuthService
from src.db.session import db_session


def show_login(navigate):
    # Centered login card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="main-header">🎯 ProofSkill AI</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Proof of skill, not a template resume</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        login_type = st.radio("Login as", ["Candidate", "Recruiter"], horizontal=True)
        if login_type == "Recruiter":
            show_recruiter_login(navigate)
            return

        st.markdown("### 🔐 Candidate Login")
        st.caption("Enter your assigned User ID and Password")
        
        with st.form("login_form", clear_on_submit=False):
            user_id = st.text_input(
                "User ID",
                placeholder="e.g., CAND-0042",
                help="Your unique candidate identifier"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="••••••••••••",
                help="Your 12-character password"
            )
            
            submitted = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
            
            if submitted:
                if not user_id or not password:
                    st.error("Please enter both User ID and Password")
                else:
                    with st.spinner("Verifying credentials..."):
                        auth = AuthService()
                        user = auth.validate_credentials(user_id.strip().upper(), password.strip())
                        
                        if user:
                            st.session_state.user = user
                            st.success(f"Welcome back, {user.user_id}!")
                            st.balloons()
                            navigate("dashboard")
                        else:
                            st.error("❌ Invalid User ID or Password")
                            st.caption("Credentials are case-sensitive. Check with your coordinator.")
        
        st.markdown("---")
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #9ca3af; font-size: 0.85rem;">
            <p>Integraminds • AI FRONTIER • IM-105</p>
            <p>Proof of skill, not a template resume</p>
        </div>
        """, unsafe_allow_html=True)


# Recruiter login (separate flow)
def show_recruiter_login(navigate):
    st.markdown("### 🔐 Recruiter Login")
    st.caption("Recruiter credentials are required to access candidate uploads and rankings.")
    with st.form("recruiter_login"):
        recruiter_id = st.text_input("Admin ID", placeholder="admin")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button(
            "Login as Recruiter", use_container_width=True, type="primary"
        )
        if submitted:
            auth = AuthService()
            if auth.validate_recruiter_credentials(recruiter_id, password):
                st.session_state.recruiter_authenticated = True
                st.session_state.user = None
                navigate("recruiter")
            else:
                st.error("Invalid recruiter email or password.")