# src/services/voice_pipeline.py
"""
Voice Pipeline — TTS + STT integration.
Supports: ElevenLabs TTS / Gradio TTS / edge-tts / pyttsx3 + Whisper API (Colab) / Local Whisper
"""
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Optional, AsyncGenerator
import httpx
import whisper
from src.config.settings import settings
from src.services.whisper_api_client import HybridWhisperClient, WhisperAPIClient
from src.services.gradio_tts_client import GradioTTSClient, HybridTTSClient, create_gradio_tts

logger = logging.getLogger(__name__)


class ElevenLabsClient:
    """ElevenLabs Text-to-Speech client."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
    
    async def text_to_speech(
        self,
        text: str,
        voice_id: str = None,
        model_id: str = "eleven_multilingual_v2",
        voice_settings: dict = None
    ) -> bytes:
        """Convert text to speech audio bytes."""
        voice_id = voice_id or settings.ELEVENLABS_VOICE_ID
        voice_settings = voice_settings or {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings,
            "output_format": "mp3_44100_128"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
            
            return response.content
    
    async def text_to_speech_stream(
        self,
        text: str,
        voice_id: str = None
    ) -> AsyncGenerator[bytes, None]:
        """Stream TTS audio (for real-time playback)."""
        # ElevenLabs supports streaming via websocket or chunked response
        # For simplicity, we return full audio
        audio = await self.text_to_speech(text, voice_id)
        yield audio
    
    def get_voices(self) -> list:
        """Get available voices."""
        url = f"{self.base_url}/voices"
        response = httpx.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("voices", [])
        return []


class WhisperClient:
    """Whisper Speech-to-Text client — Hybrid (API first, local fallback)."""
    
    def __init__(
        self,
        api_url: str = None,
        model_name: str = "large-v3",
        device: str = "cuda",
        compute_type: str = "float16",
        api_timeout: int = 120
    ):
        # Use API URL from settings or default to your Colab ngrok
        self.api_url = api_url or getattr(settings, 'WHISPER_API_URL', None) or \
                       "https://unhelpful-corny-jumbo.ngrok-free.dev/transcribe"
        
        self.hybrid_client = HybridWhisperClient(
            api_url=self.api_url,
            local_model=model_name,
            local_device=device,
            api_timeout=api_timeout
        )
        self._model_loaded = False
    
    def transcribe(self, audio_path: Path, language: str = "en") -> dict:
        """Transcribe audio file — tries API first, falls back to local."""
        return self.hybrid_client.transcribe_file(audio_path, language)
    
    def transcribe_bytes(self, audio_bytes: bytes, language: str = "en") -> dict:
        """Transcribe from bytes."""
        return self.hybrid_client.transcribe_bytes(audio_bytes, language)
    
    def force_local_mode(self):
        """Force local Whisper (e.g., API quota exceeded)."""
        self.hybrid_client.force_local()
    
    def force_api_mode(self):
        """Reset to try API again."""
        self.hybrid_client.force_api()
    
    @property
    def model(self):
        """Backward compatibility — returns local model if loaded."""
        return self.hybrid_client.local_model
    
    def is_using_local(self) -> bool:
        """Check if currently using local fallback."""
        return self.hybrid_client._use_local


class VoicePipeline:
    """Complete voice pipeline: TTS + STT."""
    
    def __init__(self, tts_provider: str = "auto"):
        """
        Initialize voice pipeline.
        
        Args:
            tts_provider: "elevenlabs", "gradio", "edge", "system", or "auto"
        """
        self.tts_provider = tts_provider
        self.tts = self._init_tts(tts_provider)
        self.stt = WhisperClient(
            api_url=getattr(settings, 'WHISPER_API_URL', None),
            model_name=settings.WHISPER_MODEL,
            device=settings.WHISPER_DEVICE,
            compute_type=settings.WHISPER_COMPUTE_TYPE,
            api_timeout=getattr(settings, 'WHISPER_API_TIMEOUT', 120)
        )
        
        # Voice configs for different contexts
        self.voice_configs = {
            "intro": {"voice_id": "21m00Tcm4TlvDq8ikWAM", "style": 0.3},  # Rachel - warm
            "technical": {"voice_id": "ErXwobaYiN019PkySvjV", "style": 0.0},  # Antoni - precise
            "behavioral": {"voice_id": "AZnzlk1XvdvUeBnXmlld", "style": 0.2},  # Domi - conversational
            "feedback": {"voice_id": "VR6AewLTigWG4xSOukaG", "style": 0.3},  # Brian - encouraging
        }
    
    def _init_tts(self, provider: str):
        """Initialize TTS client based on provider."""
        if provider == "elevenlabs":
            return ElevenLabsClient(settings.ELEVENLABS_API_KEY)
        elif provider == "gradio":
            # Use Gradio TTS with edge-tts fallback
            return create_gradio_tts(
                space_url=getattr(settings, 'GRADIO_TTS_URL', "https://bd512e52f4484d878a.gradio.live/"),
                api_name=getattr(settings, 'GRADIO_TTS_API_NAME', "/predict"),
                fallback="edge"
            )
        elif provider == "edge":
            try:
                from src.services.free_tts import EdgeTTSClient
                return EdgeTTSClient()
            except ImportError:
                logger.warning("edge-tts not installed, falling back to system")
                return self._init_tts("system")
        elif provider == "system":
            try:
                from src.services.free_tts import SystemTTSClient
                return SystemTTSClient()
            except ImportError:
                logger.warning("pyttsx3 not installed")
                return None
        elif provider == "auto":
            # Try in order: ElevenLabs (if key), Gradio (if URL), edge-tts, system
            if getattr(settings, 'ELEVENLABS_API_KEY', None):
                return ElevenLabsClient(settings.ELEVENLABS_API_KEY)
            elif getattr(settings, 'GRADIO_TTS_URL', None):
                return create_gradio_tts(
                    space_url=settings.GRADIO_TTS_URL,
                    api_name=getattr(settings, 'GRADIO_TTS_API_NAME', "/predict"),
                    fallback="edge"
                )
            else:
                try:
                    from src.services.free_tts import EdgeTTSClient
                    return EdgeTTSClient()
                except ImportError:
                    try:
                        from src.services.free_tts import SystemTTSClient
                        return SystemTTSClient()
                    except ImportError:
                        return None
        else:
            raise ValueError(f"Unknown TTS provider: {provider}")
    
    def speak_question(self, question: str, question_type: str = "technical") -> bytes:
        """Convert question to speech (sync wrapper)."""
        return self._synthesize(question, question_type)
    
    def speak_intro(self, text: str) -> bytes:
        """Speak introduction (sync wrapper)."""
        return self._synthesize(text, "intro")
    
    def _synthesize(self, text: str, voice_type: str = "technical") -> bytes:
        """Internal synthesis method - handles both sync and async TTS clients."""
        if self.tts is None:
            raise RuntimeError("No TTS client available")
        
        # Gradio/Hybrid TTS clients have synthesize() method
        if hasattr(self.tts, 'synthesize'):
            return self.tts.synthesize(text)
        
        # ElevenLabs has async text_to_speech
        elif hasattr(self.tts, 'text_to_speech'):
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.tts.text_to_speech(text))
        
        # Free TTS clients (EdgeTTSClient, SystemTTSClient)
        elif hasattr(self.tts, 'text_to_speech_sync'):
            return self.tts.text_to_speech_sync(text)
        elif hasattr(self.tts, 'text_to_speech'):
            # Try sync version if exists
            if asyncio.iscoroutinefunction(self.tts.text_to_speech):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                return loop.run_until_complete(self.tts.text_to_speech(text))
            else:
                return self.tts.text_to_speech(text)
        
        raise RuntimeError(f"TTS client {type(self.tts)} has no compatible synthesize method")
    
    def transcribe_answer(self, audio_path: Path) -> str:
        """Transcribe candidate's answer."""
        result = self.stt.transcribe(audio_path)
        return result["text"].strip()
    
    def transcribe_bytes(self, audio_bytes: bytes) -> str:
        """Transcribe from audio bytes."""
        result = self.stt.transcribe_bytes(audio_bytes)
        return result["text"].strip()
    
    def is_available(self) -> bool:
        """Check if voice pipeline is ready."""
        return self.tts is not None and self.stt is not None


