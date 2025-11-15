# Meeting Joiner Bot with Real-time Transcription

Automated bot that joins Google Meet and Microsoft Teams meetings with real-time speech-to-text transcription using Groq Whisper, Silero VAD, and speaker identification.

## Features

- **Automated Meeting Join**: Joins Google Meet and Microsoft Teams meetings automatically
- **Real-time Transcription**: Uses Groq Whisper (ultra-fast, 216x real-time)
- **Voice Activity Detection (VAD)**: Silero VAD detects when someone is speaking
- **Speaker Identification**: Tracks who is speaking by monitoring the meeting UI
- **Windows Audio Capture**: Uses PyAudioWPatch for WASAPI loopback (captures system audio)
- **Headless Mode**: Can run without showing the browser
- **Smart Audio Processing**: Only transcribes when speech is detected, saves API costs

## How It Works

```
Meeting (Google Meet/Teams)
    ↓
Browser (Playwright) → Monitors active speaker in UI
    ↓
Windows Audio (WASAPI Loopback) → Captures all meeting audio
    ↓
Silero VAD → Detects when someone is speaking
    ↓
Groq Whisper API → Transcribes speech to text
    ↓
Output File → [Timestamp] Speaker Name: Transcription
```

## Requirements

- **Windows OS** (for WASAPI loopback audio capture)
- **Python 3.7+**
- **Groq API Key** (free at https://console.groq.com/)
- **Internet connection**

## Installation

### 1. Clone or Download This Repository

```bash
cd /path/to/ProjectS
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `playwright` - Browser automation
- `PyAudioWPatch` - Windows audio capture with WASAPI loopback
- `torch` & `torchaudio` - For Silero VAD
- `numpy` - Audio processing
- `groq` - Groq API client for Whisper

### 3. Install Playwright Browsers

```bash
playwright install chromium
```

### 4. Get Groq API Key

1. Go to https://console.groq.com/
2. Sign up for a free account
3. Create an API key
4. Set it as an environment variable:

**Windows (Command Prompt):**
```cmd
set GROQ_API_KEY=your_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY="your_api_key_here"
```

**Or add to Windows Environment Variables permanently:**
1. Search "Environment Variables" in Windows
2. Add new User Variable: `GROQ_API_KEY` = `your_api_key_here`

## Usage

### Command Line

**Basic usage (no transcription):**
```bash
python meeting_joiner.py "https://meet.google.com/abc-defg-hij" "Bot Name" --duration 300
```

**With transcription:**
```bash
python meeting_joiner.py "https://meet.google.com/abc-defg-hij" "Bot Name" --duration 300 --groq-api-key YOUR_KEY
```

**All options:**
```bash
python meeting_joiner.py "MEETING_URL" "DISPLAY_NAME" \
    --duration 600 \
    --groq-api-key YOUR_KEY \
    --transcription-file transcript.txt \
    --headless
```

### Python Code

See `example_usage.py` for detailed examples:

```python
import asyncio
from meeting_joiner import MeetingJoiner, AudioTranscriber

async def main():
    # Create transcriber
    transcriber = AudioTranscriber(
        groq_api_key="your_groq_api_key",
        output_file="transcript.txt"
    )

    # Create meeting joiner
    joiner = MeetingJoiner(
        meeting_url="https://meet.google.com/abc-defg-hij",
        display_name="Transcription Bot",
        headless=False,
        transcriber=transcriber
    )

    # Join meeting for 5 minutes
    await joiner.join_meeting(duration=300)

asyncio.run(main())
```

## Command Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `meeting_url` | Yes | Google Meet or Teams meeting URL |
| `display_name` | Yes | Your display name in the meeting |
| `--duration` | No | Duration in seconds (default: 60) |
| `--groq-api-key` | No | Groq API key (or use GROQ_API_KEY env var) |
| `--transcription-file` | No | Output file (default: transcription.txt) |
| `--headless` | No | Run browser in headless mode |
| `--no-transcription` | No | Disable transcription |

## Output Format

Transcriptions are saved to a text file with this format:

```
[2025-01-15 14:32:10] John Doe: Hello everyone, welcome to the meeting.
[2025-01-15 14:32:15] Jane Smith: Thanks for joining. Let's get started.
[2025-01-15 14:32:25] John Doe: First item on the agenda is the project update.
```

Each line contains:
- Timestamp
- Speaker name (from meeting UI)
- Transcribed speech

## Architecture Details

### Audio Capture (Windows)

Uses **PyAudioWPatch** with WASAPI loopback to capture system audio:
- Captures all audio playing through your speakers
- No need for virtual audio cables
- Works with any Windows application
- 16kHz mono audio for optimal VAD/transcription

### Voice Activity Detection (VAD)

Uses **Silero VAD** (state-of-the-art):
- < 1ms processing time per audio chunk
- Supports 6000+ languages
- Extremely accurate speech detection
- Reduces unnecessary API calls to Groq

### Transcription

Uses **Groq Whisper Large v3 Turbo**:
- 216x faster than real-time
- Near-instant transcription
- Supports 90+ languages
- Free tier available

### Speaker Identification

Monitors meeting UI to identify active speaker:
- **Google Meet**: Scrapes participant aria-labels
- **Microsoft Teams**: Monitors roster participant names
- Updates speaker name in real-time
- Falls back to "Unknown" if name can't be detected

## Troubleshooting

### Audio Not Capturing

**Problem**: No audio being captured from meeting

**Solutions**:
1. Make sure PyAudioWPatch is installed: `pip install PyAudioWPatch`
2. Check that audio is playing through your default speakers
3. Test audio device: `python -m pyaudiowpatch` (lists all devices)
4. Try increasing VAD sensitivity: `transcriber.vad_threshold = 0.3`

### Transcription Not Working

**Problem**: No transcriptions appearing

**Solutions**:
1. Verify Groq API key is set: `echo %GROQ_API_KEY%` (Windows CMD)
2. Check internet connection
3. Check Groq API quota: https://console.groq.com/
4. Look for errors in console output

### Speaker Names Not Detected

**Problem**: All transcriptions show "Unknown" as speaker

**Solutions**:
1. This is normal for the first few seconds
2. Meeting UI selectors may have changed - check console for errors
3. Try joining without headless mode to see the UI
4. Speaker detection works best when participants have their names visible

### VAD Not Detecting Speech

**Problem**: VAD not detecting speech (no transcriptions)

**Solutions**:
1. Lower VAD threshold: `transcriber.vad_threshold = 0.3` (default: 0.5)
2. Check audio volume is adequate
3. Ensure Silero VAD model downloaded: Check console for "✓ Silero VAD model loaded"

### PyTorch/Torch Installation Issues

**Problem**: torch or torchaudio won't install

**Solutions**:
```bash
# Install CPU-only version (smaller, faster for VAD)
pip install torch==2.1.2+cpu torchaudio==2.1.2+cpu -f https://download.pytorch.org/whl/torch_stable.html
```

## Configuration Options

### Adjust VAD Sensitivity

```python
transcriber = AudioTranscriber(groq_api_key="key")
transcriber.vad_threshold = 0.3  # 0.0 to 1.0
# Lower = more sensitive (detects quieter speech)
# Higher = less sensitive (only loud/clear speech)
```

### Change Audio Settings

```python
transcriber = AudioTranscriber(groq_api_key="key")
transcriber.CHUNK = 1024  # Larger chunks = less CPU, more latency
transcriber.RATE = 16000   # Sample rate (16000 recommended for Silero)
```

### Silence Detection Timing

In `meeting_joiner.py`, line 205-206:

```python
max_silence_frames = int(self.RATE / self.CHUNK * 2)  # 2 seconds of silence
min_speech_frames = int(self.RATE / self.CHUNK * 0.5)  # 0.5 seconds minimum
```

Adjust these values to change when transcription is triggered.

## Limitations

1. **Windows Only**: WASAPI loopback is Windows-specific
   - For macOS/Linux, you'd need different audio capture methods (BlackHole, PulseAudio)

2. **Speaker Identification**: Relies on UI scraping
   - May break if Google Meet/Teams changes their UI
   - Doesn't work with some privacy settings

3. **Single Audio Stream**: Captures mixed audio
   - Can't separate individual speakers in audio
   - Relies on VAD + UI scraping to attribute speakers

4. **Network Required**: Both for Groq API and downloading Silero VAD model

## Performance

- **VAD Processing**: < 1ms per chunk
- **Transcription Speed**: 216x real-time (Groq Whisper)
- **End-to-End Latency**: ~2-5 seconds from speech to transcription
- **CPU Usage**: Low (mostly waiting for audio/network)
- **Memory**: ~500MB (including torch + VAD model)

## API Costs

**Groq Whisper Pricing** (as of 2025):
- Free tier: Available
- Paid tier: Very affordable
- Check latest: https://console.groq.com/

**Tips to reduce costs**:
- VAD ensures only speech is transcribed (not silence)
- Adjust silence detection timing to avoid partial words

## License

This project uses:
- Silero VAD: MIT License
- Groq API: Commercial API (free tier available)
- Playwright: Apache 2.0
- PyAudioWPatch: MIT License

## Credits

- **Silero VAD**: https://github.com/snakers4/silero-vad
- **Groq**: https://groq.com/
- **PyAudioWPatch**: https://github.com/s0d3s/PyAudioWPatch
- **Playwright**: https://playwright.dev/

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review `example_usage.py` for code examples
3. Check console output for error messages

## Future Enhancements

Potential improvements:
- [ ] Speaker diarization (AI-based speaker separation)
- [ ] Real-time display dashboard
- [ ] Support for Zoom, Webex
- [ ] Export to SRT/VTT subtitle formats
- [ ] Multi-language support
- [ ] WebSocket streaming for real-time updates
- [ ] Cloud storage integration
