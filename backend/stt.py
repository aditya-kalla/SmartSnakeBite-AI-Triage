"""
Speech-to-Text wrapper using faster-whisper.
Loads local CTranslate2 models for te/hi/ta/kn, uses faster-whisper's
auto-download "small" model (multilingual) for English AND as the
language detector for "auto" mode.
"""

import tempfile
import os
from pathlib import Path

try:
    from faster_whisper import WhisperModel
    _WHISPER_AVAILABLE = True
except ImportError as e:
    _WHISPER_AVAILABLE = False
    _WHISPER_ERROR = str(e)
    WhisperModel = None

MODELS_DIR = Path(__file__).parent / "speech" / "models" / "stt"

MODEL_PATHS = {
    "te": str(MODELS_DIR / "te"),
    "hi": str(MODELS_DIR / "hi"),
    "ta": str(MODELS_DIR / "ta"),
    "kn": str(MODELS_DIR / "kn"),
    "en": "small",
}

_loaded_models = {}


def _get_model(language: str):
    if not _WHISPER_AVAILABLE:
        return None
    if language not in _loaded_models:
        path = MODEL_PATHS.get(language, MODEL_PATHS["en"])
        _loaded_models[language] = WhisperModel(path, device="cpu", compute_type="int8")
    return _loaded_models[language]


def _detect_language(tmp_path: str) -> str:
    """
    Runs the multilingual 'small' model with language=None so Whisper's
    built-in language ID picks the spoken language. This model is
    multilingual by default (it's the base openai/whisper-small weights),
    so it can distinguish te/hi/ta/kn/en even though we only use it
    directly for English transcription elsewhere.
    """
    detector = _get_model("en")
    _, info = detector.transcribe(tmp_path, beam_size=1, language=None)
    return info.language


def transcribe_audio(audio_bytes: bytes, language: str = "auto") -> dict:
    if not _WHISPER_AVAILABLE:
        print(f"[STT WARNING] faster_whisper not installed in current Python environment ({_WHISPER_ERROR}). Please run using backend\\venv\\Scripts\\python.exe! Returning fallback transcript.")
        return {
            "transcript": "[Voice transcription unavailable — please use demo buttons or run in venv]",
            "language": "en" if language == "auto" else language,
            "detected_language": "en",
            "duration": 0.0,
        }

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        if language == "auto":
            detected = _detect_language(tmp_path)
            lang_to_use = detected if detected in MODEL_PATHS else "en"
        else:
            lang_to_use = language
            detected = language

        model = _get_model(lang_to_use)
        transcribe_lang = None if lang_to_use == "en" else lang_to_use
        segments, info = model.transcribe(tmp_path, beam_size=5, language=transcribe_lang)
        text = " ".join(seg.text.strip() for seg in segments)

        return {
            "transcript": text.strip(),
            "language": lang_to_use,
            "detected_language": detected,
            "duration": info.duration if hasattr(info, "duration") else None,
        }
    finally:
        os.unlink(tmp_path)
