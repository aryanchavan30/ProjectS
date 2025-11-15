"""
Meeting Joiner Bot with Real-time Transcription
Supports: Google Meet and Microsoft Teams
Features: Silero VAD, Groq Whisper STT, Speaker Identification, Windows Audio Capture
"""
import asyncio
import argparse
import threading
import queue
import time
import wave
import io
import os
from datetime import datetime
from typing import Optional, Dict
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Audio capture and processing
try:
    import pyaudiowpatch as pyaudio
except ImportError:
    import pyaudio
    print("Warning: PyAudioWPatch not found. Using standard PyAudio (Windows loopback may not work)")

import numpy as np
import torch
from groq import Groq


class AudioTranscriber:
    """Handles audio capture, VAD, and transcription using Groq Whisper"""

    def __init__(self, groq_api_key: str, output_file: str = "transcription.txt"):
        """
        Initialize the Audio Transcriber

        Args:
            groq_api_key: Groq API key for Whisper
            output_file: File to save transcriptions
        """
        self.groq_api_key = groq_api_key
        self.output_file = output_file
        self.groq_client = Groq(api_key=groq_api_key)

        # Audio settings
        self.CHUNK = 512  # Frames per buffer
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1  # Mono
        self.RATE = 16000  # 16kHz for Silero VAD

        # VAD settings
        self.vad_model = None
        self.vad_threshold = 0.5
        self.speech_pad_ms = 300  # Padding before/after speech

        # Audio buffer
        self.audio_queue = queue.Queue()
        self.current_speaker = "Unknown"
        self.is_recording = False
        self.audio_thread = None

        # Load Silero VAD
        self._load_vad_model()

    def _load_vad_model(self):
        """Load Silero VAD model"""
        try:
            print("Loading Silero VAD model...")
            self.vad_model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            self.get_speech_timestamps = utils[0]
            print("✓ Silero VAD model loaded successfully")
        except Exception as e:
            print(f"Error loading Silero VAD: {e}")
            print("Install torch: pip install torch torchaudio")

    def _get_default_loopback_device(self):
        """Get default Windows WASAPI loopback device for capturing system audio"""
        p = pyaudio.PyAudio()
        try:
            # Try to get WASAPI loopback (Windows only)
            if hasattr(p, 'get_default_wasapi_loopback'):
                device_info = p.get_default_wasapi_loopback()
                print(f"✓ Using WASAPI loopback device: {device_info['name']}")
                return device_info
            else:
                # Fallback to default input device
                print("Warning: WASAPI loopback not available. Using default input device.")
                print("Install PyAudioWPatch for Windows speaker audio: pip install PyAudioWPatch")
                default_device = p.get_default_input_device_info()
                return default_device
        except Exception as e:
            print(f"Error getting audio device: {e}")
            return None
        finally:
            p.terminate()

    def detect_speech(self, audio_chunk: np.ndarray) -> bool:
        """
        Use Silero VAD to detect if audio contains speech

        Args:
            audio_chunk: Audio data as numpy array

        Returns:
            True if speech detected, False otherwise
        """
        if self.vad_model is None:
            return True  # If VAD not loaded, assume all audio is speech

        try:
            # Convert to torch tensor
            audio_tensor = torch.from_numpy(audio_chunk).float()

            # Normalize to [-1, 1]
            if audio_tensor.abs().max() > 0:
                audio_tensor = audio_tensor / 32768.0

            # Get speech probability
            speech_prob = self.vad_model(audio_tensor, self.RATE).item()

            return speech_prob > self.vad_threshold
        except Exception as e:
            print(f"VAD error: {e}")
            return True  # On error, assume speech

    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio using Groq Whisper

        Args:
            audio_data: Raw audio bytes

        Returns:
            Transcribed text or None
        """
        try:
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(self.CHANNELS)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.RATE)
                wav_file.writeframes(audio_data)

            wav_buffer.seek(0)
            wav_buffer.name = "audio.wav"  # Required for Groq API

            # Call Groq Whisper API
            transcription = self.groq_client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=wav_buffer,
                response_format="text",
                language="en"
            )

            return transcription.strip() if transcription else None

        except Exception as e:
            print(f"Transcription error: {e}")
            return None

    def save_transcription(self, speaker: str, text: str):
        """Save transcription to file with timestamp and speaker"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {speaker}: {text}\n"

        print(f"\n{entry.strip()}")

        try:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        except Exception as e:
            print(f"Error saving transcription: {e}")

    def audio_capture_loop(self):
        """Continuous audio capture and processing loop"""
        p = pyaudio.PyAudio()
        device_info = self._get_default_loopback_device()

        if device_info is None:
            print("Error: No audio device available")
            return

        try:
            # Open audio stream
            stream = p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=device_info['index'],
                frames_per_buffer=self.CHUNK
            )

            print("✓ Audio capture started")

            speech_buffer = []
            speech_frames = 0
            silence_frames = 0
            max_silence_frames = int(self.RATE / self.CHUNK * 2)  # 2 seconds of silence
            min_speech_frames = int(self.RATE / self.CHUNK * 0.5)  # 0.5 seconds minimum

            while self.is_recording:
                try:
                    # Read audio chunk
                    audio_data = stream.read(self.CHUNK, exception_on_overflow=False)
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)

                    # Check for speech using VAD
                    has_speech = self.detect_speech(audio_array)

                    if has_speech:
                        speech_buffer.append(audio_data)
                        speech_frames += 1
                        silence_frames = 0
                    else:
                        silence_frames += 1
                        if speech_frames > 0:
                            speech_buffer.append(audio_data)  # Add some silence padding

                    # If we have enough speech and then silence, process it
                    if speech_frames >= min_speech_frames and silence_frames >= max_silence_frames:
                        # Combine audio chunks
                        full_audio = b''.join(speech_buffer)

                        # Transcribe
                        text = self.transcribe_audio(full_audio)

                        if text and len(text) > 0:
                            self.save_transcription(self.current_speaker, text)

                        # Reset buffers
                        speech_buffer = []
                        speech_frames = 0
                        silence_frames = 0

                except Exception as e:
                    print(f"Audio capture error: {e}")
                    continue

        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            p.terminate()
            print("✓ Audio capture stopped")

    def start_recording(self):
        """Start audio recording in background thread"""
        if not self.is_recording:
            self.is_recording = True
            self.audio_thread = threading.Thread(target=self.audio_capture_loop, daemon=True)
            self.audio_thread.start()
            print("✓ Transcription started")

    def stop_recording(self):
        """Stop audio recording"""
        if self.is_recording:
            self.is_recording = False
            if self.audio_thread:
                self.audio_thread.join(timeout=2)
            print("✓ Transcription stopped")

    def update_speaker(self, speaker_name: str):
        """Update current speaker name"""
        if speaker_name != self.current_speaker:
            self.current_speaker = speaker_name
            print(f"→ Active speaker: {speaker_name}")


