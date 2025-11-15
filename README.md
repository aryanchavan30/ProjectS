# Meeting Bot with Real-Time Transcription 🤖🎙️

Automated meeting bot for **Google Meet** and **Microsoft Teams** with **real-time transcription** using **Groq Whisper** and **Silero VAD**.

## ✨ Features

### Meeting Bot
- ✅ Join Google Meet and Microsoft Teams automatically
- ✅ Headless or visible browser mode
- ✅ Auto-mute camera and microphone
- ✅ Custom display name
- ✅ Configurable meeting duration

### Real-Time Transcription (NEW!)
- 🎙️ **Real-time speech-to-text** using Groq Whisper API
- 🔊 **Voice Activity Detection (VAD)** with Silero VAD (reduces costs)
- 👤 **Speaker identification** from meeting interface
- 📝 **Live console output** with timestamps
- 💾 **Save transcripts** to text files
- ⚡ **Ultra-low latency** (<100ms)
- 🌐 **Multi-language support**

## 🚀 Quick Start

### 1. Install
```bash
# Clone or download this repository
cd ProjectS

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### 2. Setup (for transcription)
```bash
# Get Groq API key (free): https://console.groq.com/
export GROQ_API_KEY='your-api-key-here'

# Install VB-Cable (Windows): https://vb-audio.com/Cable/
# Or BlackHole (Mac): https://github.com/ExistentialAudio/BlackHole
```

### 3. Run

**Basic (no transcription):**
```bash
python meeting_joiner.py "MEETING_URL" "Your Name" --duration 300
```

**With transcription:**
```bash
python meeting_joiner.py "MEETING_URL" "Your Name" \
  --transcribe \
  --audio-device "CABLE Output" \
  --save-transcript \
  --duration 300
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | **START HERE** - 5-minute quick setup |
| [README_TRANSCRIPTION.md](README_TRANSCRIPTION.md) | Complete transcription guide |
| [README_MEETING_JOINER.md](README_MEETING_JOINER.md) | Meeting bot documentation |
| [example_usage.py](example_usage.py) | Code examples |

## 🎯 Usage Examples

### List Audio Devices
```bash
python meeting_joiner.py --list-audio-devices
```

### Google Meet with Transcription
```bash
python meeting_joiner.py \
  "https://meet.google.com/xxx-xxxx-xxx" \
  "Bot Name" \
  --transcribe \
  --audio-device "CABLE Output" \
  --duration 600 \
  --save-transcript
```

### Microsoft Teams with Transcription
```bash
python meeting_joiner.py \
  "https://teams.microsoft.com/l/meetup-join/..." \
  "Bot Name" \
  --transcribe \
  --audio-device "CABLE Output" \
  --duration 600
```

### Headless Mode (Background)
```bash
python meeting_joiner.py \
  "MEETING_URL" \
  "Bot Name" \
  --transcribe \
  --headless \
  --save-transcript
```

## 📊 Example Output

```
================================================================================
[14:32:15] John Doe: Hello everyone, welcome to the meeting.
================================================================================

================================================================================
[14:32:18] Jane Smith: Hi John, thanks for having us.
================================================================================

================================================================================
[14:32:25] John Doe: Let's discuss the project updates for Q1.
================================================================================
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Meeting (Meet/Teams)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Playwright Browser  │
          │  - Join meeting      │
          │  - Detect speakers   │
          └──────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Virtual Audio Cable │
          │  (VB-Cable/BlackHole)│
          └──────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   Audio Capture      │
          │   (sounddevice)      │
          └──────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   Silero VAD         │
          │   (Speech Detection) │
          └──────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   Groq Whisper       │
          │   (Transcription)    │
          └──────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Console + File      │
          │  Output              │
          └──────────────────────┘
```

## 📦 Components

| Module | Purpose |
|--------|---------|
| `meeting_joiner.py` | Main bot with transcription integration |
| `transcription_service.py` | Orchestrates transcription pipeline |
| `audio_capture.py` | Captures audio from virtual devices |
| `vad_handler.py` | Voice activity detection (Silero VAD) |
| `groq_transcriber.py` | Groq Whisper API integration |
| `speaker_detector.py` | Extract speaker names from meeting UI |

## ⚙️ Command-Line Options

```bash
python meeting_joiner.py [OPTIONS] MEETING_URL DISPLAY_NAME

Required:
  MEETING_URL           Google Meet or Teams URL
  DISPLAY_NAME          Your name in the meeting

Options:
  --transcribe          Enable real-time transcription
  --audio-device NAME   Audio device for transcription
  --save-transcript     Save transcript to file
  --duration SECONDS    Meeting duration (default: 60)
  --headless            Hide browser window
  --list-audio-devices  List available audio devices
  -h, --help           Show help message
```

## 🔧 Requirements

### Software
- Python 3.9+
- Windows, Mac, or Linux

### For Transcription
- Groq API key (free tier available)
- Virtual audio device:
  - **Windows:** VB-Cable (free)
  - **Mac:** BlackHole (free)
  - **Linux:** PulseAudio (built-in)

### Python Packages
See [requirements.txt](requirements.txt)

## 🌟 Use Cases

- **Accessibility:** Real-time captions for hearing-impaired
- **Note-taking:** Automatic meeting minutes
- **Compliance:** Meeting documentation
- **Research:** Conversation analysis
- **Multilingual:** Transcribe + translate
- **Automation:** Trigger actions based on keywords

## 🔐 Security & Privacy

- Audio is captured locally and sent to Groq API for transcription
- Groq does not permanently store audio
- API key should be kept secret
- Always get permission before recording meetings
- Complies with your responsibility to follow organizational policies

## 🐛 Troubleshooting

### Audio device not found
```bash
python meeting_joiner.py --list-audio-devices
# Use exact device name from output
```

### GROQ_API_KEY not set
```bash
export GROQ_API_KEY='your-key-here'
# Or create .env file (see .env.example)
```

### No transcriptions appearing
1. Verify audio routing to virtual cable
2. Check GROQ_API_KEY is set
3. Test with `--audio-device "EXACT DEVICE NAME"`
4. Check internet connection

### Slow transcription
- Use `whisper-large-v3-turbo` (default)
- Check internet speed
- Consider Groq paid tier for heavy use

## 📄 License

Educational and demonstration purposes. Use responsibly and with permission.

## 🤝 Contributing

This is a demonstration project. Feel free to fork and modify for your needs.

## 📞 Support

- Check documentation in `/docs` folder
- Review troubleshooting sections
- Test with `--list-audio-devices`
- Verify setup with short test meetings

## 🎓 Tips

1. **Test first:** Join a 1-minute test meeting before production use
2. **Audio quality:** Use wired internet for stable transcription
3. **Monitor output:** Watch console for first few transcriptions
4. **Save important:** Always use `--save-transcript` for important meetings
5. **Privacy:** Inform participants about recording/transcription

---

**Quick Links:**
- [5-Minute Setup Guide](SETUP_GUIDE.md)
- [Full Transcription Docs](README_TRANSCRIPTION.md)
- [Meeting Bot Docs](README_MEETING_JOINER.md)
- [Code Examples](example_usage.py)

**Get Started:**
```bash
# 1. Install
pip install -r requirements.txt && playwright install chromium

# 2. Setup Groq API
export GROQ_API_KEY='your-key'

# 3. Install VB-Cable (Windows) or BlackHole (Mac)

# 4. Run!
python meeting_joiner.py "MEETING_URL" "Your Name" --transcribe
```

Made with ❤️ using Playwright, Groq Whisper, and Silero VAD
