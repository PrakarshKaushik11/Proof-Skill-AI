# pages/Candidate_Dashboard.py
"""
Candidate Dashboard — Resume preview, GitHub repo selection, analysis trigger.
"""
import streamlit as st
import json
from pathlib import Path
from src.services.resume_parser import ResumeParser
from src.services.github_fetcher import GitHubFetcher
from src.services.repo_analyzer import RepoAnalyzer
from src.services.evidence_synthesizer import EvidenceSynthesizer
from src.db.session import db_session
from src.models.schemas import *
from src.config.settings import settings


def show_dashboard():
    user = st.session_state.user
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<h1 class="main-header">📊 Dashboard — {user.user_id}</h1>', unsafe_allow_html=True)
    with col2:
        st.caption("Recruiter access is available only through recruiter login.")
    
    has_github = candidate_has_github(user)
    step_key = f"dashboard_step_{user.user_id}"
    if step_key not in st.session_state:
        st.session_state[step_key] = "resume"
    if not has_github and st.session_state[step_key] == "github":
        st.session_state[step_key] = "analysis"

    current_step = st.session_state[step_key]
    if current_step == "resume":
        show_resume_tab(user)
        render_dashboard_navigation(step_key, "resume", has_github)
    elif current_step == "github":
        show_github_tab(user)
        render_dashboard_navigation(step_key, "github", has_github)
    elif current_step == "analysis":
        show_analysis_tab(user)
        render_dashboard_navigation(step_key, "analysis", has_github)
    else:
        show_proof_card_tab(user)
        render_dashboard_navigation(step_key, "proof_card", has_github)


def candidate_has_github(user) -> bool:
    """Return whether the candidate has a GitHub profile or repository link."""
    with db_session() as db:
        from sqlalchemy import text
        links = db.execute(
            text("SELECT url, link_type FROM github_links WHERE user_id = :uid"),
            {"uid": user.user_id},
        ).fetchall()
        profile_links = [link for link in links if link.link_type == "profile"]
        if profile_links:
            return True
        resume = db.execute(
            text("SELECT parsed_json FROM resumes WHERE user_id = :uid ORDER BY created_at DESC LIMIT 1"),
            {"uid": user.user_id},
        ).fetchone()
        if not resume:
            return False
        try:
            github_urls = json.loads(resume.parsed_json).get("github_urls", [])
        except (TypeError, json.JSONDecodeError):
            return False
        if not github_urls:
            return False
        for github_url in github_urls:
            url = str(github_url)
            if not url.startswith(("http://", "https://")):
                url = "https://github.com/" + url.lstrip("@/")
            db.execute(text("""
                INSERT OR IGNORE INTO github_links
                    (user_id, url, link_type, extracted_from)
                VALUES (:uid, :url, 'profile', 'resume')
            """), {"uid": user.user_id, "url": url})
        db.commit()
        return True


def render_dashboard_navigation(step_key: str, current_step: str, has_github: bool):
    """Render centered previous/next buttons for the dashboard flow."""
    steps = ["resume", "github", "analysis", "proof_card"] if has_github else [
        "resume", "analysis", "proof_card"
    ]
    index = steps.index(current_step)
    st.markdown("---")
    left, center, right = st.columns([1, 2, 1])
    with center:
        if index > 0:
            if st.button("← Previous", use_container_width=True, key=f"previous_{current_step}"):
                st.session_state[step_key] = steps[index - 1]
                st.rerun()
        if index < len(steps) - 1:
            next_labels = {
                "resume": "Continue to GitHub Repos →" if has_github else "Continue to Analysis →",
                "github": "Continue to Analysis →",
                "analysis": "Continue to Proof Card →",
            }
            if st.button(next_labels[current_step], type="primary",
                         use_container_width=True, key=f"next_{current_step}"):
                st.session_state[step_key] = steps[index + 1]
                st.rerun()


