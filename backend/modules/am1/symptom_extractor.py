"""
A-M1 helper: Symptom Keyword Extractor
Extracts symptom keys (matching AM2's symptom_ontology.json) from narrative text.
English only for now — extend with per-language phrase lists (see AM3's
practice_detector.py pattern) when ready.
"""

import re

# phrase -> symptom_key (keys MUST match AM2/knowledge_base/symptom_ontology.json)
SYMPTOM_PHRASES = {
    "ptosis":                 ["drooping eyelid", "eyelids are drooping", "can't open my eyes", "eyelid droop"],
    "dysphagia":               ["cannot swallow", "can't swallow", "difficulty swallowing", "unable to swallow"],
    "dysarthria":              ["slurred speech", "can't speak clearly", "difficulty speaking"],
    "respiratory_distress":    ["difficulty breathing", "can't breathe", "shortness of breath", "breathless"],
    "respiratory_paralysis":   ["stopped breathing", "not breathing"],
    "paralysis":               ["paralysis", "paralyzed", "cannot move", "can't move"],
    "muscle_weakness":         ["weak", "weakness", "feel weak", "muscles weak"],
    "diplopia":                ["double vision", "seeing double"],
    "neck_weakness":           ["neck weak", "can't hold neck", "head drooping"],
    "hoarseness":              ["hoarse voice", "voice changed"],
    "blurred_vision":          ["blurred vision", "blurry vision", "vision blurred"],
    "facial_paralysis":        ["face paralyzed", "facial droop"],
    "hypersalivation":         ["excess saliva", "drooling"],
    "abdominal_cramp":         ["stomach cramp", "abdominal cramp", "stomach pain"],
    "minimal_local_swelling":  ["slight swelling", "minimal swelling"],
    "painless_bite":           ["no pain", "painless", "didn't hurt"],

    "spontaneous_bleeding":    ["bleeding on its own", "spontaneous bleeding", "bleeding from nose"],
    "gum_bleeding":            ["gums are bleeding", "gum bleeding", "blood from gums"],
    "hematuria":               ["blood in urine", "bloody urine"],
    "blood_in_urine":          ["blood in urine", "bloody urine"],
    "clotting_failure":        ["blood won't clot", "not clotting"],
    "hematemesis":             ["vomiting blood", "blood in vomit"],
    "vomiting_blood":          ["vomiting blood", "blood in vomit"],
    "bruising":                ["bruising", "bruises appearing"],
    "prolonged_bleeding":      ["won't stop bleeding", "prolonged bleeding", "bleeding a lot"],
    "haemoptysis":             ["coughing blood", "cough up blood"],
    "coughing_blood":          ["coughing blood", "cough up blood"],

    "tissue_necrosis":         ["tissue dying", "flesh turning black", "necrosis"],
    "necrosis":                ["tissue dying", "flesh turning black", "necrosis"],
    "severe_local_swelling":   ["severe swelling", "very swollen", "swelling badly"],
    "blistering":              ["blisters", "blistering"],
    "local_pain":              ["pain at bite", "hurts a lot", "severe pain at site"],
    "progressive_edema":       ["swelling spreading", "swelling getting worse"],
    "swelling_spreading":      ["swelling spreading", "spreading swelling"],
    "skin_darkening":          ["skin turning black", "skin darkening"],

    "muscle_breakdown":        ["muscle breaking down", "muscle damage"],
    "dark_urine":              ["dark urine", "urine is dark"],
    "brown_urine":             ["brown urine", "urine is brown"],
    "generalized_body_pain":   ["whole body pain", "body aches all over"],
    "muscle_tenderness":       ["muscles tender", "sore muscles"],
    "rhabdomyolysis":          ["muscle breakdown"],

    "nausea":                  ["nausea", "feel nauseous", "feel sick"],
    "vomiting":                ["vomiting", "throwing up", "vomited"],
    "dizziness":               ["dizzy", "dizziness", "lightheaded"],
    "drowsiness":              ["drowsy", "sleepy", "drowsiness"],
    "loss_of_consciousness":   ["lost consciousness", "fainted", "unconscious", "passed out"],
    "hypotension":             ["low blood pressure", "blood pressure dropped"],
    "shock":                   ["in shock", "going into shock"],
    "pain_at_bite_site":       ["pain at the bite", "hurts where bitten"],
}


def extract_symptoms(text: str) -> list[str]:
    """Return list of symptom keys found in text (English matching)."""
    text_lower = text.lower()
    found = []
    for symptom_key, phrases in SYMPTOM_PHRASES.items():
        for phrase in phrases:
            if phrase in text_lower:
                found.append(symptom_key)
                break
    return found
