"""
A-M2: Probabilistic Clinical Decision Support Engine (PCDSE)
SmartSnakebite — Aditya Module 2

Main entry point. Integrates all 4 engines into a single predict_am2() call.

Usage:
    from am2_predictor import predict_am2

    result = predict_am2(
        am1_output = {
            "venom_type": "neurotoxic",
            "urgency": "HIGH",
            "confidence": 0.93,
            "symptoms": ["ptosis", "dysphagia", "respiratory_distress"]
        },
        district       = "Khammam",
        state          = "Telangana",
        time_of_day    = "night",
        season         = "monsoon",
        elapsed_hours  = 3.5,
        patient_context = {"age": 35, "occupation": "farmer"},
        harmful_practices = {
            "tourniquet_applied": False,
            "incision_attempted": False,
            "traditional_healer_visited": True,
            "herbal_application": False
        }
    )
"""

import sys
import json
from pathlib import Path


from syndrome_engine   import compute_syndrome
from species_engine    import compute_species_probabilities
from severity_engine   import compute_severity
from mortality_engine  import compute_mortality_risk
from clinical_decision import compute_clinical_decision


def predict_am2(
    am1_output:        dict,
    district:          str   = "Unknown",
    state:             str   = None,
    time_of_day:       str   = "evening",
    season:            str   = "monsoon",
    elapsed_hours:     float = None,
    patient_context:   dict  = None,
    harmful_practices: dict  = None
) -> dict:
    """
    Full A-M2 prediction pipeline.

    Args:
        am1_output        : dict from A-M1 with venom_type, urgency, confidence, symptoms
        district          : district name (e.g. "Khammam", "Guntur")
        state             : "Telangana" or "Andhra Pradesh"
        time_of_day       : "morning" | "afternoon" | "evening" | "night"
        season            : "monsoon" | "post_monsoon" | "summer" | "winter"
        elapsed_hours     : float, hours since bite
        patient_context   : dict with optional: age, sex, occupation
        harmful_practices : dict with optional boolean flags

    Returns:
        Complete A-M2 output dict
    """

    # ── Defaults ────────────────────────────────────────────────────────
    if patient_context   is None: patient_context   = {}
    if harmful_practices is None: harmful_practices = {}
    if elapsed_hours     is None: elapsed_hours     = 2.0  # conservative default

    # ── Validate A-M1 input ──────────────────────────────────────────────
    venom_type  = am1_output.get("venom_type",  "unknown")
    urgency     = am1_output.get("urgency",     "MEDIUM")
    confidence  = am1_output.get("confidence",  0.70)
    symptoms    = am1_output.get("symptoms",    [])

    # ── Engine 1: Syndrome ───────────────────────────────────────────────
    syndrome_result = compute_syndrome(venom_type, symptoms)

    # ── Engine 2: Species Probabilities ──────────────────────────────────
    species_result = compute_species_probabilities(
        syndrome_result = syndrome_result,
        district        = district,
        time_of_day     = time_of_day,
        season          = season,
        symptoms        = symptoms,
        state           = state
    )

    # ── Engine 3: Severity ───────────────────────────────────────────────
    severity_result = compute_severity(
        am1_urgency       = urgency,
        am1_confidence    = confidence,
        syndrome_result   = syndrome_result,
        elapsed_hours     = elapsed_hours,
        patient_context   = patient_context,
        harmful_practices = harmful_practices,
        species_result    = species_result
    )

    # ── Engine 4a: Mortality ─────────────────────────────────────────────
    mortality_result = compute_mortality_risk(
        severity_result   = severity_result,
        syndrome_result   = syndrome_result,
        species_result    = species_result,
        elapsed_hours     = elapsed_hours,
        harmful_practices = harmful_practices,
        patient_context   = patient_context
    )

    # ── Engine 4b: Clinical Decision + Explanation ───────────────────────
    clinical_result = compute_clinical_decision(
        severity_result   = severity_result,
        mortality_result  = mortality_result,
        syndrome_result   = syndrome_result,
        species_result    = species_result,
        harmful_practices = harmful_practices,
        elapsed_hours     = elapsed_hours
    )

    # ── Final Output ─────────────────────────────────────────────────────
    return {
        "venom_syndrome":       syndrome_result["syndrome_label"],
        "primary_syndrome":     syndrome_result["primary_syndrome"],
        "is_mixed_syndrome":    syndrome_result["is_mixed"],

        "probable_species":     species_result["top_species"],
        "top_species_name":     species_result["top_species_name"],
        "top_species_prob":     species_result["top_probability"],
        "krait_escalation":     species_result["krait_escalation"],

        "severity_class":       severity_result["severity_class"],
        "severity_score":       severity_result["severity_score"],
        "severity_label":       severity_result["severity_label"],

        "mortality_risk_class": mortality_result["mortality_risk_class"],
        "mortality_risk_score": mortality_result["mortality_risk_score"],

        "antivenom_required":   clinical_result["antivenom_required"],
        "antivenom_priority":   clinical_result["antivenom_priority"],
        "antivenom_type":       clinical_result["antivenom_type"],
        "referral_priority":    clinical_result["referral_priority"],

        "harmful_practice_warnings": clinical_result["harmful_practice_warnings"],
        "clinical_explanation":      clinical_result["clinical_explanation"],

        "context": {
            "district":      district,
            "state":         state,
            "time_of_day":   time_of_day,
            "season":        season,
            "elapsed_hours": elapsed_hours
        }
    }


