# pages/Viva_Session.py
"""Voice-first autonomous Viva interview."""
import streamlit as st
import json
import time
from datetime import datetime
from src.services.viva_engine import VivaEngine
from src.services.voice_pipeline import VoicePipeline
from src.services.model_client import RemoteModelError
from src.db.session import db_session
from src.models.schemas import *
from src.config.settings import settings


def show_viva():
    user = st.session_state.user
    
    st.markdown(f'<h1 class="main-header">🎤 Viva Session — {user.user_id}</h1>', unsafe_allow_html=True)
    
    # Check for proof card
    with db_session() as db:
        from sqlalchemy import text
        pc_result = db.execute(
            text("SELECT * FROM proof_cards WHERE user_id = :uid ORDER BY version DESC LIMIT 1"),
            {"uid": user.user_id}
        ).fetchone()
    
    if not pc_result:
        st.error("❌ No Proof Card found. Generate one first in the Dashboard.")
        if st.button("📊 Go to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    
    proof_card = ProofCard.model_validate(json.loads(pc_result.card_json))
    
    # Initialize viva session
    if "viva_session" not in st.session_state:
        st.session_state.viva_session = None
    if "viva_state" not in st.session_state:
        st.session_state.viva_state = "intro"  # intro, question, listening, evaluating, feedback, done
    if "current_question_idx" not in st.session_state:
        st.session_state.current_question_idx = 0
    if "audio_recording" not in st.session_state:
        st.session_state.audio_recording = False
    
    # Initialize engine
    if "viva_engine" not in st.session_state:
        st.session_state.viva_engine = VivaEngine()
        st.session_state.voice_pipeline = VoicePipeline()

    engine = st.session_state.viva_engine
    voice = st.session_state.voice_pipeline
    # Repair pipelines retained by Streamlit across source/config reloads.
    # CPU-only hosts must never reuse a pipeline that was initialized for CUDA.
    try:
        import torch
        hybrid = voice.stt.hybrid_client
        if not torch.cuda.is_available() and hybrid.local_device == "cuda":
            hybrid.local_device = "cpu"
            hybrid._local_model = None
    except (AttributeError, ImportError):
        pass
    
    # Session state machine
    if st.session_state.viva_state == "intro":
        show_intro(engine, proof_card, user, pc_result.id)
    elif st.session_state.viva_state == "question":
        show_question(engine, voice, proof_card)
    elif st.session_state.viva_state == "listening":
        show_listening(voice)
    elif st.session_state.viva_state == "evaluating":
        show_evaluating(engine, voice)
    elif st.session_state.viva_state == "done":
        show_completion()


def show_intro(engine, proof_card: ProofCard, user, proof_card_id: int):
    """Introduction and viva setup."""
    st.markdown("### 👋 Welcome to your AI Viva Session")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        **Candidate:** {user.user_id}  
        **Skills to assess:** {len(proof_card.unified_skills)}  
        **Mode:** Voice-only AI interview
        
        **What to expect:**
        - {settings.VIVA_MAX_QUESTIONS} questions tailored to YOUR code and resume
        - Mix of code walkthroughs, alternatives, debugging, and behavioral questions
        - AI will speak, listen, transcribe, evaluate, and continue automatically
        - Technical code context is shown read-only; explanations are spoken
        """)
    
    with col2:
        st.markdown("#### 🎙️ Browser microphone")
        st.caption("The browser will request microphone permission when the interview starts.")
    
    st.markdown("---")
    
    if engine.model.model_type == "mock":
        st.warning(
            "The AI interviewer is temporarily unavailable. "
            "Please contact the recruiter before starting the Viva."
        )
        return

    if st.button("🚀 Start Viva", type="primary", use_container_width=True):
        # Generate questions
        with st.spinner("Generating personalized questions from your Proof Card..."):
            try:
                questions = engine.generate_questions(proof_card)
            except RemoteModelError as exc:
                st.error(str(exc))
                st.info("Please try again after the AI service is online.")
                return
            if not questions:
                st.error(
                    "The AI interviewer could not prepare this session. "
                    "Please contact the recruiter and try again."
                )
                return
            
            # Create session in DB
            with db_session() as db:
                from sqlalchemy import text
                result = db.execute(text("""
                    INSERT INTO viva_sessions (user_id, proof_card_id, mode, question_count, status, session_json, started_at)
                    VALUES (:uid, :pcid, :mode, :qcount, 'in_progress', :json, :started)
                """), {
                    "uid": user.user_id,
                    "pcid": proof_card_id,
                    "mode": "hybrid",
                    "qcount": len(questions),
                    "json": json.dumps({
                        "questions": [q.model_dump() for q in questions],
                        "responses": []
                    }),
                    "started": datetime.utcnow().isoformat()
                })
                db.commit()
                session_id = result.lastrowid
            
            st.session_state.viva_session = {
                "id": session_id,
                "questions": questions,
                "responses": [],
                "started_at": datetime.utcnow()
            }
            st.session_state.viva_state = "question"
            st.session_state.current_question_idx = 0
            st.rerun()


def show_question(engine, voice, proof_card):
    """Display current question and get answer."""
    session = st.session_state.viva_session
    idx = st.session_state.current_question_idx
    questions = session["questions"]
    
    if idx >= len(questions):
        st.session_state.viva_state = "done"
        st.rerun()
        return
    
    question = questions[idx]
    
    # Progress
    progress = (idx + 1) / len(questions)
    st.progress(progress, text=f"Question {idx + 1} of {len(questions)}")
    
    # Question display
    type_icons = {
        "code_walkthrough": "🔍",
        "alternative_approach": "🔄",
        "debug": "🐛",
        "extend_feature": "➕",
        "behavioral": "💬",
        "knowledge_check": "📚"
    }
    icon = type_icons.get(question.type.value, "❓")
    
    st.markdown(f"### {icon} Question {idx + 1} — {question.skill}")
    st.markdown(f"**{question.prompt}**")
    show_ai_speaking(voice, question, idx)

    # Show context if available
    if question.context.code_snippet:
        with st.expander("📄 Code Context"):
            st.code(question.context.code_snippet, language="python")
    
    if question.context.file:
        st.caption(f"📁 {question.context.repo}/{question.context.file}")
    
    st.markdown("---")
    
    show_listening(voice)


def show_ai_speaking(voice, question, idx: int):
    """Speak each prompt once and show the AI's current voice state."""
    speech_key = f"spoken_question_{idx}"
    if speech_key not in st.session_state:
        st.session_state[speech_key] = True
        try:
            audio = voice.speak_question(question.prompt, question.type.value)
            st.audio(audio, autoplay=True)
        except Exception as exc:
            st.caption(f"AI voice unavailable; read the prompt below. ({exc})")
    st.markdown(
        '<div class="ai-speaking"><span class="ai-orb">🤖</span>'
        '<span><strong>AI interviewer</strong><br>'
        '<small>Prompt delivered — waiting for your response</small></span></div>',
        unsafe_allow_html=True,
    )


def show_listening(voice):
    """Show listening state with audio capture."""
    st.markdown("### 🔴 AI is listening...")
    st.markdown(
        '<div class="ai-listening"><span class="ai-orb">🎙️</span>'
        '<strong>Speak naturally. The AI will evaluate your answer automatically.</strong></div>',
        unsafe_allow_html=True,
    )
    
    # Visual indicator
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <div style="width: 80px; height: 80px; border-radius: 50%; background: #ef4444; 
                    animation: pulse 1.5s infinite; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 2rem;">🎙️</span>
        </div>
        <style>
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
                70% { box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }
                100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
            }
        </style>
    </div>
    """, unsafe_allow_html=True)
    
    idx = st.session_state.current_question_idx
    audio_file = st.audio_input(
        "🎙️ Speak your answer, then stop recording",
        key=f"viva_answer_{idx}",
        help="Click the microphone, speak, and stop recording when finished.",
    )
    if audio_file is not None:
        audio_bytes = audio_file.getvalue()
        st.session_state.audio_answer = audio_bytes
        st.session_state.audio_recording = False
        st.session_state.viva_state = "evaluating"
        st.rerun()


def show_evaluating(engine, voice):
    """Evaluate the answer."""
    session = st.session_state.viva_session
    idx = st.session_state.current_question_idx
    question = session["questions"][idx]
    
    # All candidate answers are transcribed voice responses.
    answer = None
    audio_answer = st.session_state.pop("audio_answer", None)
    if not answer and audio_answer:
        with st.spinner("Transcribing your answer..."):
            try:
                answer = voice.transcribe_bytes(audio_answer)
            except Exception as exc:
                st.error(f"Transcription failed: {exc}")
                st.session_state.viva_state = "question"
                st.session_state.audio_recording = False
                return
    if not answer:
        st.session_state.viva_state = "question"
        st.rerun()
        return
    
    with st.spinner("🤖 AI is evaluating your answer..."):
        evaluation = engine.evaluate_response(question, answer)
        # Streamlit reruns can retain model instances created by a previous
        # module load. Re-validate nested values against the current schema
        # classes before constructing the persisted response.
        question = VivaQuestion.model_validate(question.model_dump())
        evaluation = ResponseEvaluation.model_validate(evaluation.model_dump())
        
        # Store response
        response = VivaResponse(
            question=question,
            answer_text=answer,
            evaluation=evaluation,
            response_time_ms=5000,  # placeholder
            timestamp=datetime.utcnow()
        )
        session["responses"].append(response)
        
        # Update in DB
        with db_session() as db:
            from sqlalchemy import text
            db.execute(text("""
                INSERT INTO viva_responses (session_id, question_id, question_type, skill, question_prompt,
                                          answer_text, evaluation_json, score, confidence_delta, response_time_ms)
                VALUES (:sid, :qid, :qtype, :skill, :prompt, :answer, :eval, :score, :delta, :time)
            """), {
                "sid": session["id"],
                "qid": question.id,
                "qtype": question.type.value,
                "skill": question.skill,
                "prompt": question.prompt,
                "answer": answer,
                "eval": evaluation.model_dump_json(),
                "score": evaluation.score,
                "delta": evaluation.confidence_delta,
                "time": 5000,
            })
            
            # Update proof card confidence
            # (simplified - in real app, update proof_cards table)
            
            db.commit()
        
        st.session_state[f"evaluation_{idx}"] = evaluation
        st.session_state.last_viva_evaluation = evaluation
        st.session_state.current_question_idx += 1
        st.session_state.viva_state = "done" if st.session_state.current_question_idx >= len(session["questions"]) else "question"
        st.rerun()


def show_completion():
    """Viva completed - show summary and navigate to results."""
    session = st.session_state.viva_session
    
    st.balloons()
    st.markdown("### 🎉 Viva Session Complete!")
    
    # Summary stats
    responses = session["responses"]
    st.success(
        f"The AI interviewer completed {len(responses)} conversational turns. "
        "Your recruiter will receive the detailed assessment."
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📈 View Results", use_container_width=True, type="primary"):
            st.session_state.page = "results"
            st.rerun()
    with col2:
        if st.button("📊 Back to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    
    # Cleanup
    for key in ["viva_session", "viva_state", "current_question_idx", "audio_recording"]:
        if key in st.session_state:
            del st.session_state[key]
    for key in list(st.session_state.keys()):
        if key.startswith("answer_") or key.startswith("evaluation_"):
            del st.session_state[key]