"""
SmartSnakebite Synthetic Training Data Simulator
=================================================
Samples random-but-realistic patient cases and runs them through the ACTUAL
A-M2 rule-based engines (syndrome_engine, species_engine, severity_engine,
mortality_engine, clinical_decision) shipped in smartsnakebite.zip.

No clinical logic is invented here — every label column comes directly from
calling the user's own functions. This script only samples inputs and adds
two clerical derived fields (antivenom name string + naive travel-time
estimate) built from arithmetic explicitly specified by the user.
"""

import sys
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# ── Wire up the real engine code ──────────────────────────────────────────
AM2_DIR = Path("/home/claude/project/smartsnakebite/backend/modules/am2")
sys.path.insert(0, str(AM2_DIR))

from syndrome_engine import compute_syndrome
from species_engine import compute_species_probabilities
from severity_engine import compute_severity
from mortality_engine import compute_mortality_risk
from clinical_decision import compute_clinical_decision

KB = AM2_DIR / "knowledge_base"
with open(KB / "species_db.json") as f:
    SPECIES_DB = json.load(f)
with open(KB / "district_priors.json") as f:
    DISTRICT_PRIORS = json.load(f)
with open(KB / "symptom_ontology.json") as f:
    ONTOLOGY = json.load(f)

SPECIES_KEYS = [k for k in SPECIES_DB if not k.startswith("_")]
ALL_SYMPTOMS = list(ONTOLOGY["symptoms"].keys())
BIG_FOUR = {"russells_viper", "saw_scaled_viper", "indian_cobra", "common_krait"}
URBAN_DISTRICTS = {"Hyderabad", "Visakhapatnam", "Vijayawada", "Warangal"}

random.seed(42)
np.random.seed(42)

N_ROWS = 15000

# ── Build district list: (state_label, district_key) ─────────────────────
DISTRICTS = []
for state_key, state_label in [("telangana", "Telangana"), ("andhra_pradesh", "Andhra Pradesh")]:
    for dk in DISTRICT_PRIORS[state_key]:
        if dk.startswith("DEFAULT"):
            continue
        DISTRICTS.append((state_label, dk))


def get_district_species_prior(state_label, district_key):
    state_key = "telangana" if state_label == "Telangana" else "andhra_pradesh"
    entry = DISTRICT_PRIORS[state_key][district_key]
    weights = {k: v for k, v in entry.items() if k in SPECIES_KEYS}
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


def sample_true_species(state_label, district_key):
    weights = get_district_species_prior(state_label, district_key)
    keys = list(weights.keys())
    probs = list(weights.values())
    return random.choices(keys, weights=probs, k=1)[0]


def sample_timestamp():
    start = datetime(2024, 1, 1)
    delta_days = random.randint(0, 729)
    dt = start + timedelta(days=delta_days)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    return dt.replace(hour=hour, minute=minute)


def derive_season(dt):
    m = dt.month
    if m in (6, 7, 8, 9):
        return "monsoon"
    elif m in (10, 11):
        return "post_monsoon"
    elif m in (12, 1, 2):
        return "winter"
    else:
        return "summer"


def derive_time_of_day(dt):
    h = dt.hour
    if h >= 20 or h < 5:
        return "night"
    elif 5 <= h < 12:
        return "morning"
    elif 12 <= h < 17:
        return "afternoon"
    else:
        return "evening"


CRITICAL_SYMPTOMS = set(ONTOLOGY["critical_symptoms"])
MILD_GENERIC_SYMPTOMS = ["pain_at_bite_site", "local_pain", "minimal_local_swelling",
                          "painless_bite", "nausea", "dizziness"]

# Real-world envenomation is NOT always severe: WHO/India field studies report
# a substantial share of dry bites and mild presentations, especially early
# after the bite. This layer is not part of the user's original field list,
# but is needed so symptom richness (and therefore am1_urgency/severity)
# isn't artificially maxed out on every single row. Documented in the data
# dictionary as an added simulation parameter.
ENVENOMATION_LEVELS = ["dry", "mild", "moderate", "severe"]
ENVENOMATION_WEIGHTS = [0.15, 0.30, 0.30, 0.25]


def sample_envenomation_level():
    return random.choices(ENVENOMATION_LEVELS, weights=ENVENOMATION_WEIGHTS, k=1)[0]