def show_resume_tab(user):
    """Display parsed resume data."""
    if st.button("🔄 Re-parse Resume", help="Refresh extracted resume data after a parser update"):
        with db_session() as db:
            from sqlalchemy import text
            db.execute(text("DELETE FROM resumes WHERE user_id = :uid"), {"uid": user.user_id})
            db.commit()
        st.rerun()

    with db_session() as db:
        # Check if resume already parsed
        from sqlalchemy import text
        result = db.execute(
            text("SELECT * FROM resumes WHERE user_id = :uid ORDER BY created_at DESC LIMIT 1"),
            {"uid": user.user_id}
        ).fetchone()
        
        if not result:
            # Parse resume now
            with st.spinner("Parsing resume..."):
                parser = ResumeParser()
                resume_path = settings.RESUME_DIR / user.resume_path
                parsed = parser.parse(resume_path)
                
                # Save to DB
                db.execute(text("""
                    INSERT INTO resumes (user_id, raw_text, parsed_json, skills_json, projects_json, 
                                       education_json, experience_json)
                    VALUES (:uid, :raw, :parsed, :skills, :projects, :edu, :exp)
                """), {
                    "uid": user.user_id,
                    "raw": parsed.raw_text,
                    "parsed": parsed.model_dump_json(),
                    "skills": json.dumps([s.model_dump(mode="json") for s in parsed.skills]),
                    "projects": json.dumps([p.model_dump(mode="json") for p in parsed.projects]),
                    "edu": json.dumps([e.model_dump(mode="json") for e in parsed.education]),
                    "exp": json.dumps([e.model_dump(mode="json") for e in parsed.experience]),
                })
                for github_url in parsed.github_urls:
                    github_url_text = str(github_url)
                    db.execute(text("""
                        INSERT OR IGNORE INTO github_links
                            (user_id, url, link_type, extracted_from)
                        VALUES (:uid, :url, 'profile', 'resume')
                    """), {"uid": user.user_id, "url": github_url_text})
                db.commit()
                st.success("✅ Resume parsed and saved!")
                result = db.execute(
                    text("SELECT * FROM resumes WHERE user_id = :uid ORDER BY created_at DESC LIMIT 1"),
                    {"uid": user.user_id}
                ).fetchone()
        
        # Display parsed data
        parsed_data = json.loads(result.parsed_json)
        
        # Skills
        st.markdown("#### 🛠️ Skills Extracted")
        if parsed_data.get("skills"):
            cols = st.columns(3)
            for i, skill in enumerate(parsed_data["skills"]):
                with cols[i % 3]:
                    level_color = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}.get(skill["level"], "⚪")
                    st.markdown(f"**{level_color} {skill['name']}**  \n*Level: {skill['level'].title()}*")
        else:
            st.info("No skills extracted from resume.")
        
        # Projects
        st.markdown("#### 📦 Projects")
        if parsed_data.get("projects"):
            for proj in parsed_data["projects"]:
                with st.expander(f"📁 {proj['name']}"):
                    st.write(proj.get("description", "No description"))
                    if proj.get("tech_stack"):
                        st.caption("Tech: " + ", ".join(proj["tech_stack"]))
                    if proj.get("github_url"):
                        st.link_button("🔗 GitHub", proj["github_url"])
        else:
            st.info("No projects found in resume.")
        
        # GitHub URLs found
        st.markdown("#### 🔗 GitHub Links Found")
        github_urls = parsed_data.get("github_urls", [])
        if github_urls:
            for url in github_urls:
                st.code(url)
        else:
            st.info("No GitHub URLs found in resume.")
        
        # Education & Experience
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🎓 Education")
            for edu in parsed_data.get("education", []):
                st.markdown(f"- **{edu['degree']}** — {edu['college']} ({edu['year']})" + 
                          (f" | CGPA: {edu['cgpa']}" if edu.get('cgpa') else ""))
        
        with col2:
            st.markdown("#### 💼 Experience")
            for exp in parsed_data.get("experience", []):
                st.markdown(f"- **{exp['role']}** at {exp['company']} ({exp['duration_months']} months)")
                if exp.get("skills"):
                    st.caption("Skills: " + ", ".join(exp["skills"]))


