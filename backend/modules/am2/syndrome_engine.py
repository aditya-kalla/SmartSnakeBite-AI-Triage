"""
A-M2 Engine 1: Venom Syndrome Engine
SmartSnakebite — Aditya Module 2

Converts A-M1 symptoms + venom_type into a clinically meaningful
syndrome score with mixed-syndrome detection.
"""

import json
from pathlib import Path
from thresholds import SYNDROME_ACTIVATION_THRESHOLD, MIXED_SYNDROME_THRESHOLD

ONTOLOGY_PATH = Path(__file__).parent / "knowledge_base" / "symptom_ontology.json"

with open(ONTOLOGY_PATH) as f:
    ONTOLOGY = json.load(f)

SYMPTOM_WEIGHTS   = ONTOLOGY["symptoms"]
CRITICAL_SYMPTOMS = set(ONTOLOGY["critical_symptoms"])

SYNDROME_LABELS = ["neurotoxic", "hemotoxic", "cytotoxic", "myotoxic"]


def compute_syndrome(am1_venom_type: str, symptoms: list[str]) -> dict:
    """
    Compute syndrome scores from A-M1 output.

    Args:
        am1_venom_type : venom_type string from A-M1
        symptoms       : list of symptom keys from A-M1

    Returns:
        dict with syndrome scores, primary syndrome, mixed flag, critical flag
    """
    scores = {s: 0.0 for s in SYNDROME_LABELS}
    matched_symptoms = []
    critical_found   = []

    # Score from symptom evidence
    for sym in symptoms:
        sym_clean = sym.lower().replace(" ", "_").replace("-", "_")
        if sym_clean in SYMPTOM_WEIGHTS:
            for syndrome in SYNDROME_LABELS:
                scores[syndrome] += SYMPTOM_WEIGHTS[sym_clean].get(syndrome, 0.0)
            matched_symptoms.append(sym_clean)

        if sym_clean in CRITICAL_SYMPTOMS:
            critical_found.append(sym_clean)

    # Normalise each syndrome score to 0–1 (cap at 1)
    max_possible = max(len(symptoms), 1)
    for s in SYNDROME_LABELS:
        scores[s] = min(scores[s] / max_possible, 1.0)

    # A-M1 venom_type provides a strong prior — add 0.3 boost to matching syndrome
    venom_map = {
        "neurotoxic": "neurotoxic",
        "hemotoxic":  "hemotoxic",
        "cytotoxic":  "cytotoxic",
        "myotoxic":   "myotoxic"
    }
    if am1_venom_type in venom_map:
        target = venom_map[am1_venom_type]
        scores[target] = min(scores[target] + 0.30, 1.0)

    # Detect active syndromes
    active = [s for s in SYNDROME_LABELS if scores[s] >= SYNDROME_ACTIVATION_THRESHOLD]
    mixed  = [s for s in SYNDROME_LABELS if scores[s] >= MIXED_SYNDROME_THRESHOLD]

    is_mixed = len(mixed) >= 2
    primary  = max(scores, key=scores.get)

    if is_mixed:
        syndrome_label = "Mixed (" + " + ".join(
            [s.capitalize() for s in sorted(mixed, key=lambda x: -scores[x])[:2]]
        ) + ")"
    else:
        syndrome_label = primary.capitalize()

    explanation = _build_explanation(primary, scores, matched_symptoms, am1_venom_type, is_mixed, mixed)

    return {
        "syndrome_label":    syndrome_label,
        "primary_syndrome":  primary,
        "is_mixed":          is_mixed,
        "active_syndromes":  active,
        "syndrome_scores":   {k: round(v, 3) for k, v in scores.items()},
        "critical_symptoms": critical_found,
        "has_critical":      len(critical_found) > 0,
        "matched_symptoms":  matched_symptoms,
        "explanation":       explanation
    }


def _build_explanation(primary, scores, matched, am1_venom, is_mixed, mixed):
    lines = []
    lines.append(f"A-M1 classified venom as '{am1_venom}' — used as strong prior (+0.30 to {am1_venom} score).")
    if matched:
        lines.append(f"Symptom evidence found: {', '.join(matched)}.")
    top2 = sorted(scores.items(), key=lambda x: -x[1])[:2]
    for name, val in top2:
        if val > 0:
            lines.append(f"{name.capitalize()} score: {val:.2f}.")
    if is_mixed:
        lines.append(f"Mixed syndrome detected: {' + '.join([s.capitalize() for s in mixed])}.")
    return lines