def sample_symptoms(species_key, envenomation_level, noise_rate=0.15):
    sp = SPECIES_DB[species_key]["key_symptoms"]
    pool = set()
    for bucket in ("high_weight", "moderate_weight", "distinguishing"):
        pool.update(s.replace(" ", "_") for s in sp.get(bucket, []))
    pool = list(pool) if pool else random.sample(ALL_SYMPTOMS, k=3)
    non_critical_pool = [s for s in pool if s not in CRITICAL_SYMPTOMS]

    if envenomation_level == "dry":
        n_true = random.randint(0, 1)
        base_pool = MILD_GENERIC_SYMPTOMS
        chosen = random.sample(base_pool, k=min(n_true, len(base_pool))) if n_true else []
    elif envenomation_level == "mild":
        n_true = random.randint(1, 3)
        base_pool = non_critical_pool if non_critical_pool else pool
        chosen = random.sample(base_pool, k=min(n_true, len(base_pool)))
    elif envenomation_level == "moderate":
        n_true = random.randint(3, 5)
        chosen = random.sample(pool, k=min(n_true, len(pool)))
        if random.random() < 0.20:
            crit_in_pool = [s for s in pool if s in CRITICAL_SYMPTOMS]
            if crit_in_pool:
                chosen.append(random.choice(crit_in_pool))
    else:  # severe
        n_true = random.randint(4, 7)
        chosen = random.sample(pool, k=min(n_true, len(pool)))
        crit_in_pool = [s for s in pool if s in CRITICAL_SYMPTOMS]
        if crit_in_pool and random.random() < 0.75:
            chosen.append(random.choice(crit_in_pool))

    chosen = list(dict.fromkeys(chosen))  # dedupe, preserve order

    if envenomation_level != "dry":
        survivors = [s for s in chosen if random.random() > noise_rate]
        chosen = survivors if survivors else chosen[:1]

    n_noise = np.random.binomial(2, noise_rate)
    noise_candidates = [s for s in ALL_SYMPTOMS if s not in chosen]
    if n_noise and noise_candidates:
        chosen += random.sample(noise_candidates, k=min(n_noise, len(noise_candidates)))

    random.shuffle(chosen)
    return chosen


def sample_am1_venom_type(species_key, error_rate=0.10):
    true_syndrome = SPECIES_DB[species_key]["venom_syndrome"]
    components = true_syndrome.split("_")
    # weighted toward first-listed component as the "primary" reading
    if len(components) > 1:
        weights = [0.65, 0.35] + [0] * (len(components) - 2)
        weights = weights[: len(components)]
        correct_pick = random.choices(components, weights=weights, k=1)[0]
    else:
        correct_pick = components[0]

    all_labels = ["neurotoxic", "hemotoxic", "cytotoxic", "myotoxic"]
    if random.random() < error_rate:
        wrong_options = [l for l in all_labels if l not in components]
        picked = random.choice(wrong_options)
        was_correct = False
    else:
        picked = correct_pick
        was_correct = True
    return picked, was_correct


def sample_am1_confidence(was_correct):
    if was_correct:
        return round(np.clip(np.random.normal(0.85, 0.10), 0.55, 0.99), 3)
    else:
        return round(np.clip(np.random.normal(0.60, 0.12), 0.40, 0.90), 3)


def sample_am1_urgency(envenomation_level, elapsed_hours):
    """Not part of the user's explicit sampling list, but severity_engine
    requires an am1_urgency input. Approximated from the simulated
    envenomation_level (dry/mild/moderate/severe) plus elapsed time, with
    noise, to mimic an upstream NLP severity classifier. Documented in the
    data dictionary as an added simulation parameter."""
    base_probs = {
        "dry":      {"LOW": 0.75, "MEDIUM": 0.20, "HIGH": 0.04, "CRITICAL": 0.01},
        "mild":     {"LOW": 0.40, "MEDIUM": 0.45, "HIGH": 0.13, "CRITICAL": 0.02},
        "moderate": {"LOW": 0.08, "MEDIUM": 0.42, "HIGH": 0.40, "CRITICAL": 0.10},
        "severe":   {"LOW": 0.02, "MEDIUM": 0.13, "HIGH": 0.45, "CRITICAL": 0.40},
    }
    probs = dict(base_probs[envenomation_level])
    if elapsed_hours > 6:
        probs["CRITICAL"] += 0.05
        probs["HIGH"] += 0.05
        probs["LOW"] = max(probs["LOW"] - 0.10, 0.01)
    labels = list(probs.keys())
    weights = np.array(list(probs.values()))
    weights = weights / weights.sum()
    return random.choices(labels, weights=weights, k=1)[0]


