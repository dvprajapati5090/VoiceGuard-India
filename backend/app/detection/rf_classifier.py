import os
import pickle
import librosa
import numpy as np

# Adjust path based on project structure.
# From voiceguard-india/app/detection/rf_classifier.py, we go up two levels to voiceguard-india
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "voiceguard_rf_model.pkl")

class RFClassifier:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_loaded = False
        try:
            with open(MODEL_PATH, "rb") as f:
                payload = pickle.load(f)
            if isinstance(payload, dict) and 'model' in payload:
                self.model = payload['model']
                self.scaler = payload['scaler']
            else:
                self.model = payload
                self.scaler = None
            self.is_loaded = True
            print(f"[VoiceGuard] RF Model loaded: {type(self.model).__name__}, scaler={'yes' if self.scaler else 'no'}")
        except Exception as e:
            print(f"[VoiceGuard] WARNING: RF Model not found at {MODEL_PATH} — {e}")

    def extract_features(self, audio_path: str, sr: int = 16000) -> np.ndarray:
        y, _ = librosa.load(audio_path, sr=sr, duration=4.0)
        if len(y) < 1000:
            raise ValueError("Audio too short. Please upload a longer file.")
        y = librosa.util.normalize(y)
        hop = 256

        f0 = librosa.yin(y, fmin=70, fmax=500, hop_length=hop)
        f0v = f0[(f0 > 50) & (f0 < 500)]
        if len(f0v) > 5:
            f0_cv    = np.std(f0v) / (np.mean(f0v) + 1e-8)
            f0_jit   = np.mean(np.abs(np.diff(f0v))) / (np.mean(f0v) + 1e-8)
            f0_range = np.ptp(f0v) / (np.mean(f0v) + 1e-8)
            f0_smooth = np.std(np.diff(f0v))
        else:
            f0_cv = f0_jit = f0_range = f0_smooth = 0.0

        rms = librosa.feature.rms(y=y, hop_length=hop)[0]
        rms_norm    = rms / (rms.sum() + 1e-8)
        rms_cv      = np.std(rms) / (np.mean(rms) + 1e-8)
        rms_entropy = float(-np.sum(rms_norm * np.log(rms_norm + 1e-8)))

        zcr     = librosa.feature.zero_crossing_rate(y, hop_length=hop)[0]
        zcr_cv  = np.std(zcr) / (np.mean(zcr) + 1e-8)
        onset   = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
        flux_cv = np.std(onset) / (np.mean(onset) + 1e-8)

        bw  = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=hop)[0]
        cen = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop)[0]
        bw_cv  = np.std(bw)  / (np.mean(bw)  + 1e-8)
        cen_cv = np.std(cen) / (np.mean(cen) + 1e-8)

        contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=hop)
        c_mean = np.mean(contrast.T, axis=0)
        c_std  = np.std(contrast.T, axis=0)

        mfccs  = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=hop)
        m_mean = np.mean(mfccs.T, axis=0)
        m_std  = np.std(mfccs.T, axis=0)
        m_dstd = np.std(librosa.feature.delta(mfccs).T, axis=0)

        sil_ratio = float(np.mean(rms < 0.01))

        return np.hstack([
            f0_cv, f0_jit, f0_range, f0_smooth,
            rms_cv, rms_entropy,
            zcr_cv, flux_cv,
            bw_cv, cen_cv,
            c_mean, c_std,
            m_mean, m_std, m_dstd,
            sil_ratio
        ]).reshape(1, -1)

    def predict(self, features: np.ndarray) -> tuple[float, float]:
        if not self.is_loaded:
            raise RuntimeError("Model not loaded.")
        if self.scaler is not None:
            features = self.scaler.transform(features)
        
        probabilities = self.model.predict_proba(features)[0]
        prob_fake = float(probabilities[0])
        prob_auth = float(probabilities[1])
        return prob_fake, prob_auth
