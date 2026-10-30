# src/components/repo_selector.py
"""
Repository Selector Component — Checkbox grid for repo selection.
"""
import streamlit as st
from typing import List, Dict, Optional
from src.models.schemas import RepoSummary


def RepoSelector(
    repos: List[RepoSummary],
    user_id: str,
    default_selected: Optional[List[str]] = None,
    max_selection: int = 5,
    key_prefix: str = "repo_sel"
) -> List[RepoSummary]:
    """
    Render repository selection UI with checkboxes.
    Returns list of selected repositories.
    """
    if not repos:
        st.info("No repositories available.")
        return []
    
    default_selected = default_selected or []
    
    st.markdown(f"#### 📦 Select Repositories (Max {max_selection})")
    st.caption("Choose repositories that best showcase your skills. Non-fork, recently updated repos are pre-selected.")
    
    selected = []
    cols_per_row = 2
    
    # Group repos into rows
    for i in range(0, len(repos), cols_per_row):
        row_repos = repos[i:i+cols_per_row]
        cols = st.columns(cols_per_row)
        
        for j, repo in enumerate(row_repos):
            with cols[j]:
                render_repo_card(repo, user_id, default_selected, selected, key_prefix)
    
    # Show selection summary
    if selected:
        st.markdown("---")
        st.success(f"✅ {len(selected)} repository{'s' if len(selected) > 1 else ''} selected")
        
        with st.expander("📋 Selected Repositories"):
            for repo in selected:
                st.markdown(f"- **{repo.name}** ({repo.language or 'No language'}) — ⭐ {repo.stars}")
    
    return selected


def render_repo_card(
    repo: RepoSummary,
    user_id: str,
    default_selected: List[str],
    selected_list: List[RepoSummary],
    key_prefix: str
):
    """Render a single repository card with checkbox."""
    
    is_fork = repo.is_fork
    is_archived = repo.is_archived
    disabled = is_fork or is_archived
    
    # Check if pre-selected
    is_preselected = repo.full_name in default_selected
    
    # Card container
    with st.container(border=True):
        # Header with checkbox
        col1, col2 = st.columns([1, 10])
        
        with col1:
            checked = st.checkbox(
                "",
                value=is_preselected,
                disabled=disabled,
                key=f"{key_prefix}_{repo.full_name}"
            )
            
            if checked and not disabled:
                selected_list.append(repo)
        
        with col2:
            st.markdown(f"**{repo.name}**")
            
            # Badges
            badges = []
            if repo.language:
                badges.append(f"💻 {repo.language}")
            if repo.stars > 0:
                badges.append(f"⭐ {repo.stars}")
            if is_fork:
                badges.append("🍴 Fork")
            if is_archived:
                badges.append("📦 Archived")
            if repo.description:
                # Truncate description
                desc = repo.description[:80] + ("..." if len(repo.description) > 80 else "")
                badges.append(f"📝 {desc}")
            
            st.caption("  •  ".join(badges))
        
        # Show disabled reason
        if disabled:
            reasons = []
            if is_fork:
                reasons.append("fork")
            if is_archived:
                reasons.append("archived")
            st.caption(f"⚠️ Disabled: {', '.join(reasons)}")


def RepoSelectorWithDetails(
    repos: List[RepoSummary],
    user_id: str,
    on_selection_change: Optional[callable] = None,
    key_prefix: str = "repo_sel_detail"
) -> List[RepoSummary]:
    """
    Enhanced repo selector with expandable details.
    """
    if not repos:
        return []
    
    selected = []
    
    st.markdown("#### 🐙 Your GitHub Repositories")
    
    for repo in repos:
        is_fork = repo.is_fork
        is_archived = repo.is_archived
        disabled = is_fork or is_archived
        
        with st.expander(f"{'🍴 ' if is_fork else ''}{'📦 ' if is_archived else ''}**{repo.full_name}**", expanded=not disabled):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if repo.description:
                    st.write(repo.description)
                else:
                    st.caption("_No description_")
                
                meta = []
                if repo.language:
                    meta.append(f"Language: {repo.language}")
                meta.append(f"Stars: {repo.stars}")
                meta.append(f"Updated: {repo.updated_at.strftime('%Y-%m-%d') if repo.updated_at else 'Unknown'}")
                st.caption("  |  ".join(meta))
                
                st.link_button("🔗 View on GitHub", repo.html_url, use_container_width=True)
            
            with col2:
                checked = st.checkbox(
                    "Select for analysis",
                    value=False,
                    disabled=disabled,
                    key=f"{key_prefix}_{repo.full_name}"
                )
                
                if checked:
                    selected.append(repo)
                
                if disabled:
                    reason = []
                    if is_fork: reason.append("fork")
                    if is_archived: reason.append("archived")
                    st.warning(f"Disabled: {', '.join(reason)}")
        
        if on_selection_change and checked:
            on_selection_change(repo.full_name, True)
    
    return selected


def render_repo_analysis_summary(repo_analysis: Dict) -> None:
    """Render a compact summary of repo analysis results."""
    
    st.markdown(f"### 📊 Analysis: {repo_analysis.get('name', 'Unknown')}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        auth = repo_analysis.get('authorship', {})
        score = auth.get('score', 0)
        color = "#22c55e" if score > 0.7 else "#f59e0b" if score > 0.4 else "#ef4444"
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: {color}15; border-radius: 0.5rem; border: 1px solid {color};">
            <div style="font-size: 2rem; font-weight: bold; color: {color};">{score:.0%}</div>
            <div style="font-size: 0.85rem; color: #6b7280;">Authorship</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"{auth.get('candidate_commits', 0)}/{auth.get('total_commits', 0)} commits")
    
    with col2:
        clone = repo_analysis.get('tutorial_clone', {})
        is_clone = clone.get('is_clone', False)
        if is_clone:
            st.error(f"⚠️ Tutorial Clone: {clone.get('clone_type', 'Unknown')}")
            st.caption(f"Confidence: {clone.get('confidence', 0):.0%}")
        else:
            st.success("✅ Original Project")
            st.caption(f"Clone score: {clone.get('score', 0):.0%}")
    
    with col3:
        qual = repo_analysis.get('quality', {})
        score = qual.get('score', 0)
        color = "#22c55e" if score > 0.7 else "#f59e0b" if score > 0.4 else "#ef4444"
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: {color}15; border-radius: 0.5rem; border: 1px solid {color};">
            <div style="font-size: 2rem; font-weight: bold; color: {color};">{score:.0%}</div>
            <div style="font-size: 0.85rem; color: #6b7280;">Quality</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"Tests: {'✅' if qual.get('has_tests') else '❌'}")
    
    with col4:
        evo = repo_analysis.get('evolution', {})
        score = evo.get('score', 0)
        color = "#22c55e" if score > 0.7 else "#f59e0b" if score > 0.4 else "#ef4444"
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: {color}15; border-radius: 0.5rem; border: 1px solid {color};">
            <div style="font-size: 2rem; font-weight: bold; color: {color};">{score:.0%}</div>
            <div style="font-size: 0.85rem; color: #6b7280;">Evolution</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"Trend: {evo.get('loc_growth_trend', 'unknown')}")
    
    # Skill evidence
    skills = repo_analysis.get('skill_evidence', [])
    if skills:
        st.markdown("**🛠️ Skills Demonstrated:**")
        skill_cols = st.columns(min(len(skills), 4))
        for i, skill in enumerate(skills[:8]):
            with skill_cols[i % 4]:
                conf = skill.get('confidence', 0)
                st.metric(skill.get('skill', 'Unknown'), f"{conf:.0%}")