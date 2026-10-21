import base64
import numpy as np

def make_silence(seconds: float = 3.0, sr: int = 16000) -> np.ndarray:
    return np.zeros(int(seconds * sr), dtype=np.float32)

def make_white_noise(seconds: float = 3.0, sr: int = 16000, amplitude: float = 0.1) -> np.ndarray:
    return (np.random.randn(int(seconds * sr)) * amplitude).astype(np.float32)

def make_sine_tone(freq: float = 440.0, seconds: float = 3.0, sr: int = 16000) -> np.ndarray:
    t = np.linspace(0, seconds, int(seconds * sr))
    return np.sin(2 * np.pi * freq * t).astype(np.float32)

def make_fake_b64_chunk(seconds: float = 3.0) -> str:
    audio = make_white_noise(seconds)
    pcm = (audio * 32767).astype(np.int16).tobytes()
    return base64.b64encode(pcm).decode()
