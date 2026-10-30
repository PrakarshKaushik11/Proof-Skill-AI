# pages/Recruiter_View.py
"""
Recruiter View — JD selection, ranked candidates, side-by-side comparison.
"""
import streamlit as st
import json
import pandas as pd
import re
from pathlib import Path
from src.services.scoring_engine import ScoringEngine
from src.services.imats_client import IMATSClient
from src.services.auth import AuthService
from src.db.session import db_session
from src.models.schemas import *
from src.config.settings import settings
from datetime import datetime


def show_recruiter():
    st.markdown('<h1 class="main-header">🏢 Recruiter Portal</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Fair, explainable candidate ranking against job requirements</p>', unsafe_allow_html=True)
    # JD Selector
    with db_session() as db:
        from sqlalchemy import text
        jds = db.execute(text("SELECT * FROM recruiter_jds ORDER BY jd_id")).fetchall()
    
    if not jds:
        st.warning("No job descriptions loaded. Please load the 30 JDs from the dataset.")
        if st.button("📥 Load Sample JDs"):
            load_sample_jds()
            st.rerun()
        return
    
    show_candidate_uploads(jds)


def _candidate_name_from_file(file_path: Path) -> str:
    """Read the first useful line from a resume, falling back to its filename."""
    try:
        if file_path.suffix.lower() == ".pdf":
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join((page.extract_text() or "") for page in pdf.pages[:2])
        else:
            from docx import Document
            text = "\n".join(paragraph.text for paragraph in Document(file_path).paragraphs[:10])
        for line in text.splitlines():
            candidate = re.sub(r"\s+", " ", line).strip()
            if candidate and len(candidate) >= 2 and "@" not in candidate:
                return candidate[:120]
    except Exception:
        pass
    fallback = re.sub(r"[_\-]+", " ", file_path.stem)
    return re.sub(r"\s+", " ", fallback).strip()[:120] or "Candidate"


def _next_candidate_id(db) -> str:
    """Return the next unused sequential candidate identifier."""
    from sqlalchemy import text
    rows = db.execute(text("SELECT user_id FROM users WHERE user_id LIKE 'CAND-%'")).fetchall()
    numbers = []
    for row in rows:
        match = re.fullmatch(r"CAND-(\d+)", row.user_id or "")
        if match:
            numbers.append(int(match.group(1)))
    return f"CAND-{max(numbers, default=0) + 1:04d}"


