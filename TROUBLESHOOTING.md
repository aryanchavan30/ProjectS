# Quick Fix for Groq Client Error

## Error: `Client.__init__() got an unexpected keyword argument 'proxies'`

### Solution 1: Update Groq Package (Recommended)

```powershell
# Uninstall current version
pip uninstall groq -y

# Install latest version
pip install groq --upgrade

# Or reinstall all requirements
pip install -r requirements.txt --upgrade
```

### Solution 2: Use Specific Groq Version

If the latest doesn't work, try a specific stable version:

```powershell
pip install groq==0.9.0
```

### Solution 3: Check Your GROQ_API_KEY

Make sure your API key is valid:

```powershell
# Windows PowerShell
echo $env:GROQ_API_KEY

# If not set:
$env:GROQ_API_KEY = "your-actual-groq-api-key-here"
```

### Test Groq Installation

```powershell
python -c "from groq import Groq; print('Groq imported successfully!')"
```

---

## Why Camera and Microphone Are Disabled

Good question! Here's why:

### The Bot's Role
The bot is a **passive listener**, not an active participant. It:
- ✅ **Receives** audio FROM the meeting (to transcribe)
- ❌ **Does NOT send** video/audio TO the meeting

### How It Works

```
Meeting Audio Output → Virtual Cable → Your PC → Transcription
     (You hear this)         ↓
                    Bot captures & transcribes
```

The bot:
1. **Joins the meeting** (so it can access the meeting stream)
2. **Mutes camera/mic** (it doesn't need to broadcast anything)
3. **Captures system audio** via Virtual Cable (CABLE Output)
4. **Transcribes** what it hears

### Why Mute?

If we DIDN'T mute:
- 🎥 **Camera ON** = Sends black/fake video to meeting (wastes bandwidth, confuses participants)
- 🎤 **Mic ON** = Could create audio feedback loop or send unwanted noise

### Audio Flow Diagram

```
┌─────────────────────────────────────────────┐
│         Google Meet / Teams                  │
│                                              │
│  [Speaker 1] → Audio Stream → [Your PC]     │
│  [Speaker 2] → Audio Stream → [Your PC]     │
│                                              │
│  Bot (Camera OFF, Mic OFF) = Silent Listener│
└─────────────────────────────────────────────┘
                     ↓
         Audio plays through speakers
                     ↓
        Routed to Virtual Cable (CABLE Input)
                     ↓
        Bot captures from CABLE Output
                     ↓
        VAD detects speech segments
                     ↓
        Groq Whisper transcribes
                     ↓
        Output to console
```

### Can I Enable Camera/Mic?

**Technically yes, but NOT recommended** because:
1. The bot uses **fake media devices** (not your real camera/mic)
2. It would send fake/black video and silent audio
3. Wastes bandwidth and looks suspicious to other participants
4. Serves no purpose for transcription

### If You Want the Bot to Speak/Show Video

You would need to:
1. Remove the camera/mic muting code in `meeting_joiner.py`
2. Provide real media streams (not fake devices)
3. Implement audio output to send pre-recorded or synthesized speech
4. Use a real webcam or video source

But for **transcription only**, muted is perfect! 👌

---

## Summary

- **Camera/Mic OFF** = Bot is a silent listener (good for transcription)
- **Audio Capture** = Via Virtual Cable, not through the meeting itself
- **The bot receives audio** but doesn't send anything

This is the standard setup for meeting bots, transcription services, and recording bots.
