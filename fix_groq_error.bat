@echo off
REM Quick Fix Script for Groq Client Error
REM This script uninstalls and reinstalls the correct version of the groq package

echo ============================================================
echo Groq Client Error Fix - Uninstalling and Reinstalling Groq
echo ============================================================
echo.

echo Step 1: Uninstalling current groq package...
pip uninstall groq -y

echo.
echo Step 2: Installing groq version 0.9.0...
pip install groq==0.9.0

echo.
echo Step 3: Verifying installation...
python -c "from groq import Groq; print('✓ Groq imported successfully!')"

echo.
echo ============================================================
echo Fix complete! You can now run your transcription bot.
echo ============================================================
echo.
echo Test with:
echo python meeting_joiner.py "YOUR_MEETING_URL" "Your Name" --transcribe --audio-device "CABLE Output"
echo.
pause