# Fallback TTS using browser SpeechSynthesis (for when ElevenLabs fails)
class BrowserTTS:
    """Fallback TTS using browser's built-in speech synthesis."""
    
    @staticmethod
    def get_speech_script(text: str, lang: str = "en-US", rate: float = 1.0) -> str:
        """Generate JavaScript to speak text in browser."""
        escaped = text.replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
        return f"""
        <script>
        if ('speechSynthesis' in window) {{
            const utterance = new SpeechSynthesisUtterance("{escaped}");
            utterance.lang = "{lang}";
            utterance.rate = {rate};
            utterance.volume = 1.0;
            speechSynthesis.speak(utterance);
        }} else {{
            alert("Speech synthesis not supported in this browser.");
        }}
        </script>
        """


# Audio recording helper (for Streamlit)
def create_audio_recorder_html() -> str:
    """Create HTML/JS for audio recording in Streamlit."""
    return """
    <div id="audio-recorder">
        <button id="record-btn" onclick="toggleRecording()">🎤 Start Recording</button>
        <button id="stop-btn" onclick="stopRecording()" disabled>⏹️ Stop</button>
        <audio id="audio-playback" controls style="display:none; margin-top:10px;"></audio>
        <p id="status"></p>
    </div>
    <script>
    let mediaRecorder;
    let audioChunks = [];
    
    async function toggleRecording() {
        const btn = document.getElementById('record-btn');
        const stopBtn = document.getElementById('stop-btn');
        const status = document.getElementById('status');
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = document.getElementById('audio-playback');
                audio.src = audioUrl;
                audio.style.display = 'block';
                // Send to Streamlit via custom event or callback
                window.parent.postMessage({type: 'audio_recorded', blob: audioBlob}, '*');
            };
            
            mediaRecorder.start();
            btn.disabled = true;
            stopBtn.disabled = false;
            status.textContent = 'Recording...';
        } catch (err) {
            status.textContent = 'Microphone access denied: ' + err.message;
        }
    }
    
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            document.getElementById('record-btn').disabled = false;
            document.getElementById('stop-btn').disabled = true;
            document.getElementById('status').textContent = 'Recording stopped. Processing...';
        }
    }
    </script>
    """