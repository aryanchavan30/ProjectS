"""
Component Testing Script
Tests each component individually to identify issues
"""
import sys
import os
import numpy as np
import sounddevice as sd

print("=" * 80)
print("COMPONENT DIAGNOSTIC TEST")
print("=" * 80)

# Test 1: List Audio Devices
print("\n[TEST 1] Audio Devices")
print("-" * 80)
try:
    devices = sd.query_devices()
    default_input = sd.query_devices(kind='input')

    print(f"✓ Default Input Device: {default_input['name']}")
    print(f"\nAll Input Devices:")

    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"  [{idx}] {device['name']}")
            print(f"      Channels: {device['max_input_channels']}")
            print(f"      Sample Rate: {device['default_samplerate']} Hz")

    print("\n✓ Audio device enumeration works")
except Exception as e:
    print(f"✗ Audio device test failed: {e}")
    sys.exit(1)

# Test 2: Capture Audio
print("\n[TEST 2] Audio Capture (5 seconds)")
print("-" * 80)
print("Speak into your microphone NOW...")

try:
    # Record 5 seconds
    duration = 5
    sample_rate = 16000

    print(f"Recording {duration} seconds at {sample_rate} Hz...")
    audio_data = sd.rec(int(duration * sample_rate),
                       samplerate=sample_rate,
                       channels=1,
                       dtype=np.float32)
    sd.wait()

    # Analyze the recording
    audio_level = np.abs(audio_data).max()
    audio_rms = np.sqrt(np.mean(audio_data**2))

    print(f"✓ Recording complete")
    print(f"  Audio peak level: {audio_level:.4f}")
    print(f"  Audio RMS level: {audio_rms:.4f}")

    if audio_level < 0.001:
        print("\n⚠ WARNING: Audio level is very low!")
        print("  Possible issues:")
        print("  - Microphone is muted")
        print("  - Wrong input device selected")
        print("  - Microphone not connected")
    elif audio_level > 0.01:
        print("✓ Good audio level detected!")
    else:
        print("⚠ Audio level is low but detectable")

except Exception as e:
    print(f"✗ Audio capture failed: {e}")
    sys.exit(1)

# Test 3: VAD (Silero)
print("\n[TEST 3] Voice Activity Detection (Silero VAD)")
print("-" * 80)

try:
    import torch

    # Load VAD model
    print("Loading Silero VAD model...")
    model, utils = torch.hub.load(
        repo_or_dir='snakers4/silero-vad',
        model='silero_vad',
        force_reload=False,
        onnx=False
    )

    print("✓ VAD model loaded")

    # Test VAD on recorded audio
    # Take 512 sample chunks and test
    chunk_size = 512
    num_chunks = len(audio_data) // chunk_size
    speech_detected_count = 0

    print(f"\nTesting VAD on {num_chunks} chunks...")

    for i in range(min(num_chunks, 20)):  # Test first 20 chunks
        chunk = audio_data[i*chunk_size:(i+1)*chunk_size].flatten()

        # Ensure exactly 512 samples
        if len(chunk) == 512:
            chunk_tensor = torch.from_numpy(chunk.astype(np.float32))
            confidence = model(chunk_tensor, sample_rate).item()

            if confidence > 0.3:
                speech_detected_count += 1
                print(f"  Chunk {i}: Speech detected! (confidence: {confidence:.3f})")

    print(f"\n✓ VAD test complete")
    print(f"  Speech detected in {speech_detected_count}/{min(num_chunks, 20)} chunks")

    if speech_detected_count == 0:
        print("\n⚠ WARNING: No speech detected by VAD!")
        print("  Possible issues:")
        print("  - You didn't speak during recording")
        print("  - Audio level too low")
        print("  - Background noise only")
        print("  - VAD threshold too high")
    else:
        print("✓ VAD is detecting speech!")

except Exception as e:
    print(f"✗ VAD test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Groq API
print("\n[TEST 4] Groq Whisper API")
print("-" * 80)

try:
    groq_key = os.getenv("GROQ_API_KEY")

    if not groq_key:
        print("✗ GROQ_API_KEY not set!")
        print("  Set it with: $env:GROQ_API_KEY='your-key-here'")
    else:
        print(f"✓ GROQ_API_KEY is set: {groq_key[:10]}...")

        from groq import Groq

        client = Groq(api_key=groq_key)
        print("✓ Groq client initialized")

        # Try to transcribe a small portion of our recording
        if audio_level > 0.001:
            print("\nAttempting to transcribe recorded audio...")

            # Take first 3 seconds of audio
            import io
            import wave
            import tempfile

            test_audio = audio_data[:3*sample_rate].flatten()

            # Normalize
            if test_audio.max() > 1.0 or test_audio.min() < -1.0:
                test_audio = test_audio / np.abs(test_audio).max()

            # Convert to int16
            audio_int16 = (test_audio * 32767).astype(np.int16)

            # Save to temp WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_path = f.name

            with wave.open(temp_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())

            try:
                with open(temp_path, 'rb') as audio_file:
                    transcription = client.audio.transcriptions.create(
                        file=(temp_path, audio_file.read()),
                        model="whisper-large-v3-turbo",
                        response_format="text",
                        language="en"
                    )

                print(f"\n✓ Transcription successful!")
                print(f"  Result: \"{transcription}\"")

                if len(transcription.strip()) == 0:
                    print("\n⚠ WARNING: Empty transcription!")
                    print("  This means Whisper didn't detect any speech")

            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        else:
            print("⚠ Skipping transcription test (audio level too low)")

except Exception as e:
    print(f"✗ Groq API test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
print("\nSummary:")
print("1. Check if audio level is good (> 0.01)")
print("2. Check if VAD detected speech")
print("3. Check if Groq API is working")
print("4. If all pass but transcription doesn't work, there may be an integration issue")
print("\nRun this test while speaking into your microphone!")
