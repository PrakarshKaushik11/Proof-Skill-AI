# src/components/comparison_table.py
"""
Comparison Table Component — Side-by-side candidate comparison for recruiters.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from src.models.schemas import *


def ComparisonTable(
    candidates: List[Dict[str, Any]],  # Each: {candidate_id, rank, score, skills, etc.}
    jd_skills: List[str] = None,
    show_evidence: bool = True,
    key_prefix: str = "comp"
) -> None:
    """
    Render side-by-side comparison table for 2+ candidates.
    """
    if len(candidates) < 2:
        st.info("Select at least 2 candidates to compare.")
        return
    
    if len(candidates) > 4:
        st.warning("Comparison limited to 4 candidates. Showing first 4.")
        candidates = candidates[:4]
    
    # Header
    st.markdown("### ⚖️ Side-by-Side Comparison")
    
    # Candidate headers
    cols = st.columns(len(candidates))
    for i, cand in enumerate(candidates):
        with cols[i]:
            rank_color = "#22c55e" if cand.get('rank', 999) <= 3 else "#f59e0b" if cand.get('rank', 999) <= 10 else "#ef4444"
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: {rank_color}15; border-radius: 0.5rem; border: 2px solid {rank_color};">
                <div style="font-size: 1.5rem; font-weight: bold; color: {rank_color};">
                    #{cand.get('rank', '?')}
                </div>
                <div style="font-size: 1.1rem; font-weight: 600;">{cand.get('candidate_id', 'Unknown')}</div>
                <div style="font-size: 1.25rem; font-weight: bold; color: {rank_color};">
                    {cand.get('score', 0):.1f}/100
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Skill comparison
    if jd_skills:
        render_skill_comparison(candidates, jd_skills)
    
    # Detailed skill breakdown
    render_detailed_comparison(candidates, show_evidence)
    
    # Reasons
    render_reasons_comparison(candidates)


def render_skill_comparison(candidates: List[Dict], jd_skills: List[str]) -> None:
    """Render skill-by-skill comparison aligned with JD."""
    st.markdown("#### 🎯 Job Requirements Match")
    
    # Build comparison data
    rows = []
    for skill in jd_skills:
        row = {"JD Skill": skill}
        for cand in candidates:
            skill_data = cand.get('skills', {}).get(skill, {})
            score = skill_data.get('total', 0)
            level = _score_to_level(score)
            has_repo = skill_data.get('has_repo', False)
            
            row[cand['candidate_id']] = f"{score:.0f} ({level}){' 🐙' if has_repo else ''}"
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_detailed_comparison(candidates: List[Dict], show_evidence: bool) -> None:
    """Render detailed skill comparison with expandable evidence."""
    
    # Collect all skills across candidates
    all_skills = set()
    for cand in candidates:
        all_skills.update(cand.get('skills', {}).keys())
    
    if not all_skills:
        st.info("No skill data available for comparison.")
        return
    
    st.markdown("#### 🛠️ All Skills Comparison")
    
    # Create tabs for each skill
    skill_list = sorted(all_skills)
    tabs = st.tabs(skill_list)
    
    for i, skill in enumerate(skill_list):
        with tabs[i]:
            render_skill_detail_comparison(skill, candidates, show_evidence)


def render_skill_detail_comparison(skill: str, candidates: List[Dict], show_evidence: bool) -> None:
    """Render detailed comparison for a single skill."""
    
    cols = st.columns(len(candidates))
    
    for j, cand in enumerate(candidates):
        with cols[j]:
            skill_data = cand.get('skills', {}).get(skill, {})
            score = skill_data.get('total', 0)
            
            # Score display
            color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: {color}15; border-radius: 0.5rem; border: 1px solid {color};">
                <div style="font-size: 2rem; font-weight: bold; color: {color};">{score:.0f}</div>
                <div style="font-size: 0.85rem; color: #6b7280;">/100</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Component scores
            components = ['evidence', 'viva', 'assessment', 'consistency']
            labels = ['Evidence', 'Viva', 'Assessment', 'Consistency']
            
            for comp, label in zip(components, labels):
                val = skill_data.get(comp, 0)
                st.caption(f"{label}: {val:.0f}")
            
            # Evidence details
            if show_evidence:
                evidence = skill_data.get('evidence_bundle', [])
                if evidence:
                    with st.expander("📋 Evidence"):
                        for ev in evidence:
                            source_icons = {"repo": "🐙", "assessment": "📝", "resume": "📄", "viva": "🎤"}
                            icon = source_icons.get(ev.get('type'), "📌")
                            st.markdown(f"""
                            <div style="background: #f9fafb; border-left: 3px solid #2563eb; padding: 0.5rem; margin: 0.25rem 0; border-radius: 0 0.25rem 0.25rem 0;">
                                {icon} <strong>{ev.get('source', 'Unknown')}</strong> ({ev.get('weight', 0):.0%}): {ev.get('detail', '')}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.caption("_No evidence details_")


