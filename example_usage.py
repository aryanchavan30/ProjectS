"""
Example usage of the Meeting Joiner Bot
This demonstrates how to use the MeetingJoiner class programmatically
With and without real-time transcription
"""
import asyncio
import os
from meeting_joiner import MeetingJoiner


async def example_google_meet():
    """Example: Join a Google Meet meeting"""
    print("\n=== Example 1: Google Meet ===")

    # Replace with your actual meeting URL
    meeting_url = "https://meet.google.com/abc-defg-hij"
    display_name = "Bot User"

    joiner = MeetingJoiner(
        meeting_url=meeting_url,
        display_name=display_name,
        headless=False  # Set to True for headless mode
    )

    # Join for 30 seconds
    await joiner.join_meeting(duration=30)


async def example_teams():
    """Example: Join a Microsoft Teams meeting"""
    print("\n=== Example 2: Microsoft Teams ===")

    # Replace with your actual meeting URL
    meeting_url = "https://teams.microsoft.com/l/meetup-join/..."
    display_name = "Bot User"

    joiner = MeetingJoiner(
        meeting_url=meeting_url,
        display_name=display_name,
        headless=False
    )

    # Join for 30 seconds
    await joiner.join_meeting(duration=30)


async def example_headless():
    """Example: Join in headless mode"""
    print("\n=== Example 3: Headless Mode ===")

    meeting_url = "https://meet.google.com/abc-defg-hij"
    display_name = "Headless Bot"

    joiner = MeetingJoiner(
        meeting_url=meeting_url,
        display_name=display_name,
        headless=True  # No visible browser window
    )

    # Join for 60 seconds
    await joiner.join_meeting(duration=60)


async def example_long_meeting():
    """Example: Join for an extended period"""
    print("\n=== Example 4: Long Meeting (5 minutes) ===")

    meeting_url = "https://meet.google.com/abc-defg-hij"
    display_name = "Long Meeting Bot"

    joiner = MeetingJoiner(
        meeting_url=meeting_url,
        display_name=display_name,
        headless=False
    )

    # Join for 5 minutes (300 seconds)
    await joiner.join_meeting(duration=300)


async def example_with_transcription():
    """Example: Join with real-time transcription"""
    print("\n=== Example 5: Meeting with Transcription ===")

    meeting_url = "https://meet.google.com/abc-defg-hij"
    display_name = "Transcription Bot"

    # Make sure GROQ_API_KEY is set
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set!")
        print("Set it with: export GROQ_API_KEY='your-api-key'")
        return

    joiner = MeetingJoiner(
        meeting_url=meeting_url,
        display_name=display_name,
        headless=False,
        enable_transcription=True,  # Enable transcription
        audio_device="CABLE Output"  # Specify your virtual audio device
    )

    # Join for 5 minutes with transcription
    await joiner.join_meeting(duration=300, save_transcript=True)


async def example_transcription_with_custom_device():
    """Example: Transcription with specific audio device"""
    print("\n=== Example 6: Custom Audio Device ===")

    meeting_url = "https://meet.google.com/abc-defg-hij"
    display_name = "Custom Audio Bot"

    joiner = MeetingJoiner(
        meeting_url=meeting_url,
        display_name=display_name,
        headless=False,
        enable_transcription=True,
        audio_device="CABLE Output (VB-Audio Virtual Cable)"  # Full device name
    )

    # Join and save transcript
    await joiner.join_meeting(duration=600, save_transcript=True)


async def example_teams_with_transcription():
    """Example: Microsoft Teams with transcription"""
    print("\n=== Example 7: Teams with Transcription ===")

    meeting_url = "https://teams.microsoft.com/l/meetup-join/..."
    display_name = "Teams Bot"

    joiner = MeetingJoiner(
        meeting_url=meeting_url,
        display_name=display_name,
        headless=False,
        enable_transcription=True,
        audio_device="CABLE Output"
    )

    await joiner.join_meeting(duration=300, save_transcript=True)


async def main():
    """Run the examples"""
    print("Meeting Joiner Bot - Example Usage")
    print("=" * 80)
    print("\nChoose an example to run:")
    print("1. Google Meet (30 seconds)")
    print("2. Microsoft Teams (30 seconds)")
    print("3. Headless mode (60 seconds)")
    print("4. Long meeting (5 minutes)")
    print("\n--- NEW: Transcription Examples ---")
    print("5. Meeting with Transcription (5 minutes)")
    print("6. Custom Audio Device Transcription")
    print("7. Microsoft Teams with Transcription")
    print("\nNote: Update the meeting URLs in the code before running!")
    print("\nFor transcription examples:")
    print("  - Set GROQ_API_KEY environment variable")
    print("  - Install virtual audio device (VB-Cable, etc.)")
    print("  - Update audio_device parameter to match your device")

    # Uncomment the example you want to run:

    # await example_google_meet()
    # await example_teams()
    # await example_headless()
    # await example_long_meeting()

    # --- Transcription Examples ---
    # await example_with_transcription()
    # await example_transcription_with_custom_device()
    # await example_teams_with_transcription()

    print("\nTo run an example, uncomment one of the function calls in main()")


if __name__ == "__main__":
    asyncio.run(main())
