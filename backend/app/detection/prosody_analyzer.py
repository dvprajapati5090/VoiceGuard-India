import numpy as np
import librosa

class ProsodyAnalyzer:
    def score(self, audio: np.ndarray, sample_rate: int) -> float:
        try:
            f0, voiced_flag, _ = librosa.pyin(audio, fmin=50, fmax=500, sr=sample_rate)
            valid_f0 = f0[voiced_flag] if f0 is not None and len(f0[voiced_flag]) > 0 else []
            
            pitch_flag = 1 if len(valid_f0) > 0 and np.std(valid_f0) < 8 else 0
            
            shimmer_flag = 1
            zcr = librosa.feature.zero_crossing_rate(audio)
            zcr_flag = 1 if np.var(zcr) < 0.001 else 0
            
            rms = librosa.feature.rms(y=audio)
            energy_flag = 1 if np.std(rms) < 0.01 else 0
            
            return pitch_flag * 0.35 + shimmer_flag * 0.25 + zcr_flag * 0.20 + energy_flag * 0.20
        except Exception:
            return 0.5
