import base64
import numpy as np

def decode_audio_chunk(audio_b64: str, expected_sample_rate: int = 16000) -> np.ndarray:
    """
    Decode base64 string -> numpy float32 array normalized to [-1.0, 1.0].
    Assumes 16kHz mono 16-bit LE PCM input.
    """
    raw_bytes = base64.b64decode(audio_b64)
    # 16-bit PCM to float32
    audio_int16 = np.frombuffer(raw_bytes, dtype=np.int16)
    audio_float32 = audio_int16.astype(np.float32) / 32768.0
    
    # Check length (0.5s to 10s)
    duration = len(audio_float32) / expected_sample_rate
    if duration < 0.5 or duration > 10.0:
        raise ValueError(f"Audio length {duration:.2f}s is out of bounds (0.5s - 10.0s)")
        
    return audio_float32
