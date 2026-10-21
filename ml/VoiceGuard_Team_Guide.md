# 🇮🇳 VoiceGuard India - Technical Architecture Guide

Welcome to the **VoiceGuard India** team! This document outlines the technical architecture of our Real-Time Hindi Deepfake Audio Detector so the frontend and backend teams can start building the app in parallel while the AI model finishes training on AWS.

---

## 🧠 1. The AI Engine (AWS SageMaker)
We are currently training a highly optimized **XGBoost Classifier** on AWS SageMaker. 
- **The Data:** It is trained on tens of thousands of authentic human Hindi voices (Google Fleurs, IndicTTS, UD-NLP) and AI-generated Hindi deepfakes (Abhirl/Sarvam AI).
- **The Feature Extraction:** We extract 20 MFCCs (Mel-Frequency Cepstral Coefficients), Spectral Centroids, and Zero-Crossing Rates using `librosa`.
- **The Output:** The training pipeline will output a massive `voiceguard_ultimate_model.pkl` file.

**Team Action:** Once the AWS training is complete, we will drop this `.pkl` file into the `ml_engine/models/` directory for the backend to use.

---

## ⚙️ 2. The Backend API (FastAPI)
The backend is built with **FastAPI**. It securely loads the `.pkl` AI model into RAM and exposes an endpoint for the frontend to upload audio files.

### 🔌 API Endpoint Contract
**Endpoint:** `POST /api/detect`
**Content-Type:** `multipart/form-data`
**Payload:** `file` (A `.wav`, `.mp3`, or `.flac` audio file)

**Successful Response (JSON):**
```json
{
  "filename": "suspicious_audio.wav",
  "is_deepfake": true,
  "confidence_score": 98.4,
  "processing_time_ms": 142.3,
  "explainability": {
    "reason": "High probability of AI-generated robotic artifacts detected.",
    "stage_breakdown": {
      "mfcc_artifacts": 96.2,
      "spectral_centroid": 88.1,
      "zero_crossing_rate": 99.4
    }
  }
}
```
**Team Action:** The backend team should spin up `voiceguard_backend/api.py` using `uvicorn api:app --reload`. Ensure the server is running on `localhost:8000`.

---

## 💻 3. The Frontend App (React + Wavesurfer.js)
The frontend UI is designed to be highly visual and interactive. Users upload a suspicious WhatsApp audio forward, and the app visually flags deepfake anomalies.

### Key Technologies
- **React.js:** Component architecture.
- **Tailwind CSS:** For the futuristic red/green security UI.
- **Wavesurfer.js:** To render the audio waveform visually in the browser.

### The UI Flow
1. **Upload State:** User drops an audio file into the Dropzone.
2. **Scanning State:** The frontend displays a scanning animation while it sends the file to `POST /api/detect`.
3. **Results State:** 
   - If `is_deepfake == true`, the Wavesurfer waveform turns **Red**, and the `explainability.stage_breakdown` metrics are displayed in warning cards.
   - If `is_deepfake == false`, the UI turns **Green** (Authentic Human).

**Team Action:** The frontend team can open `voiceguard_frontend/index.html` in their browser and start styling the UI. You can mock the API response using the JSON contract above until the real AI model is attached!

---

## 🔒 4. Compliance (DPDP Act 2023)
To ensure compliance with the **Digital Personal Data Protection (DPDP) Act of 2023**:
- VoiceGuard India operates strictly **on-device/edge** (or securely in memory).
- No uploaded audio files are ever saved to the hard drive. They are processed in temporary RAM and immediately purged.
- No PII (Personal Identifiable Information) or speaker identity is stored.

Let's build this and protect India from AI fraud! 🚀
