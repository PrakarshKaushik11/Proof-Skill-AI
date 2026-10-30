# src/services/whisper_api_client.py
"""
Whisper API Client — Calls your Colab/ngrok Whisper endpoint.
Falls back to local Whisper if API unavailable.
"""
import requests
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
import time

logger = logging.getLogger(__name__)


class WhisperAPIClient:
    """Client for remote Whisper transcription API (your Colab ngrok endpoint)."""
    
    def __init__(
        self,
        api_url: str = "https://unhelpful-corny-jumbo.ngrok-free.dev/transcribe",
        timeout: int = 120,
        max_retries: int = 3,
        retry_delay: float = 2.0
    ):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        # Ngrok needs this header sometimes
        self.session.headers.update({"ngrok-skip-browser-warning": "true"})
    
    def transcribe_file(
        self,
        audio_path: Path,
        language: Optional[str] = "en"
    ) -> dict:
        """
        Transcribe audio file via API.
        
        Returns dict with keys: text, language, segments, duration
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Prepare file upload
        with open(audio_path, "rb") as f:
            files = {"file": (audio_path.name, f, "audio/wav")}
            data = {}
            if language:
                data["language"] = language
            
            last_error = None
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Transcribing via API (attempt {attempt + 1}/{self.max_retries})...")
                    response = self.session.post(
                        self.api_url,
                        files=files,
                        data=data,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    # Normalize response format
                    return self._normalize_response(result)
                    
                except requests.exceptions.Timeout:
                    last_error = f"API timeout after {self.timeout}s"
                    logger.warning(f"Attempt {attempt + 1} timed out")
                except requests.exceptions.ConnectionError as e:
                    last_error = f"Connection error: {e}"
                    logger.warning(f"Attempt {attempt + 1} connection failed")
                except requests.exceptions.HTTPError as e:
                    last_error = f"HTTP {e.response.status_code}: {e.response.text}"
                    logger.warning(f"Attempt {attempt + 1} HTTP error: {e}")
                except Exception as e:
                    last_error = f"Unexpected error: {e}"
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
            
            # All retries failed
            raise ConnectionError(f"Whisper API failed after {self.max_retries} attempts: {last_error}")
    
    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = "en"
    ) -> dict:
        """Transcribe from bytes (saves to temp file first)."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = Path(f.name)
        
        try:
            return self.transcribe_file(temp_path, language)
        finally:
            temp_path.unlink(missing_ok=True)
    
    def _normalize_response(self, raw: dict) -> dict:
        """Normalize various API response formats to standard structure."""
        # Expected format from your Colab endpoint
        if isinstance(raw, dict):
            # Handle different possible response structures
            text = (
                raw.get("text") 
                or raw.get("transcription") 
                or raw.get("transcript")
                or ""
            )
            return {
                "text": text.strip(),
                "language": raw.get("language", "en"),
                "segments": raw.get("segments", []),
                "duration": raw.get("duration", 0)
            }
        return {"text": str(raw).strip(), "language": "en", "segments": [], "duration": 0}
    
    def health_check(self) -> bool:
        """Check if API is reachable."""
        try:
            # Try a simple GET or POST to root
            resp = self.session.get(self.api_url.replace("/transcribe", "/"), timeout=5)
            return resp.status_code < 500
        except:
            return False


class HybridWhisperClient:
    """
    Hybrid client: tries API first, falls back to local Whisper.
    """
    
    def __init__(
        self,
        api_url: str = "https://unhelpful-corny-jumbo.ngrok-free.dev/transcribe",
        local_model: str = "large-v3",
        local_device: str = "cuda",
        api_timeout: int = 120
    ):
        self.api_client = WhisperAPIClient(api_url, timeout=api_timeout)
        self.local_model_name = local_model
        self.local_device = self._resolve_device(local_device)
        self._local_model = None
        self._use_local = False

    @staticmethod
    def _resolve_device(requested_device: str) -> str:
        """Use CPU automatically when CUDA is configured but unavailable."""
        if requested_device.lower() != "cuda":
            return requested_device

        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
        except ImportError:
            logger.warning("Torch is unavailable; using CPU for local Whisper.")
            return "cpu"

        logger.warning("CUDA is unavailable; using CPU for local Whisper.")
        return "cpu"
    
    @property
    def local_model(self):
        """Lazy-load local Whisper model."""
        if self._local_model is None and self._use_local:
            logger.info(f"Loading local Whisper {self.local_model_name} on {self.local_device}...")
            import whisper
            try:
                self._local_model = whisper.load_model(
                    self.local_model_name,
                    device=self.local_device,
                )
            except RuntimeError as exc:
                if self.local_device != "cuda":
                    raise
                logger.warning("CUDA Whisper load failed; retrying on CPU: %s", exc)
                self.local_device = "cpu"
                self._local_model = whisper.load_model(
                    self.local_model_name,
                    device=self.local_device,
                )
        return self._local_model
    
    def transcribe_file(self, audio_path: Path, language: str = "en") -> dict:
        """Try API first, fallback to local."""
        # Try API
        if not self._use_local:
            try:
                result = self.api_client.transcribe_file(audio_path, language)
                if result.get("text"):
                    logger.info("✅ API transcription successful")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ API failed, falling back to local: {e}")
                self._use_local = True
        
        # Fallback to local
        logger.info("🔄 Using local Whisper...")
        return self._transcribe_local(audio_path, language)
    
    def transcribe_bytes(self, audio_bytes: bytes, language: str = "en") -> dict:
        """Transcribe from bytes."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = Path(f.name)
        try:
            return self.transcribe_file(temp_path, language)
        finally:
            temp_path.unlink(missing_ok=True)
    
    def _transcribe_local(self, audio_path: Path, language: str) -> dict:
        """Local Whisper transcription."""
        try:
            self._ensure_ffmpeg()
            model = self.local_model
            result = model.transcribe(
                str(audio_path),
                language=language,
                beam_size=5,
                fp16=self.local_device == "cuda"
            )
            return {
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "segments": result.get("segments", []),
                "duration": result.get("duration", 0)
            }
        except Exception as e:
            logger.error(f"Local Whisper also failed: {e}")
            raise

    @staticmethod
    def _ensure_ffmpeg() -> None:
        """Ensure Whisper can find an ffmpeg executable on Windows."""
        if shutil.which("ffmpeg"):
            return

        try:
            import imageio_ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            ffmpeg_dir = str(Path(ffmpeg_path).parent)
            # imageio's Windows binary has a versioned filename, while
            # Whisper invokes the conventional `ffmpeg` executable.
            ffmpeg_alias_dir = Path(tempfile.gettempdir()) / "proofskill-ffmpeg"
            ffmpeg_alias_dir.mkdir(parents=True, exist_ok=True)
            ffmpeg_alias = ffmpeg_alias_dir / "ffmpeg.exe"
            if not ffmpeg_alias.exists():
                shutil.copy2(ffmpeg_path, ffmpeg_alias)
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
            os.environ["PATH"] = str(ffmpeg_alias_dir) + os.pathsep + os.environ["PATH"]
            if shutil.which("ffmpeg"):
                return
        except ImportError:
            pass

        raise RuntimeError(
            "Whisper requires ffmpeg to decode microphone audio. "
            "Install the project dependencies again, or install ffmpeg and add "
            "its bin directory to PATH, then restart Streamlit."
        )
    
    def force_local(self):
        """Force use of local model (e.g., if API quota exceeded)."""
        self._use_local = True
        _ = self.local_model  # Trigger load
    
    def force_api(self):
        """Reset to try API again."""
        self._use_local = False