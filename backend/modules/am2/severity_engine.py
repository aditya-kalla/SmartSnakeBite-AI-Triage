"""
A-M2 Engine 3: Severity Assessment Engine
SmartSnakebite — Aditya Module 2

Computes refined severity (LOW → MODERATE → HIGH → CRITICAL)
using A-M1 urgency + critical symptoms + elapsed time + harmful practices + patient context.
"""

from thresholds import (
    SEVERITY_THRESHOLDS, ELAPSED_TIME_WEIGHTS, HARMFUL_PRACTICE_WEIGHTS,
    PATIENT_RISK_WEIGHTS, AM1_CONFIDENCE_PENALTY, CRITICAL_SYMPTOM_ESCALATION_THRESHOLD
)

URGENCY_BASE_SCORES = {
    "HIGH":   60,
    "MEDIUM": 35,
    "LOW":    15,
    "CRITICAL": 85
}


def compute_severity(
    am1_urgency: str,
    am1_confidence: float,
    syndrome_result: dict,
    elapsed_hours: float,
    patient_context: dict,
    harmful_practices: dict,
    species_result: dict
) -> dict:
    """
    Compute refined severity score and class.

    Args:
        am1_urgency      : 'HIGH' | 'MEDIUM' | 'LOW'
        am1_confidence   : float 0–1 from A-M1
        syndrome_result  : output from syndrome_engine
        elapsed_hours    : hours since bite (float)
        patient_context  : dict with age, occupation
        harmful_practices: dict with tourniquet, healer, etc.
        species_result   : output from species_engine

    Returns:
        dict with severity_score, severity_class, severity_label, explanation
    """
    score = 0
    explanation = []

    # 1. Base from A-M1 urgency
    base = URGENCY_BASE_SCORES.get(am1_urgency.upper(), 35)
    score += base
    explanation.append(f"A-M1 urgency '{am1_urgency}' → base score {base}.")

    # 2. A-M1 confidence penalty
    if am1_confidence >= 0.85:
        penalty = AM1_CONFIDENCE_PENALTY["high"]
    elif am1_confidence >= 0.60:
        penalty = AM1_CONFIDENCE_PENALTY["medium"]
    else:
        penalty = AM1_CONFIDENCE_PENALTY["low"]
    # Low confidence → add penalty (more uncertainty = assume worse)
    score += penalty
    if penalty > 0:
        explanation.append(f"Low A-M1 confidence ({am1_confidence:.2f}) → +{penalty} uncertainty penalty.")

    # 3. Critical symptom escalation
    critical_found = syndrome_result.get("critical_symptoms", [])
    if critical_found:
        crit_bonus = min(len(critical_found) * 12, 36)
        score += crit_bonus
        explanation.append(f"Critical symptoms detected: {', '.join(critical_found)} → +{crit_bonus}.")

    # 4. Elapsed time
    elapsed_add = _elapsed_score(elapsed_hours)
    score += elapsed_add
    if elapsed_add > 0:
        explanation.append(f"Elapsed time {elapsed_hours:.1f}h → +{elapsed_add} delay penalty.")

    # 5. Harmful practices
    harm_total = 0
    for practice, flag in harmful_practices.items():
        if flag and practice in HARMFUL_PRACTICE_WEIGHTS:
            w = HARMFUL_PRACTICE_WEIGHTS[practice]
            harm_total += w
            explanation.append(f"Harmful practice '{practice}' → +{w}.")
    score += harm_total

    # 6. Patient risk factors
    age = patient_context.get("age")
    if age is not None:
        if age < 12:
            score += PATIENT_RISK_WEIGHTS["age_pediatric"]
            explanation.append(f"Pediatric patient (age {age}) → +{PATIENT_RISK_WEIGHTS['age_pediatric']}.")
        elif age > 65:
            score += PATIENT_RISK_WEIGHTS["age_elderly"]
            explanation.append(f"Elderly patient (age {age}) → +{PATIENT_RISK_WEIGHTS['age_elderly']}.")

    # 7. Krait escalation override
    if species_result.get("krait_escalation"):
        krait_bonus = 15
        score += krait_bonus
        explanation.append(
            f"Krait probability {species_result['krait_combined_prob']*100:.0f}% + neurotoxic + "
            f"→ +{krait_bonus} krait escalation."
        )

    # 8. Mixed syndrome penalty
    if syndrome_result.get("is_mixed"):
        score += 10
        explanation.append("Mixed syndrome detected → +10.")

    # Cap at 100
    score = min(score, 100)

    # Map to class
    severity_class = _score_to_class(score)

    # Hard override: any critical symptom → minimum HIGH
    if critical_found and severity_class == "MODERATE":
        severity_class = "HIGH"
        explanation.append("Override: critical symptoms present → minimum HIGH severity.")

    return {
        "severity_score": score,
        "severity_class": severity_class,
        "severity_label": _label(severity_class),
        "explanation":    explanation
    }


def _elapsed_score(hours: float) -> int:
    if hours is None:
        return ELAPSED_TIME_WEIGHTS["1_to_3h"]  # assume moderate delay if unknown
    if hours <= 1:
        return ELAPSED_TIME_WEIGHTS["within_1h"]
    elif hours <= 3:
        return ELAPSED_TIME_WEIGHTS["1_to_3h"]
    elif hours <= 6:
        return ELAPSED_TIME_WEIGHTS["3_to_6h"]
    elif hours <= 12:
        return ELAPSED_TIME_WEIGHTS["6_to_12h"]
    else:
        return ELAPSED_TIME_WEIGHTS["over_12h"]


def _score_to_class(score: int) -> str:
    if score >= SEVERITY_THRESHOLDS["CRITICAL"]:
        return "CRITICAL"
    elif score >= SEVERITY_THRESHOLDS["HIGH"]:
        return "HIGH"
    elif score >= SEVERITY_THRESHOLDS["MODERATE"]:
        return "MODERATE"
    else:
        return "LOW"


def _label(cls: str) -> str:
    labels = {
        "CRITICAL": "CRITICAL — Immediate emergency transport required",
        "HIGH":     "HIGH — Urgent hospital admission required",
        "MODERATE": "MODERATE — Hospital treatment required",
        "LOW":      "LOW — Monitor, hospital observation recommended"
    }
    return labels.get(cls, cls)