def show_candidate_uploads(jds):
    """Upload resumes in bulk and issue one-time candidate credentials."""
    st.markdown("### 📥 Upload Candidate Resumes")
    st.caption("Upload PDF or DOCX resumes. Each file receives a candidate name, generated ID, and password.")
    if "candidate_upload_version" not in st.session_state:
        st.session_state.candidate_upload_version = 0
    if "new_candidate_credentials" not in st.session_state:
        st.session_state.new_candidate_credentials = []
    if "candidate_management_version" not in st.session_state:
        st.session_state.candidate_management_version = 0

    if st.session_state.new_candidate_credentials:
        st.success("Candidate accounts created successfully. Save these credentials before leaving this page.")
        credentials_df = pd.DataFrame(st.session_state.new_candidate_credentials)
        st.dataframe(credentials_df, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download Credentials CSV",
            credentials_df.to_csv(index=False),
            "candidate_credentials.csv",
            "text/csv",
            key="download_new_candidate_credentials",
        )
        if st.button("Clear Credential Display", key="clear_new_candidate_credentials"):
            st.session_state.new_candidate_credentials = []
            st.rerun()

    uploaded_files = st.file_uploader(
        "Select one or more resumes",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key=f"candidate_resume_uploads_{st.session_state.candidate_upload_version}",
    )
    if uploaded_files and st.button("Create Candidate Accounts", type="primary"):
        auth = AuthService()
        created = []
        failures = []
        for uploaded_file in uploaded_files:
            suffix = Path(uploaded_file.name).suffix.lower()
            if suffix not in {".pdf", ".docx"}:
                failures.append(f"{uploaded_file.name}: only PDF and DOCX are supported")
                continue
            try:
                with db_session() as db:
                    candidate_id = _next_candidate_id(db)
                stored_name = f"{candidate_id}{suffix}"
                destination = settings.RESUME_DIR / stored_name
                destination.write_bytes(uploaded_file.getvalue())
                candidate_name = _candidate_name_from_file(destination)
                password = auth.setup_candidate_credentials(
                    candidate_id,
                    stored_name,
                    password=settings.CANDIDATE_DEFAULT_PASSWORD,
                    candidate_name=candidate_name,
                )
                created.append({
                    "Candidate Name": candidate_name,
                    "Generated ID": candidate_id,
                    "Password": password,
                })
            except Exception as exc:
                failures.append(f"{uploaded_file.name}: {exc}")

        if created:
            st.session_state.new_candidate_credentials = created
            st.session_state.candidate_upload_version += 1
            st.rerun()
        for failure in failures:
            st.error(failure)

    with st.expander("👥 Manage Candidate Accounts", expanded=True):
        with db_session() as db:
            from sqlalchemy import text
            candidates = db.execute(text("""
                SELECT candidate_name, user_id, resume_path, created_at
                FROM users ORDER BY created_at DESC
            """)).fetchall()
        if candidates:
            candidate_rows = [{
                "Candidate Name": row.candidate_name,
                "Generated ID": row.user_id,
                "Resume": row.resume_path,
                "Created": row.created_at,
            } for row in candidates]
            st.dataframe(pd.DataFrame(candidate_rows), use_container_width=True, hide_index=True)
            candidate_ids = [row.user_id for row in candidates]
            selected_for_removal = st.multiselect(
                "Select account(s) to remove",
                options=candidate_ids,
                format_func=lambda user_id: next(
                    f"{row.candidate_name} — {row.user_id}" for row in candidates
                    if row.user_id == user_id
                ),
                key=f"selected_candidate_accounts_{st.session_state.candidate_management_version}",
            )
            if selected_for_removal and st.button(
                "🗑️ Remove Selected Accounts",
                type="secondary",
                key="remove_selected_candidate_accounts",
            ):
                with db_session() as db:
                    from sqlalchemy import bindparam, text
                    rows_to_remove = db.execute(text("""
                        SELECT user_id, resume_path
                        FROM users
                        WHERE user_id IN :user_ids
                    """).bindparams(bindparam("user_ids", expanding=True)), {
                        "user_ids": selected_for_removal
                    }).fetchall()
                    for row in rows_to_remove:
                        db.execute(
                            text("DELETE FROM users WHERE user_id = :user_id"),
                            {"user_id": row.user_id},
                        )
                        resume_path = settings.RESUME_DIR / row.resume_path
                        if resume_path.is_file():
                            resume_path.unlink()
                st.session_state.candidate_management_version += 1
                st.success(f"Removed {len(selected_for_removal)} candidate account(s).")
                st.rerun()
        else:
            st.info("No candidate accounts yet.")
    
    # JD Selection
    jd_options = {f"{jd.jd_id}: {jd.title}": jd.jd_id for jd in jds}
    selected_jd_label = st.selectbox("Select Job Description", options=list(jd_options.keys()))
    selected_jd_id = jd_options[selected_jd_label]
    
    # Load JD details
    with db_session() as db:
        from sqlalchemy import text
        jd = db.execute(
            text("SELECT * FROM recruiter_jds WHERE jd_id = :id"),
            {"id": selected_jd_id}
        ).fetchone()
        
        # Get rankings for this JD
        rankings = db.execute(text("""
            SELECT r.*, u.user_id, fs.total_score, fs.skill_scores_json, fs.reasons_json
            FROM rankings r
            JOIN users u ON u.user_id = r.user_id
            JOIN final_scores fs ON fs.id = r.final_score_id
            WHERE r.jd_id = :jd_id
            ORDER BY r.rank
        """), {"jd_id": selected_jd_id}).fetchall()
    
    # JD Info
    with st.expander("📋 Job Description Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{jd.title}**")
            st.caption(f"JD ID: {jd.jd_id} | Company: {jd.company or 'N/A'}")
        with col2:
            required = json.loads(jd.required_skills_json) if jd.required_skills_json else []
            preferred = json.loads(jd.preferred_skills_json) if jd.preferred_skills_json else []
            st.markdown(f"**Required Skills:** {len(required)}")
            st.markdown(f"**Preferred Skills:** {len(preferred)}")
        
        st.markdown(jd.description[:500] + ("..." if len(jd.description) > 500 else ""))
    
    if not rankings:
        st.info("No candidates ranked for this JD yet. Run ranking computation first.")
        if st.button("🔄 Compute Rankings", type="primary"):
            compute_rankings(selected_jd_id)
            st.rerun()
        return
    
    # Ranked Candidate Table
    st.markdown(f"### 📊 Ranked Candidates ({len(rankings)} total)")
    
    # Summary table
    table_data = []
    for r in rankings:
        skill_scores = json.loads(r.skill_scores_json) if r.skill_scores_json else {}
        top_skills = sorted(skill_scores.items(), key=lambda x: x[1].get('total', 0), reverse=True)[:3]
        skill_str = ", ".join([f"{s} ({v.get('total', 0):.0f})" for s, v in top_skills])
        
        table_data.append({
            "Rank": r.rank,
            "Candidate": r.user_id,
            "Total Score": f"{r.score:.1f}",
            "Top Skills": skill_str,
            "Reasons": "; ".join(json.loads(r.reasons_json)[:2]) if r.reasons_json else ""
        })
    
    df = pd.DataFrame(table_data)
    
    # Selection for comparison
    selected_candidates = st.multiselect(
        "Select 2 candidates to compare side-by-side",
        options=[r.user_id for r in rankings],
        max_selections=2,
        format_func=lambda x: f"Rank {next(r.rank for r in rankings if r.user_id == x)} — {x}"
    )
    
    st.dataframe(
        df.style.apply(
            lambda x: ['background-color: #d1fae5' if x.Rank == 1 else 
                      'background-color: #fef3c7' if x.Rank <= 3 else 
                      'background-color: #fef2f2' if x.Rank <= 10 else '' for _ in x],
            axis=1
        ),
        use_container_width=True,
        hide_index=True
    )
    
    # Side-by-side comparison
    if len(selected_candidates) == 2:
        st.markdown("---")
        show_side_by_side(selected_jd_id, selected_candidates[0], selected_candidates[1])
    elif len(selected_candidates) == 1:
        st.info("Select one more candidate to enable side-by-side comparison.")
    
    # IMATS Sync
    st.markdown("---")
    st.markdown("### 🔗 IMATS Integration")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📤 Push Rankings to IMATS", use_container_width=True, type="primary"):
            push_to_imats(selected_jd_id, rankings)
    
    with col2:
        if st.button("📥 Pull Shortlist Decisions", use_container_width=True):
            pull_shortlist_decisions(selected_jd_id)
    
    with col3:
        if st.button("📋 View Sync History", use_container_width=True):
            show_sync_history()