def show_github_tab(user):
    """GitHub repo fetching and selection."""
    with db_session() as db:
        from sqlalchemy import text
        
        # Check for GitHub links in resume
        result = db.execute(
            text("SELECT * FROM github_links WHERE user_id = :uid"),
            {"uid": user.user_id}
        ).fetchall()
        
        profile_urls = [r for r in result if r.link_type == "profile"]
        
        if not profile_urls:
            st.info("📭 No GitHub profile URL found in your resume.")
            st.caption("Add your GitHub profile (github.com/username) to your resume to enable repo analysis.")
            return
        
        # Use first profile URL
        profile_url = profile_urls[0].url
        username = profile_url.rstrip("/").split("/")[-1]
        
        st.markdown(f"#### 🐙 GitHub Profile: `@{username}`")
        st.link_button("View Profile", profile_url)
        
        repos_key = f"repos_{user.user_id}"
        fetch_error_key = f"repos_error_{user.user_id}"

        def fetch_repositories(force_refresh: bool = False):
            with st.spinner("Fetching repositories from GitHub..."):
                fetcher = GitHubFetcher(settings.GITHUB_TOKEN, settings.REPO_CACHE_DIR)
                try:
                    repos = fetcher.get_user_repos(username, force_refresh=force_refresh)
                except Exception as exc:
                    st.session_state[fetch_error_key] = str(exc)
                    return

                # Save to github_links if not exists
                for repo in repos:
                    db.execute(text("""
                        INSERT OR IGNORE INTO github_links (user_id, url, link_type, extracted_from)
                        VALUES (:uid, :url, 'repo', 'profile_fetch')
                    """), {"uid": user.user_id, "url": str(repo.html_url)})
                db.commit()
                
                st.session_state[repos_key] = repos
                st.session_state.pop(fetch_error_key, None)

        if repos_key not in st.session_state:
            fetch_repositories()

        if st.button("🔄 Refresh Public Repositories", type="secondary", use_container_width=True):
            fetch_repositories(force_refresh=True)

        if fetch_error_key in st.session_state:
            st.error(f"Could not load GitHub repositories: {st.session_state[fetch_error_key]}")
        
        # Display repos with selection
        repos = st.session_state.get(repos_key, [])
        
        if repos:
            st.markdown("#### 📦 Select Repositories to Analyze")
            st.caption("Choose up to 5 repositories that best showcase your skills. Non-fork, recently updated repos are pre-selected.")
            
            # Get already selected
            selected_result = db.execute(
                text("SELECT repo_full_name FROM selected_repos WHERE user_id = :uid"),
                {"uid": user.user_id}
            ).fetchall()
            already_selected = {r.repo_full_name for r in selected_result}
            
            # Repo selection UI
            selected_repos = []
            for repo in repos:
                is_fork = repo.is_fork
                is_archived = repo.is_archived
                default_select = not is_fork and not is_archived and repo.full_name in already_selected
                
                col1, col2, col3, col4, col5 = st.columns([0.5, 3, 1, 1, 1])
                
                with col1:
                    selected = st.checkbox("", value=default_select, key=f"sel_{repo.full_name}",
                                         disabled=is_fork or is_archived)
                    if selected:
                        selected_repos.append(repo)
                
                with col2:
                    st.markdown(f"**{repo.name}**")
                    if repo.description:
                        st.caption(repo.description[:100] + ("..." if len(repo.description) > 100 else ""))
                
                with col3:
                    st.caption(f"⭐ {repo.stars}")
                
                with col4:
                    st.caption(f"💻 {repo.language or 'N/A'}")
                
                with col5:
                    if is_fork:
                        st.caption("🍴 Fork")
                    elif is_archived:
                        st.caption("📦 Archived")
            
            # Save selection
            if st.button("💾 Save Selection", type="primary", use_container_width=True):
                for repo in selected_repos:
                    db.execute(text("""
                        INSERT OR REPLACE INTO selected_repos 
                        (user_id, owner, repo_name, repo_full_name, description, stars, language, updated_at, analysis_status)
                        VALUES (:uid, :owner, :name, :full, :desc, :stars, :lang, :updated, 'pending')
                    """), {
                        "uid": user.user_id,
                        "owner": repo.full_name.split("/")[0],
                        "name": repo.name,
                        "full": repo.full_name,
                        "desc": repo.description,
                        "stars": repo.stars,
                        "lang": repo.language,
                        "updated": repo.updated_at.isoformat() if repo.updated_at else None,
                    })
                db.commit()
                st.success(f"Saved {len(selected_repos)} repositories for analysis!")
                st.rerun()


