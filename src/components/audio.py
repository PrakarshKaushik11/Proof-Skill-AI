# src/components/audio.py
"""
Streamlit Audio Components — Reusable audio recording and playback.
"""
import streamlit as st
import base64
import html
import json
from typing import Optional, Callable
from src.utils.audio import audio_to_base64, base64_to_audio


def AudioPlayerComponent(audio_bytes: bytes, format: str = "audio/mp3", key: str = None) -> None:
    """Render audio player in Streamlit."""
    if audio_bytes:
        st.audio(audio_bytes, format=format)
    else:
        st.caption("No audio available")


def AudioRecorderComponent(
    key: str = "audio_recorder",
    on_submit: Optional[Callable[[bytes], None]] = None,
    max_duration_seconds: int = 60
) -> Optional[bytes]:
    """
    Audio recorder component using Streamlit's built-in audio input.
    Returns recorded audio bytes when submitted.
    """
    st.markdown("#### 🎤 Record Your Answer")
    
    # Use Streamlit's native audio input (available in 1.25+)
    audio_file = st.audio_input(
        "Click to record",
        key=f"{key}_input"
    )
    
    if audio_file is not None:
        audio_bytes = audio_file.read()
        
        # Show playback
        st.audio(audio_bytes, format="audio/wav")
        
        # Submit button
        if st.button("✅ Submit Answer", key=f"{key}_submit", use_container_width=True, type="primary"):
            if on_submit:
                on_submit(audio_bytes)
            return audio_bytes
    
    return None


def AudioRecorderAdvanced(
    key: str = "audio_recorder_adv",
    on_submit: Optional[Callable[[bytes], None]] = None,
    show_waveform: bool = True
) -> Optional[bytes]:
    """
    Advanced audio recorder with visual feedback.
    Uses HTML5 MediaRecorder API via streamlit.components.v1.html
    """
    import streamlit.components.v1 as components
    
    recorder_html = f"""
    <div id="recorder-{key}">
        <div style="margin-bottom: 1rem;">
            <button id="start-btn-{key}" onclick="startRecording('{key}')" 
                    style="background: #ef4444; color: white; border: none; padding: 0.75rem 1.5rem; 
                           border-radius: 0.5rem; font-size: 1rem; cursor: pointer; margin-right: 0.5rem;">
                🎤 Start Recording
            </button>
            <button id="stop-btn-{key}" onclick="stopRecording('{key}')" disabled
                    style="background: #6b7280; color: white; border: none; padding: 0.75rem 1.5rem; 
                           border-radius: 0.5rem; font-size: 1rem; cursor: pointer;">
                ⏹️ Stop Recording
            </button>
        </div>
        <div id="status-{key}" style="margin: 1rem 0; font-weight: 500; color: #374151;">Ready to record</div>
        <audio id="playback-{key}" controls style="width: 100%; display: none; margin-top: 1rem;"></audio>
        <div id="waveform-{key}" style="height: 60px; background: #f3f4f6; border-radius: 0.5rem; display: {'block' if show_waveform else 'none'}; margin-top: 1rem;"></div>
        <button id="submit-btn-{key}" onclick="submitAudio('{key}')" disabled
                style="margin-top: 1rem; background: #2563eb; color: white; border: none; padding: 0.75rem 1.5rem; 
                       border-radius: 0.5rem; font-size: 1rem; cursor: pointer; width: 100%;">
            ✅ Submit Answer
        </button>
    </div>
    
    <script>
    let mediaRecorder;
    let audioChunks = [];
    let audioContext;
    let analyser;
    let dataArray;
    let animationId;
    
    async function startRecording(key) {{
        const status = document.getElementById('status-' + key);
        const startBtn = document.getElementById('start-btn-' + key);
        const stopBtn = document.getElementById('stop-btn-' + key);
        const submitBtn = document.getElementById('submit-btn-' + key);
        const playback = document.getElementById('playback-' + key);
        const waveform = document.getElementById('waveform-' + key);
        
        try {{
            const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
            
            // Setup audio context for visualization
            audioContext = new AudioContext();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            const source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);
            dataArray = new Uint8Array(analyser.frequencyBinCount);
            
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = e => {{
                audioChunks.push(e.data);
            }};
            
            mediaRecorder.onstop = () => {{
                const audioBlob = new Blob(audioChunks, {{ type: 'audio/wav' }});
                const audioUrl = URL.createObjectURL(audioBlob);
                playback.src = audioUrl;
                playback.style.display = 'block';
                startBtn.disabled = false;
                stopBtn.disabled = true;
                submitBtn.disabled = false;
                status.textContent = 'Recording complete. Click Submit to send.';
                
                // Stop visualization
                cancelAnimationFrame(animationId);
                audioContext.close();
            }};
            
            mediaRecorder.start();
            
            // Visualize waveform
            function drawWaveform() {{
                analyser.getByteFrequencyData(dataArray);
                const canvas = waveform;
                const ctx = canvas.getContext('2d');
                if (!ctx) return;
                
                canvas.width = canvas.offsetWidth;
                canvas.height = canvas.offsetHeight;
                ctx.fillStyle = '#f3f4f6';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                const barWidth = canvas.width / dataArray.length;
                for (let i = 0; i < dataArray.length; i++) {{
                    const barHeight = (dataArray[i] / 255) * canvas.height;
                    const x = i * barWidth;
                    const y = canvas.height - barHeight;
                    const gradient = ctx.createLinearGradient(0, canvas.height, 0, 0);
                    gradient.addColorStop(0, '#2563eb');
                    gradient.addColorStop(1, '#60a5fa');
                    ctx.fillStyle = gradient;
                    ctx.fillRect(x, y, barWidth - 1, barHeight);
                }}
                animationId = requestAnimationFrame(drawWaveform);
            }}
            drawWaveform();
            
            startBtn.disabled = true;
            stopBtn.disabled = false;
            submitBtn.disabled = true;
            status.textContent = '🔴 Recording... Speak now';
            playback.style.display = 'none';
            
        }} catch (err) {{
            status.textContent = 'Error: ' + err.message;
            console.error(err);
        }}
    }}
    
    function stopRecording(key) {{
        if (mediaRecorder && mediaRecorder.state === 'recording') {{
            mediaRecorder.stop();
        }}
    }}
    
    function submitAudio(key) {{
        const audioBlob = new Blob(audioChunks, {{ type: 'audio/wav' }});
        const reader = new FileReader();
        reader.onloadend = function() {{
            const base64data = reader.result.split(',')[1];
            // Send to Streamlit via session state
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                key: '{key}_audio',
                value: base64data
            }}, '*');
        }};
        reader.readAsDataURL(audioBlob);
    }}
    </script>
    """
    
    components.html(recorder_html, height=250)
    
    # Check for submitted audio
    audio_data = st.session_state.get(f"{key}_audio")
    if audio_data:
        audio_bytes = base64_to_audio(audio_data)
        if on_submit:
            on_submit(audio_bytes)
        # Clear after use
        del st.session_state[f"{key}_audio"]
        return audio_bytes
    
    return None


