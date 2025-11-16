"""
Groq Whisper Transcription Module
Uses Groq's Whisper API for fast, accurate speech-to-text transcription
"""
import os
import io
import wave
import numpy as np
from groq import Groq
from typing import Optional, Dict, List
import tempfile
from datetime import datetime


class GroqTranscriber:
    """
    Handles speech-to-text transcription using Groq's Whisper API
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "whisper-large-v3-turbo",
        language: str = "en",
        temperature: float = 0.0
    ):
        """
        Initialize Groq Transcriber

        Args:
            api_key: Groq API key (will use GROQ_API_KEY env var if not provided)
            model: Whisper model to use (whisper-large-v3-turbo or whisper-large-v3)
            language: Language code (ISO-639-1 format, e.g., 'en' for English)
            temperature: Sampling temperature (0.0 to 1.0)
        """
        # Get API key
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Groq API key not found! "
                "Set GROQ_API_KEY environment variable or pass api_key parameter."
            )

        # Initialize Groq client
        try:
            self.client = Groq(api_key=self.api_key)
        except TypeError as e:
            # Handle version compatibility issues
            if "proxies" in str(e):
                # Try without proxies argument (for older versions)
                import groq
                self.client = groq.Client(api_key=self.api_key)
            else:
                raise

        # Configuration
        self.model = model
        self.language = language
        self.temperature = temperature

        # Validate model
        valid_models = ["whisper-large-v3", "whisper-large-v3-turbo"]
        if self.model not in valid_models:
            print(f"Warning: Model '{self.model}' may not be supported.")
            print(f"Recommended models: {', '.join(valid_models)}")

        print(f"✓ Groq Transcriber initialized with model: {self.model}")

    def _numpy_to_wav_bytes(self, audio: np.ndarray, sample_rate: int = 16000) -> bytes:
        """
        Convert numpy array to WAV bytes

        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            WAV file as bytes
        """
        # Ensure audio is float32
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Normalize to [-1, 1] if needed
        if audio.max() > 1.0 or audio.min() < -1.0:
            audio = audio / np.abs(audio).max()

        # Convert to int16
        audio_int16 = (audio * 32767).astype(np.int16)

        # Create WAV file in memory
        with io.BytesIO() as wav_buffer:
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes per sample (int16)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())

            wav_bytes = wav_buffer.getvalue()

        return wav_bytes

    def transcribe_numpy(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000,
        prompt: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio from numpy array

        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate in Hz
            prompt: Optional prompt to guide the transcription

        Returns:
            Dictionary containing transcription results
        """
        try:
            # Convert numpy to WAV bytes
            wav_bytes = self._numpy_to_wav_bytes(audio, sample_rate)

            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(wav_bytes)
                temp_path = temp_file.name

            try:
                # Transcribe using Groq API
                with open(temp_path, 'rb') as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        file=(temp_path, audio_file.read()),
                        model=self.model,
                        prompt=prompt,
                        response_format="verbose_json",
                        language=self.language,
                        temperature=self.temperature
                    )

                # Parse response
                result = {
                    'text': transcription.text,
                    'language': getattr(transcription, 'language', self.language),
                    'duration': getattr(transcription, 'duration', None),
                    'segments': getattr(transcription, 'segments', []),
                    'timestamp': datetime.now().isoformat()
                }

                return result

            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return {
                'text': '',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def transcribe_file(self, file_path: str, prompt: Optional[str] = None) -> Dict:
        """
        Transcribe audio from file

        Args:
            file_path: Path to audio file (WAV, MP3, FLAC, etc.)
            prompt: Optional prompt to guide the transcription

        Returns:
            Dictionary containing transcription results
        """
        try:
            with open(file_path, 'rb') as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=(file_path, audio_file.read()),
                    model=self.model,
                    prompt=prompt,
                    response_format="verbose_json",
                    language=self.language,
                    temperature=self.temperature
                )

            # Parse response
            result = {
                'text': transcription.text,
                'language': getattr(transcription, 'language', self.language),
                'duration': getattr(transcription, 'duration', None),
                'segments': getattr(transcription, 'segments', []),
                'timestamp': datetime.now().isoformat()
            }

            return result

        except Exception as e:
            print(f"Error transcribing file: {e}")
            return {
                'text': '',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_word_timestamps(self, result: Dict) -> List[Dict]:
        """
        Extract word-level timestamps from transcription result

        Args:
            result: Transcription result from transcribe_numpy or transcribe_file

        Returns:
            List of words with timestamps
        """
        words = []

        if 'segments' in result and result['segments']:
            for segment in result['segments']:
                if hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        words.append({
                            'word': word.word,
                            'start': word.start,
                            'end': word.end
                        })

        return words


class TranscriptionBuffer:
    """
    Buffers and manages transcription results
    """

    def __init__(self, max_history: int = 100):
        """
        Initialize transcription buffer

        Args:
            max_history: Maximum number of transcriptions to keep in history
        """
        self.max_history = max_history
        self.transcriptions = []

    def add(self, text: str, speaker: Optional[str] = None, metadata: Optional[Dict] = None):
        """
        Add transcription to buffer

        Args:
            text: Transcribed text
            speaker: Speaker name (optional)
            metadata: Additional metadata (optional)
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'text': text,
            'speaker': speaker,
            'metadata': metadata or {}
        }

        self.transcriptions.append(entry)

        # Trim history if needed
        if len(self.transcriptions) > self.max_history:
            self.transcriptions = self.transcriptions[-self.max_history:]

    def get_recent(self, count: int = 10) -> List[Dict]:
        """
        Get recent transcriptions

        Args:
            count: Number of recent transcriptions to retrieve

        Returns:
            List of recent transcription entries
        """
        return self.transcriptions[-count:]

    def get_all(self) -> List[Dict]:
        """Get all transcriptions"""
        return self.transcriptions.copy()

    def clear(self):
        """Clear all transcriptions"""
        self.transcriptions = []

    def format_output(self, entry: Dict) -> str:
        """
        Format transcription entry for display

        Args:
            entry: Transcription entry

        Returns:
            Formatted string
        """
        timestamp = entry['timestamp'].split('T')[1].split('.')[0]  # Get time only
        speaker = entry.get('speaker', 'Unknown')
        text = entry.get('text', '')

        return f"[{timestamp}] {speaker}: {text}"

    def print_recent(self, count: int = 10):
        """
        Print recent transcriptions

        Args:
            count: Number of recent transcriptions to print
        """
        recent = self.get_recent(count)

        if not recent:
            print("No transcriptions yet.")
            return

        print("\n" + "=" * 80)
        print("Recent Transcriptions:")
        print("=" * 80)

        for entry in recent:
            print(self.format_output(entry))

        print("=" * 80 + "\n")


if __name__ == "__main__":
    # Test Groq Transcriber
    print("Groq Transcriber - Test")
    print("=" * 80)

    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set!")
        print("Set it with: export GROQ_API_KEY='your-api-key'")
    else:
        transcriber = GroqTranscriber()
        print("Groq Transcriber initialized successfully!")

        # Test with sample audio (uncomment to test)
        # sample_audio = np.random.randn(16000).astype(np.float32) * 0.1
        # result = transcriber.transcribe_numpy(sample_audio, sample_rate=16000)
        # print(f"Result: {result}")
