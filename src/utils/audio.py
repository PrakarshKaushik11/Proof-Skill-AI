# src/utils/audio.py
"""
Audio Utilities — Recording, playback, format conversion.
"""
import io
import wave
import tempfile
from pathlib import Path
from typing import Optional, Generator
import numpy as np


class AudioRecorder:
    """Audio recording utilities."""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.frames = []
    
    def start_recording(self):
        """Start recording (placeholder - actual implementation needs pyaudio/sounddevice)."""
        self.recording = True
        self.frames = []
        # Real implementation would use:
        # import pyaudio
        # self.stream = pyaudio.PyAudio().open(...)
    
    def stop_recording(self) -> bytes:
        """Stop recording and return WAV bytes."""
        self.recording = False
        # Real implementation would collect frames and write WAV
        # For now, return empty bytes
        return b""
    
    def save_wav(self, audio_data: bytes, filepath: Path):
        """Save raw audio data as WAV file."""
        with wave.open(str(filepath), 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data)
    
    @staticmethod
    def convert_to_wav(audio_bytes: bytes, input_format: str = "webm") -> bytes:
        """Convert audio to WAV format using ffmpeg."""
        import subprocess
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix=f".{input_format}", delete=False) as inf:
            inf.write(audio_bytes)
            in_path = inf.name
        
        out_path = in_path.replace(f".{input_format}", ".wav")
        
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", in_path,
                "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
                out_path
            ], capture_output=True, check=True)
            
            with open(out_path, "rb") as f:
                wav_bytes = f.read()
            
            return wav_bytes
        finally:
            Path(in_path).unlink(missing_ok=True)
            Path(out_path).unlink(missing_ok=True)


class AudioPlayer:
    """Audio playback utilities."""
    
    @staticmethod
    def play_bytes(audio_bytes: bytes, format: str = "mp3") -> bool:
        """Play audio bytes (placeholder - needs pygame/simpleaudio)."""
        # Real implementation:
        # import pygame
        # pygame.mixer.init()
        # sound = pygame.mixer.Sound(io.BytesIO(audio_bytes))
        # sound.play()
        return True
    
    @staticmethod
    def get_duration(audio_bytes: bytes, format: str = "mp3") -> float:
        """Get audio duration in seconds."""
        # Would use mutagen or ffprobe
        return 0.0
    
    @staticmethod
    def create_streamlit_audio(audio_bytes: bytes, format: str = "audio/mp3"):
        """Create Streamlit audio element."""
        import streamlit as st
        st.audio(audio_bytes, format=format)


def create_audio_recorder_component():
    """Create Streamlit-compatible audio recorder using streamlit-webrtc."""
    # This would be used with streamlit-webrtc component
    # Example usage:
    # from streamlit_webrtc import webrtc_streamer, WebRtcMode
    # webrtc_streamer(key="viva", mode=WebRtcMode.SENDONLY, audio_processor_factory=AudioProcessor)
    pass


class AudioProcessor:
    """WebRTC audio processor for real-time recording."""
    
    def __init__(self):
        self.frames = []
        self.recording = False
    
    def recv(self, frame):
        """Process incoming audio frame."""
        if self.recording:
            self.frames.append(frame.to_ndarray())
        return frame
    
    def start(self):
        self.recording = True
        self.frames = []
    
    def stop(self) -> np.ndarray:
        self.recording = False
        if self.frames:
            return np.concatenate(self.frames, axis=1)
        return np.array([])


def audio_to_base64(audio_bytes: bytes) -> str:
    """Convert audio bytes to base64 string."""
    import base64
    return base64.b64encode(audio_bytes).decode('utf-8')


def base64_to_audio(b64_string: str) -> bytes:
    """Convert base64 string to audio bytes."""
    import base64
    return base64.b64decode(b64_string)