def show_side_by_side(jd_id, cand_a_id, cand_b_id):
    """Side-by-side comparison of two candidates."""
    st.markdown("### ⚖️ Side-by-Side Comparison")
    
    with db_session() as db:
        from sqlalchemy import text
        
        # Get full data for both candidates
        cand_a = db.execute(text("""
            SELECT r.*, fs.skill_scores_json, fs.reasons_json, fs.total_score,
                   pc.unified_skills_json, pc.tutorial_clone_flags_json, pc.evidence_coverage
            FROM rankings r
            JOIN final_scores fs ON fs.id = r.final_score_id
            JOIN proof_cards pc ON pc.user_id = r.user_id
            WHERE r.jd_id = :jd AND r.user_id = :uid
        """), {"jd": jd_id, "uid": cand_a_id}).fetchone()
        
        cand_b = db.execute(text("""
            SELECT r.*, fs.skill_scores_json, fs.reasons_json, fs.total_score,
                   pc.unified_skills_json, pc.tutorial_clone_flags_json, pc.evidence_coverage
            FROM rankings r
            JOIN final_scores fs ON fs.id = r.final_score_id
            JOIN proof_cards pc ON pc.user_id = r.user_id
            WHERE r.jd_id = :jd AND r.user_id = :uid
        """), {"jd": jd_id, "uid": cand_b_id}).fetchone()
    
    if not cand_a or not cand_b:
        st.error("Could not load candidate data")
        return
    
    # Parse data
    skills_a = json.loads(cand_a.unified_skills_json) if cand_a.unified_skills_json else []
    skills_b = json.loads(cand_b.unified_skills_json) if cand_b.unified_skills_json else []
    clones_a = json.loads(cand_a.tutorial_clone_flags_json) if cand_a.tutorial_clone_flags_json else []
    clones_b = json.loads(cand_b.tutorial_clone_flags_json) if cand_b.tutorial_clone_flags_json else []
    reasons_a = json.loads(cand_a.reasons_json) if cand_a.reasons_json else []
    reasons_b = json.loads(cand_b.reasons_json) if cand_b.reasons_json else []
    
    # Header
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### 🥇 Rank {cand_a.rank} — {cand_a_id}")
        st.metric("Total Score", f"{cand_a.total_score:.1f}")
        st.metric("Evidence Coverage", f"{cand_a.evidence_coverage:.0f}%")
        if clones_a:
            st.warning(f"⚠️ {len(clones_a)} tutorial clone flag(s)")
    with col2:
        st.markdown(f"#### 🥈 Rank {cand_b.rank} — {cand_b_id}")
        st.metric("Total Score", f"{cand_b.total_score:.1f}")
        st.metric("Evidence Coverage", f"{cand_b.evidence_coverage:.0f}%")
        if clones_b:
            st.warning(f"⚠️ {len(clones_b)} tutorial clone flag(s)")
    
    st.markdown("---")
    
    # Skill comparison table
    st.markdown("#### 🛠️ Skill-by-Skill Comparison")
    
    all_skills = set([s['skill'] for s in skills_a] + [s['skill'] for s in skills_b])
    
    comparison_rows = []
    for skill in sorted(all_skills):
        sa = next((s for s in skills_a if s['skill'] == skill), None)
        sb = next((s for s in skills_b if s['skill'] == skill), None)
        
        conf_a = sa['final_confidence'] if sa else 0
        conf_b = sb['final_confidence'] if sb else 0
        
        ev_a = sa['evidence_bundle'] if sa else []
        ev_b = sb['evidence_bundle'] if sb else []
        
        has_repo_a = any(e['type'] == 'repo' for e in ev_a)
        has_repo_b = any(e['type'] == 'repo' for e in ev_b)
        
        comparison_rows.append({
            "Skill": skill,
            f"{cand_a_id}\nConfidence": f"{conf_a:.0f}%",
            f"{cand_b_id}\nConfidence": f"{conf_b:.0f}%",
            f"{cand_a_id}\nRepo Evidence": "✅" if has_repo_a else "❌",
            f"{cand_b_id}\nRepo Evidence": "✅" if has_repo_b else "❌",
            "Advantage": cand_a_id if conf_a > conf_b else cand_b_id if conf_b > conf_a else "Tie"
        })
    
    df_comp = pd.DataFrame(comparison_rows)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)
    
    # Rank reasons
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### 🎯 Why {cand_a_id} is Rank {cand_a.rank}")
        for reason in reasons_a:
            st.markdown(f"• {reason}")
    with col2:
        st.markdown(f"#### 🎯 Why {cand_b_id} is Rank {cand_b.rank}")
        for reason in reasons_b:
            st.markdown(f"• {reason}")
    
    # Detailed evidence
    with st.expander("🔍 Detailed Evidence Comparison"):
        skill_tabs = st.tabs(sorted(all_skills))
        for i, skill in enumerate(sorted(all_skills)):
            with skill_tabs[i]:
                col1, col2 = st.columns(2)
                sa = next((s for s in skills_a if s['skill'] == skill), None)
                sb = next((s for s in skills_b if s['skill'] == skill), None)
                
                with col1:
                    if sa:
                        render_skill_detail(sa, cand_a_id)
                    else:
                        st.info(f"Not claimed by {cand_a_id}")
                
                with col2:
                    if sb:
                        render_skill_detail(sb, cand_b_id)
                    else:
                        st.info(f"Not claimed by {cand_b_id}")


