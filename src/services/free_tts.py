# src/services/free_tts.py
"""
Free TTS Clients — Edge TTS, System TTS (pyttsx3), Coqui TTS
"""
import asyncio
import tempfile
import os
from pathlib import Path
from typing import Optional

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


class EdgeTTSClient:
    """Microsoft Edge TTS - Free, high quality, no API key."""
    
    # Best voices for interview scenarios
    VOICES = {
        "intro": "en-US-AriaNeural",        # Warm, welcoming
        "technical": "en-US-GuyNeural",     # Clear, precise male
        "behavioral": "en-US-JennyNeural",  # Conversational female
        "feedback": "en-US-DavisNeural",    # Encouraging male
    }
    
    def __init__(self):
        if not EDGE_TTS_AVAILABLE:
            raise RuntimeError("edge-tts not installed. Run: pip install edge-tts")
    
    async def _synthesize_async(self, text: str, voice: str = "en-US-AriaNeural", rate: str = "+0%") -> bytes:
        """Async synthesis."""
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        return b"".join(audio_chunks)
    
    def text_to_speech_sync(self, text: str, voice_type: str = "technical") -> bytes:
        """Synchronous wrapper."""
        voice = self.VOICES.get(voice_type, "en-US-AriaNeural")
        return asyncio.run(self._synthesize_async(text, voice))
    
    async def text_to_speech(self, text: str, voice_type: str = "technical") -> bytes:
        """Async synthesis with voice type."""
        voice = self.VOICES.get(voice_type, "en-US-AriaNeural")
        return await self._synthesize_async(text, voice)


class SystemTTSClient:
    """System TTS using pyttsx3 - completely offline."""
    
    def __init__(self):
        if not PYTTSX3_AVAILABLE:
            raise RuntimeError("pyttsx3 not installed. Run: pip install pyttsx3")
        
        self.engine = pyttsx3.init()
        self._configure_voices()
    
    def _configure_voices(self):
        voices = self.engine.getProperty('voices')
        # Prefer English voices
        for v in voices:
            if 'english' in v.name.lower() or 'en_' in v.id.lower():
                self.engine.setProperty('voice', v.id)
                break
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 0.9)
    
    def text_to_speech(self, text: str, voice_type: str = "technical") -> bytes:
        """Synthesize and return bytes via temp file."""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = f.name
        
        try:
            self.engine.save_to_file(text, temp_path)
            self.engine.runAndWait()
            
            with open(temp_path, 'rb') as f:
                return f.read()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    # Alias for compatibility
    text_to_speech_sync = text_to_speech


class CoquiTTSClient:
    """Coqui XTTS v2 - Best open-source quality, voice cloning."""
    
    def __init__(self):
        try:
            from TTS.api import TTS
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
            print("✅ Coqui XTTS v2 loaded")
        except ImportError:
            raise RuntimeError("Coqui TTS not installed. Run: pip install TTS")
        except Exception as e:
            raise RuntimeError(f"Failed to load Coqui TTS: {e}")
    
    def text_to_speech(self, text: str, voice_type: str = "technical") -> bytes:
        """Synthesize using Coqui XTTS."""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = f.name
        
        try:
            # XTTS can use built-in speakers or clone from reference
            self.tts.tts_to_file(text=text, file_path=temp_path, language="en")
            
            with open(temp_path, 'rb') as f:
                return f.read()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    text_to_speech_sync = text_to_speech


def get_available_tts_clients():
    """Get list of available TTS clients."""
    clients = []
    if EDGE_TTS_AVAILABLE:
        clients.append(("edge", "Edge TTS (Microsoft) - Free, cloud", EdgeTTSClient))
    if PYTTSX3_AVAILABLE:
        clients.append(("system", "System TTS (pyttsx3) - Offline", SystemTTSClient))
    try:
        from TTS.api import TTS
        clients.append(("coqui", "Coqui XTTS v2 - Best local quality", CoquiTTSClient))
    except:
        pass
    return clients