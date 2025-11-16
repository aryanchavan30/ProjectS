"""
Voice Activity Detection (VAD) Handler using Silero VAD
Detects speech segments in real-time audio streams
"""
import torch
import numpy as np
from typing import Optional, Tuple


class VADHandler:
    """
    Handles Voice Activity Detection using Silero VAD model
    """

    def __init__(self, sample_rate: int = 16000, threshold: float = 0.5):
        """
        Initialize VAD Handler

        Args:
            sample_rate: Audio sample rate in Hz (default: 16000)
            threshold: VAD confidence threshold (0.0 to 1.0, default: 0.5)
        """
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.model = None
        self.utils = None
        self._load_model()

    def _load_model(self):
        """Load the Silero VAD model"""
        try:
            print("Loading Silero VAD model...")

            # Load Silero VAD model from torch hub
            self.model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )

            # Get utility functions
            (self.get_speech_timestamps,
             self.save_audio,
             self.read_audio,
             self.VADIterator,
             self.collect_chunks) = self.utils

            print("✓ Silero VAD model loaded successfully!")

        except Exception as e:
            print(f"Error loading Silero VAD model: {e}")
            print("Make sure torch and torchaudio are installed: pip install torch torchaudio")
            raise

    def is_speech(self, audio_chunk: np.ndarray) -> Tuple[bool, float]:
        """
        Detect if audio chunk contains speech

        Args:
            audio_chunk: Audio data as numpy array (shape: [samples] or [samples, channels])

        Returns:
            Tuple of (is_speech: bool, confidence: float)
        """
        try:
            # Convert to float32 if needed
            if audio_chunk.dtype != np.float32:
                audio_chunk = audio_chunk.astype(np.float32)

            # Handle stereo to mono conversion
            if len(audio_chunk.shape) > 1:
                audio_chunk = audio_chunk.mean(axis=1)

            # Normalize audio to [-1, 1] range if needed
            if audio_chunk.max() > 1.0 or audio_chunk.min() < -1.0:
                audio_chunk = audio_chunk / np.abs(audio_chunk).max()

            # Silero VAD requires EXACTLY 512 samples for 16kHz (or 256 for 8kHz)
            # Calculate required sample count based on sample rate
            if self.sample_rate == 16000:
                required_samples = 512
            elif self.sample_rate == 8000:
                required_samples = 256
            else:
                # For other sample rates, estimate
                required_samples = 512 if self.sample_rate > 12000 else 256

            # Ensure chunk is exactly the required length
            if len(audio_chunk) < required_samples:
                # Pad with zeros if too short
                padded = np.zeros(required_samples, dtype=np.float32)
                padded[:len(audio_chunk)] = audio_chunk
                audio_chunk = padded
            elif len(audio_chunk) > required_samples:
                # Trim if too long (take first N samples)
                audio_chunk = audio_chunk[:required_samples]

            # Convert to torch tensor
            audio_tensor = torch.from_numpy(audio_chunk)

            # Get VAD confidence
            confidence = self.model(audio_tensor, self.sample_rate).item()

            # Determine if speech based on threshold
            is_speech = confidence >= self.threshold

            return is_speech, confidence

        except Exception as e:
            print(f"Error in VAD detection: {e}")
            return False, 0.0

    def get_speech_segments(self, audio: np.ndarray) -> list:
        """
        Get speech timestamps from longer audio

        Args:
            audio: Audio data as numpy array

        Returns:
            List of speech segments with start and end timestamps
        """
        try:
            # Convert to float32 if needed
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            # Handle stereo to mono conversion
            if len(audio.shape) > 1:
                audio = audio.mean(axis=1)

            # Normalize audio
            if audio.max() > 1.0 or audio.min() < -1.0:
                audio = audio / np.abs(audio).max()

            # Convert to torch tensor
            audio_tensor = torch.from_numpy(audio)

            # Get speech timestamps
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor,
                self.model,
                sampling_rate=self.sample_rate,
                threshold=self.threshold,
                min_speech_duration_ms=250,  # Minimum speech duration
                min_silence_duration_ms=100   # Minimum silence between speech
            )

            return speech_timestamps

        except Exception as e:
            print(f"Error getting speech segments: {e}")
            return []

    def set_threshold(self, threshold: float):
        """
        Update VAD threshold

        Args:
            threshold: New threshold value (0.0 to 1.0)
        """
        if 0.0 <= threshold <= 1.0:
            self.threshold = threshold
            print(f"VAD threshold updated to: {threshold}")
        else:
            print(f"Invalid threshold: {threshold}. Must be between 0.0 and 1.0")


class StreamingVAD:
    """
    Streaming VAD for real-time audio processing
    Maintains state across audio chunks
    """

    def __init__(self, sample_rate: int = 16000, threshold: float = 0.5):
        """
        Initialize Streaming VAD

        Args:
            sample_rate: Audio sample rate in Hz
            threshold: VAD confidence threshold
        """
        self.vad_handler = VADHandler(sample_rate, threshold)
        self.sample_rate = sample_rate
        self.is_speaking = False
        self.speech_buffer = []
        self.silence_counter = 0
        self.max_silence_chunks = 10  # Number of silent chunks before ending speech
        self.chunk_counter = 0  # For debug output
        self.debug_interval = 100  # Print debug every N chunks

    def process_chunk(self, audio_chunk: np.ndarray) -> Optional[np.ndarray]:
        """
        Process audio chunk and return complete speech segment when detected

        Args:
            audio_chunk: Audio data chunk

        Returns:
            Complete speech segment when speech ends, None otherwise
        """
        is_speech, confidence = self.vad_handler.is_speech(audio_chunk)

        # Debug output every N chunks
        self.chunk_counter += 1
        if self.chunk_counter % self.debug_interval == 0:
            print(f"[VAD DEBUG] Chunk {self.chunk_counter}: confidence={confidence:.3f}, threshold={self.vad_handler.threshold:.3f}, is_speech={is_speech}, speaking={self.is_speaking}")

        if is_speech:
            # Speech detected
            if not self.is_speaking:
                print(f"[VAD] Speech started! (confidence: {confidence:.3f})")
            self.is_speaking = True
            self.silence_counter = 0
            self.speech_buffer.append(audio_chunk)
            return None

        else:
            # No speech detected
            if self.is_speaking:
                # We were speaking, count silence
                self.silence_counter += 1
                self.speech_buffer.append(audio_chunk)

                # Check if silence duration exceeded threshold
                if self.silence_counter >= self.max_silence_chunks:
                    # Speech segment ended
                    print(f"[VAD] Speech ended! Buffer size: {len(self.speech_buffer)} chunks")
                    complete_segment = np.concatenate(self.speech_buffer)

                    # Reset state
                    self.is_speaking = False
                    self.speech_buffer = []
                    self.silence_counter = 0

                    return complete_segment

            return None

    def reset(self):
        """Reset VAD state"""
        self.is_speaking = False
        self.speech_buffer = []
        self.silence_counter = 0


if __name__ == "__main__":
    # Test the VAD handler
    print("Testing VAD Handler...")

    vad = VADHandler(sample_rate=16000, threshold=0.5)
    print("VAD Handler initialized successfully!")

    # Create a test audio chunk (1 second of random noise)
    test_audio = np.random.randn(16000).astype(np.float32) * 0.1

    is_speech, confidence = vad.is_speech(test_audio)
    print(f"Test chunk - Is speech: {is_speech}, Confidence: {confidence:.3f}")