def render_skill_detail(skill, candidate_id):
    """Render detailed skill evidence."""
    st.markdown(f"**{skill['skill']}** — {skill['final_confidence']:.0f}%")
    
    if skill.get('tutorial_clone_flag'):
        st.error("⚠️ Tutorial clone flag")
    
    if skill.get('gap_notes'):
        st.info(f"💡 Gap: {skill['gap_notes']}")
    
    for ev in skill.get('evidence_bundle', []):
        source_icons = {"repo": "🐙", "assessment": "📝", "resume": "📄", "viva": "🎤"}
        icon = source_icons.get(ev['type'], "📌")
        st.markdown(f'<div class="evidence-item">{icon} <strong>{ev["source"]}</strong> ({ev["weight"]:.0%}): {ev["detail"]}</div>', 
                  unsafe_allow_html=True)


def compute_rankings(jd_id):
    """Compute rankings for all candidates against a JD."""
    with st.spinner("Computing rankings..."):
        with db_session() as db:
            from sqlalchemy import text
            
            # Get all candidates with final scores
            candidates = db.execute(text("""
                SELECT u.user_id, fs.id as fs_id, fs.total_score, fs.skill_scores_json
                FROM users u
                JOIN final_scores fs ON fs.user_id = u.user_id
                WHERE fs.id = (SELECT MAX(id) FROM final_scores WHERE user_id = u.user_id)
            """)).fetchall()
            
            if not candidates:
                st.error("No candidates with final scores found.")
                return
            
            # Get JD requirements
            jd = db.execute(text("SELECT * FROM recruiter_jds WHERE jd_id = :id"), {"id": jd_id}).fetchone()
            required_skills = json.loads(jd.required_skills_json) if jd.required_skills_json else []
            
            # Simple ranking by total score (in real app, use ScoringEngine.rank_candidates)
            ranked = sorted(candidates, key=lambda c: c.total_score, reverse=True)
            
            # Save rankings
            for rank, cand in enumerate(ranked, 1):
                skill_scores = json.loads(cand.skill_scores_json) if cand.skill_scores_json else {}
                
                # Generate comparison
                comparison = {}
                for req in required_skills:
                    skill_name = req['skill']
                    candidate_score = skill_scores.get(skill_name, {}).get('total', 0)
                    required_level = req['level']
                    
                    if candidate_score >= 80:
                        gap = "none"
                    elif candidate_score >= 60:
                        gap = "low"
                    elif candidate_score >= 40:
                        gap = "moderate"
                    else:
                        gap = "high"
                    
                    comparison[skill_name] = {
                        "jd_required": required_level,
                        "candidate_score": candidate_score,
                        "gap": gap,
                        "evidence": "Repo + Viva" if skill_scores.get(skill_name, {}).get('evidence', 0) > 50 else "Limited"
                    }
                
                reasons = [f"Strong evidence in {k}" for k, v in skill_scores.items() if v.get('evidence', 0) > 70]
                if not reasons:
                    reasons = ["Overall solid profile"]
                
                db.execute(text("""
                    INSERT OR REPLACE INTO rankings (jd_id, user_id, final_score_id, rank, score, comparison_json, reasons_json)
                    VALUES (:jd, :uid, :fsid, :rank, :score, :comp, :reasons)
                """), {
                    "jd": jd_id,
                    "uid": cand.user_id,
                    "fsid": cand.fs_id,
                    "rank": rank,
                    "score": cand.total_score,
                    "comp": json.dumps(comparison),
                    "reasons": json.dumps(reasons)
                })
            
            db.commit()
            st.success(f"✅ Ranked {len(ranked)} candidates for {jd_id}")


