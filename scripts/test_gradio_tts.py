#!/usr/bin/env python
"""
Test script for Gradio TTS integration.
Run with: python scripts/test_gradio_tts.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.gradio_tts_client import GradioTTSClient, create_gradio_tts
from src.config.settings import settings


def test_gradio_tts():
    """Test the Gradio TTS client directly."""
    print("=" * 50)
    print("Testing Gradio TTS Client (Audio8-TTS)")
    print("=" * 50)
    
    print(f"\n1. Connecting to {settings.GRADIO_TTS_URL}...")
    try:
        client = GradioTTSClient(
            space_url=settings.GRADIO_TTS_URL,
            api_name=settings.GRADIO_TTS_API_NAME,
            timeout=settings.GRADIO_TTS_TIMEOUT
        )
        print("✅ Gradio client connected")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("\n⚠️  Make sure:")
        print("   1. Your HF Space is running (not sleeping)")
        print("   2. The URL is correct in .env")
        print("   3. pip install gradio_client")
        return False
    
    # Health check
    print("\n2. Health check...")
    try:
        healthy = client.health_check()
        print(f"   Space reachable: {healthy}")
    except Exception as e:
        print(f"   Health check error: {e}")
        healthy = False
    
    # Test synthesis
    print("\n3. Testing synthesis...")
    test_texts = [
        "Hello! This is a test of the Audio8 TTS model.",
        "Welcome to your ProofSkill AI viva session.",
    ]
    
    for i, text in enumerate(test_texts):
        print(f"\n   Test {i+1}: '{text[:50]}...'")
        try:
            audio_bytes = client.synthesize(text)
            print(f"   ✅ Generated {len(audio_bytes)} bytes")
            
            # Save for verification
            output_path = Path(f"test_output_{i+1}.wav")
            output_path.write_bytes(audio_bytes)
            print(f"   💾 Saved to {output_path}")
            
        except Exception as e:
            print(f"   ❌ Synthesis failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n4. Testing model info...")
    try:
        info = client.get_model_info()
        print(f"   Model API info retrieved")
    except Exception as e:
        print(f"   Could not get model info: {e}")
    
    return True


def test_hybrid_tts():
    """Test the hybrid TTS with fallback."""
    print("\n" + "=" * 50)
    print("Testing Hybrid TTS (Gradio + Edge fallback)")
    print("=" * 50)
    
    try:
        hybrid = create_gradio_tts(
            space_url=settings.GRADIO_TTS_URL,
            api_name=settings.GRADIO_TTS_API_NAME,
            fallback="edge"
        )
        print("✅ Hybrid TTS created")
        
        # Test synthesis
        print("\n1. Testing hybrid synthesis...")
        audio_bytes = hybrid.primary.synthesize("Hello from hybrid TTS!")
        print(f"   ✅ Generated {len(audio_bytes)} bytes via primary")
        
        # Test fallback
        print("\n2. Testing fallback...")
        hybrid.force_fallback()
        audio_bytes = hybrid.synthesize("This uses fallback TTS.")
        print(f"   ✅ Generated {len(audio_bytes)} bytes via fallback")
        
        # Reset
        hybrid.force_primary()
        print("   ✅ Reset to primary")
        
    except Exception as e:
        print(f"❌ Hybrid test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_voice_pipeline():
    """Test VoicePipeline with Gradio TTS."""
    print("\n" + "=" * 50)
    print("Testing VoicePipeline with Gradio TTS")
    print("=" * 50)
    
    from src.services.voice_pipeline import VoicePipeline
    
    try:
        # Test with gradio provider
        pipeline = VoicePipeline(tts_provider="gradio")
        print("✅ VoicePipeline initialized with Gradio TTS")
        print(f"   TTS Provider: {pipeline.tts_provider}")
        print(f"   TTS Client: {type(pipeline.tts).__name__}")
        print(f"   Available: {pipeline.is_available()}")
        
        # Test synthesis
        print("\n1. Testing speak_question...")
        audio = pipeline.speak_question("This is a test question from the AI interviewer.")
        print(f"   ✅ Generated {len(audio)} bytes")
        
        print("\n2. Testing speak_intro...")
        audio = pipeline.speak_intro("Welcome to your viva session.")
        print(f"   ✅ Generated {len(audio)} bytes")
        
    except Exception as e:
        print(f"❌ VoicePipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    print("🎯 ProofSkill AI - Gradio TTS Integration Test")
    print(f"   Space URL: {settings.GRADIO_TTS_URL}")
    print(f"   API Name: {settings.GRADIO_TTS_API_NAME}")
    
    # Check if gradio_client is installed
    try:
        import gradio_client
        print(f"✅ gradio_client version: {gradio_client.__version__}")
    except ImportError:
        print("❌ gradio_client not installed")
        print("   Run: pip install gradio_client")
        return
    
    # Run tests
    gradio_ok = test_gradio_tts()
    hybrid_ok = test_hybrid_tts()
    pipeline_ok = test_voice_pipeline()
    
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Gradio TTS: {'✅' if gradio_ok else '❌'}")
    print(f"  Hybrid TTS: {'✅' if hybrid_ok else '❌'}")
    print(f"  VoicePipeline: {'✅' if pipeline_ok else '❌'}")
    print("=" * 50)
    
    if not gradio_ok:
        print("\n⚠️  Troubleshooting:")
        print("   1. Check if your HF Space is awake (not sleeping)")
        print("   2. Verify the URL in .env: GRADIO_TTS_URL")
        print("   3. Check the API name: GRADIO_TTS_API_NAME (usually /predict)")
        print("   4. Make sure the Space allows API access")


if __name__ == "__main__":
    main()