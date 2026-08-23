# SmartSnakebite AI Triage

**An AI-powered clinical decision support system for rapid snakebite triage.**
Bridging the gap between rural healthcare delays and immediate, life-saving medical intervention.

## The Vision

In remote areas, snakebite envenomation is a critical medical emergency where time is the most crucial factor. Misdiagnosis, language barriers, and lack of immediate medical expertise often lead to fatal delays. 

SmartSnakebite solves this by introducing a localized, intelligent triage architecture:
- **The Voice Intake (Edge STT)**: A fast, offline multilingual speech-to-text engine (`faster-whisper`) that allows patients or bystanders to report symptoms naturally in their native language (Hindi, Telugu, Tamil, Kannada, English).
- **The Clinical Engine**: An automated diagnostic reasoning pipeline that analyzes symptoms to categorize the bite severity (Low, Moderate, High, Critical) and determines the immediate necessity of antivenom.
- **The Acoustic Alert (Edge TTS)**: An offline text-to-speech module (`indic-parler-tts`) that instantly broadcasts localized safety instructions (e.g., "Keep the bitten limb still") without requiring internet connectivity.

## Architecture & Modules

The application is built around a decoupled frontend-backend architecture to ensure high performance and clinical reliability:

- **Frontend (React & Vite)**: A responsive, decoupled clinical triage workspace. It provides a real-time dashboard for healthcare workers to track incoming cases, view patient histories, and manage the triage queue.
- **Backend (FastAPI & SQLite)**: A stateless API layer managing the clinical reasoning logic, model inference, and persistent data storage.
- **Report Generation**: Instant synthesis of PDF and DOCX clinical summaries for rapid hospital handoffs.
- **Visual Classification (Optional)**: A PyTorch-based machine learning module designed to identify snake species from uploaded photographs.

## Quick Start (Local Deployment)

To run the full-stack demonstration locally:

### Prerequisites
- Python 3.9+
- Node.js & npm

### 1. Start the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```
*(Alternatively, on Windows, execute `start_backend.bat`)*

### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

Navigate to `http://localhost:5173` to view the live dashboard and triage workspace.

## What's Next

- **Diagnostic Expansion**: Enhancing the clinical engine with multimodal inputs (combining visual bite-mark analysis with acoustic symptom reporting).
- **Hardware Integration**: Deploying the lightweight STT and TTS models directly onto low-power edge devices for field workers.
- **Expanded Dialects**: Broadening the acoustic models to support highly localized rural dialects across the Indian subcontinent.