def sample_age():
    r = random.random()
    if r < 0.08:
        return int(np.clip(np.random.normal(8, 3), 1, 11))
    elif r < 0.85:
        return int(np.clip(np.random.normal(38, 13), 12, 65))
    else:
        return int(np.clip(np.random.normal(72, 6), 66, 95))


def sample_elapsed_hours():
    val = np.random.exponential(scale=2.2)
    return round(float(np.clip(val, 0.1, 24.0)), 2)


def sample_harmful_practices(is_rural):
    if is_rural:
        p = {"tourniquet_applied": 0.28, "incision_attempted": 0.16,
             "traditional_healer_visited": 0.22, "herbal_application": 0.20}
    else:
        p = {"tourniquet_applied": 0.10, "incision_attempted": 0.05,
             "traditional_healer_visited": 0.05, "herbal_application": 0.08}
    return {k: (random.random() < v) for k, v in p.items()}


def recommended_antivenom_name(top_species_key):
    if top_species_key is None:
        return "Insufficient evidence — Polyvalent ASV as empirical default"
    vials = SPECIES_DB[top_species_key]["antivenom"].get("vials_range", [None, None])
    vial_str = f" (est. {vials[0]}-{vials[1]} vials)" if vials[0] is not None else ""
    if top_species_key in BIG_FOUR:
        return f"Polyvalent ASV (Big Four coverage){vial_str}"
    else:
        return f"Polyvalent ASV (limited/uncertain efficacy — species not in standard antivenom coverage){vial_str}"


REFERRAL_BASE_MIN = {"EMERGENCY": 15, "URGENT": 30, "REQUIRED": 120, "ADVISORY": 240}


def estimate_time_to_hospital(referral_priority_text, district_key):
    key = referral_priority_text.split(" ")[0].split("—")[0].strip().upper()
    if key not in REFERRAL_BASE_MIN:
        key = "REQUIRED"
    base = REFERRAL_BASE_MIN[key]
    jitter = np.random.uniform(0.8, 1.2)
    val = base * jitter
    if district_key not in URBAN_DISTRICTS:
        val += np.random.uniform(15, 45)
    return round(float(val), 1)