def push_to_imats(jd_id, rankings):
    """Push rankings to IMATS sandbox."""
    with st.spinner("Pushing to IMATS..."):
        try:
            client = IMATSClient(settings.IMATS_API_URL, settings.IMATS_API_KEY)
            
            # Prepare payload
            payload = {
                "jd_id": jd_id,
                "rankings": [
                    {
                        "candidate_id": r.user_id,
                        "rank": r.rank,
                        "score": r.score,
                        "reasons": json.loads(r.reasons_json) if r.reasons_json else []
                    }
                    for r in rankings
                ]
            }
            
            # In real app: await client.push_rankings(payload)
            # For demo, just log
            with db_session() as db:
                from sqlalchemy import text
                db.execute(text("""
                    INSERT INTO imats_sync (sync_type, payload_json, response_json, status)
                    VALUES ('rankings', :payload, :resp, 'success')
                """), {
                    "payload": json.dumps(payload),
                    "resp": json.dumps({"status": "accepted", "count": len(rankings)})
                })
                db.commit()
            
            st.success(f"✅ Pushed {len(rankings)} rankings to IMATS!")
            
        except Exception as e:
            st.error(f"❌ IMATS push failed: {str(e)}")


def pull_shortlist_decisions(jd_id):
    """Pull shortlist decisions from IMATS."""
    with st.spinner("Pulling from IMATS..."):
        try:
            client = IMATSClient(settings.IMATS_API_URL, settings.IMATS_API_KEY)
            
            # In real app: decisions = await client.pull_shortlist_decisions([jd_id])
            # Demo data
            decisions = [
                {"jd_id": jd_id, "candidate_id": "CAND-0042", "decision": "shortlisted", "notes": "Strong backend skills"},
                {"jd_id": jd_id, "candidate_id": "CAND-0117", "decision": "rejected", "notes": "Insufficient evidence"},
            ]
            
            with db_session() as db:
                from sqlalchemy import text
                for d in decisions:
                    db.execute(text("""
                        INSERT INTO imats_sync (sync_type, payload_json, response_json, status)
                        VALUES ('shortlist_pull', :payload, :resp, 'success')
                    """), {
                        "payload": json.dumps({"jd_id": jd_id}),
                        "resp": json.dumps(d)
                    })
                db.commit()
            
            st.success(f"✅ Pulled {len(decisions)} shortlist decisions!")
            st.json(decisions)
            
        except Exception as e:
            st.error(f"❌ IMATS pull failed: {str(e)}")


