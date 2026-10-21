import pytest
import numpy as np
from app.detection.spectral_filter import LCNNSpectralFilter
from app.detection.prosody_analyzer import ProsodyAnalyzer
from app.detection.ensemble import EnsembleScorer
from app.utils.privacy_guard import AudioSandbox
import sys

def test_spectral_filter_returns_0_to_1():
    sf = LCNNSpectralFilter()
    audio = np.random.randn(48000).astype(np.float32) * 0.1
    score = sf.score(audio, 16000)
    assert 0.0 <= score <= 1.0

def test_prosody_analyzer_returns_0_to_1():
    pa = ProsodyAnalyzer()
    audio = np.random.randn(48000).astype(np.float32) * 0.1
    score = pa.score(audio, 16000)
    assert 0.0 <= score <= 1.0

def test_ensemble_score_range():
    scorer = EnsembleScorer()
    audio = np.random.randn(48000).astype(np.float32) * 0.1
    score, ms = scorer.score_chunk(audio, "hi", 16000)
    assert 0 <= score <= 100
    assert ms >= 0

def test_audio_sandbox_zeros_memory():
    audio = np.ones(1000, dtype=np.float32)
    with AudioSandbox(audio) as box:
        assert box[0] == 1.0
    
    assert audio[0] == 0.0

def test_final_verdict_consecutive_high():
    scorer = EnsembleScorer()
    v, _ = scorer.compute_final_verdict([80, 85, 90])
    assert v == "SYNTHETIC"

def test_final_verdict_all_low():
    scorer = EnsembleScorer()
    v, _ = scorer.compute_final_verdict([5, 8, 12])
    assert v == "AUTHENTIC"
