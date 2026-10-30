# src/services/gradio_tts_client.py
"""
Gradio TTS Client — Calls your Hugging Face Space / Gradio endpoint for TTS.
Supports Edge0/Audio8-TTS-Realistic-0.6b and similar models.
"""
import logging
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any
import shutil

logger = logging.getLogger(__name__)


class GradioTTSClient:
    """Client for Gradio-hosted TTS models (e.g., Edge0/Audio8-TTS-Realistic-0.6b)."""
    
    def __init__(
        self,
        space_url: str = "https://bd512e52f4484d878a.gradio.live/",
        api_name: str = "/predict",
        timeout: int = 120,
        max_retries: int = 3,
        retry_delay: float = 3.0
    ):
        """
        Initialize Gradio TTS client.
        
        Args:
            space_url: Full URL of the Gradio Space (e.g., https://xxx.gradio.live/)
            api_name: API endpoint name (usually "/predict" or "/generate")
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            retry_delay: Delay between retries (seconds)
        """
        self.space_url = space_url.rstrip("/")
        self.api_name = api_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize gradio_client."""
        try:
            from gradio_client import Client
            self._client = Client(self.space_url)
            logger.info(f"Connected to Gradio TTS at {self.space_url}")
        except ImportError:
            logger.error("gradio_client not installed. Run: pip install gradio_client")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Gradio Space: {e}")
            raise
    
    def synthesize(
        self,
        text: str,
        **kwargs
    ) -> bytes:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            **kwargs: Additional parameters for the TTS model (voice, speed, etc.)
            
        Returns:
            Audio bytes (WAV/MP3)
        """
        if not self._client:
            self._init_client()
        
        # Prepare inputs - adjust based on your model's API
        # Common patterns:
        # - Single text input: api_name="/predict", inputs=[text]
        # - Text + params: api_name="/predict", inputs=[text, speed, voice]
        # - Named params: api_name="/predict", inputs={"text": text, "speed": 1.0}
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Synthesizing via Gradio TTS (attempt {attempt + 1}/{self.max_retries})...")
                
                # Call the API - adjust input format based on your model's signature
                result = self._client.predict(
                    text,
                    api_name=self.api_name
                )
                
                # Result is typically a file path or dict with file path
                audio_path = self._extract_audio_path(result)
                
                if audio_path and Path(audio_path).exists():
                    # Read and return audio bytes
                    with open(audio_path, "rb") as f:
                        audio_bytes = f.read()
                    
                    logger.info(f"✅ TTS synthesis successful ({len(audio_bytes)} bytes)")
                    return audio_bytes
                else:
                    raise ValueError(f"Unexpected result format: {result}")
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
        
        raise ConnectionError(f"Gradio TTS failed after {self.max_retries} attempts: {last_error}")
    
    def _extract_audio_path(self, result: Any) -> Optional[str]:
        """Extract audio file path from Gradio result."""
        if result is None:
            return None
        
        # Gradio returns various formats depending on output component
        if isinstance(result, str):
            # Direct file path
            return result
        elif isinstance(result, dict):
            # File dict from File component
            return result.get("path") or result.get("name") or result.get("url")
        elif isinstance(result, (list, tuple)):
            # Multiple outputs - first is usually audio
            for item in result:
                path = self._extract_audio_path(item)
                if path:
                    return path
        elif hasattr(result, 'name'):  # tempfile object
            return result.name
        
        return None
    
    def synthesize_to_file(
        self,
        text: str,
        output_path: Path,
        **kwargs
    ) -> Path:
        """Synthesize and save directly to file."""
        audio_bytes = self.synthesize(text, **kwargs)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio_bytes)
        return output_path
    
    def health_check(self) -> bool:
        """Check if Gradio Space is reachable."""
        try:
            # Try a simple prediction with minimal input
            _ = self._client.predict("", api_name=self.api_name)
            return True
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get info about the connected model."""
        try:
            # Try to get view API info
            from gradio_client import Client
            client = Client(self.space_url)
            return client.view_api()
        except:
            return {}


class HybridTTSClient:
    """
    Hybrid TTS: tries primary (Gradio) first, falls back to secondary (edge-tts/pyttsx3).
    """
    
    def __init__(
        self,
        primary_client: GradioTTSClient,
        fallback_client: Any = None
    ):
        self.primary = primary_client
        self.fallback = fallback_client
        self._use_fallback = False
    
    def synthesize(self, text: str, **kwargs) -> bytes:
        """Try primary TTS, fallback to secondary."""
        if not self._use_fallback:
            try:
                return self.primary.synthesize(text, **kwargs)
            except Exception as e:
                logger.warning(f"⚠️ Primary TTS failed, trying fallback: {e}")
                self._use_fallback = True
        
        if self.fallback:
            logger.info("🔄 Using fallback TTS...")
            return self.fallback.synthesize(text, **kwargs)
        else:
            raise RuntimeError("No TTS available (primary failed, no fallback)")
    
    def force_fallback(self):
        """Force use of fallback."""
        self._use_fallback = True
    
    def force_primary(self):
        """Reset to try primary again."""
        self._use_fallback = False


# Convenience function for easy setup
def create_gradio_tts(
    space_url: str = "https://bd512e52f4484d878a.gradio.live/",
    api_name: str = "/predict",
    fallback: str = "edge"  # "edge", "system", or None
) -> HybridTTSClient:
    """Create Gradio TTS with automatic fallback."""
    
    primary = GradioTTSClient(space_url=space_url, api_name=api_name)
    
    fallback_client = None
    if fallback == "edge":
        try:
            from src.services.free_tts import EdgeTTSClient
            fallback_client = EdgeTTSClient()
        except ImportError:
            logger.warning("edge-tts not available for fallback")
    elif fallback == "system":
        try:
            from src.services.free_tts import SystemTTSClient
            fallback_client = SystemTTSClient()
        except ImportError:
            logger.warning("pyttsx3 not available for fallback")
    
    return HybridTTSClient(primary, fallback_client)