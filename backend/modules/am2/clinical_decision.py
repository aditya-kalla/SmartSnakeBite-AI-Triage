"""
A-M2 Engine 4b: Clinical Decision Layer + Explanation Engine
SmartSnakebite — Aditya Module 2

Produces final antivenom recommendation, referral priority, and
human-readable clinical explanation from all engine outputs.
"""

import json
from pathlib import Path
from thresholds import ANTIVENOM_PRIORITY

KB = Path(__file__).parent / "knowledge_base"
with open(KB / "species_db.json") as f:
    SPECIES_DB = json.load(f)


def compute_clinical_decision(
    severity_result: dict,
    mortality_result: dict,
    syndrome_result: dict,
    species_result: dict,
    harmful_practices: dict,
    elapsed_hours: float
) -> dict:
    """Produce final clinical decision output."""

    severity_class = severity_result["severity_class"]
    antivenom_priority = ANTIVENOM_PRIORITY[severity_class]

    # Antivenom requirement logic
    antivenom_required = severity_class in ["HIGH", "CRITICAL"] or \
                         syndrome_result.get("has_critical") or \
                         mortality_result["mortality_risk_class"] in ["HIGH", "VERY_HIGH"]

    # Referral priority
    referral_priority = _referral_priority(severity_class, mortality_result["mortality_risk_class"])

    # Special clinical notes for top species
    top_key  = species_result.get("top_species_key")
    sp_notes = []
    if top_key and top_key in SPECIES_DB:
        sp  = SPECIES_DB[top_key]
        note = sp["antivenom"].get("note", "")
        if note:
            sp_notes.append(note)
        vials = sp["antivenom"].get("vials_range")
        if vials:
            sp_notes.append(f"Estimated antivenom vials required: {vials[0]}–{vials[1]}.")

    # Harmful practice warnings
    harm_warnings = _harmful_practice_warnings(harmful_practices)

    explanation = _build_full_explanation(
        severity_result, mortality_result, syndrome_result,
        species_result, harm_warnings, elapsed_hours
    )

    return {
        "antivenom_required":   antivenom_required,
        "antivenom_priority":   antivenom_priority,
        "antivenom_type":       "Polyvalent ASV (Polyvalent Anti-Snake Venom)",
        "referral_priority":    referral_priority,
        "species_clinical_notes": sp_notes,
        "harmful_practice_warnings": harm_warnings,
        "clinical_explanation": explanation
    }


def _referral_priority(severity: str, mortality: str) -> str:
    if severity == "CRITICAL" or mortality == "VERY_HIGH":
        return "EMERGENCY — Call ambulance immediately. Do not wait."
    elif severity == "HIGH" or mortality == "HIGH":
        return "URGENT — Transport to hospital within 30 minutes."
    elif severity == "MODERATE":
        return "REQUIRED — Hospital treatment needed within 2 hours."
    else:
        return "ADVISORY — Hospital observation recommended. Monitor closely."


def _harmful_practice_warnings(practices: dict) -> list:
    warnings = []
    if practices.get("tourniquet_applied"):
        warnings.append("WARNING: Tourniquet applied. Inform doctor immediately. Do NOT remove without medical supervision — sudden removal can cause venom surge.")
    if practices.get("incision_attempted"):
        warnings.append("WARNING: Incision at bite site. Increases infection risk. Keep wound clean.")
    if practices.get("traditional_healer_visited"):
        warnings.append("WARNING: Time lost at traditional healer. This is the leading cause of preventable death. Proceed to hospital immediately.")
    if practices.get("herbal_application"):
        warnings.append("WARNING: Herbal substances applied to wound. Inform treating doctor.")
    return warnings


def _build_full_explanation(severity, mortality, syndrome, species, harm_warnings, elapsed):
    lines = []
    lines.append("=" * 50)
    lines.append("CLINICAL REASONING SUMMARY")
    lines.append("=" * 50)

    lines.append(f"\n[SYNDROME] {syndrome['syndrome_label']}")
    for e in syndrome.get("explanation", []):
        lines.append(f"  • {e}")

    lines.append(f"\n[SPECIES ESTIMATE]")
    for e in species.get("explanation", []):
        lines.append(f"  • {e}")

    top_n = species.get("top_species", {})
    if top_n:
        lines.append("  Top probabilities:")
        for k, v in top_n.items():
            name = SPECIES_DB.get(k, {}).get("common_name", k)
            lines.append(f"    - {name}: {v*100:.1f}%")

    lines.append(f"\n[SEVERITY] {severity['severity_class']} (Score: {severity['severity_score']}/100)")
    for e in severity.get("explanation", []):
        lines.append(f"  • {e}")

    lines.append(f"\n[MORTALITY RISK] {mortality['mortality_risk_class']} (Score: {mortality['mortality_risk_score']}/100)")
    for e in mortality.get("explanation", []):
        lines.append(f"  • {e}")

    if harm_warnings:
        lines.append(f"\n[HARMFUL PRACTICES DETECTED]")
        for w in harm_warnings:
            lines.append(f"  ⚠ {w}")

    if elapsed:
        lines.append(f"\n[TIME] {elapsed:.1f} hours elapsed since bite.")
        if elapsed > 6:
            lines.append("  ⚠ Significant delay. Prioritise immediate transport.")

    lines.append("\n" + "=" * 50)
    return lines
