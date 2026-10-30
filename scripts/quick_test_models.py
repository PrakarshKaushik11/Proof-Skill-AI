#!/usr/bin/env python
"""
Quick test for both models - tests local fallback paths first, then API.
Run with: python scripts/quick_test_models.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.services.whisper_api_client import HybridWhisperClient
from src.services.gradio_tts_client import create_gradio_tts
from src.services.voice_pipeline import VoicePipeline


def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"  {status} | {test_name}")
    if details:
        print(f"         {details}")


def test_whisper_local_fallback():
    """Test Whisper local fallback (fast, no API needed)."""
    print_header("WHISPER LOCAL FALLBACK TEST")
    
    try:
        hybrid = HybridWhisperClient(
            api_url=settings.WHISPER_API_URL,
            local_model="base",  # Fast model
            local_device="cpu",
            api_timeout=5  # Short timeout
        )
        hybrid.force_local()
        
        import wave
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_file = wave.open(f, 'wb')
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b'\x00' * 16000)  # 0.5 sec silence
            wav_file.close()
            temp_path = Path(f.name)
        
        result = hybrid.transcribe_file(temp_path)
        success = isinstance(result, dict) and 'text' in result
        print_result("Whisper Local Fallback", success, f"Result: {result}")
        temp_path.unlink(missing_ok=True)
        return success
    except Exception as e:
        print_result("Whisper Local Fallback", False, str(e))
        return False


def test_edge_tts_fallback():
    """Test edge-tts fallback (fast, no API needed)."""
    print_header("EDGE TTS FALLBACK TEST")
    
    try:
        from src.services.gradio_tts_client import HybridTTSClient
        from src.services.free_tts import EdgeTTSClient
        
        edge_client = EdgeTTSClient()
        
        # Test with short text
        audio_bytes = edge_client.text_to_speech_sync("Testing edge TTS fallback.")
        success = isinstance(audio_bytes, bytes) and len(audio_bytes) > 1000
        
        output_path = Path("test_edge_fallback.wav")
        output_path.write_bytes(audio_bytes)
        
        print_result("Edge TTS Fallback", success, f"Generated {len(audio_bytes)} bytes")
        return success
    except Exception as e:
        print_result("Edge TTS Fallback", False, str(e))
        return False


def test_voice_pipeline_with_fallbacks():
    """Test VoicePipeline with forced fallbacks."""
    print_header("VOICEPIPELINE WITH FALLBACKS")
    
    try:
        # Force TTS fallback (edge-tts) and STT fallback (local Whisper)
        pipeline = VoicePipeline(tts_provider="edge")
        pipeline.stt.force_local()
        
        # Test TTS
        audio1 = pipeline.speak_question("Testing fallback TTS.")
        success1 = isinstance(audio1, bytes) and len(audio1) > 1000
        print_result("Pipeline TTS (edge-tts)", success1, f"Generated {len(audio1)} bytes")
        
        # Test STT
        import wave
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            import wave
            wav_file = wave.open(f, 'wb')
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b'\x00' * 16000)
            wav_file.close()
            temp_path = Path(f.name)
        
        pipeline.stt.force_local()
        result = pipeline.stt.transcribe_file(temp_path)
        success2 = isinstance(result, dict) and 'text' in result
        print_result("Pipeline STT (local Whisper)", success2, f"Result: {result}")
        temp_path.unlink(missing_ok=True)
        
        return success1 and success2
    except Exception as e:
        print_result("VoicePipeline Fallbacks", False, str(e))
        return False


def test_gradio_tts_quick():
    """Quick test Gradio TTS with short timeout."""
    print_header("GRADIO TTS QUICK TEST (may timeout if Space sleeping)")
    
    try:
        from src.services.gradio_tts_client import GradioTTSClient
        from src.config.settings import settings
        
        # Very short timeout for quick fail
        client = GradioTTSClient(
            space_url=settings.GRADIO_TTS_URL,
            api_name=settings.GRADIO_TTS_API_NAME,
            timeout=10,  # 10 sec timeout
            max_retries=1
        )
        
        # Just test connection, not synthesis
        healthy = client.health_check()
        print_result("Gradio TTS Connection", healthy, "Space awake" if healthy else "Space sleeping/unreachable")
        return healthy
    except Exception as e:
        print_result("Gradio TTS Connection", False, f"Space unreachable: {str(e)[:100]}")
        return False


def print_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"  {status} | {test_name}")
    if details:
        print(f"         {details}")


def main():
    print_header("QUICK MODEL INTEGRATION TEST")
    print(f"  Whisper API: {settings.WHISPER_API_URL}")
    print(f"  Gradio TTS:  {settings.GRADIO_TTS_URL}")
    
    # Check key dependencies
    print("\n[0] Checking Dependencies...")
    deps = {}
    for dep in ['gradio_client', 'edge_tts', 'whisper', 'llama_cpp']:
        try:
            __import__(dep)
            deps[dep] = True
        except:
            deps[dep] = False
        print_result(f"Dependency: {dep}", deps[dep])
    
    if not deps['whisper']:
        print("❌ CRITICAL: whisper not installed")
        return False
    
    all_results = {}
    
    # Test 1: Whisper local fallback (always works)
    all_results['Whisper Local'] = test_whisper_local_fallback()
    
    # Test 2: Edge TTS fallback (always works if installed)
    all_results['Edge TTS Fallback'] = test_edge_tts_fallback()
    
    # Test 3: VoicePipeline with fallbacks
    all_results['VoicePipeline Fallbacks'] = test_voice_pipeline_with_fallbacks()
    
    # Test 4: Gradio TTS (may be slow/sleeping)
    all_results['Gradio TTS (Optional)'] = test_gradio_tts_quick()
    
    # Summary
    print_header("QUICK TEST SUMMARY")
    total = 0
    passed = 0
    
    for category, result in all_results.items():
        total += 1
        if result:
            passed += 1
        icon = "✅" if result else "❌"
        print(f"  {icon} {category}")
    
    print(f"\n  {'='*40}")
    overall = "✅ CORE WORKING" if passed >= 3 else "⚠️ NEEDS ATTENTION" if passed >= 2 else "❌ BROKEN"
    print(f"  {overall} | {passed}/{total} core tests passed")
    print(f"  {'='*40}")
    
    if passed >= 3:
        print("\n🎉 Core fallback chain working! Ready for development.")
        print("   Note: Gradio TTS is optional - will auto-fallback to edge-tts")
    else:
        print("\n⚠️  Core issues detected. Check missing dependencies.")
    
    return passed >= 3


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)