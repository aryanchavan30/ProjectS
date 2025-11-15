"""
Example usage of the Meeting Joiner Bot with Transcription
This demonstrates how to use the MeetingJoiner and AudioTranscriber classes
"""
import asyncio
import os
from meeting_joiner import MeetingJoiner, AudioTranscriber


async def example_google_meet_with_transcription():
    """Example: Join Google Meet with real-time transcription"""
    print("\n=== Example 1: Google Meet with Transcription ===")

    # Get Groq API key from environment or set it here
    groq_api_key = os.environ.get('GROQ_API_KEY', 'your_groq_api_key_here')

    # Replace with your actual meeting URL
    meeting_url = "https://meet.google.com/abc-defg-hij"
    display_name = "Transcription Bot"

    # Create transcriber
    transcriber = AudioTranscriber(
        groq_api_key=groq_api_key,
        output_file="google_meet_transcript.txt"
    )

    # Create joiner with transcriber
    joiner = MeetingJoiner(
        meeting_url=meeting_url,
        display_name=display_name,
        headless=False,  # Set to True for headless mode
        transcriber=transcriber
    )

    # Join for 5 minutes (300 seconds)
    await joiner.join_meeting(duration=300)


async def example_teams_with_transcription():
    """Example: Join Microsoft Teams with real-time transcription"""
    print("\n=== Example 2: Microsoft Teams with Transcription ===")

    groq_api_key = os.environ.get('GROQ_API_KEY', 'your_groq_api_key_here')

    # Replace with your actual meeting URL
    meeting_url = "https://teams.microsoft.com/l/meetup-join/..."
    display_name = "Transcription Bot"

    # Create transcriber
    transcriber = AudioTranscriber(
        groq_api_key=groq_api_key,
        output_file="teams_transcript.txt"
    )

    # Create joiner with transcriber
    joiner = MeetingJoiner(
        meeting_url=meeting_url,
        display_name=display_name,
        headless=False,
        transcriber=transcriber
    )

    # Join for 5 minutes
    await joiner.join_meeting(duration=300)


async def example_without_transcription():
    """Example: Join meeting without transcription"""
    print("\n=== Example 3: Join Meeting Without Transcription ===")

    meeting_url = "https://meet.google.com/abc-defg-hij"
    display_name = "Basic Bot"

    # Create joiner without transcriber
    joiner = MeetingJoiner(
        meeting_url=meeting_url,
        display_name=display_name,
        headless=False,
        transcriber=None  # No transcription
    )

    # Join for 1 minute
    await joiner.join_meeting(duration=60)


async def example_headless_with_transcription():
    """Example: Join in headless mode with transcription"""
    print("\n=== Example 4: Headless Mode with Transcription ===")

    groq_api_key = os.environ.get('GROQ_API_KEY', 'your_groq_api_key_here')

    meeting_url = "https://meet.google.com/abc-defg-hij"
    display_name = "Headless Transcription Bot"

    # Create transcriber
    transcriber = AudioTranscriber(
        groq_api_key=groq_api_key,
        output_file="headless_transcript.txt"
    )

    # Create joiner in headless mode
    joiner = MeetingJoiner(
        meeting_url=meeting_url,
        display_name=display_name,
        headless=True,  # No visible browser window
        transcriber=transcriber
    )

    # Join for 10 minutes
    await joiner.join_meeting(duration=600)


async def example_custom_transcriber_settings():
    """Example: Custom transcriber with adjusted VAD settings"""
    print("\n=== Example 5: Custom VAD Settings ===")

    groq_api_key = os.environ.get('GROQ_API_KEY', 'your_groq_api_key_here')

    meeting_url = "https://meet.google.com/abc-defg-hij"
    display_name = "Custom VAD Bot"

    # Create transcriber with custom settings
    transcriber = AudioTranscriber(
        groq_api_key=groq_api_key,
        output_file="custom_transcript.txt"
    )

    # Adjust VAD threshold (0.0 to 1.0)
    # Lower = more sensitive (detects quieter speech)
    # Higher = less sensitive (only loud/clear speech)
    transcriber.vad_threshold = 0.3  # More sensitive

    # Create joiner
    joiner = MeetingJoiner(
        meeting_url=meeting_url,
        display_name=display_name,
        headless=False,
        transcriber=transcriber
    )

    # Join for 5 minutes
    await joiner.join_meeting(duration=300)


async def main():
    """Run the examples"""
    print("Meeting Joiner Bot - Example Usage with Transcription")
    print("=" * 60)
    print("\nIMPORTANT: Before running, make sure to:")
    print("1. Set your GROQ_API_KEY environment variable")
    print("   OR update the groq_api_key in the examples")
    print("2. Update the meeting URLs in the code")
    print("3. Install all dependencies: pip install -r requirements.txt")
    print("4. Install Playwright browsers: playwright install chromium")
    print("\nNote: For Windows audio capture, PyAudioWPatch will be used.")
    print("=" * 60)
    print("\nChoose an example to run:")
    print("1. Google Meet with Transcription")
    print("2. Microsoft Teams with Transcription")
    print("3. Join Meeting Without Transcription")
    print("4. Headless Mode with Transcription")
    print("5. Custom VAD Settings")
    print()

    # Uncomment the example you want to run:

    # await example_google_meet_with_transcription()
    # await example_teams_with_transcription()
    # await example_without_transcription()
    # await example_headless_with_transcription()
    # await example_custom_transcriber_settings()

    print("\nTo run an example, uncomment one of the function calls in main()")


if __name__ == "__main__":
    asyncio.run(main())
