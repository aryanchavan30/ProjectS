# Quick Setup Guide - Real-Time Meeting Transcription

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies (2 min)
```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Get Groq API Key (1 min)
1. Go to https://console.groq.com/
2. Sign up (free)
3. Copy your API key
4. Set it:
   ```bash
   export GROQ_API_KEY='your-api-key-here'
   ```

### Step 3: Install Virtual Audio Cable (2 min)
**Windows (VB-Cable - FREE):**
1. Download: https://vb-audio.com/Cable/
2. Install and restart
3. Done!

**Mac (BlackHole - FREE):**
1. Download: https://github.com/ExistentialAudio/BlackHole
2. Install
3. Done!

**Linux (PulseAudio - Built-in):**
```bash
pactl load-module module-loopback
```

### Step 4: Run! (30 sec)
```bash
python meeting_joiner.py \
  "YOUR_MEETING_URL" \
  "Your Name" \
  --transcribe \
  --audio-device "CABLE Output" \
  --duration 300
```

## ✅ Verify Setup

### Test 1: Check API Key
```bash
echo $GROQ_API_KEY
# Should show your key
```

### Test 2: List Audio Devices
```bash
python meeting_joiner.py --list-audio-devices
# Should show "CABLE Output" or similar
```

### Test 3: Test Each Module
```bash
# Test VAD
python vad_handler.py

# Test Audio Capture
python audio_capture.py

# Test Groq Transcriber (needs API key)
python groq_transcriber.py
```

## 🔊 Audio Routing Setup

### Windows
**Option 1: System-wide (Simple)**
- Right-click volume → Sound settings
- Set "CABLE Input" as default playback
- All audio goes to transcription

**Option 2: Browser-only (Better)**
- Open Volume Mixer (right-click volume icon)
- Find your browser
- Set it to use "CABLE Input (VB-Audio Virtual Cable)"
- Only meeting audio is captured

### Mac
1. Install BlackHole
2. Create Multi-Output Device in Audio MIDI Setup
3. Set browser to use BlackHole
4. Script captures from BlackHole

### Linux
```bash
# Create loopback
pactl load-module module-loopback

# List devices
python meeting_joiner.py --list-audio-devices
```

## 📝 Common Commands

**Basic transcription:**
```bash
python meeting_joiner.py "MEETING_URL" "Name" --transcribe --audio-device "CABLE Output"
```

**Save transcript:**
```bash
python meeting_joiner.py "MEETING_URL" "Name" --transcribe --save-transcript
```

**Long meeting (30 min):**
```bash
python meeting_joiner.py "MEETING_URL" "Name" --transcribe --duration 1800 --save-transcript
```

**Headless mode:**
```bash
python meeting_joiner.py "MEETING_URL" "Name" --transcribe --headless
```

## 🐛 Troubleshooting

### "Audio device not found"
```bash
# List devices
python meeting_joiner.py --list-audio-devices

# Copy exact device name
python meeting_joiner.py "URL" "Name" --transcribe --audio-device "EXACT DEVICE NAME"
```

### "No transcriptions"
1. Check audio is routing to virtual cable
2. Play music → should see in VB-Cable output
3. Verify GROQ_API_KEY is set
4. Check internet connection

### "VAD model download slow"
```bash
# Pre-download model
python -c "import torch; torch.hub.load('snakers4/silero-vad', 'silero_vad')"
```

## 📚 Full Documentation

- **Complete Guide:** [README_TRANSCRIPTION.md](README_TRANSCRIPTION.md)
- **Original Bot:** [README_MEETING_JOINER.md](README_MEETING_JOINER.md)
- **Examples:** [example_usage.py](example_usage.py)

## ⚡ Pro Tips

1. **Test audio first:** Play YouTube video, verify VB-Cable captures it
2. **Use wired internet:** Stable connection = better transcription
3. **Start small:** Test with 1-minute meeting first
4. **Monitor console:** Watch for errors in first few transcriptions
5. **Save transcripts:** Always use `--save-transcript` for important meetings

## 🎯 Next Steps

1. ✅ Complete setup above
2. ✅ Test with short meeting
3. ✅ Verify transcriptions are accurate
4. ✅ Adjust VAD threshold if needed
5. ✅ Use in production!

---

Need help? Check [README_TRANSCRIPTION.md](README_TRANSCRIPTION.md) for detailed troubleshooting.
