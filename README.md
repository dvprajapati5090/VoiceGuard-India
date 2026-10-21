# VoiceGuard India 🛡️

> **Privacy-First, Real-Time, On-Device Deepfake Audio Detection for Indic Languages**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)

---

## Project Structure

```
AGENTIS/
├── backend/           # FastAPI microservice (deepfake detection API + WebSocket)
├── frontend/          # Single clean marketing & admin demo frontend
├── ml/                # ML training engine, notebooks, datasets
├── infra/             # AWS deployment, Elastic Beanstalk, Docker configs
├── assets/            # Shared brand assets (logos)
├── _archive/          # Legacy / deprecated code kept for reference
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Quick Start

### 1. Backend (FastAPI)

```bash
cd backend
# Activate your virtual environment:
.\venv\Scripts\activate
# Start backend server:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **WebSocket Endpoint**: `ws://localhost:8000/ws/session/new`

---

### 2. Frontend

```bash
cd frontend
npx serve .
```

- **Home & Marketing**: [http://localhost:3000](http://localhost:3000)
- **Live Demo & Mic Test**: [http://localhost:3000/admin.html](http://localhost:3000/admin.html)

---

### 3. ML Training Engine

```bash
cd ml
.\venv\Scripts\activate
python engine/train_real_rf_model.py
```

---

## License

MIT
