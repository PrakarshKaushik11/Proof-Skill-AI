"""Streamlit entrypoint for the ProofSkill AI candidate and recruiter journeys."""

from __future__ import annotations

from typing import Any

import streamlit as st

from proofskill.ui import config, state
from proofskill.ui.services import get_services
from proofskill.ui.services.contracts import (
    AssessmentTask,
    CandidateSummary,
    ComparisonResult,
    ConsentRecord,
    DiscoveryResult,
    ExtractedProfile,
    JobRequirements,
    ProofCard,
    Question,
    ServiceResult,
)
from proofskill.ui.services.fixtures import DEMO_RESUME_FILENAME, DEMO_RESUME_TEXT

st.set_page_config(page_title="ProofSkill AI", page_icon="✅", layout="wide")


def _services() -> Any:
    services = state.get("psa_services")
    if services is None:
        services = get_services()
        state.set("psa_services", services)
    return services


def _result_error(result: ServiceResult) -> None:
    if result.error:
        state.set_notice("error", result.error.message)
    else:
        state.set_notice("error", "The service did not return a usable result.")


def _notice() -> None:
    notice = state.current_notice()
    if notice:
        getattr(st, notice["kind"])(notice["text"])


def _provider_label(result: ServiceResult | None = None) -> str:
    mode = result.provider_mode if result else _services().mode
    return "Demo / synthetic services" if mode == "demo" else f"{mode.title()} services"


def _status(status: str) -> str:
    return {
        "candidate_claim": "Claimed from resume",
        "assessed": "Assessed",
        "verified_evidence": "Verified evidence",
        "not_assessed": "Not assessed",
        "unavailable": "Unavailable",
    }.get(status, status.replace("_", " ").title())


def _advance(stage_name: str) -> None:
    state.clear_notice()
    state.set_stage(stage_name)


def _render_header() -> None:
    st.title("ProofSkill AI")
    st.caption("Proof of skill, not a template resume.")
    st.info(
        "Decision support for human reviewers. Resume statements are claims until "
        "supported by assessment evidence."
    )
    if _services().mode == "demo":
        st.warning(
            "Demo mode is active. Results are synthetic and deterministic; no live "
            "model or GitHub request is being used."
        )


def _render_sidebar() -> None:
    with st.sidebar:
        st.header("Assessment")
        stages = (
            ("home", "Home"),
            ("resume", "Resume"),
            ("profile", "Profile"),
            ("job", "Target job"),
            ("route", "Evidence route"),
            ("interview", "Interview"),
            ("tasks", "Project tasks"),
            ("proof_card", "Proof Card"),
        )
        current = state.stage()
        for key, label in stages:
            disabled = key not in {"home", current} and not _stage_available(key)
            if st.button(label, key=f"nav_{key}", disabled=disabled, use_container_width=True):
                _advance(key)
                st.rerun()
        st.divider()
        if st.button("Recruiter review", use_container_width=True):
            _advance("recruiter")
            st.rerun()
        if st.button("Restart assessment", use_container_width=True):
            state.set("psa_restart_confirm", True)
        if state.get("psa_restart_confirm"):
            st.warning("This clears the current assessment progress.")
            if st.button("Confirm restart", type="primary"):
                state.reset_assessment()
                st.rerun()


def _stage_available(stage_name: str) -> bool:
    requirements = {
        "profile": state.get("psa_resume_text") is not None,
        "job": state.get("psa_profile") is not None,
        "route": state.get("psa_profile") is not None and state.get("psa_job") is not None,
        "interview": state.get("psa_questions"),
        "tasks": state.get("psa_questions") or state.get("psa_tasks"),
        "proof_card": state.get("psa_interview_done") or state.get("psa_tasks_done"),
    }
    return requirements.get(stage_name, True)


