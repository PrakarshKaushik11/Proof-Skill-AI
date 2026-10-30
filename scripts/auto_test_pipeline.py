#!/usr/bin/env python
"""
Automated Pipeline Test - No interactive input needed.
Run: python scripts/auto_test_pipeline.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.whisper_api_client import HybridWhisperClient
from src.services.free_tts import EdgeTTSClient
from src.services.gradio_tts_client import create_gradio_tts
from src.services.voice_pipeline import VoicePipeline
from src.config.settings import settings
import wave


def print_result(name, success, detail=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"  {status} | {name}" + (f" — {detail}" if detail else ""))


def test_tts(tts_client, name):
    """Test TTS synthesis."""
    text = "Welcome to your ProofSkill AI viva session. Let's begin with the first question."
    try:
        # Try different method names
        if hasattr(tts_client, 'synthesize'):
            audio_bytes = tts_client.synthesize(text)
        elif hasattr(tts_client, 'text_to_speech_sync'):
            audio_bytes = tts_client.text_to_speech_sync(text)
        elif hasattr(tts_client, 'text_to_speech'):
            import asyncio
            audio_bytes = asyncio.run(tts_client.text_to_speech(text))
        else:
            raise AttributeError("No synthesis method found")
        
        success = isinstance(audio_bytes, bytes) and len(audio_bytes) > 1000
        
        # Save for verification
        output = Path(f"test_{name}_output.wav")
        output.write_bytes(audio_bytes)
        
        print_result(f"{name} TTS", success, f"{len(audio_bytes)} bytes → {output}")
        return success, audio_bytes
    except Exception as e:
        print_result(f"{name} TTS", False, str(e)[:100])
        return False, None


def test_stt(stt_client, audio_bytes, name):
    """Test STT transcription."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = Path(f.name)
        
        # Try different method names
        if hasattr(stt_client, 'transcribe_file'):
            result = stt_client.transcribe_file(temp_path)
        elif hasattr(stt_client, 'transcribe'):
            result = stt_client.transcribe(temp_path)
        else:
            raise AttributeError("No transcription method found")
        
        success = isinstance(result, dict) and 'text' in result
        
        transcribed = result.get('text', '').strip()
        print_result(f"{name} STT", success, f"'{transcribed[:60]}...'")
        
        temp_path.unlink(missing_ok=True)
        return success, transcribed
    except Exception as e:
        print_result(f"{name} STT", False, str(e)[:100])
        return False, ""


def test_round_trip(tts_name, tts_client, stt_client):
    """Full TTS → STT round trip."""
    text = "In your ecommerce API repository, walk me through the authentication flow in the auth module."
    
    print(f"\n🔄 ROUND TRIP: {tts_name} → STT")
    print(f"   Original: '{text[:60]}...'")
    
    success_tts, audio_bytes = test_tts(tts_client, f"roundtrip_{tts_name}")
    if not success_tts:
        return False
    
    success_stt, transcribed = test_stt(stt_client, audio_bytes, f"roundtrip_{tts_name}")
    
    if success_stt:
        original_lower = "in your ecommerce api repository walk me through the authentication flow"
        transcribed_lower = transcribed.lower().replace('.', '').replace(',', '')
        # Simple similarity check
        match = all(word in transcribed_lower for word in original_lower.split()[:8])
        print_result(f"   Semantic Match", match, f"'{transcribed[:50]}...'")
    
    return success_tts and success_stt


