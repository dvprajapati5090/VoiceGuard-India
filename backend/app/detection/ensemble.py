import numpy as np
import time
from app.detection.spectral_filter import LCNNSpectralFilter
from app.detection.acoustic_model import XLSRAcousticModel
from app.detection.prosody_analyzer import ProsodyAnalyzer

class EnsembleScorer:
    def __init__(self):
        self.spectral = LCNNSpectralFilter()
        self.acoustic = XLSRAcousticModel.get_instance()
        self.prosody = ProsodyAnalyzer()
    
    def score_chunk(self, audio: np.ndarray, language: str, sample_rate: int = 16000) -> tuple[int, int]:
        start = time.time()
        
        s_score = self.spectral.score(audio, sample_rate)
        p_score = self.prosody.score(audio, sample_rate)
        
        if s_score > 0.85:
            final_float = s_score * 0.8 + p_score * 0.2
        else:
            a_score = self.acoustic.score(audio, sample_rate, language)
            final_float = s_score * 0.3 + a_score * 0.5 + p_score * 0.2
            
        final_int = int(final_float * 100)
        final_int = max(0, min(100, final_int))
        
        proc_ms = int((time.time() - start) * 1000)
        return final_int, proc_ms
    
    def compute_final_verdict(self, chunk_scores: list[int]) -> tuple[str, float]:
        if not chunk_scores:
            return "INCONCLUSIVE", 0.0
            
        avg = np.mean(chunk_scores)
        std = np.std(chunk_scores)
        mx = np.max(chunk_scores)
        
        is_synth = False
        
        if mx > 90:
            is_synth = True
        elif avg > 55:
            is_synth = True
        else:
            for i in range(len(chunk_scores) - 1):
                if chunk_scores[i] > 70 and chunk_scores[i+1] > 70:
                    is_synth = True
                    break
                    
        is_auth = all(c < 40 for c in chunk_scores)
        
        if is_synth:
            verdict = "SYNTHETIC"
        elif is_auth:
            verdict = "AUTHENTIC"
        else:
            verdict = "INCONCLUSIVE"
            
        conf = 1.0 - (float(std) / 50.0)
        conf = max(0.0, min(1.0, conf))
        return verdict, conf

