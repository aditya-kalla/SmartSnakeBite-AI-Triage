"""
A-M3: Harmful Practice Detector
Detects dangerous first aid in patient narrative across 5 languages.
"""

import json
import re
from pathlib import Path

BASE = Path(__file__).parent
KB   = BASE / "knowledge_base"

with open(KB / "harmful_phrases.json",    encoding="utf-8") as f:
    HARMFUL_PHRASES = json.load(f)

with open(KB / "corrective_messages.json", encoding="utf-8") as f:
    CORRECTIVE_MESSAGES = json.load(f)

LANGUAGES = ["english", "telugu", "hindi", "kannada", "tamil"]

SEVERITY_RANK = {
    "electric_shock":      5,
    "tourniquet":          4,
    "traditional_healer":  4,
    "incision":            3,
    "suction":             3,
    "herbal_remedy":       2,
}

def detect_harmful_practices(text: str, language: str = "auto") -> dict:
    """
    Main function. Returns all detected harmful practices + corrective messages.
    language: 'auto' tries all languages; or pass 'telugu', 'hindi', etc.
    """
    text_lower = text.lower()
    detected   = []

    langs_to_check = LANGUAGES if language == "auto" else [language, "english"]

    for practice, lang_phrases in HARMFUL_PHRASES.items():
        matched_phrases = []
        matched_lang    = None

        for lang in langs_to_check:
            if lang not in lang_phrases:
                continue
            for phrase in lang_phrases[lang]:
                if phrase.lower() in text_lower:
                    matched_phrases.append(phrase)
                    matched_lang = lang

        if matched_phrases:
            # Get corrective message — prefer detected language, fallback english
            msg_lang = matched_lang if matched_lang in CORRECTIVE_MESSAGES.get(practice, {}) else "english"
            corrective = CORRECTIVE_MESSAGES[practice][msg_lang]

            detected.append({
                "practice":          practice,
                "severity":          SEVERITY_RANK[practice],
                "matched_phrases":   matched_phrases,
                "detected_language": matched_lang,
                "corrective_message": corrective,
                "am2_flag":          practice  # passes directly to AM2 severity engine
            })

    # Sort by severity descending
    detected.sort(key=lambda x: x["severity"], reverse=True)

    # Summary flags for AM2
    am2_flags = [d["am2_flag"] for d in detected]
    critical  = any(d["severity"] >= 4 for d in detected)

    return {
        "harmful_practices_detected": len(detected) > 0,
        "count":                      len(detected),
        "practices":                  detected,
        "am2_harmful_flags":          am2_flags,
        "critical_intervention_needed": critical,
        "primary_corrective_message": detected[0]["corrective_message"] if detected else None,
        "all_corrective_messages":    [d["corrective_message"] for d in detected]
    }