def show_analysis_tab(user):
    """Repo analysis trigger and progress."""
    with db_session() as db:
        from sqlalchemy import text
        
        selected = db.execute(
            text("SELECT * FROM selected_repos WHERE user_id = :uid AND analysis_status != 'done'"),
            {"uid": user.user_id}
        ).fetchall()
        
        if not selected:
            st.info("No repositories selected for analysis. Use the previous step to select repositories.")
            return
        
        st.markdown("#### 🔬 Repository Analysis")
        st.caption("Deep analysis of your code: authorship, evolution, tutorial-clone detection, quality, and skill mapping.")
        
        # Show pending repos
        for repo in selected:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{repo.repo_full_name}**")
                    status_class = f"status-{repo.analysis_status}"
                    st.markdown(f'<span class="status-badge {status_class}">{repo.analysis_status.upper()}</span>', 
                              unsafe_allow_html=True)
                with col2:
                    if repo.analysis_status == "pending":
                        if st.button("▶️ Analyze", key=f"analyze_{repo.id}", use_container_width=True):
                            run_analysis(user, repo.id)
                    elif repo.analysis_status == "running":
                        st.spinner("Analyzing...")
                with col3:
                    if repo.analysis_status == "done":
                        if st.button("📊 View", key=f"view_{repo.id}", use_container_width=True):
                            show_repo_analysis_result(repo.id)
        
        # Already analyzed
        done = db.execute(
            text("SELECT * FROM selected_repos WHERE user_id = :uid AND analysis_status = 'done'"),
            {"uid": user.user_id}
        ).fetchall()
        
        if done:
            st.markdown("---")
            st.markdown("#### ✅ Completed Analyses")
            for repo in done:
                if st.button(f"📊 {repo.repo_full_name}", key=f"view_done_{repo.id}", use_container_width=True):
                    show_repo_analysis_result(repo.id)


def run_analysis(user, repo_id):
    """Trigger repo analysis in background."""
    with db_session() as db:
        from sqlalchemy import text
        db.execute(
            text("UPDATE selected_repos SET analysis_status = 'running' WHERE id = :id"),
            {"id": repo_id}
        )
        db.commit()
    
    # Get repo details
    with db_session() as db:
        from sqlalchemy import text
        repo = db.execute(
            text("SELECT * FROM selected_repos WHERE id = :id"),
            {"id": repo_id}
        ).fetchone()
    
    # Run analysis (in real app, use background task)
    with st.spinner(f"Analyzing {repo.repo_full_name}... This may take 30-60 seconds."):
        try:
            # Download repo
            fetcher = GitHubFetcher(settings.GITHUB_TOKEN, settings.REPO_CACHE_DIR)
            repo_path = fetcher.download_repo(repo.owner, repo.repo_name)
            
            # Analyze
            analyzer = RepoAnalyzer()
            analysis = analyzer.analyze(repo_path)
            
            # Save results
            with db_session() as db:
                db.execute(text("""
                    INSERT INTO repo_analyses 
                    (selected_repo_id, user_id, analysis_json, authorship_score, evolution_score,
                     tutorial_clone_score, quality_score, is_tutorial_clone, clone_type, clone_confidence,
                     skills_json, analysis_duration_ms)
                    VALUES (:srid, :uid, :json, :auth, :evo, :clone_s, :qual, :is_clone, :ctype, :cconf, :skills, :dur)
                """), {
                    "srid": repo_id,
                    "uid": user.user_id,
                    "json": analysis.model_dump_json(),
                    "auth": analysis.authorship.score,
                    "evo": analysis.evolution.score,
                    "clone_s": analysis.tutorial_clone.score,
                    "qual": analysis.quality.score,
                    "is_clone": int(analysis.tutorial_clone.is_clone),
                    "ctype": analysis.tutorial_clone.clone_type,
                    "cconf": analysis.tutorial_clone.confidence,
                    "skills": json.dumps([s.model_dump() for s in analysis.skill_evidence]),
                    "dur": analysis.analysis_duration_ms,
                })
                db.execute(
                    text("UPDATE selected_repos SET analysis_status = 'done' WHERE id = :id"),
                    {"id": repo_id}
                )
                db.commit()
            
            st.success(f"✅ Analysis complete for {repo.repo_full_name}!")
            st.rerun()
            
        except Exception as e:
            with db_session() as db:
                db.execute(
                    text("UPDATE selected_repos SET analysis_status = 'failed' WHERE id = :id"),
                    {"id": repo_id}
                )
                db.commit()
            st.error(f"❌ Analysis failed: {str(e)}")


