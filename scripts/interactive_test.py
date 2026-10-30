#!/usr/bin/env python
"""
Interactive Test Environment for ProofSkill AI Voice Pipeline
Run: python scripts/interactive_test.py
"""
import sys
import asyncio
from pathlib import Path
import tempfile
import wave

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.services.whisper_api_client import HybridWhisperClient
from src.services.gradio_tts_client import create_gradio_tts
from src.services.voice_pipeline import VoicePipeline
from src.services.free_tts import EdgeTTSClient


class InteractiveTest:
    def __init__(self):
        self.setup_clients()
    
    def setup_clients(self):
        print("🔧 Initializing clients...")
        
        # STT: Hybrid (API + Local fallback)
        self.stt = HybridWhisperClient(
            api_url=settings.WHISPER_API_URL,
            local_model="base",
            local_device="cpu",
            api_timeout=30
        )
        self.stt.force_local()  # Use local for reliable testing
        
        # TTS: Try Gradio first, fallback to Edge
        try:
            self.tts = create_gradio_tts(
                space_url=settings.GRADIO_TTS_URL,
                api_name=settings.GRADIO_TTS_API_NAME,
                fallback="edge"
            )
            self.tts_provider = "Gradio + Edge fallback"
        except:
            self.tts = EdgeTTSClient()
            self.tts_provider = "Edge TTS only"
        
        print(f"✅ STT: Local Whisper (base/CPU)")
        print(f"✅ TTS: {self.tts_provider}")
        print()
    
    def record_audio(self, duration=5):
        """Record audio from microphone (requires PyAudio)."""
        try:
            import pyaudio
        except ImportError:
            print("❌ PyAudio not installed. Cannot record from microphone.")
            print("   Install MSVC Build Tools + pip install pyaudio")
            return None
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                           rate=RATE, input=True, frames_per_buffer=CHUNK)
        
        print(f"🎤 Recording for {duration} seconds... Speak now!")
        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("🛑 Recording stopped")
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wf = wave.open(f, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b''.join(frames))
            wf.close()
            return Path(f.name)
    
    def test_tts(self, text):
        """Test TTS synthesis."""
        print(f"\n🔊 TTS: '{text}'")
        try:
            audio_bytes = self.tts.synthesize(text)
            output = Path("output_tts.wav")
            output.write_bytes(audio_bytes)
            print(f"✅ Generated {len(audio_bytes)} bytes → {output}")
            return True
        except Exception as e:
            print(f"❌ TTS failed: {e}")
            return False
    
    def test_stt(self, audio_path):
        """Test STT transcription."""
        print(f"\n🎤 STT: Transcribing {audio_path}")
        try:
            result = self.stt.transcribe_file(audio_path)
            print(f"✅ Transcription: '{result.get('text', '')}'")
            return result
        except Exception as e:
            print(f"❌ STT failed: {e}")
            return None
    
    def round_trip_test(self, text):
        """Full TTS → STT round trip."""
        print(f"\n🔄 ROUND TRIP: '{text}'")
        print("1. TTS → Audio")
        audio_bytes = self.tts.synthesize(text)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            audio_path = Path(f.name)
        
        print("2. Audio → STT")
        result = self.stt.transcribe_file(audio_path)
        audio_path.unlink(missing_ok=True)
        
        transcribed = result.get('text', '').strip()
        print(f"   Original:  '{text}'")
        print(f"   Transcribed: '{transcribed}'")
        print(f"   Match: {text.lower().strip() == transcribed.lower().strip()}")
        return transcribed
    
    def run_interactive(self):
        """Interactive menu."""
        while True:
            print("\n" + "="*50)
            print("🎯 PROOFSKILL AI - INTERACTIVE VOICE TEST")
            print("="*50)
            print("1. Test TTS (text → speech)")
            print("2. Test STT (record → transcribe) [needs PyAudio]")  
            print("3. Test STT (use generated TTS audio file)")
            print("4. Round-trip test (TTS → STT)")
            print("5. Quick TTS test (predefined)")
            print("6. Exit")
            
            choice = input("\nSelect (1-6): ").strip()
            
            if choice == "1":
                text = input("Enter text to synthesize: ").strip()
                if text:
                    self.test_tts(text)
            
            elif choice == "2":
                duration = int(input("Record duration (seconds) [5]: ") or "5")
                audio_path = self.record_audio(duration)
                if audio_path:
                    self.test_stt(audio_path)
                    audio_path.unlink(missing_ok=True)
            
            elif choice == "3":
                # Generate TTS then test STT on it
                text = input("Enter text to synthesize then transcribe: ").strip()
                if text:
                    print("Generating TTS audio...")
                    audio_bytes = self.tts.synthesize(text)
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        f.write(audio_bytes)
                        audio_path = Path(f.name)
                    
                    print("Transcribing generated audio...")
                    self.test_stt(audio_path)
                    audio_path.unlink(missing_ok=True)
            
            elif choice == "4":
                text = input("Enter text for round-trip: ").strip()
                if text:
                    self.round_trip_test(text)
            
            elif choice == "5":
                tests = [
                    "Welcome to your ProofSkill AI viva session.",
                    "In your ecommerce-api repository, walk me through the authentication flow.",
                    "How would you handle rate limiting differently in this API?",
                    "Tell me about a challenging bug you fixed in a team project."
                ]
                for t in tests:
                    self.test_tts(t)
            
            elif choice == "6":
                print("👋 Goodbye!")
                break
            
            else:
                print("Invalid choice. Try again.")


def main():
    print("🎯 ProofSkill AI - Interactive Voice Test Environment")
    print("="*55)
    
    print("\n📋 Available features:")
    print("  1. TTS (text → speech) - Always works")
    print("  2. STT via file - Always works")
    print("  3. Microphone recording - Needs PyAudio (optional)")
    print()
    
    try:
        test_env = InteractiveTest()
        test_env.run_interactive()
    except KeyboardInterrupt:
        print("\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()