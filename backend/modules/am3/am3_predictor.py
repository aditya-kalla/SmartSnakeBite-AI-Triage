"""
A-M3: Main Predictor
Combines harmful practice detection + Three Delays extraction.
Input  : raw narrative text + language + elapsed hours
Output : structured report ready for AM2 integration
"""

from practice_detector import detect_harmful_practices
from delay_extractor    import extract_delays

def predict_am3(
    narrative:     str,
    language:      str   = "auto",
    elapsed_hours: float = None
) -> dict:

    practices = detect_harmful_practices(narrative, language)
    delays    = extract_delays(narrative, elapsed_hours, language)

    # Compose AM2-ready output
    return {
        "am3_output": {
            "harmful_practices":          practices,
            "delay_analysis":             delays,
            "am2_harmful_flags":          practices["am2_harmful_flags"],
            "am2_total_delay_hours":      delays["total_estimated_delay_hours"],
            "critical_alert":             practices["critical_intervention_needed"],
            "primary_corrective_message": practices["primary_corrective_message"],
        }
    }


# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json

    test_cases = [
        {
            "label":    "Telugu — tourniquet + healer",
            "text":     "కాటు పైన త్రాడు కట్టారు మరియు మంత్రవాది దగ్గరకు వెళ్ళారు 3 గంటలు",
            "language": "telugu",
            "elapsed":  3.5
        },
        {
            "label":    "Hindi — incision + herbal remedy",
            "text":     "काटने की जगह काटा और हल्दी लगाई और घरेलू उपाय किया",
            "language": "hindi",
            "elapsed":  2.0
        },
        {
            "label":    "English — suction + electric shock",
            "text":     "They sucked the wound with mouth and gave electric shock to the bite site",
            "language": "english",
            "elapsed":  1.5
        },
        {
            "label":    "Tamil — healer visit",
            "text":     "ஓஜா வீட்டிற்கு சென்றார்கள் 2 மணிநேரம் இருந்தார்கள்",
            "language": "tamil",
            "elapsed":  4.0
        },
        {
            "label":    "Kannada — herbal remedy only",
            "text":     "ಗಾಯಕ್ಕೆ ಅರಿಶಿಣ ಹಚ್ಚಿದರು ಮತ್ತು ಬೇವಿನ ಎಲೆ ಹಚ್ಚಿದರು",
            "language": "kannada",
            "elapsed":  1.0
        },
        {
            "label":    "Clean case — no harmful practices",
            "text":     "Patient was bitten on the leg, kept still, brought directly to hospital",
            "language": "english",
            "elapsed":  0.5
        },
    ]

    for case in test_cases:
        print("=" * 60)
        print(f"TEST: {case['label']}")
        print("=" * 60)
        result = predict_am3(case["text"], case["language"], case["elapsed"])
        out    = result["am3_output"]

        print(f"Harmful Practices Found : {out['harmful_practices']['count']}")
        for p in out["harmful_practices"]["practices"]:
            print(f"  ⚠ {p['practice'].upper()} (severity {p['severity']}/5)")
        print(f"Total Delay Estimate    : {out['am2_total_delay_hours']}h")
        print(f"Delay Risk              : {out['delay_analysis']['delay_risk']}")
        print(f"Critical Alert          : {out['critical_alert']}")
        if out["primary_corrective_message"]:
            msg = out["primary_corrective_message"]
            print(f"Primary Message         : {msg[:120]}...")
        print()