def render_question_audio(question_text: str, question_type: str = "technical") -> str:
    """Generate HTML for question with TTS playback button."""
    # This would integrate with ElevenLabs in real implementation
    # For now, return HTML with browser TTS fallback
    escaped = html.escape(question_text, quote=True)
    spoken_text = json.dumps(question_text)
    
    voice_map = {
        "technical": "Google US English",
        "behavioral": "Google US English", 
        "intro": "Google US English"
    }
    
    return f"""
    <div style="background: #f8fafc; border-radius: 0.75rem; padding: 1.5rem; margin: 1rem 0;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">🤖</span>
            <strong style="font-size: 1.1rem;">AI Interviewer</strong>
            <span style="color: #6b7280; font-size: 0.85rem;">({question_type})</span>
        </div>
        <p style="font-size: 1.05rem; line-height: 1.6; color: #1f2937; margin-bottom: 1rem;">{escaped}</p>
        <button onclick="speakText({spoken_text})" 
                style="background: #2563eb; color: white; border: none; padding: 0.5rem 1rem; 
                       border-radius: 0.375rem; cursor: pointer; font-size: 0.9rem;">
            🔊 Play Question
        </button>
    </div>
    <script>
    function speakText(text) {{
        if ('speechSynthesis' in window) {{
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.rate = 0.95;
            utterance.volume = 1.0;
            speechSynthesis.speak(utterance);
        }}
    }}
    </script>
    """


def render_viva_status(state: str, current: int, total: int) -> str:
    """Render viva session status indicator."""
    icons = {
        "intro": "👋",
        "question": "❓",
        "listening": "🔴",
        "evaluating": "🤔",
        "feedback": "📊",
        "done": "🎉"
    }
    
    colors = {
        "intro": "#2563eb",
        "question": "#f59e0b",
        "listening": "#ef4444",
        "evaluating": "#8b5cf6",
        "feedback": "#22c55e",
        "done": "#22c55e"
    }
    
    color = colors.get(state, "#6b7280")
    icon = icons.get(state, "❓")
    
    return f"""
    <div style="background: {color}15; border: 2px solid {color}; border-radius: 0.75rem; padding: 1rem; margin: 1rem 0;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 2rem;">{icon}</span>
            <div>
                <div style="font-size: 1.25rem; font-weight: 600; color: {color};">{state.title()}</div>
                <div style="color: #6b7280;">Question {current} of {total}</div>
            </div>
            <div style="margin-left: auto; background: {color}; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600;">
                {int(current/total*100)}% Complete
            </div>
        </div>
    </div>
    """