class MeetingJoiner:
    def __init__(self, meeting_url: str, display_name: str, headless: bool = False,
                 transcriber: Optional[AudioTranscriber] = None):
        """
        Initialize the Meeting Joiner

        Args:
            meeting_url: URL of the meeting (Google Meet or Microsoft Teams)
            display_name: Name to display in the meeting
            headless: Whether to run browser in headless mode (default: False)
            transcriber: AudioTranscriber instance for transcription
        """
        self.meeting_url = meeting_url
        self.display_name = display_name
        self.headless = headless
        self.meeting_type = self._detect_meeting_type()
        self.transcriber = transcriber
        self.speaker_monitor_task = None

    def _detect_meeting_type(self) -> str:
        """Detect if the meeting is Google Meet or Microsoft Teams"""
        if "meet.google.com" in self.meeting_url:
            return "google_meet"
        elif "teams.microsoft.com" in self.meeting_url or "teams.live.com" in self.meeting_url:
            return "teams"
        else:
            raise ValueError("Unsupported meeting URL. Only Google Meet and Microsoft Teams are supported.")

    async def monitor_active_speaker_google_meet(self, page):
        """Monitor active speaker in Google Meet"""
        print("Monitoring active speaker in Google Meet...")

        while True:
            try:
                await asyncio.sleep(1)  # Check every second

                # Try to find active speaker indicator
                # Google Meet highlights the active speaker's video tile
                active_speaker_selectors = [
                    '[data-self-name][data-resolution-cap]',  # Current speaker's tile
                    '[data-participant-id][aria-label]',  # Participant tiles
                ]

                for selector in active_speaker_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for element in elements:
                            # Check if this element is the active speaker
                            aria_label = await element.get_attribute('aria-label')
                            if aria_label:
                                # Extract name from aria-label
                                # Format is usually like "John Doe" or "John Doe (Host)"
                                speaker_name = aria_label.split('(')[0].strip()
                                if speaker_name and self.transcriber:
                                    self.transcriber.update_speaker(speaker_name)
                                break
                    except:
                        continue

            except asyncio.CancelledError:
                break
            except Exception as e:
                # Silently continue on errors
                continue

    async def monitor_active_speaker_teams(self, page):
        """Monitor active speaker in Microsoft Teams"""
        print("Monitoring active speaker in Teams...")

        while True:
            try:
                await asyncio.sleep(1)  # Check every second

                # Try to find active speaker in Teams
                # Teams shows active speaker name in various places
                active_speaker_selectors = [
                    '[data-tid="roster-participant-name"]',
                    '[class*="name"]',
                ]

                for selector in active_speaker_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            # Get first participant name as active speaker
                            text = await elements[0].inner_text()
                            if text and self.transcriber:
                                self.transcriber.update_speaker(text.strip())
                            break
                    except:
                        continue

            except asyncio.CancelledError:
                break
            except Exception as e:
                continue

    async def join_google_meet(self, page):
        """Join a Google Meet meeting"""
        print(f"Joining Google Meet: {self.meeting_url}")

        # Navigate to the meeting URL
        await page.goto(self.meeting_url, wait_until="networkidle")
        await asyncio.sleep(2)

        try:
            # Turn off camera and microphone
            print("Disabling camera and microphone...")

            # Wait for and click the camera button to turn it off (if it's on)
            try:
                camera_button = page.locator('div[data-is-muted="false"][aria-label*="camera" i], div[data-is-muted="false"][aria-label*="cam" i]').first
                if await camera_button.count() > 0:
                    await camera_button.click()
                    await asyncio.sleep(0.5)
            except:
                print("Camera already off or button not found")

            # Wait for and click the microphone button to turn it off (if it's on)
            try:
                mic_button = page.locator('div[data-is-muted="false"][aria-label*="microphone" i], div[data-is-muted="false"][aria-label*="mic" i]').first
                if await mic_button.count() > 0:
                    await mic_button.click()
                    await asyncio.sleep(0.5)
            except:
                print("Microphone already off or button not found")

            # Enter display name if there's a name input field
            print(f"Entering display name: {self.display_name}")
            try:
                name_input = page.locator('input[placeholder*="name" i], input[aria-label*="name" i]').first
                if await name_input.count() > 0:
                    await name_input.fill(self.display_name)
                    await asyncio.sleep(0.5)
            except:
                print("Name input field not found or not needed")

            # Click the "Ask to join" or "Join now" button
            print("Clicking join button...")
            join_button_selectors = [
                'button:has-text("Ask to join")',
                'button:has-text("Join now")',
                'button[aria-label*="Ask to join" i]',
                'button[aria-label*="Join" i]',
                'span:has-text("Ask to join")',
                'span:has-text("Join now")'
            ]

            joined = False
            for selector in join_button_selectors:
                try:
                    join_button = page.locator(selector).first
                    if await join_button.count() > 0:
                        await join_button.click()
                        joined = True
                        print("✓ Successfully clicked join button!")
                        break
                except:
                    continue

            if not joined:
                print("Warning: Could not find join button. You may need to join manually.")

            # Wait a bit to ensure we're in the meeting
            await asyncio.sleep(3)
            print("✓ Joined Google Meet successfully!")

            # Start monitoring active speaker
            if self.transcriber:
                self.speaker_monitor_task = asyncio.create_task(
                    self.monitor_active_speaker_google_meet(page)
                )

        except PlaywrightTimeoutError as e:
            print(f"Timeout error: {e}")
            print("The meeting page may require manual intervention.")
        except Exception as e:
            print(f"Error joining Google Meet: {e}")

    async def join_teams(self, page):
        """Join a Microsoft Teams meeting"""
        print(f"Joining Microsoft Teams: {self.meeting_url}")

        # Navigate to the meeting URL
        await page.goto(self.meeting_url, wait_until="networkidle")
        await asyncio.sleep(2)

        try:
            # Click "Join on the web instead" if it appears
            print("Looking for 'Join on the web' option...")
            try:
                web_join_selectors = [
                    'a:has-text("Join on the web instead")',
                    'button:has-text("Join on the web instead")',
                    'a:has-text("Continue on this browser")',
                    'button:has-text("Continue on this browser")'
                ]

                for selector in web_join_selectors:
                    web_button = page.locator(selector).first
                    if await web_button.count() > 0:
                        await web_button.click()
                        await asyncio.sleep(2)
                        print("✓ Clicked 'Join on the web'")
                        break
            except:
                print("Web join button not found, continuing...")

            # Enter display name
            print(f"Entering display name: {self.display_name}")
            try:
                name_input_selectors = [
                    'input[placeholder*="name" i]',
                    'input[aria-label*="name" i]',
                    'input[type="text"]'
                ]

                for selector in name_input_selectors:
                    name_input = page.locator(selector).first
                    if await name_input.count() > 0:
                        await name_input.fill(self.display_name)
                        await asyncio.sleep(0.5)
                        print("✓ Entered display name")
                        break
            except:
                print("Name input not found")

            # Turn off camera and microphone
            print("Disabling camera and microphone...")
            try:
                # Toggle camera off
                camera_toggle = page.locator('button[data-tid="toggle-video"], button[aria-label*="camera" i]').first
                if await camera_toggle.count() > 0:
                    # Check if camera is on and toggle it off
                    await camera_toggle.click()
                    await asyncio.sleep(0.5)
            except:
                print("Camera toggle not found or already off")

            try:
                # Toggle microphone off
                mic_toggle = page.locator('button[data-tid="toggle-mute"], button[aria-label*="microphone" i], button[aria-label*="mic" i]').first
                if await mic_toggle.count() > 0:
                    await mic_toggle.click()
                    await asyncio.sleep(0.5)
            except:
                print("Microphone toggle not found or already off")

            # Click the "Join now" button
            print("Clicking join button...")
            join_button_selectors = [
                'button:has-text("Join now")',
                'button[data-tid="prejoin-join-button"]',
                'button:has-text("Join")',
                'button[aria-label*="Join" i]'
            ]

            joined = False
            for selector in join_button_selectors:
                try:
                    join_button = page.locator(selector).first
                    if await join_button.count() > 0:
                        await join_button.click()
                        joined = True
                        print("✓ Successfully clicked join button!")
                        break
                except:
                    continue

            if not joined:
                print("Warning: Could not find join button. You may need to join manually.")

            # Wait a bit to ensure we're in the meeting
            await asyncio.sleep(3)
            print("✓ Joined Microsoft Teams successfully!")

            # Start monitoring active speaker
            if self.transcriber:
                self.speaker_monitor_task = asyncio.create_task(
                    self.monitor_active_speaker_teams(page)
                )

        except PlaywrightTimeoutError as e:
            print(f"Timeout error: {e}")
            print("The meeting page may require manual intervention.")
        except Exception as e:
            print(f"Error joining Teams: {e}")

    async def join_meeting(self, duration: int = 60):
        """
        Join the meeting and stay for the specified duration

        Args:
            duration: Time to stay in the meeting in seconds (default: 60)
        """
        async with async_playwright() as p:
            print(f"Launching browser (headless={self.headless})...")

            # Launch browser with specific arguments to avoid permission prompts
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    '--use-fake-ui-for-media-stream',  # Auto-grant camera/mic permissions
                    '--use-fake-device-for-media-stream',  # Use fake media devices
                    '--disable-blink-features=AutomationControlled'  # Avoid detection
                ]
            )

            # Create a new context with permissions
            context = await browser.new_context(
                permissions=['camera', 'microphone'],
                viewport={'width': 1280, 'height': 720}
            )

            page = await context.new_page()

            try:
                # Join the appropriate meeting type
                if self.meeting_type == "google_meet":
                    await self.join_google_meet(page)
                elif self.meeting_type == "teams":
                    await self.join_teams(page)

                # Start transcription if transcriber is available
                if self.transcriber:
                    self.transcriber.start_recording()

                # Stay in the meeting for the specified duration
                print(f"\nStaying in the meeting for {duration} seconds...")
                print("Press Ctrl+C to leave early")
                await asyncio.sleep(duration)

            except KeyboardInterrupt:
                print("\n\nLeaving meeting (interrupted by user)...")
            except Exception as e:
                print(f"\nError during meeting: {e}")
            finally:
                # Stop transcription
                if self.transcriber:
                    self.transcriber.stop_recording()

                # Cancel speaker monitor
                if self.speaker_monitor_task:
                    self.speaker_monitor_task.cancel()
                    try:
                        await self.speaker_monitor_task
                    except asyncio.CancelledError:
                        pass

                print("Closing browser...")
                await browser.close()
                print("✓ Browser closed. Goodbye!")