# ── Demo run ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST CASE 1: Krait bite — night, Khammam, monsoon")
    print("="*60)
    result = predict_am2(
        am1_output = {
            "venom_type": "neurotoxic",
            "urgency": "HIGH",
            "confidence": 0.93,
            "symptoms": ["ptosis", "dysphagia", "respiratory_distress", "paralysis"]
        },
        district    = "Khammam",
        state       = "Telangana",
        time_of_day = "night",
        season      = "monsoon",
        elapsed_hours = 3.5,
        patient_context   = {"age": 38, "occupation": "farmer"},
        harmful_practices = {"traditional_healer_visited": True, "tourniquet_applied": False}
    )
    print(f"Syndrome:       {result['venom_syndrome']}")
    print(f"Top Species:    {result['top_species_name']} ({result['top_species_prob']*100:.1f}%)")
    print(f"All Species:    {result['probable_species']}")
    print(f"Severity:       {result['severity_class']} ({result['severity_score']}/100)")
    print(f"Mortality Risk: {result['mortality_risk_class']}")
    print(f"Antivenom:      {result['antivenom_required']} — {result['antivenom_priority']}")
    print(f"Referral:       {result['referral_priority']}")
    if result["harmful_practice_warnings"]:
        print("Warnings:")
        for w in result["harmful_practice_warnings"]:
            print(f"  ⚠ {w}")
    print("\nFull Explanation:")
    for line in result["clinical_explanation"]:
        print(line)

    print("\n" + "="*60)
    print("TEST CASE 2: Russell's Viper — evening, Kurnool, post-monsoon")
    print("="*60)
    result2 = predict_am2(
        am1_output = {
            "venom_type": "hemotoxic",
            "urgency": "HIGH",
            "confidence": 0.88,
            "symptoms": ["spontaneous_bleeding", "gum_bleeding", "severe_local_swelling", "hematuria"]
        },
        district    = "Kurnool",
        state       = "Andhra Pradesh",
        time_of_day = "evening",
        season      = "post_monsoon",
        elapsed_hours = 1.5,
        patient_context   = {"age": 55, "occupation": "farmer"},
        harmful_practices = {"incision_attempted": True, "herbal_application": True}
    )
    print(f"Syndrome:       {result2['venom_syndrome']}")
    print(f"Top Species:    {result2['top_species_name']} ({result2['top_species_prob']*100:.1f}%)")
    print(f"All Species:    {result2['probable_species']}")
    print(f"Severity:       {result2['severity_class']} ({result2['severity_score']}/100)")
    print(f"Mortality Risk: {result2['mortality_risk_class']}")
    print(f"Antivenom:      {result2['antivenom_required']} — {result2['antivenom_priority']}")
    print(f"Referral:       {result2['referral_priority']}")
    if result2["harmful_practice_warnings"]:
        print("Warnings:")
        for w in result2["harmful_practice_warnings"]:
            print(f"  ⚠ {w}")

    print("\n" + "="*60)
    print("TEST CASE 3: Unknown — dry bite suspected")
    print("="*60)
    result3 = predict_am2(
        am1_output = {
            "venom_type": "unknown",
            "urgency": "LOW",
            "confidence": 0.55,
            "symptoms": ["local_pain", "pain_at_bite_site"]
        },
        district    = "Guntur",
        state       = "Andhra Pradesh",
        time_of_day = "morning",
        season      = "summer",
        elapsed_hours = 0.5,
        patient_context   = {"age": 22},
        harmful_practices = {}
    )
    print(f"Syndrome:       {result3['venom_syndrome']}")
    print(f"Top Species:    {result3['top_species_name']} ({result3['top_species_prob']*100:.1f}%)")
    print(f"Severity:       {result3['severity_class']} ({result3['severity_score']}/100)")
    print(f"Mortality Risk: {result3['mortality_risk_class']}")
    print(f"Antivenom:      {result3['antivenom_required']} — {result3['antivenom_priority']}")
    print(f"Referral:       {result3['referral_priority']}")