def show_repo_analysis_result(repo_id):
    """Display repo analysis results in a modal/expander."""
    with db_session() as db:
        from sqlalchemy import text
        result = db.execute(
            text("SELECT * FROM repo_analyses WHERE selected_repo_id = :id"),
            {"id": repo_id}
        ).fetchone()
    
    if not result:
        st.warning("Analysis results not found.")
        return
    
    analysis = json.loads(result.analysis_json)
    
    @st.dialog(f"Analysis: {analysis['name']}")
    def show_modal():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📝 Authorship")
            auth = analysis["authorship"]
            st.metric("Score", f"{auth['score']:.0%}")
            st.caption(f"Commits: {auth['candidate_commits']}/{auth['total_commits']} | Primary: {auth['primary_author']}")
            
            st.markdown("#### 📈 Evolution")
            evo = analysis["evolution"]
            st.metric("Score", f"{evo['score']:.0%}")
            st.caption(f"LOC trend: {evo['loc_growth_trend']} | Complexity: {evo['complexity_trend']}")
            
            st.markdown("#### ⭐ Quality")
            qual = analysis["quality"]
            st.metric("Score", f"{qual['score']:.0%}")
            st.caption(f"Tests: {'✅' if qual['has_tests'] else '❌'} | Docs: {'✅' if qual['has_docs'] else '❌'} | Lint: {qual['lint_score']:.0%}")
        
        with col2:
            st.markdown("#### 🛠️ Skill Evidence")
            for skill in analysis.get("skill_evidence", []):
                with st.expander(f"{skill['skill']} — {skill['confidence']:.0%}"):
                    st.caption(f"Type: {skill['evidence_type']}")
                    st.caption(f"Files: {', '.join(skill['files'][:5])}")
                    if skill['details']:
                        st.write(skill['details'])
    
    show_modal()


def show_proof_card_tab(user):
    """Generate and display Proof Card."""
    with db_session() as db:
        from sqlalchemy import text
        
        # Check if proof card exists
        pc_result = db.execute(
            text("SELECT * FROM proof_cards WHERE user_id = :uid ORDER BY version DESC LIMIT 1"),
            {"uid": user.user_id}
        ).fetchone()
        
        # Check if we have analyses
        analyses = db.execute(
            text("SELECT * FROM repo_analyses WHERE user_id = :uid"),
            {"uid": user.user_id}
        ).fetchall()
        
        # Check resume
        resume = db.execute(
            text("SELECT * FROM resumes WHERE user_id = :uid ORDER BY created_at DESC LIMIT 1"),
            {"uid": user.user_id}
        ).fetchone()
    
    if pc_result:
        st.markdown("#### 🎴 Existing Proof Card")
        card = json.loads(pc_result.card_json)
        render_proof_card(card)
        
        if st.button("🔄 Regenerate Proof Card", type="secondary", use_container_width=True):
            generate_proof_card(user)
    else:
        if not resume:
            st.warning("Resume not parsed yet. Return to the previous step first.")
        else:
            st.markdown("#### 🎴 Generate Proof Card")
            st.caption("Combines resume claims, repository evidence, and assessment scores into a unified skill profile.")
            
            has_github = len(analyses) > 0
            if not has_github:
                st.info("ℹ️ No GitHub repos analyzed. Proof Card will use alternative evidence path (assessment + resume + viva).")
            
            if st.button("✨ Generate Proof Card", type="primary", use_container_width=True, 
                        disabled=not resume):
                generate_proof_card(user)


