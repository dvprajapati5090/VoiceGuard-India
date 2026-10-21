import numpy as np
import librosa

class LCNNSpectralFilter:
    def __init__(self):
        self.HIGH_FREQ_RATIO_THRESHOLD = 0.12
        self.FLATNESS_VAR_THRESHOLD = 0.008
        self.HNR_THRESHOLD = 18.0
        self.CENTROID_DRIFT_THRESHOLD = 120.0

    def score(self, audio: np.ndarray, sample_rate: int) -> float:
        try:
            mel_spec = self._compute_mel_spectrogram(audio, sample_rate)
            hf_ratio = self._high_freq_ratio(mel_spec)
            flat_var = self._spectral_flatness_variance(audio, sample_rate)
            hnr = self._harmonic_noise_ratio(audio, sample_rate)
            cd = self._centroid_drift(audio, sample_rate)
            
            score = 0.0
            if hf_ratio < self.HIGH_FREQ_RATIO_THRESHOLD: score += 0.25
            if flat_var < self.FLATNESS_VAR_THRESHOLD: score += 0.25
            if hnr > self.HNR_THRESHOLD: score += 0.25
            if cd < self.CENTROID_DRIFT_THRESHOLD: score += 0.25
            return min(1.0, score)
        except Exception:
            return 0.5

    def _compute_mel_spectrogram(self, audio, sr):
        return librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128, hop_length=512, n_fft=2048)

    def _high_freq_ratio(self, mel_spec):
        top_half = np.sum(mel_spec[64:, :])
        total = np.sum(mel_spec) + 1e-6
        return top_half / total

    def _spectral_flatness_variance(self, audio, sr):
        flatness = librosa.feature.spectral_flatness(y=audio)
        return float(np.var(flatness))

    def _harmonic_noise_ratio(self, audio, sr):
        harm = librosa.effects.harmonic(y=audio)
        noise = audio - harm
        return float(10 * np.log10(np.sum(harm**2) / (np.sum(noise**2) + 1e-6)))

    def _centroid_drift(self, audio, sr):
        centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)
        return float(np.std(centroids))
