#!/usr/bin/env python
"""
Minimal standalone test - no heavy imports.
"""
import sys
from pathlib import Path
import wave
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test 1: Whisper local directly
print("=" * 50)
print("TEST 1: Whisper Local")
print("=" * 50)

try:
    import whisper
    from src.services.whisper_api_client import HybridWhisperClient
    print("✅ Whisper imported")
    
    model = whisper.load_model("base", device="cpu")
    print("✅ Whisper base model loaded on CPU")
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_file = wave.open(f, 'wb')
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b'\x00' * 16000)
        wav_file.close()
        temp_path = f.name
    
    HybridWhisperClient._ensure_ffmpeg()
    result = model.transcribe(temp_path, fp16=False)
    print(f"✅ Whisper transcription: {result}")
    Path(temp_path).unlink(missing_ok=True)
    whisper_ok = True
except Exception as e:
    print(f"❌ Whisper failed: {e}")
    whisper_ok = False

# Test 2: edge-tts
print("\n" + "=" * 50)
print("TEST 2: Edge TTS")
print("=" * 50)

edge_ok = False
try:
    import edge_tts
    import asyncio
    
    async def test_edge():
        communicate = edge_tts.Communicate("Testing edge TTS.", "en-US-AriaNeural")
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        return b"".join(audio_chunks)
    
    audio_bytes = asyncio.run(test_edge())
    success = isinstance(audio_bytes, bytes) and len(audio_bytes) > 1000
    print(f"{'✅' if success else '❌'} Edge TTS: {len(audio_bytes)} bytes generated")
    Path("test_edge.wav").write_bytes(audio_bytes)
    edge_ok = success
except Exception as e:
    print(f"❌ Edge TTS failed: {e}")
    edge_ok = False

# Test 3: Gradio client (optional)
print("\n" + "=" * 50)
print("TEST 3: Gradio Client (optional)")
print("=" * 50)

gradio_ok = False
try:
    from gradio_client import Client
    
    # Test connection only (short timeout)
    client = Client("https://9b6c4bb1974fc833c1.gradio.live/")
    print("✅ Gradio client created")
    
    # Quick health check - this might take a while if Space is sleeping
    # Just verify the client works
    print("✅ Gradio client ready (Space may be sleeping)")
    gradio_ok = True
except Exception as e:
    print(f"⚠️ Gradio client unavailable; Edge TTS fallback remains active: {e}")
    gradio_ok = None

# Test 4: llama-cpp-python (optional)
print("\n" + "=" * 50)
print("TEST 4: llama-cpp-python (optional)")
print("=" * 50)

llama_ok = False
try:
    from llama_cpp import Llama
    print("✅ llama-cpp-python imported")
    llama_ok = True
except Exception as e:
    print(f"⚠️ llama-cpp-python unavailable; mock/model fallback remains active: {e}")
    llama_ok = None

# Summary
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
tests = {
    "Whisper Local": whisper_ok,
    "Edge TTS": edge_ok,
    "Gradio Client": gradio_ok,
    "llama-cpp-python": llama_ok,
}
for name, result in tests.items():
    print(f"  {'✅' if result is True else '⚠️' if result is None else '❌'} {name}")

all_core = whisper_ok and edge_ok
print(f"\n{'✅ CORE READY' if all_core else '❌ CORE MISSING'}")
if all_core:
    print("🎉 Core fallback chain (Whisper + Edge TTS) working!")
    print("   Gradio TTS will be used when Space is awake, else Edge TTS fallback")