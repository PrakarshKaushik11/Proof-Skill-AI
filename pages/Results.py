# pages/Results.py
"""
Results Page — Pre vs Post comparison, final score breakdown, actionable gaps.
"""
import streamlit as st
import json
from src.services.scoring_engine import ScoringEngine
from src.db.session import db_session
from src.models.schemas import *
from src.config.settings import settings


def show_results():
    user = st.session_state.user
    
    st.markdown(f'<h1 class="main-header">📈 Results — {user.user_id}</h1>', unsafe_allow_html=True)
    
    # Load data
    with db_session() as db:
        from sqlalchemy import text
        
        # Proof card
        pc_result = db.execute(
            text("SELECT * FROM proof_cards WHERE user_id = :uid ORDER BY version DESC LIMIT 1"),
            {"uid": user.user_id}
        ).fetchone()
        
        # Viva session
        vs_result = db.execute(
            text("SELECT * FROM viva_sessions WHERE user_id = :uid AND status = 'completed' ORDER BY completed_at DESC LIMIT 1"),
            {"uid": user.user_id}
        ).fetchone()
        
        # Final score
        fs_result = db.execute(
            text("SELECT * FROM final_scores WHERE user_id = :uid ORDER BY computed_at DESC LIMIT 1"),
            {"uid": user.user_id}
        ).fetchone()
    
    if not pc_result:
        st.error("No Proof Card found. Generate one first.")
        if st.button("📊 Go to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    
    proof_card = json.loads(pc_result.card_json)
    
    # If no final score yet, compute it
    if not fs_result:
        if not vs_result:
            st.warning("Viva session not completed yet.")
            if st.button("🎤 Start Viva"):
                st.session_state.page = "viva"
                st.rerun()
            return
        
        # Compute final score
        with st.spinner("Computing final score..."):
            viva_result = json.loads(vs_result.session_json)
            engine = ScoringEngine()
            final_score = engine.compute_final_score(proof_card, viva_result)
            
            # Save
            with db_session() as db:
                from sqlalchemy import text
                db.execute(text("""
                    INSERT INTO final_scores (user_id, viva_session_id, proof_card_id,
                                            evidence_strength, viva_performance, assessment_score, consistency,
                                            total_score, skill_scores_json, reasons_json,
                                            pre_viva_confidence_json, post_viva_confidence_json)
                    VALUES (:uid, :vsid, :pcid, :ev, :vp, :as, :cons, :total, :skills, :reasons, :pre, :post)
                """), {
                    "uid": user.user_id,
                    "vsid": vs_result.id,
                    "pcid": pc_result.id,
                    "ev": final_score.evidence_strength,
                    "vp": final_score.viva_performance,
                    "as": final_score.assessment_score,
                    "cons": final_score.consistency,
                    "total": final_score.total_score,
                    "skills": json.dumps(final_score.skill_scores),
                    "reasons": json.dumps(final_score.reasons),
                    "pre": json.dumps(final_score.pre_viva_confidence),
                    "post": json.dumps(final_score.post_viva_confidence),
                })
                db.commit()
            
            st.success("✅ Final score computed!")
            st.rerun()
        return
    
    # Display results
    final_score = json.loads(fs_result.skill_scores_json) if fs_result.skill_scores_json else {}
    reasons = json.loads(fs_result.reasons_json) if fs_result.reasons_json else []
    pre_conf = json.loads(fs_result.pre_viva_confidence_json) if fs_result.pre_viva_confidence_json else {}
    post_conf = json.loads(fs_result.post_viva_confidence_json) if fs_result.post_viva_confidence_json else {}
    
    # Overall Score Card
    st.markdown("### 🏆 Final Score")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("**Total**", f"{fs_result.total_score:.1f}/100", 
                 help="Weighted composite score")
    with col2:
        st.metric("Evidence", f"{fs_result.evidence_strength:.1f}",
                 help="Proof Card confidence (resume + repos + assessments)")
    with col3:
        st.metric("Viva", f"{fs_result.viva_performance:.1f}",
                 help="Interview performance average")
    with col4:
        st.metric("Assessment", f"{fs_result.assessment_score:.1f}",
                 help="External test scores")
    with col5:
        st.metric("Consistency", f"{fs_result.consistency:.1f}",
                 help="Cross-source alignment")
    
    # Score breakdown chart
    st.markdown("#### 📊 Score Breakdown")
    chart_data = {
        "Component": ["Evidence", "Viva", "Assessment", "Consistency"],
        "Score": [fs_result.evidence_strength, fs_result.viva_performance, 
                 fs_result.assessment_score, fs_result.consistency],
        "Weight": [settings.WEIGHT_EVIDENCE_STRENGTH, settings.WEIGHT_VIVA_PERFORMANCE,
                  settings.WEIGHT_ASSESSMENT, settings.WEIGHT_CONSISTENCY]
    }
    st.bar_chart(chart_data, x="Component", y="Score", color="Component")
    
    st.markdown("---")
    
    # Pre vs Post Comparison
    st.markdown("### 📊 Pre vs Post Viva Comparison")
    
    if pre_conf and post_conf:
        comparison_data = []
        for skill in set(list(pre_conf.keys()) + list(post_conf.keys())):
            pre = pre_conf.get(skill, 0)
            post = post_conf.get(skill, 0)
            comparison_data.append({
                "Skill": skill,
                "Pre-Viva": pre,
                "Post-Viva": post,
                "Change": post - pre
            })
        
        if comparison_data:
            import pandas as pd
            df = pd.DataFrame(comparison_data)
            st.dataframe(
                df.style.format({"Pre-Viva": "{:.0f}", "Post-Viva": "{:.0f}", "Change": "{:+.0f}"})
                .background_gradient(subset=["Change"], cmap="RdYlGn", vmin=-20, vmax=20),
                use_container_width=True
            )
            
            # Visual bars
            for item in comparison_data:
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    st.markdown(f"**{item['Skill']}**")
                with col2:
                    pre_pct = item['Pre-Viva']
                    post_pct = item['Post-Viva']
                    st.markdown(f"""
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <div style="flex: 1; height: 20px; background: #e5e7eb; border-radius: 10px; overflow: hidden;">
                            <div style="width: {pre_pct}%; height: 100%; background: #9ca3af; border-radius: 10px;"></div>
                        </div>
                        <span style="width: 40px; text-align: center;">→</span>
                        <div style="flex: 1; height: 20px; background: #e5e7eb; border-radius: 10px; overflow: hidden;">
                            <div style="width: {post_pct}%; height: 100%; background: {'#22c55e' if item['Change'] >= 0 else '#ef4444'}; border-radius: 10px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    color = "#22c55e" if item['Change'] >= 0 else "#ef4444"
                    st.markdown(f"<span style='color: {color}; font-weight: bold;'>{item['Change']:+.0f}</span>", 
                              unsafe_allow_html=True)
    else:
        st.info("Pre/Post comparison data not available.")
    
    st.markdown("---")
    
    # Per-skill detailed breakdown
    st.markdown("### 🛠️ Per-Skill Breakdown")
    
    for skill_name, scores in final_score.items():
        with st.expander(f"{skill_name} — Total: {scores.get('total', 0):.1f}"):
            cols = st.columns(4)
            components = ["evidence", "viva", "assessment", "consistency"]
            labels = ["Evidence", "Viva", "Assessment", "Consistency"]
            
            for i, (comp, label) in enumerate(zip(components, labels)):
                with cols[i]:
                    val = scores.get(comp, 0)
                    st.metric(label, f"{val:.1f}")
            
            # Evidence details from proof card
            for skill in proof_card.get('unified_skills', []):
                if skill['skill'] == skill_name:
                    st.markdown("**Evidence Bundle:**")
                    for ev in skill.get('evidence_bundle', []):
                        source_icons = {"repo": "🐙", "assessment": "📝", "resume": "📄", "viva": "🎤"}
                        icon = source_icons.get(ev['type'], "📌")
                        st.markdown(f'<div class="evidence-item">{icon} <strong>{ev["source"]}</strong> ({ev["weight"]:.0%}): {ev["detail"]}</div>', 
                                  unsafe_allow_html=True)
                    
                    if skill.get('gap_notes'):
                        st.info(f"💡 **Gap to address:** {skill['gap_notes']}")
                    break
    
    st.markdown("---")
    
    # Rank Reasons
    if reasons:
        st.markdown("### 🎯 Why This Score?")
        for i, reason in enumerate(reasons, 1):
            st.markdown(f"{i}. {reason}")
    
    st.markdown("---")
    
    # Actionable gaps
    st.markdown("### 💡 Actionable Gaps — What to Strengthen")
    
    gaps_found = False
    for skill in proof_card.get('unified_skills', []):
        if skill.get('gap_notes'):
            gaps_found = True
            st.warning(f"**{skill['skill']}**: {skill['gap_notes']}")
    
    if not gaps_found:
        st.success("🎉 No major gaps identified! Your profile is well-rounded.")
    
    st.markdown("---")
    
    # Export & Next Steps
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Export Report (JSON)", use_container_width=True):
            export_data = {
                "candidate_id": user.user_id,
                "proof_card": proof_card,
                "final_score": {
                    "total": fs_result.total_score,
                    "components": {
                        "evidence": fs_result.evidence_strength,
                        "viva": fs_result.viva_performance,
                        "assessment": fs_result.assessment_score,
                        "consistency": fs_result.consistency
                    },
                    "skill_scores": final_score,
                    "reasons": reasons
                },
                "pre_post_comparison": comparison_data if 'comparison_data' in locals() else []
            }
            st.download_button(
                "💾 Download JSON",
                data=json.dumps(export_data, indent=2, default=str),
                file_name=f"proofskill_{user.user_id}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
        if st.button("📊 View Recruiter Comparison", use_container_width=True):
            st.session_state.page = "recruiter"
            st.rerun()
    
    with col3:
        if st.button("🔄 Retake Viva", use_container_width=True):
            # Reset viva session
            with db_session() as db:
                from sqlalchemy import text
                db.execute(text("UPDATE viva_sessions SET status = 'completed' WHERE user_id = :uid AND status = 'in_progress'"),
                          {"uid": user.user_id})
                db.commit()
            st.session_state.page = "viva"
            st.rerun()