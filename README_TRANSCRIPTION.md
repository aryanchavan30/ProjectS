# Real-Time Meeting Transcription with Groq Whisper & VAD

Complete guide for setting up and using real-time meeting transcription with Google Meet and Microsoft Teams.

## 🎯 Features

- **Real-time transcription** using Groq's Whisper API (ultra-fast)
- **Voice Activity Detection (VAD)** using Silero VAD (reduces API costs)
- **Speaker identification** from meeting interface
- **Automatic audio capture** from virtual audio devices
- **Live console output** with timestamps and speaker names
- **Transcript saving** to text files
- **Low latency** (<100ms with Whisper Turbo + Silero VAD)

## 📋 Prerequisites

### 1. Python Requirements
- Python 3.9 or higher
- pip package manager

### 2. Groq API Key
- Sign up at [Groq Console](https://console.groq.com/)
- Get your API key from the dashboard
- Free tier available!

### 3. Virtual Audio Device (REQUIRED for Windows)

You **MUST** install a virtual audio cable to route meeting audio to the transcription system.

#### Option A: VB-Cable (FREE - Recommended)
1. Download from: https://vb-audio.com/Cable/
2. Install and restart your computer
3. Configure:
   - Set **CABLE Input** as your default playback device
   - Or route browser audio to CABLE Input
   - The bot will capture from **CABLE Output**

#### Option B: VoiceMeeter (FREE)
1. Download from: https://vb-audio.com/Voicemeeter/
2. More advanced routing options
3. Good for mixing multiple audio sources

#### Option C: Virtual Audio Cable (VAC) (Paid ~$25)
- Professional solution
- Lower latency
- Download from: https://vac.muzychenko.net/

#### Option D: Windows Stereo Mix (Built-in, if available)
- Some Windows systems have "Stereo Mix" in recording devices
- Right-click sound icon → Sounds → Recording tab
- Enable "Stereo Mix" if available
- **Note:** Not all systems have this option

## 🚀 Installation

### Step 1: Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 2: Set Up Groq API Key

**Option A: Environment Variable (Recommended)**
```bash
# Linux/Mac
export GROQ_API_KEY='your-groq-api-key-here'

# Windows PowerShell
$env:GROQ_API_KEY='your-groq-api-key-here'

# Windows CMD
set GROQ_API_KEY=your-groq-api-key-here
```

**Option B: .env File**
```bash
# Create .env file in project directory
echo "GROQ_API_KEY=your-groq-api-key-here" > .env
```

### Step 3: Configure Virtual Audio Device

1. **Install VB-Cable** (see Prerequisites above)

2. **Set up audio routing:**

   **Method 1: System-wide (Easiest)**
   - Right-click volume icon → Sound settings
   - Set **CABLE Input** as default playback device
   - All system audio will now route to transcription

   **Method 2: Browser-specific (Recommended)**
   - Keep default speakers for system
   - In Windows Volume Mixer: Set browser to use **CABLE Input**
   - Only meeting audio routes to transcription

3. **Verify setup:**
```bash
# List available audio devices
python meeting_joiner.py --list-audio-devices
```

You should see:
```
CABLE Output (VB-Audio Virtual Cable)  <- Use this for --audio-device
```

## 💻 Usage

### Basic Transcription

```bash
# Google Meet with transcription
python meeting_joiner.py \
  "https://meet.google.com/xxx-xxxx-xxx" \
  "Bot Name" \
  --transcribe \
  --audio-device "CABLE Output" \
  --duration 300

# Microsoft Teams with transcription
python meeting_joiner.py \
  "https://teams.microsoft.com/l/meetup-join/..." \
  "Bot Name" \
  --transcribe \
  --audio-device "CABLE Output" \
  --duration 300
```

### Save Transcript to File

```bash
python meeting_joiner.py \
  "MEETING_URL" \
  "Your Name" \
  --transcribe \
  --audio-device "CABLE Output" \
  --save-transcript \
  --duration 600
```

This will create: `transcript_YYYYMMDD_HHMMSS.txt`

### Using Default Audio Device

If you set CABLE Input as default playback device:

```bash
python meeting_joiner.py \
  "MEETING_URL" \
  "Your Name" \
  --transcribe
```

(No `--audio-device` needed)

### List Available Audio Devices

```bash
python meeting_joiner.py --list-audio-devices
```

## 📊 Command-Line Arguments

| Argument | Description | Required | Default |
|----------|-------------|----------|---------|
| `meeting_url` | Google Meet or Teams URL | Yes | - |
| `display_name` | Your name in the meeting | Yes | - |
| `--transcribe` | Enable transcription | No | False |
| `--audio-device` | Audio device name | No | Default |
| `--save-transcript` | Save to file | No | False |
| `--duration` | Meeting duration (seconds) | No | 60 |
| `--headless` | Hide browser window | No | False |
| `--list-audio-devices` | List audio devices | No | False |

## 📝 Example Output

```
================================================================================
[14:32:15] John Doe: Hello everyone, welcome to the meeting.
================================================================================

================================================================================
[14:32:18] Jane Smith: Hi John, thanks for having us.
================================================================================

================================================================================
[14:32:25] John Doe: Let's discuss the project updates.
================================================================================
```

## 🏗️ Architecture

```
Google Meet/Teams (Browser)
         ↓
    Speaker Output
         ↓
  Virtual Audio Cable (VB-Cable)
         ↓
   Loopback to Input
         ↓
  Python Audio Capture (sounddevice)
         ↓
    Silero VAD - Detects speech segments
         ↓
  Audio Chunks (when speech detected)
         ↓
   Groq Whisper API (whisper-large-v3-turbo)
         ↓
  Transcription + Speaker Name (from Playwright)
         ↓
  Console Output & File Save
```

## 🔧 Troubleshooting

### "GROQ_API_KEY not set"
```bash
# Set the environment variable
export GROQ_API_KEY='your-key-here'

# Or create .env file
echo "GROQ_API_KEY=your-key-here" > .env
```

### "Audio device not found"
```bash
# List all devices
python meeting_joiner.py --list-audio-devices

# Use exact device name
python meeting_joiner.py "URL" "Name" --transcribe --audio-device "CABLE Output (VB-Audio Virtual Cable)"
```

### "No audio being captured"
1. **Check VB-Cable is installed:**
   - Look for CABLE Input in playback devices
   - Look for CABLE Output in recording devices

2. **Route browser audio to CABLE Input:**
   - Windows: Volume Mixer → Browser → CABLE Input
   - Play test audio to verify

3. **Verify with system test:**
   ```python
   from audio_capture import AudioCaptureDevice
   device = AudioCaptureDevice(device_name="CABLE Output")
   device.start_recording()
   # Speak in meeting
   ```

### "VAD model download fails"
```bash
# Manually download Silero VAD
python -c "import torch; torch.hub.load('snakers4/silero-vad', 'silero_vad')"
```

### "Speaker names not detected"
- This is normal for some meetings
- Speaker detection uses Playwright to read meeting UI
- Fallback: Shows "Unknown" speaker
- Still transcribes correctly!

### "High latency / slow transcription"
1. Use `whisper-large-v3-turbo` (default, faster)
2. Check internet connection (Groq API is cloud-based)
3. Reduce `min_speech_duration` (but may increase API calls)

### "API rate limits exceeded"
- Groq free tier has limits
- VAD helps by only sending speech (not silence)
- Consider upgrading Groq plan for heavy use

## ⚙️ Advanced Configuration

### Adjust VAD Sensitivity

Edit `meeting_joiner.py`:

```python
self.transcription_service = TranscriptionService(
    vad_threshold=0.3,  # Lower = more sensitive (0.0-1.0)
    min_speech_duration=0.5  # Minimum seconds before transcription
)
```

### Change Whisper Model

Edit `groq_transcriber.py`:

```python
# For more accuracy (slower)
model="whisper-large-v3"

# For speed (default)
model="whisper-large-v3-turbo"
```

### Custom Output Callback

```python
def my_callback(data):
    print(f"Speaker: {data['speaker']}")
    print(f"Text: {data['text']}")
    # Send to database, API, etc.

service = TranscriptionService(
    output_callback=my_callback
)
```

## 📦 Module Overview

| Module | Purpose |
|--------|---------|
| `meeting_joiner.py` | Main bot + transcription integration |
| `transcription_service.py` | Orchestrates all components |
| `audio_capture.py` | Captures audio from virtual device |
| `vad_handler.py` | Voice activity detection (Silero VAD) |
| `groq_transcriber.py` | Groq Whisper API integration |
| `speaker_detector.py` | Extract speaker names from meeting UI |

## 🔐 Security & Privacy

- **Your audio stays local** until sent to Groq API
- **Groq API**: Audio is transcribed, not stored permanently
- **No recording**: Only transcripts are saved (if enabled)
- **API Key**: Keep your GROQ_API_KEY secret
- **Compliance**: Ensure you have permission to transcribe meetings

## 📄 License

Educational and demonstration purposes. Use responsibly and with permission.

## 🆘 Support

For issues:
1. Check this documentation
2. Verify prerequisites are installed
3. Test audio device with `--list-audio-devices`
4. Check Groq API key is set correctly
5. Review error messages in console

## 🎓 Tips for Best Results

1. **Use wired internet** for stable Groq API connection
2. **Close other audio apps** to avoid conflicts
3. **Test audio routing** before important meetings
4. **Monitor first few transcriptions** to verify quality
5. **Use --save-transcript** to keep records
6. **Set proper duration** to avoid early disconnect

## 🌟 Example Use Cases

- **Accessibility**: Real-time captions for hearing-impaired
- **Note-taking**: Automatic meeting minutes
- **Multilingual**: Translate after transcription
- **Compliance**: Meeting documentation
- **Research**: Conversation analysis
- **Automation**: Trigger actions based on keywords

---

**Need help?** Check the troubleshooting section or review module documentation in the code comments.