# ── Main simulation loop ──────────────────────────────────────────────────
rows = []
for i in range(N_ROWS):
    state_label, district_key = random.choice(DISTRICTS)
    is_rural = district_key not in URBAN_DISTRICTS

    dt = sample_timestamp()
    season = derive_season(dt)
    time_of_day = derive_time_of_day(dt)

    true_species = sample_true_species(state_label, district_key)
    envenomation_level = sample_envenomation_level()
    symptoms = sample_symptoms(true_species, envenomation_level)
    am1_venom_type, venom_correct = sample_am1_venom_type(true_species)
    am1_confidence = sample_am1_confidence(venom_correct)
    elapsed_hours = sample_elapsed_hours()
    am1_urgency = sample_am1_urgency(envenomation_level, elapsed_hours)
    age = sample_age()
    harmful_practices = sample_harmful_practices(is_rural)
    patient_context = {"age": age}

    # ── Run the ACTUAL pipeline, in order ──────────────────────────────
    syndrome_result = compute_syndrome(am1_venom_type, symptoms)
    species_result = compute_species_probabilities(
        syndrome_result=syndrome_result,
        district=district_key,
        time_of_day=time_of_day,
        season=season,
        symptoms=symptoms,
        state=state_label,
    )
    severity_result = compute_severity(
        am1_urgency=am1_urgency,
        am1_confidence=am1_confidence,
        syndrome_result=syndrome_result,
        elapsed_hours=elapsed_hours,
        patient_context=patient_context,
        harmful_practices=harmful_practices,
        species_result=species_result,
    )
    mortality_result = compute_mortality_risk(
        severity_result=severity_result,
        syndrome_result=syndrome_result,
        species_result=species_result,
        elapsed_hours=elapsed_hours,
        harmful_practices=harmful_practices,
        patient_context=patient_context,
    )
    clinical_result = compute_clinical_decision(
        severity_result=severity_result,
        mortality_result=mortality_result,
        syndrome_result=syndrome_result,
        species_result=species_result,
        harmful_practices=harmful_practices,
        elapsed_hours=elapsed_hours,
    )

    top_species_key = species_result["top_species_key"]

    row = {
        # ── inputs ──
        "case_id": i + 1,
        "bite_timestamp": dt.isoformat(),
        "state": state_label,
        "district": district_key,
        "time_of_day": time_of_day,
        "season": season,
        "elapsed_hours": elapsed_hours,
        "age": age,
        "symptoms": ",".join(symptoms),
        "am1_venom_type": am1_venom_type,
        "am1_confidence": am1_confidence,
        "am1_urgency": am1_urgency,
        "tourniquet_applied": harmful_practices["tourniquet_applied"],
        "incision_attempted": harmful_practices["incision_attempted"],
        "traditional_healer_visited": harmful_practices["traditional_healer_visited"],
        "herbal_application": harmful_practices["herbal_application"],
        "hidden_true_species": true_species,  # ground truth, NOT fed to the model
        "hidden_envenomation_level": envenomation_level,  # ground truth, NOT fed to the model

        # ── syndrome engine outputs ──
        "primary_syndrome": syndrome_result["primary_syndrome"],
        "syndrome_label": syndrome_result["syndrome_label"],
        "is_mixed_syndrome": syndrome_result["is_mixed"],
        "syndrome_score_neurotoxic": syndrome_result["syndrome_scores"]["neurotoxic"],
        "syndrome_score_hemotoxic": syndrome_result["syndrome_scores"]["hemotoxic"],
        "syndrome_score_cytotoxic": syndrome_result["syndrome_scores"]["cytotoxic"],
        "syndrome_score_myotoxic": syndrome_result["syndrome_scores"]["myotoxic"],
        "has_critical_symptom": syndrome_result["has_critical"],

        # ── species engine outputs ──
        "top_species_key": top_species_key,
        "top_species_name": species_result["top_species_name"],
        "top_species_probability": species_result["top_probability"],
        "krait_escalation": species_result["krait_escalation"],
        "top_species_correct": (top_species_key == true_species),

        # ── severity / mortality ──
        "severity_score": severity_result["severity_score"],
        "severity_class": severity_result["severity_class"],
        "mortality_risk_score": mortality_result["mortality_risk_score"],
        "mortality_risk_class": mortality_result["mortality_risk_class"],

        # ── clinical decision ──
        "antivenom_required": clinical_result["antivenom_required"],
        "antivenom_priority": clinical_result["antivenom_priority"],
        "referral_priority": clinical_result["referral_priority"],

        # ── derived fields (arithmetic only, per user spec) ──
        "recommended_antivenom_name": recommended_antivenom_name(top_species_key),
        "estimated_time_to_hospital_minutes": estimate_time_to_hospital(
            clinical_result["referral_priority"], district_key
        ),
    }

    # per-species probability columns
    for sk in SPECIES_KEYS:
        row[f"species_prob_{sk}"] = species_result["all_probabilities"].get(sk, 0.0)

    rows.append(row)

df = pd.DataFrame(rows)

OUT_CSV = Path("/home/claude/smartsnakebite_synthetic_dataset.csv")
df.to_csv(OUT_CSV, index=False)

print(f"Saved {len(df)} rows to {OUT_CSV}")
print("\n=== SANITY STATS ===")
print("\nSeverity class balance:")
print(df["severity_class"].value_counts())
print("\nMortality risk class balance:")
print(df["mortality_risk_class"].value_counts())
print("\nTop species (model-predicted) distribution:")
print(df["top_species_key"].value_counts())
print("\nHidden true species distribution:")
print(df["hidden_true_species"].value_counts())
print("\nTop-species prediction accuracy vs hidden true species:", df["top_species_correct"].mean())
print("\nDistrict row counts (min/max):", df["district"].value_counts().min(), df["district"].value_counts().max())
print("\nAntivenom required rate:", df["antivenom_required"].mean())
print("\nReferral priority distribution:")
print(df["referral_priority"].apply(lambda s: s.split(" ")[0]).value_counts())
