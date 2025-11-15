"""
Real-Time Meeting Transcription Service
Combines audio capture, VAD, speaker detection, and Groq Whisper transcription
"""
import asyncio
import threading
import numpy as np
from typing import Optional, Callable
from datetime import datetime
import os

from audio_capture import AudioCaptureDevice
from vad_handler import StreamingVAD
from groq_transcriber import GroqTranscriber, TranscriptionBuffer
from speaker_detector import SpeakerDetector
from playwright.async_api import Page


class TranscriptionService:
    """
    Real-time meeting transcription service
    Captures audio, detects speech, identifies speakers, and transcribes
    """

    def __init__(
        self,
        page: Optional[Page] = None,
        meeting_type: str = "google_meet",
        audio_device: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        sample_rate: int = 16000,
        vad_threshold: float = 0.5,
        min_speech_duration: float = 1.0,
        output_callback: Optional[Callable] = None
    ):
        """
        Initialize Transcription Service

        Args:
            page: Playwright page object (for speaker detection)
            meeting_type: 'google_meet' or 'teams'
            audio_device: Audio input device name (e.g., 'CABLE Output')
            groq_api_key: Groq API key
            sample_rate: Audio sample rate (16000 Hz recommended)
            vad_threshold: VAD confidence threshold (0.0 to 1.0)
            min_speech_duration: Minimum speech duration in seconds
            output_callback: Callback function for transcription output
        """
        # Configuration
        self.page = page
        self.meeting_type = meeting_type
        self.sample_rate = sample_rate
        self.min_speech_duration = min_speech_duration
        self.output_callback = output_callback

        # Components
        self.audio_capture = None
        self.vad = None
        self.transcriber = None
        self.speaker_detector = None
        self.transcription_buffer = TranscriptionBuffer(max_history=500)

        # State
        self.is_running = False
        self.processing_thread = None
        self.current_speaker = "Unknown"

        # Initialize components
        self._initialize_components(audio_device, groq_api_key, vad_threshold)

    def _initialize_components(self, audio_device: Optional[str], groq_api_key: Optional[str], vad_threshold: float):
        """Initialize all service components"""
        try:
            print("\n" + "=" * 80)
            print("Initializing Transcription Service Components")
            print("=" * 80)

            # 1. Initialize Audio Capture
            print("\n[1/4] Initializing Audio Capture...")
            self.audio_capture = AudioCaptureDevice(
                device_name=audio_device,
                sample_rate=self.sample_rate,
                channels=1,
                chunk_duration_ms=30
            )
            print("✓ Audio capture initialized")

            # 2. Initialize VAD
            print("\n[2/4] Initializing Voice Activity Detection (Silero VAD)...")
            self.vad = StreamingVAD(
                sample_rate=self.sample_rate,
                threshold=vad_threshold
            )
            print("✓ VAD initialized")

            # 3. Initialize Groq Transcriber
            print("\n[3/4] Initializing Groq Whisper Transcriber...")
            self.transcriber = GroqTranscriber(
                api_key=groq_api_key,
                model="whisper-large-v3-turbo",
                language="en",
                temperature=0.0
            )
            print("✓ Groq Transcriber initialized")

            # 4. Initialize Speaker Detector (if page available)
            print("\n[4/4] Initializing Speaker Detector...")
            if self.page:
                self.speaker_detector = SpeakerDetector(
                    page=self.page,
                    meeting_type=self.meeting_type
                )
                print("✓ Speaker Detector initialized")
            else:
                print("⚠ Speaker Detector not initialized (no Playwright page provided)")
                print("  Speaker names will not be available")

            print("\n" + "=" * 80)
            print("✓ All components initialized successfully!")
            print("=" * 80 + "\n")

        except Exception as e:
            print(f"\n✗ Error initializing components: {e}")
            raise

    def _process_audio_chunk(self, audio_chunk: np.ndarray):
        """
        Process single audio chunk through VAD

        Args:
            audio_chunk: Audio data
        """
        # Process through VAD
        speech_segment = self.vad.process_chunk(audio_chunk)

        # If we have a complete speech segment, transcribe it
        if speech_segment is not None:
            # Check minimum duration
            duration = len(speech_segment) / self.sample_rate

            if duration >= self.min_speech_duration:
                # Transcribe in separate thread to avoid blocking
                threading.Thread(
                    target=self._transcribe_segment,
                    args=(speech_segment,),
                    daemon=True
                ).start()

    def _transcribe_segment(self, audio_segment: np.ndarray):
        """
        Transcribe audio segment

        Args:
            audio_segment: Audio data to transcribe
        """
        try:
            # Transcribe using Groq Whisper
            result = self.transcriber.transcribe_numpy(
                audio_segment,
                sample_rate=self.sample_rate
            )

            # Get transcribed text
            text = result.get('text', '').strip()

            if text:
                # Get current speaker (using last known speaker)
                speaker = self.current_speaker

                # Add to buffer
                self.transcription_buffer.add(text, speaker=speaker, metadata=result)

                # Format output
                timestamp = datetime.now().strftime("%H:%M:%S")
                output = f"[{timestamp}] {speaker}: {text}"

                # Print to console
                print("\n" + "=" * 80)
                print(output)
                print("=" * 80 + "\n")

                # Call output callback if provided
                if self.output_callback:
                    self.output_callback({
                        'timestamp': timestamp,
                        'speaker': speaker,
                        'text': text,
                        'metadata': result
                    })

        except Exception as e:
            print(f"Error transcribing segment: {e}")

    async def _update_speaker_loop(self):
        """Continuously update current speaker"""
        if not self.speaker_detector:
            return

        try:
            while self.is_running:
                # Get active speaker
                speaker = await self.speaker_detector.get_active_speaker()

                if speaker and speaker != "Unknown":
                    self.current_speaker = speaker

                # Update every 500ms
                await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Error in speaker update loop: {e}")

    def start(self):
        """Start transcription service"""
        try:
            print("\n" + "=" * 80)
            print("Starting Real-Time Transcription Service")
            print("=" * 80)

            self.is_running = True

            # Start audio capture
            self.audio_capture.start_recording()

            # Start processing thread
            self.processing_thread = threading.Thread(
                target=self._audio_processing_loop,
                daemon=True
            )
            self.processing_thread.start()

            print("\n✓ Transcription service started!")
            print("  Listening for speech...")
            print("  Transcriptions will appear below:")
            print("=" * 80 + "\n")

        except Exception as e:
            print(f"Error starting transcription service: {e}")
            self.is_running = False
            raise

    def _audio_processing_loop(self):
        """Main audio processing loop (runs in separate thread)"""
        try:
            while self.is_running:
                # Get audio chunk
                audio_chunk = self.audio_capture.get_audio_chunk(timeout=1.0)

                if audio_chunk is not None:
                    # Process through VAD and transcription
                    self._process_audio_chunk(audio_chunk)

        except Exception as e:
            print(f"Error in audio processing loop: {e}")

    def stop(self):
        """Stop transcription service"""
        try:
            print("\n" + "=" * 80)
            print("Stopping Transcription Service")
            print("=" * 80)

            self.is_running = False

            # Stop audio capture
            if self.audio_capture:
                self.audio_capture.stop_recording()

            # Wait for processing thread
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=2.0)

            print("\n✓ Transcription service stopped")
            print("=" * 80 + "\n")

            # Print summary
            self.print_summary()

        except Exception as e:
            print(f"Error stopping transcription service: {e}")

    def print_summary(self):
        """Print transcription summary"""
        print("\n" + "=" * 80)
        print("Transcription Summary")
        print("=" * 80)

        transcriptions = self.transcription_buffer.get_all()

        if not transcriptions:
            print("No transcriptions recorded.")
        else:
            print(f"Total transcriptions: {len(transcriptions)}\n")

            # Show all transcriptions
            for entry in transcriptions:
                print(self.transcription_buffer.format_output(entry))

        print("=" * 80 + "\n")

    def get_transcriptions(self):
        """Get all transcriptions"""
        return self.transcription_buffer.get_all()

    def save_transcriptions(self, filename: str):
        """
        Save transcriptions to file

        Args:
            filename: Output filename
        """
        try:
            transcriptions = self.transcription_buffer.get_all()

            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Meeting Transcription\n")
                f.write("=" * 80 + "\n\n")

                for entry in transcriptions:
                    f.write(self.transcription_buffer.format_output(entry) + "\n")

            print(f"✓ Transcriptions saved to: {filename}")

        except Exception as e:
            print(f"Error saving transcriptions: {e}")


