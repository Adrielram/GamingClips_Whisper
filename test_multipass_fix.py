# Test script to verify multipass transcription fix
import os
import sys

# Change to the project directory
os.chdir(r"d:\Ingenieria\GameClipping")

try:
    # Import the multipass transcriber
    from transcribe_multipass import MultipassTranscriber
    
    print("✅ Successfully imported MultipassTranscriber")
    
    # Create transcriber instance
    transcriber = MultipassTranscriber(
        model_name="large-v3",
        device="cuda",
        compute_type="float16"
    )
    
    print("✅ Successfully created MultipassTranscriber instance")
    print(f"   Model: {transcriber.model_name}")
    print(f"   Device: {transcriber.device}")
    print(f"   Compute type: {transcriber.compute_type}")
    print(f"   Model loaded: {transcriber.model is not None}")
    
    # Test model loading
    print("\n🔄 Testing model loading...")
    transcriber.load_model()
    
    print(f"✅ Model successfully loaded: {transcriber.model is not None}")
    
    if transcriber.model is not None:
        print("✅ MultipassTranscriber fix successful!")
        print("   The model will now be available for transcription")
    else:
        print("❌ Model loading failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()