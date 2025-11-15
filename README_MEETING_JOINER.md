# Meeting Joiner Bot - Playwright Python

An automated bot that joins Google Meet and Microsoft Teams meetings using Playwright for Python.

## Features

- **Supports Google Meet and Microsoft Teams**
- **Headless or visible browser mode**
- **Automatic camera and microphone muting**
- **Custom display name**
- **Configurable meeting duration**
- **Auto-handles permission prompts**

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:

```bash
playwright install chromium
```

Or install all browsers:

```bash
playwright install
```

## Usage

### Basic Usage

**Google Meet:**
```bash
python meeting_joiner.py "https://meet.google.com/xxx-xxxx-xxx" "John Doe"
```

**Microsoft Teams:**
```bash
python meeting_joiner.py "https://teams.microsoft.com/l/meetup-join/..." "John Doe"
```

### Advanced Options

**Run in headless mode (no visible browser):**
```bash
python meeting_joiner.py "MEETING_URL" "Your Name" --headless
```

**Stay in meeting for specific duration (in seconds):**
```bash
python meeting_joiner.py "MEETING_URL" "Your Name" --duration 300
```

**Combine options:**
```bash
python meeting_joiner.py "MEETING_URL" "Your Name" --headless --duration 1800
```

### Command Line Arguments

```
positional arguments:
  meeting_url          Meeting URL (Google Meet or Microsoft Teams)
  display_name         Your display name in the meeting

optional arguments:
  -h, --help           Show help message
  --headless           Run in headless mode (default: False, shows browser)
  --duration DURATION  Duration to stay in meeting in seconds (default: 60)
```

## Examples

### Example 1: Join Google Meet for 5 minutes
```bash
python meeting_joiner.py "https://meet.google.com/abc-defg-hij" "Alice Smith" --duration 300
```

### Example 2: Join Teams meeting in headless mode for 30 minutes
```bash
python meeting_joiner.py "https://teams.microsoft.com/l/meetup-join/..." "Bob Johnson" --headless --duration 1800
```

### Example 3: Quick test (1 minute, visible browser)
```bash
python meeting_joiner.py "https://meet.google.com/abc-defg-hij" "Test User"
```

## How It Works

1. **Browser Launch**: Launches Chromium browser with special flags to auto-grant media permissions
2. **Meeting Detection**: Automatically detects if the URL is Google Meet or Microsoft Teams
3. **Join Process**:
   - Navigates to the meeting URL
   - Enters your display name
   - Disables camera and microphone
   - Clicks the join button
4. **Duration**: Stays in the meeting for the specified duration
5. **Cleanup**: Closes the browser when done or when interrupted (Ctrl+C)

## Important Notes

### Authentication
- **Google Meet**: For private meetings, you may need to be signed into a Google account. The bot works best with public or organization meetings.
- **Microsoft Teams**: Anonymous joining must be enabled on the meeting. Some meetings require authentication.

### Headless Mode
- Headless mode (`--headless`) runs the browser without a visible window
- Useful for running on servers or automated systems
- Default is non-headless so you can see what's happening

### Camera & Microphone
- The bot automatically mutes both camera and microphone when joining
- Uses fake media devices to avoid actual camera/mic usage
- Auto-grants permissions to avoid browser permission prompts

### Limitations
- Does not support meetings requiring authentication (unless you modify the script to handle login)
- Cannot interact with meeting content (chat, reactions, etc.) - this is a basic join bot
- Some organizations may block automated joining
- Meeting hosts can still remove the bot from the meeting

## Troubleshooting

### "Could not find join button"
- The meeting page layout may have changed
- Try running without `--headless` to see what's happening
- You may need to manually click join

### Browser doesn't close automatically
- Press `Ctrl+C` to interrupt and close

### Permission errors
- Make sure Playwright browsers are installed: `playwright install chromium`
- Check that you have internet connection

### Meeting requires sign-in
- This bot doesn't handle authentication
- You would need to extend the script to include login logic

## Extending the Script

You can modify `meeting_joiner.py` to:
- Add Zoom support
- Include login/authentication handling
- Add chat message sending
- Record the meeting
- Take screenshots at intervals
- Handle more complex scenarios

## License

This is a demonstration script for educational purposes. Please ensure you have permission to use automation tools in your meetings and comply with your organization's policies.

## Disclaimer

Use this tool responsibly. Always:
- Get permission before joining meetings automatically
- Comply with your organization's policies
- Respect privacy and meeting etiquette
- Be aware of legal implications of automated meeting joining

## Support

For issues or questions:
- Check the Playwright Python documentation: https://playwright.dev/python/
- Review the script comments for implementation details
- Modify selectors if UI elements have changed