def render_reasons_comparison(candidates: List[Dict]) -> None:
    """Render rank reasons comparison."""
    st.markdown("#### 🎯 Ranking Reasons")
    
    cols = st.columns(len(candidates))
    
    for j, cand in enumerate(candidates):
        with cols[j]:
            st.markdown(f"**{cand.get('candidate_id', 'Unknown')}**")
            reasons = cand.get('reasons', [])
            if reasons:
                for i, reason in enumerate(reasons, 1):
                    st.markdown(f"{i}. {reason}")
            else:
                st.caption("_No reasons available_")


def ComparisonSummary(candidates: List[Dict]) -> None:
    """Render a compact summary comparison."""
    if len(candidates) < 2:
        return
    
    # Summary metrics
    cols = st.columns(len(candidates))
    
    for i, cand in enumerate(candidates):
        with cols[i]:
            st.metric(
                label=f"#{cand.get('rank', '?')} — {cand.get('candidate_id', 'Unknown')}",
                value=f"{cand.get('score', 0):.1f}/100",
                delta=f"{cand.get('score', 0) - candidates[0].get('score', 0):+.1f}" if i > 0 else None
            )
    
    # Quick skill radar (top 5 skills)
    st.markdown("#### 📊 Top Skills Radar")
    
    # Get top 5 skills across all candidates
    all_skills = {}
    for cand in candidates:
        for skill, data in cand.get('skills', {}).items():
            if skill not in all_skills:
                all_skills[skill] = []
            all_skills[skill].append(data.get('total', 0))
    
    # Average score per skill
    avg_skills = {s: sum(scores)/len(scores) for s, scores in all_skills.items()}
    top_skills = sorted(avg_skills.items(), key=lambda x: x[1], reverse=True)[:5]
    
    if top_skills:
        radar_data = pd.DataFrame({
            'Skill': [s for s, _ in top_skills],
            'Average Score': [sc for _, sc in top_skills]
        })
        st.bar_chart(radar_data.set_index('Skill'))


def _score_to_level(score: float) -> str:
    """Convert score to level string."""
    if score >= 80:
        return "Adv"
    elif score >= 55:
        return "Int"
    elif score >= 30:
        return "Beg"
    return "—"


def render_fairness_badge(fairness_report: Dict) -> None:
    """Render fairness audit badge."""
    passed = fairness_report.get('passed', True)
    
    if passed:
        st.success("✅ **Fairness Audit Passed** — No protected attribute bias detected")
    else:
        st.error("❌ **Fairness Audit Failed** — Potential bias detected")
        
        with st.expander("🔍 View Details"):
            # Feature importance
            if fairness_report.get('feature_importance'):
                st.markdown("**Feature Importance (should be ~0):**")
                for attr, imp in fairness_report['feature_importance'].items():
                    status = "✅" if imp < 0.1 else "⚠️"
                    st.write(f"{status} {attr}: {imp:.3f}")
            
            # Disparate impact
            if fairness_report.get('disparate_impact'):
                st.markdown("**Disparate Impact Ratios (should be ≥0.8):**")
                for group, data in fairness_report['disparate_impact'].items():
                    if isinstance(data, dict) and 'ratio' in data:
                        status = "✅" if data['passed'] else "❌"
                        st.write(f"{status} {group}: {data['ratio']:.2f}")
            
            # Proxy check
            proxy = fairness_report.get('proxy_check', {})
            if proxy.get('suspected_proxies'):
                st.markdown("**⚠️ Suspected Proxy Features:**")
                for p in proxy['suspected_proxies']:
                    st.write(f"- {p['feature']}: college_corr={p['correlation_college']:.2f}, gender_corr={p['correlation_gender']:.2f}")