def _render_home() -> None:
    st.subheader("Start an evidence-based assessment")
    st.write(
        "Upload a resume, review the extracted claims, provide a target role, and "
        "complete a short assessment. GitHub analysis is optional and always consent-based."
    )
    cols = st.columns(3)
    cols[0].metric("1", "Resume claims")
    cols[1].metric("2", "Structured assessment")
    cols[2].metric("3", "Explainable Proof Card")
    st.subheader("How evidence is handled")
    st.markdown(
        "- Resume skills remain **claimed**, not verified.\n"
        "- Missing repository evidence is **not assessed**, not zero.\n"
        "- Recruiter comparisons use the same job criteria and keep a human reviewer in control."
    )
    if st.button("Begin candidate assessment", type="primary"):
        _advance("resume")
        st.rerun()


def _render_resume() -> None:
    st.header("1. Resume")
    st.write("Upload a PDF, DOCX, or TXT resume. It is processed locally in demo mode.")
    st.caption(f"Maximum size: {config.max_resume_size_mb():g} MB")
    uploaded = st.file_uploader(
        "Resume file",
        type=list(config.allowed_resume_extensions()),
        key="resume_upload",
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Use synthetic demo resume", type="secondary"):
            state.set("psa_resume_filename", DEMO_RESUME_FILENAME)
            state.set("psa_resume_text", DEMO_RESUME_TEXT)
            _advance("profile")
            st.rerun()
    with col2:
        if st.button("Extract uploaded resume", type="primary", disabled=uploaded is None):
            assert uploaded is not None
            result = _services().extract_resume_text(
                filename=uploaded.name,
                content_type=uploaded.type or "",
                data=uploaded.getvalue(),
                max_size_mb=config.max_resume_size_mb(),
            )
            if result.ok:
                state.set("psa_resume_filename", uploaded.name)
                state.set("psa_resume_text", result.data.text)
                state.set_notice("success", f"Read {uploaded.name}. Review the extracted claims next.")
                _advance("profile")
                st.rerun()
            else:
                _result_error(result)
    _notice()


def _render_profile() -> None:
    st.header("2. Review extracted claims")
    if state.get("psa_profile") is None:
        result = _services().extract_candidate_evidence(state.get("psa_resume_text", ""))
        if not result.ok:
            _result_error(result)
            _notice()
            return
        state.set("psa_profile", result.data)
        state.set("psa_github_links", result.data.github_links)
    profile: ExtractedProfile = state.get("psa_profile")
    st.caption(f"Source: {state.get('psa_resume_filename')} · {_provider_label()}")
    if profile.warnings:
        for warning in profile.warnings:
            st.warning(warning)
    if profile.limitations:
        for limitation in profile.limitations:
            st.caption(limitation)
    cols = st.columns(3)
    with cols[0]:
        st.subheader("Skills")
        for skill in profile.skills:
            with st.container(border=True):
                st.write(skill.skill_name)
                st.caption(_status(skill.status))
                for evidence in skill.evidence:
                    if evidence.excerpt:
                        st.caption(f"Resume evidence: {evidence.excerpt}")
    with cols[1]:
        st.subheader("Projects")
        if not profile.projects:
            st.info("No projects were recognised.")
        for project in profile.projects:
            st.write(f"**{project.name}**")
            st.caption(project.description)
            if project.technologies:
                st.caption("Technologies: " + ", ".join(project.technologies))
    with cols[2]:
        st.subheader("GitHub links")
        if not profile.github_links:
            st.info("No GitHub link found. You can use the alternative assessment.")
        for link in profile.github_links:
            st.write(link.url)
            st.caption("Candidate-provided link; not fetched yet.")
    if st.button("Continue to target job", type="primary"):
        _advance("job")
        st.rerun()
    _notice()


def _render_job() -> None:
    st.header("3. Target job")
    title = st.text_input("Job title", value=state.get("psa_job_title", ""))
    description = st.text_area(
        "Job description",
        value=state.get("psa_job_desc", ""),
        height=180,
        placeholder="Example: Python, SQL, REST APIs and testing are required.",
    )
    if st.button("Analyse job requirements", type="primary"):
        result = _services().parse_job_requirements(title, description)
        if result.ok:
            state.set("psa_job_title", title)
            state.set("psa_job_desc", description)
            state.set("psa_job", result.data)
            _advance("route")
            st.rerun()
        else:
            _result_error(result)
    _notice()


def _render_route() -> None:
    st.header("4. Choose evidence route")
    job: JobRequirements = state.get("psa_job")
    profile: ExtractedProfile = state.get("psa_profile")
    if job.warnings:
        for warning in job.warnings:
            st.warning(warning)
    st.write("Choose whether to use consented repository evidence or an equivalent assessment.")
    if profile.github_links:
        st.subheader("Repository discovery")
        st.write("The links below came from your resume. Nothing is fetched without consent.")
        selected_link = st.selectbox(
            "GitHub link",
            profile.github_links,
            format_func=lambda link: link.url,
        )
        consent = st.checkbox(
            "I consent to listing public repositories for this selected GitHub link.",
            key="discovery_consent_checkbox",
        )
        if st.button("Discover repositories", disabled=not consent):
            result = _services().record_repository_consent(
                list(profile.github_links), True, "repository_discovery"
            )
            if result.ok:
                discovery_result = _services().discover_repositories(selected_link, result.data)
                if discovery_result.ok:
                    state.set("psa_discovery_consent", result.data)
                    state.set("psa_discovery", discovery_result.data)
                    state.set("psa_discovery_failed", False)
                else:
                    state.set("psa_discovery_failed", True)
                    _result_error(discovery_result)
            else:
                _result_error(result)
        _render_discovery()
    else:
        st.info("No repository link is available. The alternative route provides equivalent assessment scope.")
    st.divider()
    if st.button("Use alternative assessment", type="secondary"):
        result = _services().create_alternative_assessment(profile, job)
        if result.ok:
            state.set("psa_route", "alternative")
            state.set("psa_tasks", result.data)
            state.set("psa_task_index", 0)
            _advance("tasks")
            st.rerun()
        else:
            _result_error(result)
    _notice()


def _render_discovery() -> None:
    discovery: DiscoveryResult | None = state.get("psa_discovery")
    consent: ConsentRecord | None = state.get("psa_discovery_consent")
    if discovery is None:
        return
    st.subheader(f"Repositories for {discovery.account}")
    for limitation in discovery.limitations:
        st.caption(limitation)
    if not discovery.repositories:
        st.info("No accessible repositories were found. Use the alternative assessment.")
        return
    options = list(discovery.repositories)
    selected = st.multiselect(
        "Select repositories to analyse",
        options,
        format_func=lambda repo: f"{repo.full_name} ({repo.language or 'unknown language'})",
    )
    if st.button("Confirm selected repository scope", disabled=not selected):
        analysis_consent = _services().record_repository_consent(
            [state.get("psa_profile").github_links[0]], True, "repository_analysis"
        )
        if analysis_consent.ok:
            scope_result = _services().confirm_repository_scope(analysis_consent.data, selected)
            if scope_result.ok:
                state.set("psa_analysis_consent", analysis_consent.data)
                state.set("psa_scope", scope_result.data)
                state.set("psa_route", "repository")
                tasks_result = _services().generate_project_tasks(scope_result.data, state.get("psa_job"))
                if tasks_result.ok:
                    state.set("psa_tasks", tasks_result.data)
                    state.set("psa_task_index", 0)
                    _advance("interview")
                    st.rerun()
                else:
                    _result_error(tasks_result)
            else:
                _result_error(scope_result)
        else:
            _result_error(analysis_consent)
    if consent and not consent.granted:
        st.info("Discovery consent was declined; no repositories were listed.")


def _render_interview() -> None:
    st.header("5. Technical interview")
    profile: ExtractedProfile = state.get("psa_profile")
    job: JobRequirements = state.get("psa_job")
    questions: tuple[Question, ...] = state.get("psa_questions", ())
    if not questions:
        result = _services().generate_questions(
            profile, job, config.default_interview_questions(), state.get("psa_route") or "alternative"
        )
        if not result.ok:
            _result_error(result)
            _notice()
            return
        questions = result.data
        state.set("psa_questions", questions)
    index = state.get("psa_question_index", 0)
    if index >= len(questions):
        state.set("psa_interview_done", True)
        st.success("Interview complete.")
        if st.button("Continue to project tasks"):
            _advance("tasks")
            st.rerun()
        return
    question: Question = questions[index]
    st.progress((index + 1) / len(questions), text=f"Question {index + 1} of {len(questions)}")
    st.caption(f"{question.skill_name} · {question.difficulty} · {_provider_label()}")
    if question.context:
        st.info(question.context)
    st.subheader(question.question_text)
    answer = st.text_area("Your answer", key=f"answer_{question.id}", height=180)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit answer", type="primary", disabled=not answer.strip()):
            result = _services().evaluate_answer(question, answer)
            if result.ok:
                evaluations = dict(state.get("psa_evaluations", {}))
                evaluations[question.id] = result.data
                state.set("psa_evaluations", evaluations)
                state.set("psa_question_index", index + 1)
                st.rerun()
            else:
                _result_error(result)
    with col2:
        if st.button("Skip question", disabled=not question.allow_skip):
            state.set("psa_question_index", index + 1)
            st.rerun()
    _notice()


def _render_tasks() -> None:
    st.header("6. Project or alternative tasks")
    tasks: tuple[AssessmentTask, ...] = state.get("psa_tasks", ())
    if not tasks:
        state.set("psa_tasks_done", True)
        _render_proof_card()
        return
    index = state.get("psa_task_index", 0)
    if index >= len(tasks):
        state.set("psa_tasks_done", True)
        st.success("Task assessment complete.")
        if st.button("Generate Proof Card", type="primary"):
            _advance("proof_card")
            st.rerun()
        return
    task = tasks[index]
    st.progress((index + 1) / len(tasks), text=f"Task {index + 1} of {len(tasks)}")
    st.caption(f"{task.skill_name} · {task.task_type}")
    if task.context:
        st.info(task.context)
    st.subheader(task.prompt)
    if task.file_refs:
        st.caption("Bounded evidence: " + ", ".join(task.file_refs))
    if task.code_excerpt:
        st.code(task.code_excerpt)
    response = st.text_area("Response", key=f"task_response_{task.id}", height=180)
    if st.button("Submit task response", type="primary", disabled=not response.strip()):
        result = _services().evaluate_answer(
            Question(
                id=task.id,
                skill_name=task.skill_name,
                question_text=task.prompt,
                question_type=task.task_type,
                expected_concepts=task.expected_concepts,
            ),
            response,
        )
        if result.ok:
            evaluations = dict(state.get("psa_task_evaluations", {}))
            evaluations[task.id] = result.data
            state.set("psa_task_evaluations", evaluations)
            state.set("psa_task_index", index + 1)
            st.rerun()
        else:
            _result_error(result)
    st.caption(
        "Responses are reviewed as assessment artifacts. Candidate code is never "
        "executed, committed, or pushed to GitHub."
    )
    _notice()


def _render_proof_card() -> None:
    st.header("7. Candidate Proof Card")
    profile: ExtractedProfile = state.get("psa_profile")
    job: JobRequirements = state.get("psa_job")
    card: ProofCard | None = state.get("psa_proof_card")
    if card is None:
        result = _services().generate_proof_card(
            job=job,
            profile=profile,
            route=state.get("psa_route") or "alternative",
            answer_evaluations=list(state.get("psa_evaluations", {}).values()),
            task_evaluations=list(state.get("psa_task_evaluations", {}).values()),
            scope=state.get("psa_scope"),
            candidate_id=state.get("psa_candidate_id"),
            candidate_reference=state.get("psa_candidate_reference"),
        )
        if not result.ok:
            _result_error(result)
            _notice()
            return
        card = result.data
        state.set("psa_proof_card", card)
    _render_card(card)


def _render_card(card: ProofCard) -> None:
    st.caption(f"{card.candidate_reference} · {card.job_title} · {card.provider_mode} · rubric {card.rubric_version}")
    cols = st.columns(4)
    cols[0].metric("Performance", f"{card.performance_score:.1f}/100" if card.performance_score is not None else "Not assessed")
    cols[1].metric("Evidence coverage", f"{card.evidence_coverage:.1f}%")
    cols[2].metric("Score status", card.score_status.title())
    cols[3].metric("Unassessed skills", str(len(card.unassessed_skills)))
    st.subheader("Skill results")
    for result in card.skill_results:
        with st.container(border=True):
            score = f"{result.performance_score:.1f}/100" if result.performance_score is not None else "Not assessed"
            st.write(f"**{result.skill_name}** · {score} · {_status(result.status)}")
            st.caption(
                f"Coverage {result.evidence_coverage:.0f}% · confidence {result.evidence_confidence}"
            )
            if result.explanation:
                st.write(result.explanation)
    left, right = st.columns(2)
    with left:
        st.subheader("Strengths")
        st.write(", ".join(card.strengths) if card.strengths else "No assessed strengths yet.")
        st.subheader("Claims not assessed")
        st.write(", ".join(card.claims_not_assessed) if card.claims_not_assessed else "None.")
    with right:
        st.subheader("Limitations")
        for item in card.limitations:
            st.write(f"- {item}")
        st.subheader("Recommended follow-ups")
        for item in card.recommended_follow_ups:
            st.write(f"- {item}")


def _render_recruiter() -> None:
    st.header("Recruiter review")
    st.info("Human review required. This screen is decision support, not an automatic hiring decision.")
    jobs_result = _services().list_jobs()
    if not jobs_result.ok:
        _result_error(jobs_result)
        _notice()
        return
    jobs = jobs_result.data
    job = st.selectbox("Job", jobs, format_func=lambda item: item.title)
    candidates_result = _services().list_candidates(job.job_id)
    if not candidates_result.ok:
        _result_error(candidates_result)
        _notice()
        return
    candidates: tuple[CandidateSummary, ...] = candidates_result.data
    selected = st.multiselect(
        "Candidates to compare",
        candidates,
        format_func=lambda item: item.reference_label,
    )
    if selected:
        for candidate in selected:
            if candidate.proof_card:
                with st.expander(candidate.reference_label):
                    _render_card(candidate.proof_card)
    if st.button("Compare selected candidates", type="primary", disabled=len(selected) < 2):
        result = _services().compare_candidates(job.job_id, [item.candidate_id for item in selected])
        if result.ok:
            state.set("psa_comparison", result.data)
        else:
            _result_error(result)
    comparison: ComparisonResult | None = state.get("psa_comparison")
    if comparison and comparison.job_id == job.job_id:
        st.subheader("Comparable evidence summary")
        for warning in comparison.warnings:
            st.warning(warning)
        for row in comparison.rows:
            with st.container(border=True):
                st.write(f"**{row.reference_label}** · coverage {row.evidence_coverage:.0f}%")
                for criterion, score in row.scores.items():
                    st.write(f"{criterion}: {score:.1f}/100" if score is not None else f"{criterion}: Not assessed")
                st.caption(row.explanation)
        st.caption("Excluded ranking factors: protected attributes, college prestige, location, popularity, and repository stars.")
    _notice()


def main() -> None:
    state.init()
    _render_header()
    _render_sidebar()
    stage = state.stage()
    if stage == "home":
        _render_home()
    elif stage == "resume":
        _render_resume()
    elif stage == "profile":
        _render_profile()
    elif stage == "job":
        _render_job()
    elif stage == "route":
        _render_route()
    elif stage == "interview":
        _render_interview()
    elif stage == "tasks":
        _render_tasks()
    elif stage == "proof_card":
        _render_proof_card()
    elif stage == "recruiter":
        _render_recruiter()
    else:
        state.set_stage("home")
        _render_home()


if __name__ == "__main__":
    main()
