# Quick Start Guide

Get started with Meeting Transcription Bot in 5 minutes!

## 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

## 2. Get Groq API Key

1. Visit: https://console.groq.com/
2. Sign up (free)
3. Create API key
4. Copy the key

## 3. Set API Key (Windows)

**PowerShell:**
```powershell
$env:GROQ_API_KEY="your_api_key_here"
```

**Command Prompt:**
```cmd
set GROQ_API_KEY=your_api_key_here
```

## 4. Run Your First Meeting

```bash
python meeting_joiner.py "https://meet.google.com/your-meeting-code" "Bot Name" --duration 300
```

That's it! The bot will:
- ✓ Join the meeting
- ✓ Capture audio from your speakers
- ✓ Detect when people speak (Silero VAD)
- ✓ Transcribe with Groq Whisper
- ✓ Identify speakers from UI
- ✓ Save to `transcription.txt`

## Example Output

```
[2025-01-15 14:32:10] John Doe: Hello everyone, welcome to the meeting.
[2025-01-15 14:32:15] Jane Smith: Thanks for joining.
```

## Next Steps

- Read `README.md` for detailed documentation
- Check `example_usage.py` for Python code examples
- Adjust VAD sensitivity if needed (see README)
- Try headless mode: `--headless`

## Troubleshooting

**No audio?**
```bash
# List audio devices
python -m pyaudiowpatch
```

**No transcriptions?**
- Check API key is set: `echo %GROQ_API_KEY%`
- Make sure someone is speaking in the meeting
- Try lowering VAD threshold (see README)

**Speaker names showing "Unknown"?**
- Wait 5-10 seconds for UI scraping to start
- Check console for errors
- Try non-headless mode to see the browser

## Need Help?

1. Check console output for errors
2. Read full README.md
3. Review example_usage.py
