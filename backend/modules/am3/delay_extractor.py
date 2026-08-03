"""
A-M3: Treatment Delay Extractor
Extracts WHO Three Delays from patient narrative across 5 languages.
Delay 1 — Recognition (didn't know it was serious)
Delay 2 — Reaching care (travel time)
Delay 3 — Receiving treatment (healer visit, wrong facility)
"""

import json
import re
from pathlib import Path

BASE = Path(__file__).parent
KB   = BASE / "knowledge_base"

with open(KB / "delay_patterns.json", encoding="utf-8") as f:
    DELAY_PATTERNS = json.load(f)

# Time extraction patterns (works across all languages since numbers are universal)
TIME_PATTERNS = [
    r'(\d+\.?\d*)\s*(?:hours?|hrs?|గంటలు|గంట|घंटे|घंटा|ಗಂಟೆ|ಗಂಟೆಗಳು|மணி|மணிநேரம்)',
    r'(\d+\.?\d*)\s*(?:minutes?|mins?|నిమిషాలు|मिनट|ನಿಮಿಷ|நிமிடம்)',
    r'(\d+)\s*(?:days?|రోజులు|दिन|ದಿನ|நாள்)',
]

def extract_time_from_text(text: str) -> float:
    """Extract numeric time in hours from text."""
    text_lower = text.lower()
    for pattern in TIME_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE | re.UNICODE)
        if matches:
            val = float(matches[0])
            if 'min' in pattern or 'నిమిష' in pattern or 'मिनट' in pattern:
                return round(val / 60, 2)
            if 'day' in pattern or 'రోజు' in pattern or 'दिन' in pattern:
                return round(val * 24, 2)
            return round(val, 2)
    return None

def extract_delays(text: str, elapsed_hours: float = None, language: str = "auto") -> dict:
    """
    Extracts Three Delays from narrative.
    Returns structured delay report + total estimated delay hours.
    """
    text_lower = text.lower()
    langs = ["english", "telugu", "hindi", "kannada", "tamil"] if language == "auto" else [language, "english"]

    delays = {
        "delay_1_recognition": {
            "detected": False,
            "description": "Patient/family delayed recognising severity",
            "estimated_hours": 0.0,
            "evidence": []
        },
        "delay_2_reaching_care": {
            "detected": False,
            "description": "Time lost travelling to care",
            "estimated_hours": 0.0,
            "evidence": []
        },
        "delay_3_receiving_treatment": {
            "detected": False,
            "description": "Time lost at wrong facility or healer",
            "estimated_hours": 0.0,
            "evidence": []
        }
    }

    # Delay 1 — Recognition
    recog_patterns = DELAY_PATTERNS.get("recognition_delay", {})
    for lang in langs:
        for phrase in recog_patterns.get(lang, []):
            if phrase.lower() in text_lower:
                delays["delay_1_recognition"]["detected"] = True
                delays["delay_1_recognition"]["evidence"].append(phrase)
                if delays["delay_1_recognition"]["estimated_hours"] == 0.0:
                    delays["delay_1_recognition"]["estimated_hours"] = 1.0  # conservative

    # Delay 3 — Healer visit (most critical)
    healer_patterns = DELAY_PATTERNS.get("healer_visit", {})
    for lang in langs:
        for phrase in healer_patterns.get(lang, []):
            if phrase.lower() in text_lower:
                delays["delay_3_receiving_treatment"]["detected"] = True
                delays["delay_3_receiving_treatment"]["evidence"].append(phrase)
                extracted = extract_time_from_text(text)
                if extracted:
                    delays["delay_3_receiving_treatment"]["estimated_hours"] = extracted
                elif delays["delay_3_receiving_treatment"]["estimated_hours"] == 0.0:
                    delays["delay_3_receiving_treatment"]["estimated_hours"] = 2.0  # WHO average

    # Delay 2 — Use elapsed_hours if provided and no healer extracted
    if elapsed_hours is not None:
        healer_h = delays["delay_3_receiving_treatment"]["estimated_hours"]
        travel_h = max(0.0, elapsed_hours - healer_h)
        if travel_h > 0.5:
            delays["delay_2_reaching_care"]["detected"] = True
            delays["delay_2_reaching_care"]["estimated_hours"] = round(travel_h, 2)
            delays["delay_2_reaching_care"]["evidence"].append(f"Elapsed {elapsed_hours}h minus healer {healer_h}h")

    total_delay = round(
        delays["delay_1_recognition"]["estimated_hours"] +
        delays["delay_2_reaching_care"]["estimated_hours"] +
        delays["delay_3_receiving_treatment"]["estimated_hours"], 2
    )

    active_delays = [k for k, v in delays.items() if v["detected"]]

    # Risk classification
    if total_delay >= 6:
        risk = "CRITICAL"
    elif total_delay >= 3:
        risk = "HIGH"
    elif total_delay >= 1:
        risk = "MODERATE"
    else:
        risk = "LOW"

    return {
        "three_delays": delays,
        "active_delays": active_delays,
        "total_estimated_delay_hours": total_delay,
        "delay_risk": risk,
        "who_framework_note": "Based on WHO Three Delays Model for maternal/emergency care adapted for snakebite",
    }
