"""
Audio Capture Module
Captures audio from virtual audio devices (VB-Cable, VAC, or system audio)
"""
import sounddevice as sd
import numpy as np
import queue
import threading
from typing import Optional, Callable, List
import time


class AudioCaptureDevice:
    """
    Captures audio from a specified input device in real-time
    """

    def __init__(
        self,
        device_name: Optional[str] = None,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_duration_ms: int = 100,
        callback: Optional[Callable] = None
    ):
        """
        Initialize Audio Capture Device

        Args:
            device_name: Name of the audio input device (None for default)
            sample_rate: Sample rate in Hz (default: 16000 for Whisper)
            channels: Number of audio channels (1 for mono, 2 for stereo)
            chunk_duration_ms: Duration of each audio chunk in milliseconds (default: 100ms, minimum 32ms for Silero VAD)
            callback: Callback function to process audio chunks
        """
        self.device_name = device_name
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_duration_ms = chunk_duration_ms
        self.callback = callback

        # Calculate chunk size in samples
        self.chunk_size = int(sample_rate * chunk_duration_ms / 1000)

        # Audio queue for buffering
        self.audio_queue = queue.Queue()

        # Stream and control
        self.stream = None
        self.is_recording = False
        self.device_index = None

        # Find device
        self._find_device()

    def _find_device(self):
        """Find the audio device by name or use default"""
        try:
            devices = sd.query_devices()

            if self.device_name is None:
                # Use default input device
                default_device = sd.query_devices(kind='input')
                self.device_index = default_device['index']
                print(f"Using default input device: {default_device['name']}")
                return

            # Search for device by name
            for idx, device in enumerate(devices):
                if self.device_name.lower() in device['name'].lower():
                    self.device_index = idx
                    print(f"Found audio device: {device['name']} (index: {idx})")
                    return

            # Device not found, list available devices
            print(f"Warning: Device '{self.device_name}' not found!")
            print("\nAvailable audio input devices:")
            self.list_devices()

            # Use default as fallback
            default_device = sd.query_devices(kind='input')
            self.device_index = default_device['index']
            print(f"\nUsing default input device as fallback: {default_device['name']}")

        except Exception as e:
            print(f"Error finding audio device: {e}")
            raise

    @staticmethod
    def list_devices():
        """List all available audio devices"""
        try:
            devices = sd.query_devices()
            print("\n" + "=" * 80)
            print("Available Audio Devices:")
            print("=" * 80)

            for idx, device in enumerate(devices):
                device_type = []
                if device['max_input_channels'] > 0:
                    device_type.append("INPUT")
                if device['max_output_channels'] > 0:
                    device_type.append("OUTPUT")

                print(f"\n[{idx}] {device['name']}")
                print(f"    Type: {', '.join(device_type)}")
                print(f"    Channels: In={device['max_input_channels']}, Out={device['max_output_channels']}")
                print(f"    Sample Rate: {device['default_samplerate']} Hz")

            print("\n" + "=" * 80)

            # Highlight common virtual audio devices
            print("\nCommon Virtual Audio Device Names:")
            print("  - VB-Cable: 'CABLE Output (VB-Audio Virtual Cable)'")
            print("  - VAC: 'Line 1 (Virtual Audio Cable)'")
            print("  - Stereo Mix: 'Stereo Mix'")
            print("  - Loopback: 'Loopback'")
            print()

        except Exception as e:
            print(f"Error listing devices: {e}")

    def _audio_callback(self, indata, frames, time_info, status):
        """
        Callback function called by sounddevice for each audio chunk

        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Time information
            status: Status flags
        """
        if status:
            print(f"Audio callback status: {status}")

        # Convert to mono if stereo
        if indata.shape[1] > 1:
            audio_data = indata.mean(axis=1)
        else:
            audio_data = indata[:, 0]

        # Add to queue
        self.audio_queue.put(audio_data.copy())

        # Call user callback if provided
        if self.callback:
            self.callback(audio_data.copy())

    def start_recording(self):
        """Start capturing audio"""
        try:
            print(f"\nStarting audio capture...")
            print(f"  Device: {self.device_index}")
            print(f"  Sample Rate: {self.sample_rate} Hz")
            print(f"  Channels: {self.channels}")
            print(f"  Chunk Size: {self.chunk_size} samples ({self.chunk_duration_ms}ms)")

            self.is_recording = True

            # Create and start audio stream
            self.stream = sd.InputStream(
                device=self.device_index,
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
                dtype=np.float32
            )

            self.stream.start()
            print("✓ Audio capture started!")

        except Exception as e:
            print(f"Error starting audio capture: {e}")
            self.is_recording = False
            raise

    def stop_recording(self):
        """Stop capturing audio"""
        try:
            print("\nStopping audio capture...")
            self.is_recording = False

            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            print("✓ Audio capture stopped!")

        except Exception as e:
            print(f"Error stopping audio capture: {e}")

    def get_audio_chunk(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        Get next audio chunk from queue

        Args:
            timeout: Timeout in seconds

        Returns:
            Audio chunk as numpy array, or None if timeout
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_device_info(self) -> dict:
        """Get information about the current audio device"""
        try:
            if self.device_index is not None:
                return sd.query_devices(self.device_index)
            return {}
        except Exception as e:
            print(f"Error getting device info: {e}")
            return {}


class ContinuousAudioCapture:
    """
    Continuous audio capture with buffering and processing
    """

    def __init__(
        self,
        device_name: Optional[str] = None,
        sample_rate: int = 16000,
        chunk_duration_ms: int = 100,
        buffer_duration_s: int = 10
    ):
        """
        Initialize Continuous Audio Capture

        Args:
            device_name: Audio device name
            sample_rate: Sample rate in Hz
            chunk_duration_ms: Chunk duration in milliseconds (default: 100ms, minimum 32ms for Silero VAD)
            buffer_duration_s: Buffer duration in seconds
        """
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        self.buffer_duration_s = buffer_duration_s

        # Calculate buffer size
        self.buffer_size = int(sample_rate * buffer_duration_s)
        self.audio_buffer = np.zeros(self.buffer_size, dtype=np.float32)
        self.buffer_index = 0

        # Create audio capture device
        self.capture_device = AudioCaptureDevice(
            device_name=device_name,
            sample_rate=sample_rate,
            channels=1,
            chunk_duration_ms=chunk_duration_ms,
            callback=self._buffer_callback
        )

        # Processing
        self.processing_thread = None
        self.is_running = False

    def _buffer_callback(self, audio_chunk: np.ndarray):
        """
        Callback to buffer audio chunks

        Args:
            audio_chunk: Audio data chunk
        """
        chunk_len = len(audio_chunk)

        # Add to circular buffer
        if self.buffer_index + chunk_len <= self.buffer_size:
            self.audio_buffer[self.buffer_index:self.buffer_index + chunk_len] = audio_chunk
            self.buffer_index += chunk_len
        else:
            # Wrap around
            remaining = self.buffer_size - self.buffer_index
            self.audio_buffer[self.buffer_index:] = audio_chunk[:remaining]
            self.audio_buffer[:chunk_len - remaining] = audio_chunk[remaining:]
            self.buffer_index = chunk_len - remaining

    def get_buffer(self) -> np.ndarray:
        """Get current audio buffer"""
        return self.audio_buffer.copy()

    def start(self):
        """Start continuous audio capture"""
        print("Starting continuous audio capture...")
        self.is_running = True
        self.capture_device.start_recording()

    def stop(self):
        """Stop continuous audio capture"""
        print("Stopping continuous audio capture...")
        self.is_running = False
        self.capture_device.stop_recording()


if __name__ == "__main__":
    # Test audio capture
    print("Audio Capture Module - Test")
    print("=" * 80)

    # List available devices
    AudioCaptureDevice.list_devices()

    # Test capture (uncomment to test with your device)
    # print("\nTesting audio capture for 5 seconds...")
    # capture = AudioCaptureDevice(device_name="CABLE Output")  # Change to your device
    # capture.start_recording()
    # time.sleep(5)
    # capture.stop_recording()
    # print("Test completed!")
