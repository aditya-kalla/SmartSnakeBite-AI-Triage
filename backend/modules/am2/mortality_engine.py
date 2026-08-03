"""
A-M2 Engine 4a: Mortality Risk Engine
SmartSnakebite — Aditya Module 2
"""

import json
from pathlib import Path
from thresholds import MORTALITY_THRESHOLDS

KB = Path(__file__).parent / "knowledge_base"
with open(KB / "species_db.json") as f:
    SPECIES_DB = json.load(f)

SYNDROME_MORTALITY_BASE = {
    "neurotoxic": 55,
    "hemotoxic":  45,
    "cytotoxic":  25,
    "myotoxic":   30
}

SEVERITY_MORTALITY_MAP = {
    "CRITICAL": 40,
    "HIGH":     25,
    "MODERATE": 10,
    "LOW":      0
}


def compute_mortality_risk(
    severity_result: dict,
    syndrome_result: dict,
    species_result: dict,
    elapsed_hours: float,
    harmful_practices: dict,
    patient_context: dict
) -> dict:
    score = 0
    explanation = []

    # 1. Syndrome base
    primary = syndrome_result.get("primary_syndrome", "unknown")
    syn_base = SYNDROME_MORTALITY_BASE.get(primary, 20)

    # Mixed syndrome → use higher of two
    if syndrome_result.get("is_mixed"):
        active = syndrome_result.get("active_syndromes", [primary])
        syn_base = max([SYNDROME_MORTALITY_BASE.get(s, 20) for s in active])
        syn_base = min(syn_base + 10, 70)
        explanation.append(f"Mixed syndrome → base mortality risk: {syn_base}.")
    else:
        explanation.append(f"{primary.capitalize()} syndrome → base mortality risk: {syn_base}.")
    score += syn_base

    # 2. Severity contribution
    sev_add = SEVERITY_MORTALITY_MAP.get(severity_result["severity_class"], 0)
    score += sev_add
    explanation.append(f"Severity '{severity_result['severity_class']}' → +{sev_add}.")

    # 3. Top species mortality risk
    top_key = species_result.get("top_species_key")
    if top_key and top_key in SPECIES_DB:
        sp_mortality = SPECIES_DB[top_key].get("mortality_risk_untreated", "moderate")
        sp_add = {"very_high": 20, "high": 12, "moderate": 5, "low": 0}.get(sp_mortality, 5)
        sp_prob = species_result.get("top_probability", 0)
        weighted_add = round(sp_add * sp_prob)
        score += weighted_add
        explanation.append(
            f"Top species {SPECIES_DB[top_key]['common_name']} (prob {sp_prob:.2f}, "
            f"untreated risk '{sp_mortality}') → +{weighted_add}."
        )

    # 4. Elapsed time
    if elapsed_hours:
        if elapsed_hours > 6:
            score += 15
            explanation.append(f"Elapsed {elapsed_hours:.1f}h → +15 delay mortality risk.")
        elif elapsed_hours > 3:
            score += 8
            explanation.append(f"Elapsed {elapsed_hours:.1f}h → +8 delay mortality risk.")

    # 5. Harmful practices
    if harmful_practices.get("traditional_healer_visited"):
        score += 12
        explanation.append("Traditional healer visit → +12 (treatment delay).")
    if harmful_practices.get("tourniquet_applied"):
        score += 8
        explanation.append("Tourniquet → +8 (tissue damage risk).")

    # 6. Vulnerable patient
    age = patient_context.get("age")
    if age is not None:
        if age < 12:
            score += 15
            explanation.append(f"Pediatric (age {age}) → +15.")
        elif age > 65:
            score += 10
            explanation.append(f"Elderly (age {age}) → +10.")

    # 7. Krait night bite — highest untreated mortality
    if species_result.get("krait_escalation"):
        score += 10
        explanation.append("Krait escalation flag → +10 mortality risk.")

    score = min(score, 100)

    risk_class = _score_to_class(score)

    return {
        "mortality_risk_score": score,
        "mortality_risk_class": risk_class,
        "explanation":          explanation
    }


def _score_to_class(score: int) -> str:
    if score >= MORTALITY_THRESHOLDS["VERY_HIGH"]:
        return "VERY_HIGH"
    elif score >= MORTALITY_THRESHOLDS["HIGH"]:
        return "HIGH"
    elif score >= MORTALITY_THRESHOLDS["MODERATE"]:
        return "MODERATE"
    else:
        return "LOW"
