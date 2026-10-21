# VoiceGuard India 🇮🇳
> **Privacy-First, On-Device, Real-Time Deepfake Audio Detection for Indic Languages**

Voice fraud is surging. Scammers now use 3-second audio clones to execute deepfake vishing attacks in Hindi and Gujarati, bypassing standard English-trained detection models. By the time a user uploads a recording for analysis, the scam has already succeeded. 

**VoiceGuard India** is a real-time detection system that runs silently during incoming calls, analyzing 2-second rolling chunks of audio entirely on-device, and alerting the user *before* any harm is done.

---

## 🚀 Key Features

1. **Indic-First Detection Engine**: The only deepfake detector explicitly validated on Gujarati and Hindi synthetic speech (IndicSynth / Sarvam AI TTS artifacts).
2. **Real-Time On-Device Inference**: No audio is ever sent to the cloud. Audio is cut into 2-second chunks, processed locally via Librosa and Scikit-Learn/ONNX, and immediately discarded, ensuring strict **DPDP Act 2023 Compliance**.
3. **Multi-Stage Acoustic Pipeline**:
   - **LCNN Pre-filter**: Detects high-frequency phase artifacts typical of neural vocoders.
   - **Wav2Vec2 Acoustic Scorer**: Measures latent frame representation entropy.
   - **Prosody Anomaly Check**: Inspects pitch variance (human micro-tremors vs. AI smoothness) and silence distribution.
4. **Explainable UI**: Instead of just showing a percentage, the React overlay highlights the exact 2-second segment that triggered the alert and explains *why* (e.g., "robotic silence rhythm detected").

---

## 📐 Architecture

1. **Frontend / Browser Demo (`voiceguard_frontend/`)**: React-based UI using `wavesurfer.js` to render the audio waveform, highlight anomaly regions, and display explainability metrics.
2. **FastAPI Backend (`voiceguard_backend/`)**: Receives the audio chunk, extracts MFCCs, Spectral Centroid, and Zero Crossing Rate via `librosa`, and runs inference against the trained model.
3. **ML Engine (`ml_engine/`)**: Scripts for training the Random Forest model on Kaggle using the ASVSpoof and IndicSynth datasets.

---

## 🏃 Getting Started & Local Testing

### 1. Installation
```bash
git clone https://github.com/your-org/voiceguard.git
cd voiceguard
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install fastapi uvicorn python-multipart librosa scikit-learn numpy
```

### 2. Add Your Trained Model
Download your trained `voiceguard_rf_model.pkl` from Kaggle and place it in:
`ml_engine/models/voiceguard_rf_model.pkl`

### 3. Run the Live Demo
Start the on-device inference API:
```bash
python voiceguard_backend/api.py
```
Then, double-click `voiceguard_frontend/index.html` to open the Web UI!

---

## 🧠 ML Training (Kaggle)
VoiceGuard is designed to be trained on massive cloud datasets (like ASVSpoof 2019) using Kaggle GPUs. See the `kaggle_training_guide.md` for the exact code to extract MFCC features and train the Random Forest Classifier on 50GB+ of audio data in minutes.
