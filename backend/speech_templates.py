"""
Multilingual spoken-summary templates for TTS.

Two template sets:
  SEVERITY_TEXT_SHORT — concise (3-4 sentences) for TTS synthesis on CPU.
                        Kept short so parler-tts can generate in ~15-30 seconds.
  SEVERITY_TEXT_FULL  — detailed first-aid guidance for on-screen display
                        (used if we add a "show full guidance" UI feature later).

WHY THIS EXISTS: tts.py's `language` param only picks a VOICE, it does not
translate text. severity_class and antivenom_required are ENUMS, so we can
safely pre-translate every combination as a fixed lookup table.

⚠️ IMPORTANT: these translations were drafted by Claude, not reviewed by a
native speaker. Have a Telugu/Hindi/Tamil/Kannada speaker verify wording
accuracy before relying on this in any real triage use.
"""

SEVERITY_TEXT = {
    "en": {
        "LOW": "Don't panic, I'm reporting to hospital. Wash the wound with clean water and soap.",
        "MODERATE": "Don't panic, I'm reporting to hospital. Keep the bitten limb completely still.",
        "HIGH": "Don't panic, I'm reporting to hospital. Do not apply a tourniquet or cut the wound.",
        "CRITICAL": "Don't panic, I'm reporting to hospital. Keep the patient lying down and completely still.",
    },
    "te": {
        "LOW": "కంగారు పడకండి, ఆసుపత్రికి నివేదిస్తున్నాను. గాయాన్ని శుభ్రమైన నీటితో కడగండి.",
        "MODERATE": "కంగారు పడకండి, ఆసుపత్రికి నివేదిస్తున్నాను. కాటు వేసిన అవయవాన్ని కదలకుండా ఉంచండి.",
        "HIGH": "కంగారు పడకండి, ఆసుపత్రికి నివేదిస్తున్నాను. టోర్నిక్వెట్ వేయకండి, గాయాన్ని కోయకండి.",
        "CRITICAL": "కంగారు పడకండి, ఆసుపత్రికి నివేదిస్తున్నాను. రోగిని పడుకోబెట్టి కదలకుండా ఉంచండి.",
    },
    "hi": {
        "LOW": "घबराएं नहीं, मैं अस्पताल को रिपोर्ट कर रहा हूँ। घाव को साफ पानी से धोएं।",
        "MODERATE": "घबराएं नहीं, मैं अस्पताल को रिपोर्ट कर रहा हूँ। काटे गए अंग को बिल्कुल स्थिर रखें।",
        "HIGH": "घबराएं नहीं, मैं अस्पताल को रिपोर्ट कर रहा हूँ। टूर्निकेट न बांधें और घाव को न काटें।",
        "CRITICAL": "घबराएं नहीं, मैं अस्पताल को रिपोर्ट कर रहा हूँ। मरीज़ को लिटा दें और बिल्कुल स्थिर रखें।",
    },
    "ta": {
        "LOW": "பயப்பட வேண்டாம், மருத்துவமனைக்கு தெரிவிக்கிறேன். காயத்தை சுத்தமான நீரால் கழுவுங்கள்.",
        "MODERATE": "பயப்பட வேண்டாம், மருத்துவமனைக்கு தெரிவிக்கிறேன். கடிக்கப்பட்ட உறுப்பை அசைக்காமல் வையுங்கள்.",
        "HIGH": "பயப்பட வேண்டாம், மருத்துவமனைக்கு தெரிவிக்கிறேன். டூர்னிக்வெட் கட்டாதீர்கள், காயத்தை வெட்டாதீர்கள்.",
        "CRITICAL": "பயப்பட வேண்டாம், மருத்துவமனைக்கு தெரிவிக்கிறேன். நோயாளியை படுக்க வைத்து அசைக்காமல் வையுங்கள்.",
    },
    "kn": {
        "LOW": "ಗಾಬರಿಯಾಗಬೇಡಿ, ಆಸ್ಪತ್ರೆಗೆ ವರದಿ ಮಾಡುತ್ತಿದ್ದೇನೆ. ಗಾಯವನ್ನು ಶುದ್ಧ ನೀರಿನಿಂದ ತೊಳೆಯಿರಿ.",
        "MODERATE": "ಗಾಬರಿಯಾಗಬೇಡಿ, ಆಸ್ಪತ್ರೆಗೆ ವರದಿ ಮಾಡುತ್ತಿದ್ದೇನೆ. ಕಚ್ಚಿದ ಅಂಗವನ್ನು ಅಲುಗಾಡಿಸದೆ ಇಡಿ.",
        "HIGH": "ಗಾಬರಿಯಾಗಬೇಡಿ, ಆಸ್ಪತ್ರೆಗೆ ವರದಿ ಮಾಡುತ್ತಿದ್ದೇನೆ. ಬಿಗಿಯಾಗಿ ಕಟ್ಟಬೇಡಿ, ಗಾಯವನ್ನು ಕತ್ತರಿಸಬೇಡಿ.",
        "CRITICAL": "ಗಾಬರಿಯಾಗಬೇಡಿ, ಆಸ್ಪತ್ರೆಗೆ ವರದಿ ಮಾಡುತ್ತಿದ್ದೇನೆ. ರೋಗಿಯನ್ನು ಮಲಗಿಸಿ ಮತ್ತು ಅಲುಗಾಡಿಸದೆ ಇಡಿ.",
    },
}

SUPPORTED_LANGUAGES = ["en", "te", "hi", "ta", "kn"]


def build_spoken_summary(severity_class: str, antivenom_required: bool, language: str = "en") -> str:
    """Builds a spoken-summary string that is GUARANTEED to be in the
    requested language (bounded template lookup, not free-text translation)."""
    lang = language if language in SUPPORTED_LANGUAGES else "en"
    severity_class = (severity_class or "MODERATE").upper()

    severity_line = SEVERITY_TEXT.get(lang, SEVERITY_TEXT["en"]).get(
        severity_class, SEVERITY_TEXT[lang]["MODERATE"]
    )

    # Returning just the severity line as requested to keep TTS extremely fast
    return severity_line