async def main():
    parser = argparse.ArgumentParser(
        description="Automated Meeting Joiner with Real-time Transcription"
    )
    parser.add_argument(
        'meeting_url',
        type=str,
        help='Meeting URL (Google Meet or Microsoft Teams)'
    )
    parser.add_argument(
        'display_name',
        type=str,
        help='Your display name in the meeting'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (default: False, shows browser)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Duration to stay in meeting in seconds (default: 60)'
    )
    parser.add_argument(
        '--groq-api-key',
        type=str,
        help='Groq API key for transcription (can also use GROQ_API_KEY env var)'
    )
    parser.add_argument(
        '--transcription-file',
        type=str,
        default='transcription.txt',
        help='Output file for transcriptions (default: transcription.txt)'
    )
    parser.add_argument(
        '--no-transcription',
        action='store_true',
        help='Disable transcription (just join the meeting)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Meeting Joiner Bot - With Real-time Transcription")
    print("=" * 60)
    print(f"Meeting URL: {args.meeting_url}")
    print(f"Display Name: {args.display_name}")
    print(f"Headless Mode: {args.headless}")
    print(f"Duration: {args.duration} seconds")

    # Initialize transcriber if enabled
    transcriber = None
    if not args.no_transcription:
        groq_key = args.groq_api_key or os.environ.get('GROQ_API_KEY')
        if not groq_key:
            print("\nWarning: No Groq API key provided. Transcription disabled.")
            print("Use --groq-api-key or set GROQ_API_KEY environment variable")
        else:
            print(f"Transcription: Enabled → {args.transcription_file}")
            transcriber = AudioTranscriber(groq_key, args.transcription_file)
    else:
        print("Transcription: Disabled")

    print("=" * 60)
    print()

    joiner = MeetingJoiner(
        meeting_url=args.meeting_url,
        display_name=args.display_name,
        headless=args.headless,
        transcriber=transcriber
    )

    await joiner.join_meeting(duration=args.duration)


if __name__ == "__main__":
    asyncio.run(main())
