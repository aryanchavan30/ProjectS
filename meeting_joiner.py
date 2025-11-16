"""
Meeting Joiner Bot using Playwright
Supports: Google Meet and Microsoft Teams
With Real-Time Transcription using Groq Whisper and VAD
"""
import asyncio
import argparse
import os
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from transcription_service import TranscriptionService, start_transcription_with_speaker_tracking


class MeetingJoiner:
    def __init__(
        self,
        meeting_url: str,
        display_name: str,
        headless: bool = False,
        enable_transcription: bool = False,
        audio_device: str = None,
        groq_api_key: str = None
    ):
        """
        Initialize the Meeting Joiner

        Args:
            meeting_url: URL of the meeting (Google Meet or Microsoft Teams)
            display_name: Name to display in the meeting
            headless: Whether to run browser in headless mode (default: False)
            enable_transcription: Enable real-time transcription (default: False)
            audio_device: Audio device name for transcription (e.g., 'CABLE Output')
            groq_api_key: Groq API key for transcription
        """
        self.meeting_url = meeting_url
        self.display_name = display_name
        self.headless = headless
        self.enable_transcription = enable_transcription
        self.audio_device = audio_device
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.meeting_type = self._detect_meeting_type()
        self.transcription_service = None

    def _detect_meeting_type(self) -> str:
        """Detect if the meeting is Google Meet or Microsoft Teams"""
        if "meet.google.com" in self.meeting_url:
            return "google_meet"
        elif "teams.microsoft.com" in self.meeting_url or "teams.live.com" in self.meeting_url:
            return "teams"
        else:
            raise ValueError("Unsupported meeting URL. Only Google Meet and Microsoft Teams are supported.")

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

        except PlaywrightTimeoutError as e:
            print(f"Timeout error: {e}")
            print("The meeting page may require manual intervention.")
        except Exception as e:
            print(f"Error joining Teams: {e}")

    async def join_meeting(self, duration: int = 60, save_transcript: bool = False):
        """
        Join the meeting and stay for the specified duration

        Args:
            duration: Time to stay in the meeting in seconds (default: 60)
            save_transcript: Save transcript to file (default: False)
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

                # Initialize transcription service if enabled
                if self.enable_transcription:
                    print("\n" + "=" * 80)
                    print("Initializing Real-Time Transcription")
                    print("=" * 80)

                    if not self.groq_api_key:
                        print("⚠ Warning: GROQ_API_KEY not set! Transcription disabled.")
                        print("  Set it with: export GROQ_API_KEY='your-api-key'")
                    else:
                        try:
                            self.transcription_service = TranscriptionService(
                                page=page,
                                meeting_type=self.meeting_type,
                                audio_device=self.audio_device,
                                groq_api_key=self.groq_api_key,
                                sample_rate=16000,
                                vad_threshold=0.3,  # Lowered from 0.5 for better sensitivity
                                min_speech_duration=0.5  # Reduced from 1.0 for faster detection
                            )

                            # Start transcription with speaker tracking
                            transcription_task = asyncio.create_task(
                                start_transcription_with_speaker_tracking(
                                    self.transcription_service,
                                    duration=None  # Run until meeting ends
                                )
                            )

                        except Exception as e:
                            print(f"⚠ Failed to initialize transcription: {e}")
                            self.transcription_service = None

                # Stay in the meeting for the specified duration
                print(f"\nStaying in the meeting for {duration} seconds...")
                print("Press Ctrl+C to leave early")
                await asyncio.sleep(duration)

                # Cancel transcription task if running
                if self.enable_transcription and self.transcription_service:
                    if 'transcription_task' in locals():
                        transcription_task.cancel()

            except KeyboardInterrupt:
                print("\n\nLeaving meeting (interrupted by user)...")
            except Exception as e:
                print(f"\nError during meeting: {e}")
            finally:
                # Stop transcription service
                if self.transcription_service:
                    self.transcription_service.stop()

                    # Save transcript if requested
                    if save_transcript:
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"transcript_{timestamp}.txt"
                        self.transcription_service.save_transcriptions(filename)

                print("Closing browser...")
                await browser.close()
                print("✓ Browser closed. Goodbye!")


async def main():
    parser = argparse.ArgumentParser(
        description="Automated Meeting Joiner for Google Meet and Microsoft Teams with Real-Time Transcription"
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
        '--transcribe',
        action='store_true',
        help='Enable real-time transcription with Groq Whisper (default: False)'
    )
    parser.add_argument(
        '--audio-device',
        type=str,
        default=None,
        help='Audio device name for transcription (e.g., "CABLE Output", "Stereo Mix")'
    )
    parser.add_argument(
        '--save-transcript',
        action='store_true',
        help='Save transcript to file when done (default: False)'
    )
    parser.add_argument(
        '--list-audio-devices',
        action='store_true',
        help='List available audio devices and exit'
    )

    args = parser.parse_args()

    # List audio devices if requested
    if args.list_audio_devices:
        from audio_capture import AudioCaptureDevice
        AudioCaptureDevice.list_devices()
        return

    print("=" * 80)
    print("Meeting Joiner Bot - Playwright Python")
    if args.transcribe:
        print("WITH REAL-TIME TRANSCRIPTION (Groq Whisper + Silero VAD)")
    print("=" * 80)
    print(f"Meeting URL: {args.meeting_url}")
    print(f"Display Name: {args.display_name}")
    print(f"Headless Mode: {args.headless}")
    print(f"Duration: {args.duration} seconds")

    if args.transcribe:
        print(f"Transcription: ENABLED")
        print(f"Audio Device: {args.audio_device or 'Default'}")
        print(f"Save Transcript: {args.save_transcript}")
        if not os.getenv("GROQ_API_KEY"):
            print("⚠ WARNING: GROQ_API_KEY not set! Transcription will not work.")
            print("  Set it with: export GROQ_API_KEY='your-api-key'")
    else:
        print(f"Transcription: Disabled (use --transcribe to enable)")

    print("=" * 80)
    print()

    joiner = MeetingJoiner(
        meeting_url=args.meeting_url,
        display_name=args.display_name,
        headless=args.headless,
        enable_transcription=args.transcribe,
        audio_device=args.audio_device
    )

    await joiner.join_meeting(
        duration=args.duration,
        save_transcript=args.save_transcript
    )


if __name__ == "__main__":
    asyncio.run(main())
