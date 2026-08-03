"""
A-M2 Engine 2: Species Probability Engine
SmartSnakebite — Aditya Module 2

Computes ranked species probability distribution using:
  - District prior
  - Season modifier
  - Time-of-day modifier
  - Syndrome compatibility
  - Symptom evidence match

NEVER returns a single species. Always returns a probability distribution.
"""

import json
from pathlib import Path
from thresholds import MIN_SPECIES_PROBABILITY, TOP_N_SPECIES, KRAIT_PROBABILITY_ESCALATION

KB = Path(__file__).parent / "knowledge_base"

with open(KB / "species_db.json")      as f: SPECIES_DB      = json.load(f)
with open(KB / "district_priors.json") as f: DISTRICT_PRIORS = json.load(f)
with open(KB / "season_priors.json")   as f: SEASON_PRIORS   = json.load(f)
with open(KB / "symptom_ontology.json")as f: ONTOLOGY        = json.load(f)

SYMPTOM_WEIGHTS = ONTOLOGY["symptoms"]
SPECIES_KEYS    = [k for k in SPECIES_DB if not k.startswith("_")]


def get_district_prior(district: str, state: str = None) -> dict:
    """Retrieve district-level species priors. Falls back gracefully."""
    district_clean = district.strip().replace(" ", "_") if district else ""

    # Try state-specific first
    for state_key in ["telangana", "andhra_pradesh"]:
        state_data = DISTRICT_PRIORS.get(state_key, {})
        if district_clean in state_data:
            return state_data[district_clean]

    # Try default for state
    if state:
        state_clean = state.lower().replace(" ", "_")
        if "telangana" in state_clean:
            return DISTRICT_PRIORS["telangana"]["DEFAULT_TELANGANA"]
        if "andhra" in state_clean:
            return DISTRICT_PRIORS["andhra_pradesh"]["DEFAULT_AP"]

    return DISTRICT_PRIORS["DEFAULT_REGION"]


def compute_species_probabilities(
    syndrome_result: dict,
    district: str,
    time_of_day: str,
    season: str,
    symptoms: list[str],
    state: str = None
) -> dict:
    """
    Compute ranked species probabilities from all available evidence.

    Args:
        syndrome_result : output from syndrome_engine.compute_syndrome()
        district        : district name string
        time_of_day     : 'morning' | 'afternoon' | 'evening' | 'night'
        season          : 'monsoon' | 'post_monsoon' | 'summer' | 'winter'
        symptoms        : list of symptom keys
        state           : 'Telangana' | 'Andhra Pradesh' (optional)

    Returns:
        dict with ranked species, probabilities, top species, explanation
    """
    primary_syndrome = syndrome_result["primary_syndrome"]
    syndrome_scores  = syndrome_result["syndrome_scores"]

    district_prior = get_district_prior(district, state)
    season_mods    = SEASON_PRIORS["season_multipliers"].get(season, {}).get("species_modifiers", {})
    time_mods      = SEASON_PRIORS["time_of_day_multipliers"].get(time_of_day, {}).get("species_modifiers", {})

    raw_scores = {}
    explanation_parts = {}

    for species_key in SPECIES_KEYS:
        sp = SPECIES_DB[species_key]
        score = 0.0
        parts = []

        # 1. District prior
        dist_prior = district_prior.get(species_key, 0.05)
        score += dist_prior * 3.0  # weight: district is strong signal
        parts.append(f"District prior: {dist_prior:.2f}")

        # 2. Syndrome compatibility
        sp_syndrome = sp["venom_syndrome"]
        # Handle mixed syndromes like "neurotoxic_cytotoxic"
        sp_syndromes = sp_syndrome.split("_") if "_" in sp_syndrome else [sp_syndrome]
        syndrome_compat = max([syndrome_scores.get(s, 0.0) for s in sp_syndromes if s in syndrome_scores], default=0.0)
        score += syndrome_compat * 2.5
        parts.append(f"Syndrome compatibility: {syndrome_compat:.2f}")

        # 3. Season modifier
        s_mod = season_mods.get(species_key, 1.0)
        score *= s_mod
        parts.append(f"Season modifier: x{s_mod}")

        # 4. Time of day modifier
        t_mod = time_mods.get(species_key, 1.0)
        score *= t_mod
        parts.append(f"Time-of-day modifier: x{t_mod}")

        # 5. Symptom-level evidence match
        sym_match = _symptom_species_match(species_key, sp, symptoms)
        score += sym_match * 1.5
        parts.append(f"Symptom evidence match: {sym_match:.2f}")

        raw_scores[species_key] = max(score, 0.0)
        explanation_parts[species_key] = parts

    # Normalise to probability distribution
    total = sum(raw_scores.values())
    if total == 0:
        total = 1.0

    probabilities = {k: round(v / total, 4) for k, v in raw_scores.items()}

    # Filter minimum threshold
    filtered = {k: v for k, v in probabilities.items() if v >= MIN_SPECIES_PROBABILITY}

    # Re-normalise after filter
    total2 = sum(filtered.values())
    if total2 > 0:
        filtered = {k: round(v / total2, 4) for k, v in filtered.items()}

    # Sort descending
    ranked = dict(sorted(filtered.items(), key=lambda x: -x[1]))
    top_n  = dict(list(ranked.items())[:TOP_N_SPECIES])

    # Build explanation for top species
    top_species_key  = list(ranked.keys())[0] if ranked else None
    top_explanation  = _build_species_explanation(
        top_species_key, explanation_parts, probabilities,
        district, time_of_day, season, primary_syndrome
    )

    # Krait escalation flag
    krait_prob = probabilities.get("common_krait", 0) + probabilities.get("banded_krait", 0)
    krait_escalation = krait_prob >= KRAIT_PROBABILITY_ESCALATION and primary_syndrome == "neurotoxic"

    return {
        "top_species":          top_n,
        "all_probabilities":    ranked,
        "top_species_name":     SPECIES_DB[top_species_key]["common_name"] if top_species_key else "Unknown",
        "top_species_key":      top_species_key,
        "top_probability":      probabilities.get(top_species_key, 0.0),
        "krait_escalation":     krait_escalation,
        "krait_combined_prob":  round(krait_prob, 4),
        "explanation":          top_explanation
    }


def _symptom_species_match(species_key: str, sp_data: dict, symptoms: list[str]) -> float:
    """Score how well patient symptoms match this species' known symptom profile."""
    high_weight_syms = sp_data.get("key_symptoms", {}).get("high_weight", [])
    distinguishing   = sp_data.get("key_symptoms", {}).get("distinguishing", [])

    score = 0.0
    sym_set = set([s.lower().replace(" ", "_") for s in symptoms])

    for hw in high_weight_syms:
        if hw.replace(" ", "_") in sym_set:
            score += 0.3

    for d in distinguishing:
        if d.replace(" ", "_") in sym_set:
            score += 0.4

    return min(score, 1.0)


def _build_species_explanation(species_key, parts_dict, probs, district, time, season, syndrome):
    if not species_key:
        return ["Insufficient evidence for species determination."]
    sp   = SPECIES_DB[species_key]
    prob = probs.get(species_key, 0)
    lines = [
        f"{sp['common_name']} ({sp['scientific_name']}) estimated at {prob*100:.1f}% probability.",
        f"Evidence factors:"
    ]
    for p in parts_dict.get(species_key, []):
        lines.append(f"  • {p}")
    lines.append(f"Context: {district} district | {time} | {season} | {syndrome} syndrome.")
    return lines
