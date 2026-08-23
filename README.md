# 🐍 SmartSnakebite AI Triage

**SmartSnakebite** is an AI-powered clinical decision support system designed to assist medical professionals, first responders, and rural populations in rapid snakebite triage. Built for speed and reliability, it features multilingual voice intake, automated clinical reasoning, and on-device text-to-speech for critical emergency response.

## ✨ Key Features

- **🗣️ Multilingual Voice Intake**: Native speech-to-text (STT) support for English, Hindi, Telugu, Tamil, and Kannada using offline `faster-whisper`.
- **🏥 Clinical Reasoning Engine**: Analyzes patient symptoms to automatically categorize bite severity (Low, Moderate, High, Critical) and determine antivenom necessity.
- **🔊 On-Device TTS Alerts**: Generates immediate, localized spoken alerts using `indic-parler-tts` to guide immediate safety actions without requiring an internet connection.
- **📊 Patient Case Dashboard**: Persistent SQLite-backed dashboard to track incoming triage cases, manage patient histories, and review past incidents.
- **📄 Instant Medical Reports**: One-click generation of PDF and DOCX clinical summaries for rapid hospital handoffs.
- **🔍 Visual Snake Identification**: Integrated machine learning image classification module to identify snake species from photos.

## 🛠️ Technology Stack

- **Frontend**: React.js, Vite, Vanilla CSS (Responsive, decoupled triage workspace)
- **Backend**: FastAPI, Python, SQLite (High-performance API with lightweight persistent storage)
- **AI/ML**: `faster-whisper` (Speech-to-Text), `indic-parler-tts` (Text-to-Speech), PyTorch (Image Classification)

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js & npm

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aditya-kalla/SmartSnakeBite-AI-Triage.git
   cd SmartSnakeBite-AI-Triage
   ```

2. **Start the Backend**
   Navigate to the `backend` directory, activate your virtual environment, install dependencies, and start the FastAPI server:
   ```bash
   cd backend
   python -m venv venv
   # On Windows use: venv\Scripts\activate
   # On Mac/Linux use: source venv/bin/activate
   pip install -r requirements.txt
   python -m uvicorn main:app --port 8000
   ```
   *(Alternatively, on Windows, you can simply run the provided `start_backend.bat` script.)*

3. **Start the Frontend**
   Open a new terminal, navigate to the `frontend` directory, install the required packages, and run the development server:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the App**
   Open your browser and navigate to `http://localhost:5173`.

## 🤝 Contributing

Contributions are welcome! If you'd like to improve the clinical reasoning, add new languages, or enhance the UI, please feel free to fork the repository and submit a pull request.

## 📄 License

This project is licensed under the MIT License.