async def start_transcription_with_speaker_tracking(
    service: TranscriptionService,
    duration: Optional[int] = None
):
    """
    Start transcription service with speaker tracking

    Args:
        service: TranscriptionService instance
        duration: Duration to run (seconds), None for indefinite
    """
    try:
        # Start transcription service
        service.start()

        # Start speaker tracking loop
        speaker_task = asyncio.create_task(service._update_speaker_loop())

        # Run for specified duration or until interrupted
        if duration:
            await asyncio.sleep(duration)
        else:
            # Run indefinitely
            await speaker_task

    except KeyboardInterrupt:
        print("\nTranscription interrupted by user")
    finally:
        service.stop()


if __name__ == "__main__":
    # Test transcription service
    print("Real-Time Transcription Service - Test")
    print("=" * 80)
    print("\nTo test this service, you need to:")
    print("1. Set GROQ_API_KEY environment variable")
    print("2. Have a virtual audio device configured (VB-Cable, VAC, etc.)")
    print("3. Optionally provide a Playwright page object for speaker detection")
    print("\nExample usage:")
    print("  export GROQ_API_KEY='your-api-key'")
    print("  python transcription_service.py")
    print()

    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY not set!")
    else:
        # Test without Playwright page (no speaker detection)
        print("Starting test transcription (5 seconds)...")

        service = TranscriptionService(
            page=None,
            meeting_type="google_meet",
            audio_device=None,  # Use default device
            groq_api_key=None   # Will use GROQ_API_KEY env var
        )

        # Run for 5 seconds
        import time
        service.start()
        time.sleep(5)
        service.stop()
