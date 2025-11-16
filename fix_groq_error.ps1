# Quick Fix Script for Groq Client Error
# This script uninstalls and reinstalls the correct version of the groq package

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Groq Client Error Fix - Uninstalling and Reinstalling Groq" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Uninstalling current groq package..." -ForegroundColor Yellow
pip uninstall groq -y

Write-Host ""
Write-Host "Step 2: Installing groq version 0.9.0..." -ForegroundColor Yellow
pip install groq==0.9.0

Write-Host ""
Write-Host "Step 3: Verifying installation..." -ForegroundColor Yellow
python -c "from groq import Groq; print('✓ Groq imported successfully!')"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Fix complete! You can now run your transcription bot." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Test with:" -ForegroundColor Yellow
Write-Host 'python .\meeting_joiner.py "YOUR_MEETING_URL" "Your Name" --transcribe --audio-device "CABLE Output"' -ForegroundColor White
Write-Host ""