def show_sync_history():
    """Show IMATS sync history."""
    with db_session() as db:
        from sqlalchemy import text
        history = db.execute(text("""
            SELECT * FROM imats_sync ORDER BY synced_at DESC LIMIT 20
        """)).fetchall()
    
    if history:
        df = pd.DataFrame([{
            "Time": h.synced_at,
            "Type": h.sync_type,
            "Status": h.status,
            "Error": h.error_message or ""
        } for h in history])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No sync history yet.")


def load_sample_jds():
    """Load sample job descriptions for demo."""
    sample_jds = [
        {
            "jd_id": "JD-001",
            "title": "Backend Engineer - Python",
            "company": "TechCorp",
            "description": "We are looking for a Backend Engineer with strong Python skills...",
            "required_skills": json.dumps([
                {"skill": "Python", "level": "advanced", "weight": 1.0, "required": True},
                {"skill": "FastAPI", "level": "intermediate", "weight": 0.8, "required": True},
                {"skill": "PostgreSQL", "level": "intermediate", "weight": 0.7, "required": True},
                {"skill": "Docker", "level": "beginner", "weight": 0.5, "required": False},
            ]),
            "preferred_skills": json.dumps([
                {"skill": "AWS", "level": "beginner", "weight": 0.4, "required": False},
                {"skill": "Kubernetes", "level": "beginner", "weight": 0.3, "required": False},
            ])
        },
        {
            "jd_id": "JD-002",
            "title": "Frontend Developer - React",
            "company": "StartupXYZ",
            "description": "Frontend Developer role focusing on React and TypeScript...",
            "required_skills": json.dumps([
                {"skill": "React", "level": "advanced", "weight": 1.0, "required": True},
                {"skill": "TypeScript", "level": "intermediate", "weight": 0.9, "required": True},
                {"skill": "CSS", "level": "intermediate", "weight": 0.6, "required": True},
            ]),
            "preferred_skills": json.dumps([
                {"skill": "Next.js", "level": "intermediate", "weight": 0.5, "required": False},
                {"skill": "Testing", "level": "beginner", "weight": 0.4, "required": False},
            ])
        },
        {
            "jd_id": "JD-003",
            "title": "Data Analyst",
            "company": "DataDriven Inc",
            "description": "Data Analyst position requiring SQL, Python, and visualization skills...",
            "required_skills": json.dumps([
                {"skill": "SQL", "level": "advanced", "weight": 1.0, "required": True},
                {"skill": "Python", "level": "intermediate", "weight": 0.8, "required": True},
                {"skill": "Tableau", "level": "intermediate", "weight": 0.7, "required": True},
            ]),
            "preferred_skills": json.dumps([
                {"skill": "Pandas", "level": "intermediate", "weight": 0.5, "required": False},
                {"skill": "Statistics", "level": "intermediate", "weight": 0.5, "required": False},
            ])
        }
    ]
    
    with db_session() as db:
        from sqlalchemy import text
        for jd in sample_jds:
            db.execute(text("""
                INSERT OR IGNORE INTO recruiter_jds (jd_id, title, company, description, required_skills_json, preferred_skills_json)
                VALUES (:jd_id, :title, :company, :desc, :req, :pref)
            """), jd)
        db.commit()
    
    st.success("✅ Loaded 3 sample JDs")


# Need to import datetime
from datetime import datetime