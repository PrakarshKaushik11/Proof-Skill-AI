#!/usr/bin/env python
"""
Comprehensive test for both Whisper API and Gradio TTS integration.
Run with: python scripts/test_both_models.py
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.services.whisper_api_client import WhisperAPIClient, HybridWhisperClient
from src.services.gradio_tts_client import GradioTTSClient, create_gradio_tts
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


def test_whisper_api():
    """Test Whisper API (Colab) with local fallback."""
    print_header("WHISPER STT TESTS (Colab API + Local Fallback)")
    
    results = {}
    
    # Test 1: API Client Health Check
    print("\n[1/5] Testing Whisper API Client...")
    try:
        client = WhisperAPIClient(
            api_url=settings.WHISPER_API_URL,
            timeout=settings.WHISPER_API_TIMEOUT
        )
        healthy = client.health_check()
        results['api_health'] = healthy
        print_result("API Health Check", healthy, f"URL: {settings.WHISPER_API_URL}")
    except Exception as e:
        results['api_health'] = False
        print_result("API Health Check", False, str(e))
    
    # Test 2: API Transcription (with dummy audio)
    print("\n[2/5] Testing API Transcription...")
    try:
        import wave
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_file = wave.open(f, 'wb')
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b'\x00' * 32000)  # 1 sec silence
            wav_file.close()
            temp_path = Path(f.name)
        
        result = client.transcribe_file(temp_path)
        success = isinstance(result, dict) and 'text' in result
        results['api_transcribe'] = success
        print_result("API Transcription", success, f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        temp_path.unlink(missing_ok=True)
    except Exception as e:
        results['api_transcribe'] = False
        print_result("API Transcription", False, str(e))
    
    # Test 3: Hybrid Client Initialization
    print("\n[3/5] Testing Hybrid Client (API + Local)...")
    try:
        hybrid = HybridWhisperClient(
            api_url=settings.WHISPER_API_URL,
            local_model="base",  # Fast for testing
            local_device="cpu",
            api_timeout=settings.WHISPER_API_TIMEOUT
        )
        results['hybrid_init'] = True
        print_result("Hybrid Client Init", True, "API + Local (base/CPU)")
    except Exception as e:
        results['hybrid_init'] = False
        print_result("Hybrid Client Init", False, str(e))
    
    # Test 4: Hybrid API Mode
    print("\n[4/5] Testing Hybrid API Mode...")
    try:
        hybrid = HybridWhisperClient(
            api_url=settings.WHISPER_API_URL,
            local_model="base",
            local_device="cpu",
            api_timeout=settings.WHISPER_API_TIMEOUT
        )
        hybrid.force_api()
        
        import wave
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_file = wave.open(f, 'wb')
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b'\x00' * 16000)
            wav_file.close()
            temp_path = Path(f.name)
        
        result = hybrid.transcribe_file(temp_path)
        success = isinstance(result, dict) and 'text' in result
        results['hybrid_api_mode'] = success
        print_result("Hybrid API Mode", success, f"Using local: {hybrid._use_local}")
        temp_path.unlink(missing_ok=True)
    except Exception as e:
        results['hybrid_api_mode'] = False
        print_result("Hybrid API Mode", False, str(e))
    
    # Test 5: Hybrid Local Fallback Mode
    print("\n[5/5] Testing Hybrid Local Fallback...")
    try:
        hybrid.force_local()
        import wave
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_file = wave.open(f, 'wb')
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b'\x00' * 16000)
            wav_file.close()
            temp_path = Path(f.name)
        
        result = hybrid.transcribe_file(temp_path)
        success = isinstance(result, dict) and 'text' in result
        results['hybrid_local_mode'] = success
        print_result("Hybrid Local Fallback", success, f"Using local: {hybrid._use_local}")
        temp_path.unlink(missing_ok=True)
    except Exception as e:
        results['hybrid_local_mode'] = False
        print_result("Hybrid Local Fallback", False, str(e))
    
    return results


def test_gradio_tts():
    """Test Gradio TTS (Audio8-TTS) with fallback."""
    print_header("GRADIO TTS TESTS (Audio8-TTS + Edge Fallback)")
    
    results = {}
    
    # Test 1: Gradio Client Connection
    print("\n[1/5] Testing Gradio TTS Connection...")
    try:
        client = GradioTTSClient(
            space_url=settings.GRADIO_TTS_URL,
            api_name=settings.GRADIO_TTS_API_NAME,
            timeout=settings.GRADIO_TTS_TIMEOUT
        )
        results['gradio_connect'] = True
        print_result("Gradio Connection", True, f"URL: {settings.GRADIO_TTS_URL}")
    except Exception as e:
        results['gradio_connect'] = False
        print_result("Gradio Connection", False, str(e))
        return results  # Can't continue if connection fails
    
    # Test 2: Gradio Health Check
    print("\n[2/5] Testing Gradio Health Check...")
    try:
        healthy = client.health_check()
        results['gradio_health'] = healthy
        print_result("Gradio Health Check", healthy, "Space reachable" if healthy else "Space sleeping/unreachable")
    except Exception as e:
        results['gradio_health'] = False
        print_result("Gradio Health Check", False, str(e))
    
    # Test 3: Gradio Synthesis
    print("\n[3/5] Testing Gradio Synthesis...")
    try:
        audio_bytes = client.synthesize("Hello! This is a test of the Audio8 TTS model.")
        success = isinstance(audio_bytes, bytes) and len(audio_bytes) > 1000
        results['gradio_synthesize'] = success
        print_result("Gradio Synthesis", success, f"Generated {len(audio_bytes)} bytes")
        
        # Save for manual verification
        output_path = Path("test_gradio_audio.wav")
        output_path.write_bytes(audio_bytes)
        print(f"         Saved to: {output_path.absolute()}")
    except Exception as e:
        results['gradio_synthesize'] = False
        print_result("Gradio Synthesis", False, str(e))
    
    # Test 4: Hybrid TTS (Gradio + Edge fallback)
    print("\n[4/5] Testing Hybrid TTS (Gradio + Edge Fallback)...")
    try:
        hybrid = create_gradio_tts(
            space_url=settings.GRADIO_TTS_URL,
            api_name=settings.GRADIO_TTS_API_NAME,
            fallback="edge"
        )
        results['hybrid_init'] = True
        print_result("Hybrid TTS Init", True, "Gradio primary + Edge fallback")
    except Exception as e:
        results['hybrid_init'] = False
        print_result("Hybrid TTS Init", False, str(e))
        return results
    
    # Test 5: Hybrid Primary Mode
    print("\n[5/5] Testing Hybrid Primary (Gradio) Mode...")
    try:
        audio_bytes = hybrid.synthesize("Testing primary Gradio TTS.")
        success = isinstance(audio_bytes, bytes) and len(audio_bytes) > 1000
        results['hybrid_primary'] = success
        print_result("Hybrid Primary Mode", success, f"Generated {len(audio_bytes)} bytes")
    except Exception as e:
        results['hybrid_primary'] = False
        print_result("Hybrid Primary Mode", False, str(e))
    
    # Test 6: Hybrid Fallback Mode
    print("\n[6/6] Testing Hybrid Fallback (Edge TTS) Mode...")
    try:
        hybrid.force_fallback()
        audio_bytes = hybrid.synthesize("Testing fallback Edge TTS.")
        success = isinstance(audio_bytes, bytes) and len(audio_bytes) > 1000
        results['hybrid_fallback'] = success
        print_result("Hybrid Fallback Mode", success, f"Generated {len(audio_bytes)} bytes")
        hybrid.force_primary()  # Reset
    except Exception as e:
        results['hybrid_fallback'] = False
        print_result("Hybrid Fallback Mode", False, str(e))
    
    return results


def test_voice_pipeline_integration():
    """Test full VoicePipeline integration."""
    print_header("VOICEPIPELINE INTEGRATION TEST")
    
    results = {}
    
    print("\n[1/3] Testing VoicePipeline with Gradio TTS...")
    try:
        pipeline = VoicePipeline(tts_provider="gradio")
        results['pipeline_init'] = True
        print_result("Pipeline Init", True, f"TTS: {type(pipeline.tts).__name__}, STT: {type(pipeline.stt).__name__}")
    except Exception as e:
        results['pipeline_init'] = False
        print_result("Pipeline Init", False, str(e))
        return results
    
    print("\n[2/3] Testing speak_question()...")
    try:
        audio = pipeline.speak_question("Walk me through your authentication implementation.")
        success = isinstance(audio, bytes) and len(audio) > 1000
        results['speak_question'] = success
        print_result("speak_question()", success, f"Generated {len(audio)} bytes")
        
        # Save
        Path("test_pipeline_question.wav").write_bytes(audio)
    except Exception as e:
        results['speak_question'] = False
        print_result("speak_question()", False, str(e))
    
    print("\n[3/3] Testing speak_intro()...")
    try:
        audio = pipeline.speak_intro("Welcome to your ProofSkill AI viva session.")
        success = isinstance(audio, bytes) and len(audio) > 1000
        results['speak_intro'] = success
        print_result("speak_intro()", success, f"Generated {len(audio)} bytes")
        
        # Save
        Path("test_pipeline_intro.wav").write_bytes(audio)
    except Exception as e:
        results['speak_intro'] = False
        print_result("speak_intro()", False, str(e))
    
    return results


def test_end_to_end_viva():
    """Test end-to-end viva flow simulation."""
    print_header("END-TO-END VIVA SIMULATION")
    
    results = {}
    
    print("\n[1/4] Simulating AI Question → TTS...")
    try:
        pipeline = VoicePipeline(tts_provider="gradio")
        question = "In your ecommerce-api repository, walk me through the JWT verification function in api/auth.py"
        audio = pipeline.speak_question(question)
        success = isinstance(audio, bytes) and len(audio) > 1000
        results['tts_question'] = success
        print_result("TTS Question Generation", success, f"Audio: {len(audio)} bytes")
    except Exception as e:
        results['tts_question'] = False
        print_result("TTS Question Generation", False, str(e))
    
    print("\n[2/4] Simulating Candidate Answer → STT...")
    try:
        hybrid_stt = HybridWhisperClient(
            api_url=settings.WHISPER_API_URL,
            local_model="base",
            local_device="cpu",
            api_timeout=settings.WHISPER_API_TIMEOUT
        )
        hybrid_stt.force_local()  # Use local for consistent testing
        
        # Create test audio (silence)
        import wave
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_file = wave.open(f, 'wb')
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b'\x00' * 48000)  # 3 sec silence
            wav_file.close()
            temp_path = Path(f.name)
        
        result = hybrid_stt.transcribe_file(temp_path)
        success = isinstance(result, dict) and 'text' in result
        results['stt_answer'] = success
        print_result("STT Answer Transcription", success, f"Result: '{result.get('text', '')[:50]}'")
        temp_path.unlink(missing_ok=True)
    except Exception as e:
        results['stt_answer'] = False
        print_result("STT Answer Transcription", False, str(e))
    
    print("\n[3/4] Simulating Full Pipeline Round-trip...")
    try:
        # TTS: AI speaks question
        pipeline = VoicePipeline(tts_provider="gradio")
        question_audio = pipeline.speak_question("What is your experience with FastAPI?")
        
        # STT: Transcribe (simulated candidate answer)
        hybrid_stt = HybridWhisperClient(
            api_url=settings.WHISPER_API_URL,
            local_model="base",
            local_device="cpu",
            api_timeout=settings.WHISPER_API_TIMEOUT
        )
        hybrid_stt.force_local()
        
        # Use the same audio for STT test (round-trip)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(question_audio)
            temp_path = Path(f.name)
        
        transcription = hybrid_stt.transcribe_file(temp_path)
        success = isinstance(transcription, dict) and 'text' in transcription
        results['roundtrip'] = success
        print_result("TTS→STT Round-trip", success, f"Transcribed: '{transcription.get('text', '')[:50]}'")
        temp_path.unlink(missing_ok=True)
    except Exception as e:
        results['roundtrip'] = False
        print_result("TTS→STT Round-trip", False, str(e))
    
    print("\n[4/4] Testing Fallback Chain...")
    try:
        # Test TTS fallback chain
        hybrid_tts = create_gradio_tts(
            space_url=settings.GRADIO_TTS_URL,
            api_name=settings.GRADIO_TTS_API_NAME,
            fallback="edge"
        )
        
        # Primary
        _ = hybrid_tts.synthesize("Primary test")
        
        # Force fallback
        hybrid_tts.force_fallback()
        _ = hybrid_tts.synthesize("Fallback test")
        hybrid_tts.force_primary()
        
        # STT fallback
        hybrid_stt = HybridWhisperClient(
            api_url=settings.WHISPER_API_URL,
            local_model="base",
            local_device="cpu",
            api_timeout=settings.WHISPER_API_TIMEOUT
        )
        hybrid_stt.force_api()
        _ = hybrid_stt.force_local()  # Test switching
        
        results['fallback_chain'] = True
        print_result("Fallback Chain", True, "TTS (Gradio→Edge) + STT (API→Local) working")
    except Exception as e:
        results['fallback_chain'] = False
        print_result("Fallback Chain", False, str(e))
    
    return results


def print_summary(all_results):
    """Print final summary."""
    print_header("FINAL TEST SUMMARY")
    
    total = 0
    passed = 0
    
    for category, tests in all_results.items():
        cat_passed = sum(1 for v in tests.values() if v)
        cat_total = len(tests)
        total += cat_total
        passed += cat_passed
        
        pct = (cat_passed / cat_total * 100) if cat_total > 0 else 0
        status = "✅" if pct == 100 else "⚠️" if pct >= 50 else "❌"
        print(f"\n  {status} {category}: {cat_passed}/{cat_total} ({pct:.0f}%)")
        
        for test_name, result in tests.items():
            icon = "✅" if result else "❌"
            print(f"      {icon} {test_name}")
    
    overall_pct = (passed / total * 100) if total > 0 else 0
    print(f"\n  {'='*40}")
    overall_status = "✅ ALL PASS" if overall_pct == 100 else "⚠️ PARTIAL" if overall_pct >= 70 else "❌ NEEDS FIXES"
    print(f"  {overall_status} | Overall: {passed}/{total} ({overall_pct:.0f}%)")
    print(f"  {'='*40}")
    
    return overall_pct == 100


def main():
    print_header("PROOFSKILL AI - DUAL MODEL INTEGRATION TEST")
    print(f"  Whisper API: {settings.WHISPER_API_URL}")
    print(f"  Gradio TTS:  {settings.GRADIO_TTS_URL}")
    print(f"  TTS API:     {settings.GRADIO_TTS_API_NAME}")
    
    # Check dependencies
    print("\n[0] Checking Dependencies...")
    deps = {
        'gradio_client': False,
        'edge_tts': False,
        'whisper': False,
        'llama_cpp': False
    }
    try:
        import gradio_client; deps['gradio_client'] = True
    except: pass
    try:
        import edge_tts; deps['edge_tts'] = True
    except: pass
    try:
        import whisper; deps['whisper'] = True
    except: pass
    try:
        import llama_cpp; deps['llama_cpp'] = True
    except: pass
    
    for dep, installed in deps.items():
        print_result(f"Dependency: {dep}", installed, "Install via pip" if not installed else "")
    
    if not deps['gradio_client']:
        print("\n❌ CRITICAL: gradio_client not installed!")
        print("   Run: pip install gradio_client")
        return
    
    if not deps['whisper']:
        print("\n❌ CRITICAL: whisper not installed!")
        print("   Run: pip install openai-whisper")
        return
    
    # Run all tests
    all_results = {}
    
    all_results['Whisper STT'] = test_whisper_api()
    all_results['Gradio TTS'] = test_gradio_tts()
    all_results['VoicePipeline'] = test_voice_pipeline_integration()
    all_results['E2E Viva Flow'] = test_end_to_end_viva()
    
    # Final summary
    all_passed = print_summary(all_results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Ready for hackathon!")
    else:
        print("\n⚠️  Some tests failed. Check output above.")
        print("\nCommon fixes:")
        print("  - Whisper API: Check if Colab tunnel URL is current in .env")
        print("  - Gradio TTS:  Wake up HF Space (visit URL), verify API name")
        print("  - Fallbacks:   Ensure edge-tts installed for TTS fallback")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)