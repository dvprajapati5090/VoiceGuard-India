import gc
import sys
import numpy as np
import logging

logger = logging.getLogger(__name__)

class PrivacyViolationError(Exception):
    pass

class AudioSandbox:
    """
    Context manager that holds a raw audio numpy array in memory.
    On __exit__ (normal OR exception), explicitly zeros out the array
    and deletes the reference. Logs a warning if the array reference
    count is > 1 on exit (meaning something tried to store it).
    """
    def __init__(self, audio_np: np.ndarray):
        self._audio = audio_np

    def __enter__(self) -> np.ndarray:
        return self._audio

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, '_audio') and self._audio is not None:
            # Check refcount (expect 2: one for self._audio, one for getrefcount argument)
            ref_count = sys.getrefcount(self._audio)
            if ref_count > 2:
                logger.warning(f"AudioSandbox warning: Audio array ref count is {ref_count} at exit. Something may be holding a reference.")
            
            # Zero out memory
            self._audio.fill(0)
            del self._audio
            
            # Force GC to reclaim immediately
            gc.collect()
