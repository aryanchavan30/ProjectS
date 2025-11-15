"""
Example usage of the Meeting Joiner Bot
This demonstrates how to use the MeetingJoiner class programmatically
"""
import asyncio
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


async def main():
    """Run the examples"""
    print("Meeting Joiner Bot - Example Usage")
    print("=" * 60)
    print("\nChoose an example to run:")
    print("1. Google Meet (30 seconds)")
    print("2. Microsoft Teams (30 seconds)")
    print("3. Headless mode (60 seconds)")
    print("4. Long meeting (5 minutes)")
    print("\nNote: Update the meeting URLs in the code before running!")

    # Uncomment the example you want to run:

    # await example_google_meet()
    # await example_teams()
    # await example_headless()
    # await example_long_meeting()

    print("\nTo run an example, uncomment one of the function calls in main()")


if __name__ == "__main__":
    asyncio.run(main())