def generate_proof_card(user):
    """Generate proof card from all evidence."""
    with st.spinner("Synthesizing evidence into Proof Card..."):
        with db_session() as db:
            from sqlalchemy import text
            
            # Get resume claims
            resume = db.execute(
                text("SELECT skills_json, projects_json FROM resumes WHERE user_id = :uid ORDER BY created_at DESC LIMIT 1"),
                {"uid": user.user_id}
            ).fetchone()
            resume_skills = [
                SkillClaim.model_validate(skill)
                for skill in (json.loads(resume.skills_json) if resume else [])
            ]
            
            # Get repo analyses
            analyses = db.execute(
                text("SELECT analysis_json FROM repo_analyses WHERE user_id = :uid"),
                {"uid": user.user_id}
            ).fetchall()
            repo_analyses = [
                RepoAnalysis.model_validate(json.loads(a.analysis_json))
                for a in analyses
            ]
            
            assessment_path = Path("data/assessments") / f"{user.user_id}.json"
            if assessment_path.exists():
                assessment_scores = json.loads(assessment_path.read_text(encoding="utf-8"))
            else:
                assessment_scores = {}
            
            # Synthesize
            synthesizer = EvidenceSynthesizer()
            if repo_analyses:
                proof_card = synthesizer.synthesize(resume_skills, repo_analyses, assessment_scores)
            else:
                proof_card = synthesizer.synthesize_no_github(resume_skills, assessment_scores)
            proof_card.candidate_id = user.user_id
            
            # Save
            db.execute(text("""
                INSERT INTO proof_cards (user_id, card_json, unified_skills_json, tutorial_clone_flags_json,
                                       overall_confidence, evidence_coverage, version)
                VALUES (:uid, :card, :skills, :clones, :conf, :cov, 
                       COALESCE((SELECT MAX(version) FROM proof_cards WHERE user_id = :uid), 0) + 1)
            """), {
                "uid": user.user_id,
                "card": proof_card.model_dump_json(),
                "skills": json.dumps([s.model_dump() for s in proof_card.unified_skills]),
                "clones": json.dumps([c.model_dump() for c in proof_card.tutorial_clone_flags]),
                "conf": proof_card.overall_confidence,
                "cov": proof_card.evidence_coverage,
            })
            db.commit()
        
        st.success("✅ Proof Card generated!")
        st.rerun()


def render_proof_card(card: dict):
    """Render proof card in UI."""
    st.markdown(f"### 🎴 Proof Card — {card['candidate_id']}")
    
    # Overall metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Confidence", f"{card['overall_confidence']:.0f}%")
    with col2:
        st.metric("Evidence Coverage", f"{card['evidence_coverage']:.0f}%")
    with col3:
        st.metric("Skills Assessed", len(card['unified_skills']))
    
    # Skills with evidence
    st.markdown("#### 🛠️ Skills & Evidence")
    for skill in card['unified_skills']:
        confidence = skill['final_confidence']
        color = "#22c55e" if confidence >= 70 else "#f59e0b" if confidence >= 40 else "#ef4444"
        
        with st.expander(f"{skill['skill']} — {confidence:.0f}% confidence"):
            st.markdown(f'<div class="confidence-bar"><div class="confidence-fill" style="width: {confidence}%; background: {color};"></div></div>', 
                      unsafe_allow_html=True)
            
            if skill.get('gap_notes'):
                st.info(f"💡 Gap: {skill['gap_notes']}")
            
            st.markdown("**Evidence:**")
            for ev in skill.get('evidence_bundle', []):
                source_icons = {"repo": "🐙", "assessment": "📝", "resume": "📄", "viva": "🎤"}
                icon = source_icons.get(ev['type'], "📌")
                st.markdown(f'<div class="evidence-item">{icon} <strong>{ev["source"]}</strong> ({ev["weight"]:.0%}): {ev["detail"]}</div>',
                          unsafe_allow_html=True)
    
    # Start Viva button
    st.markdown("---")
    if st.button("🎤 Start Viva Session", type="primary", use_container_width=True):
        st.session_state.page = "viva"
        st.rerun()