def main():
    print("=" * 60)
    print("🎯 PROOFSKILL AI - AUTOMATED PIPELINE TEST")
    print("=" * 60)
    
    # Initialize clients
    print("\n🔧 Initializing clients...")
    
    # STT: Hybrid (local fallback)
    stt = HybridWhisperClient(
        api_url=settings.WHISPER_API_URL,
        local_model="base",
        local_device="cpu",
        api_timeout=10
    )
    stt.force_local()
    print("✅ STT: Local Whisper (base/CPU)")
    
    # TTS: Edge (guaranteed to work)
    edge_tts = EdgeTTSClient()
    print("✅ TTS: Edge TTS (Microsoft voices)")
    
    # Try Gradio TTS
    try:
        gradio_tts = create_gradio_tts(
            space_url=settings.GRADIO_TTS_URL,
            api_name=settings.GRADIO_TTS_API_NAME,
            fallback="edge"
        )
        print("✅ TTS: Gradio (Audio8-TTS) + Edge fallback")
        has_gradio = True
    except Exception as e:
        print(f"⚠️  Gradio TTS unavailable: {e}")
        has_gradio = False
    
    print("\n" + "=" * 60)
    print("TESTING TTS (Text-to-Speech)")
    print("=" * 60)
    
    edge_ok, edge_audio = test_tts(edge_tts, "Edge")
    gradio_ok = False
    gradio_audio = None
    
    if has_gradio:
        gradio_ok, gradio_audio = test_tts(gradio_tts, "Gradio")
    
    print("\n" + "=" * 60)
    print("TESTING STT (Speech-to-Text) with Generated Audio")
    print("=" * 60)
    
    edge_stt_ok, _ = test_stt(stt, edge_audio, "Edge")
    
    if has_gradio and gradio_audio:
        gradio_stt_ok, _ = test_stt(stt, gradio_audio, "Gradio")
    
    print("\n" + "=" * 60)
    print("TESTING ROUND TRIPS (TTS → STT)")
    print("=" * 60)
    
    edge_roundtrip = test_round_trip("Edge", edge_tts, stt)
    gradio_roundtrip = False
    if has_gradio:
        gradio_roundtrip = test_round_trip("Gradio", gradio_tts, stt)
    
    print("\n" + "=" * 60)
    print("TESTING VOICE PIPELINE INTEGRATION")
    print("=" * 60)
    
    # Test VoicePipeline integration
    pipeline_ok = False
    stt_ok = False
    try:
        pipeline = VoicePipeline(tts_provider="edge")
        
        # Check if STT has force_local
        if hasattr(pipeline.stt, 'force_local'):
            pipeline.stt.force_local()
            stt_method = "force_local"
        elif hasattr(pipeline.stt, 'hybrid_client') and hasattr(pipeline.stt.hybrid_client, 'force_local'):
            pipeline.stt.hybrid_client.force_local()
            stt_method = "hybrid_client.force_local"
        else:
            stt_method = "unknown"
        
        # Test TTS
        audio = pipeline.speak_question("Test question from AI interviewer.")
        pipeline_ok = isinstance(audio, bytes) and len(audio) > 1000
        print_result("VoicePipeline TTS", pipeline_ok, f"{len(audio)} bytes")
        
        # Test STT
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            import wave
            wf = wave.open(f, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b'\x00' * 16000)
            wf.close()
            temp_path = Path(f.name)
        
        if hasattr(pipeline.stt, 'transcribe_file'):
            result = pipeline.stt.transcribe_file(temp_path)
        elif hasattr(pipeline.stt, 'transcribe'):
            result = pipeline.stt.transcribe(temp_path)
        else:
            raise AttributeError("No transcription method found")
            
        stt_ok = isinstance(result, dict) and 'text' in result
        print_result("VoicePipeline STT", stt_ok, f"Method: {stt_method}, Result: {result.get('text', '')[:40]}")
        temp_path.unlink(missing_ok=True)
        
    except Exception as e:
        print_result("VoicePipeline", False, str(e)[:80])
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    tests = {
        "Edge TTS": edge_ok,
        "Edge STT": edge_stt_ok,
        "Edge Round-trip": edge_roundtrip,
    }
    
    if has_gradio:
        tests["Gradio TTS"] = gradio_ok
        tests["Gradio Round-trip"] = gradio_roundtrip
    
    # VoicePipeline tests
    if 'pipeline_ok' in locals():
        tests["VoicePipeline"] = pipeline_ok
    if 'stt_ok' in locals():
        tests["VoicePipeline STT"] = stt_ok
    
    passed = sum(1 for v in tests.values() if v)
    total = len(tests)
    
    print(f"\n{'='*40}")
    overall = "✅ ALL WORKING" if passed == total else "⚠️ PARTIAL" if passed >= total//2 else "❌ ISSUES"
    print(f"  {overall} | {passed}/{total} tests passed")
    print(f"  {'='*40}")
    
    print("\n📋 AVAILABLE FILES FOR MANUAL CHECK:")
    for f in Path(".").glob("test_*.wav"):
        print(f"  📁 {f} ({f.stat().st_size} bytes)")
    
    print("\n🎯 NEXT STEPS:")
    print("  1. Play generated .wav files to verify audio quality")
    print("  2. If Gradio fails, ensure HF Space is awake + pyyaml installed")
    print("  3. Run `python run.py` to launch full Streamlit app")
    
    # Check core functionality
    core_tests = [v for k, v in tests.items() if "TTS" in k or "STT" in k]
    return len(core_tests) > 0 and all(core_tests) if core_tests else False


if __name__ == "__main__":
    main()