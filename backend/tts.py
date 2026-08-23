"""
TTS wrapper using ai4bharat/indic-parler-tts
"""

from pathlib import Path
import io
import numpy as np
import functools

try:
    import torch
    import soundfile as sf
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer
    _PARLER_AVAILABLE = True
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError as e:
    _PARLER_AVAILABLE = False
    _PARLER_ERROR = str(e)
    DEVICE = "cpu"

MODEL_DIR = Path(__file__).parent / "speech" / "models" / "tts" / "indic-parler-tts"

_model = None
_prompt_tokenizer = None
_description_tokenizer = None

DESCRIPTIONS = {
    "te": "Lakshmi speaks in a clear, calm, moderate pace voice, suitable for a medical alert, with minimal background noise.",
    "hi": "Rohit speaks in a clear, calm, moderate pace voice, suitable for a medical alert, with minimal background noise.",
    "ta": "Jaya speaks in a clear, calm, moderate pace voice, suitable for a medical alert, with minimal background noise.",
    "kn": "Suresh speaks in a clear, calm, moderate pace voice, suitable for a medical alert, with minimal background noise.",
    "en": "A clear, calm, moderate pace voice, suitable for a medical alert, with minimal background noise.",
}

def _generate_silent_wav() -> bytes:
    """Generates a minimal 1-second silent 16-bit PCM WAV (8000 Hz, Mono) fallback."""
    import struct
    sample_rate = 8000
    num_samples = sample_rate
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
    block_align = num_channels * (bits_per_sample // 8)
    data_size = num_samples * block_align
    chunk_size = 36 + data_size
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF', chunk_size, b'WAVE',
        b'fmt ', 16, 1, num_channels, sample_rate, byte_rate, block_align, bits_per_sample,
        b'data', data_size
    )
    return header + b'\x00' * data_size

def _load_model():
    global _model, _prompt_tokenizer, _description_tokenizer
    if not _PARLER_AVAILABLE:
        return None, None, None
    if _model is None:
        _model = ParlerTTSForConditionalGeneration.from_pretrained(str(MODEL_DIR)).to(DEVICE)
        _prompt_tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
        _description_tokenizer = AutoTokenizer.from_pretrained(
            _model.config.text_encoder._name_or_path
        )
    return _model, _prompt_tokenizer, _description_tokenizer

@functools.lru_cache(maxsize=128)
def speak(text: str, language: str = "en") -> bytes:
    if not _PARLER_AVAILABLE:
        print(f"[TTS WARNING] parler_tts not installed in current Python environment ({_PARLER_ERROR}). Please run using backend\\venv\\Scripts\\python.exe! Returning silent fallback.")
        return _generate_silent_wav()

    if not text or not text.strip():
        text = "No message."

    model, prompt_tok, desc_tok = _load_model()
    description = DESCRIPTIONS.get(language, DESCRIPTIONS["en"])

    desc_inputs = desc_tok(description, return_tensors="pt")
    prompt_inputs = prompt_tok(text, return_tensors="pt")
    
    desc_ids = desc_inputs.input_ids.to(DEVICE)
    desc_mask = desc_inputs.attention_mask.to(DEVICE)
    prompt_ids = prompt_inputs.input_ids.to(DEVICE)
    prompt_mask = prompt_inputs.attention_mask.to(DEVICE)

    with torch.no_grad():
        generation = model.generate(
            input_ids=desc_ids,
            attention_mask=desc_mask,
            prompt_input_ids=prompt_ids,
            prompt_attention_mask=prompt_mask,
            max_new_tokens=512,
        )

    audio = generation.cpu().numpy()
    if audio.ndim >= 2 and audio.shape[0] == 1:
        audio = audio[0]
    if audio.ndim > 1:
        audio = audio.squeeze()
    if audio.ndim == 0 or audio.size == 0:
        return _generate_silent_wav()
    audio = np.ascontiguousarray(audio, dtype=np.float32)
    if audio.ndim != 1:
        audio = audio.flatten()

    buf = io.BytesIO()
    sf.write(buf, audio, model.config.sampling_rate, format="WAV", subtype="PCM_16")
    buf.seek(0)
    return buf.read()
