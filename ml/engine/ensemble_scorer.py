"""
Multi-Lingual Ensemble Spoof Scorer for Agentis Voice Verification Agent.
Supports English (en), Hindi (hi), and Gujarati (gu) voice authentication.
Combines scores from LCNN, Wav2Vec2, and Prosody analyzers into a unified confidence metric.
Dynamically loads optimal trained model weights from ml_engine/models/trained_ensemble_weights.json.

Classification Thresholds:
- PASS: Score >= 0.65 (Authentic Human Voice verified)
- AMBIGUOUS: 0.35 <= Score < 0.65 (Triggers Verification Agent Self-Correction metadata pass)
- BLOCK: Score < 0.35 (AI Voice Clone detected - Transfer Halted)
"""

import os
import json
import wave
import struct
import numpy as np

from ml_engine.models.lcnn_filter import LCNNFilter
from ml_engine.models.wav2vec2_antispoof import Wav2Vec2AntiSpoof
from ml_engine.models.prosody_analyzer import ProsodyAnalyzer

MODEL_WEIGHTS_FILE = "ml_engine/models/trained_ensemble_weights.json"

class SpoofDetectionEnsemble:
    """
    Multi-Lingual Ensemble Voice Spoof Detection Model.
    Weighted combination of spectral, acoustic embedding, and prosodic features across languages.
    """
    
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.lcnn = LCNNFilter(sample_rate=sample_rate)
        self.wav2vec2 = Wav2Vec2AntiSpoof(sample_rate=sample_rate)
        self.prosody = ProsodyAnalyzer(sample_rate=sample_rate)
        
        # Default model weights
        self.w_lcnn = 0.35
        self.w_wav2vec2 = 0.40
        self.w_prosody = 0.25
        
        # Load trained weights if available
        self.load_trained_weights()

    def load_trained_weights(self):
        """Loads trained weights from JSON artifact if present."""
        if os.path.exists(MODEL_WEIGHTS_FILE):
            try:
                with open(MODEL_WEIGHTS_FILE, "r") as f:
                    data = json.load(f)
                    tw = data.get("trained_weights", {})
                    self.w_lcnn = tw.get("w_lcnn_spectral", self.w_lcnn)
                    self.w_wav2vec2 = tw.get("w_wav2vec2_acoustic", self.w_wav2vec2)
                    self.w_prosody = tw.get("w_prosody_microtremor", self.w_prosody)
            except Exception as e:
                pass

    def load_audio_from_file(self, wav_file_path):
        """Reads PCM WAV file and converts to normalized float array."""
        try:
            with wave.open(wav_file_path, 'rb') as wf:
                num_frames = wf.getnframes()
                raw_bytes = wf.readframes(num_frames)
                samples = struct.unpack(f'<{num_frames}h', raw_bytes)
                return np.array(samples, dtype=float) / 32767.0
        except Exception as e:
            return np.zeros(16000)

    def score_audio_file(self, wav_file_path, language="en"):
        """Scores an audio file path for a specified language ('en', 'hi', 'gu')."""
        audio_signal = self.load_audio_from_file(wav_file_path)
        return self.score_signal(audio_signal, language=language)

    def score_signal(self, audio_signal, language="en"):
        """
        Evaluates audio signal through all 3 ensemble sub-models.
        Returns ensemble score, language mode, classification, and breakdown metrics.
        """
        signal = np.array(audio_signal, dtype=float)
        
        lcnn_res = self.lcnn.predict(signal)
        w2v_res = self.wav2vec2.predict(signal)
        prosody_res = self.prosody.predict(signal, language=language)
        
        ensemble_score = (
            self.w_lcnn * lcnn_res["score"] +
            self.w_wav2vec2 * w2v_res["score"] +
            self.w_prosody * prosody_res["score"]
        )
        ensemble_score = round(float(ensemble_score), 4)
        
        if ensemble_score >= 0.65:
            classification = "PASS"
            decision_text = f"Authentic Human Voice Verified (Language: {language.upper()})"
            requires_self_correction = False
        elif ensemble_score >= 0.35:
            classification = "AMBIGUOUS"
            decision_text = f"Ambiguous Acoustic Score (Language: {language.upper()}) - Requires Self-Correction Metadata Pass"
            requires_self_correction = True
        else:
            classification = "BLOCK"
            decision_text = f"AI Voice Clone Detected (Language: {language.upper()}) - High Risk Fraud Alert"
            requires_self_correction = False
            
        return {
            "ensemble_score": ensemble_score,
            "language": language,
            "classification": classification,
            "decision_explanation": decision_text,
            "requires_self_correction": requires_self_correction,
            "submodel_breakdown": {
                "lcnn_spectral_score": lcnn_res["score"],
                "wav2vec2_acoustic_score": w2v_res["score"],
                "prosody_microtremor_score": prosody_res["score"]
            },
            "model_weights_used": {
                "w_lcnn": self.w_lcnn,
                "w_wav2vec2": self.w_wav2vec2,
                "w_prosody": self.w_prosody
            },
            "detailed_metrics": {
                "lcnn": lcnn_res["metrics"],
                "wav2vec2": w2v_res["metrics"],
                "prosody": prosody_res["metrics"]
            }
        }
