"""
A-M2 ML Inference Wrapper
==========================
Drop-in ML-based alternative to am2_predictor.predict_am2().
Loads models from ../ml_models/ and rebuilds the exact feature schema
used during training (see feature_schema.json).

Usage (same call shape as the rule-based version):

    from ml_inference import predict_am2_ml
    result = predict_am2_ml(
        am1_output=..., district=..., state=..., time_of_day=...,
        season=..., elapsed_hours=..., patient_context=..., harmful_practices=...
    )

This does NOT replace am2_predictor.py. Both can run side by side —
useful for A/B comparison, or as a fast fallback if the rule engine's
JSON knowledge bases are ever unavailable.
"""

import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

MODEL_DIR = Path(__file__).parent / "ml_models"
KB_DIR = Path(__file__).parent / "knowledge_base"

# ── Load models + schema once at import time ──────────────────────────
_species_model   = joblib.load(MODEL_DIR / "species_model.joblib")
_severity_model  = joblib.load(MODEL_DIR / "severity_model.joblib")
_tth_model       = joblib.load(MODEL_DIR / "time_to_hospital_model.joblib")
_species_encoder = joblib.load(MODEL_DIR / "species_label_encoder.joblib")

with open(MODEL_DIR / "feature_schema.json") as f:
    _schema = json.load(f)

FEATURE_COLUMNS  = _schema["feature_columns"]
SYMPTOM_CLASSES  = set(_schema["symptom_classes"])
SPECIES_CLASSES  = _schema["species_classes"]

with open(KB_DIR / "species_db.json") as f:
    SPECIES_DB = json.load(f)

# same thresholds as the rule engine, kept in sync manually — see note below
SEVERITY_THRESHOLDS = {"CRITICAL": 80, "HIGH": 60, "MODERATE": 35, "LOW": 0}
BIG_FOUR = {"russells_viper", "saw_scaled_viper", "indian_cobra", "common_krait"}
URBAN_DISTRICTS = {"Hyderabad", "Visakhapatnam", "Vijayawada", "Warangal"}


def _score_to_class(score: float) -> str:
    if score >= SEVERITY_THRESHOLDS["CRITICAL"]:
        return "CRITICAL"
    elif score >= SEVERITY_THRESHOLDS["HIGH"]:
        return "HIGH"
    elif score >= SEVERITY_THRESHOLDS["MODERATE"]:
        return "MODERATE"
    return "LOW"


def _referral_priority(severity_class: str) -> str:
    return {
        "CRITICAL": "EMERGENCY — Call ambulance immediately. Do not wait.",
        "HIGH":     "URGENT — Transport to hospital within 30 minutes.",
        "MODERATE": "REQUIRED — Hospital treatment needed within 2 hours.",
        "LOW":      "ADVISORY — Hospital observation recommended. Monitor closely.",
    }[severity_class]


def _recommended_antivenom_name(top_species_key: str) -> str:
    sp = SPECIES_DB.get(top_species_key, {})
    vials = sp.get("antivenom", {}).get("vials_range")
    vial_txt = f" (est. {vials[0]}-{vials[1]} vials)" if vials else ""
    if top_species_key in BIG_FOUR:
        return f"Polyvalent ASV (Big Four coverage){vial_txt}"
    return f"Polyvalent ASV (limited/uncertain efficacy — species not in standard antivenom coverage){vial_txt}"


def _build_feature_row(
    am1_output: dict, district: str, state: str, time_of_day: str,
    season: str, elapsed_hours: float, patient_context: dict,
    harmful_practices: dict
) -> pd.DataFrame:
    """Rebuilds a single-row feature vector matching training-time columns exactly."""
    row = {col: 0 for col in FEATURE_COLUMNS}

    def set_onehot(prefix, value):
        key = f"{prefix}_{value}"
        if key in row:
            row[key] = 1
        # else: unseen category at inference time -> stays all-zero for that
        # group, which XGBoost handles fine (just no signal from it)

    set_onehot("state", state)
    set_onehot("district", district)
    set_onehot("time_of_day", time_of_day)
    set_onehot("season", season)
    set_onehot("am1_venom_type", am1_output.get("venom_type", "unknown"))
    set_onehot("am1_urgency", am1_output.get("urgency", "MEDIUM"))

    row["elapsed_hours"]  = elapsed_hours if elapsed_hours is not None else 2.0
    row["age"]            = patient_context.get("age", 35)
    row["am1_confidence"] = am1_output.get("confidence", 0.70)

    for flag in ["tourniquet_applied", "incision_attempted",
                 "traditional_healer_visited", "herbal_application"]:
        row[flag] = int(bool(harmful_practices.get(flag, False)))

    for sym in am1_output.get("symptoms", []):
        col = f"sym_{sym}"
        if col in row:
            row[col] = 1
        # unseen symptom at inference time: silently dropped (schema-limited)

    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


def predict_am2_ml(
    am1_output:        dict,
    district:          str   = "Unknown",
    state:             str   = None,
    time_of_day:       str   = "evening",
    season:            str   = "monsoon",
    elapsed_hours:     float = None,
    patient_context:   dict  = None,
    harmful_practices: dict  = None,
) -> dict:
    """ML-based drop-in replacement for am2_predictor.predict_am2()."""
    patient_context   = patient_context or {}
    harmful_practices = harmful_practices or {}

    X = _build_feature_row(
        am1_output, district, state, time_of_day, season,
        elapsed_hours, patient_context, harmful_practices
    )

    # ── Species ──────────────────────────────────────────────────────
    species_probs = _species_model.predict_proba(X)[0]
    species_dist  = dict(zip(SPECIES_CLASSES, species_probs.round(4)))
    species_dist  = dict(sorted(species_dist.items(), key=lambda kv: -kv[1]))
    top_species_key = max(species_dist, key=species_dist.get)
    top_species_prob = species_dist[top_species_key]
    top_species_name = SPECIES_DB.get(top_species_key, {}).get("common_name", top_species_key)

    krait_prob = species_dist.get("common_krait", 0) + species_dist.get("banded_krait", 0)

    # ── Severity ─────────────────────────────────────────────────────
    severity_score = float(np.clip(_severity_model.predict(X)[0], 0, 100))
    severity_class = _score_to_class(severity_score)

    # ── Time to hospital ────────────────────────────────────────────
    tth_minutes = float(max(_tth_model.predict(X)[0], 5))

    # ── Derived clinical fields (same logic as clinical_decision.py) ──
    antivenom_required = severity_class in ["HIGH", "CRITICAL"]
    referral_priority = _referral_priority(severity_class)
    antivenom_name = _recommended_antivenom_name(top_species_key)

    return {
        "source": "ml_model",  # flag so callers/UI can distinguish from rule engine
        "probable_species":      {k: v for k, v in list(species_dist.items())[:3]},
        "top_species_name":      top_species_name,
        "top_species_key":       top_species_key,
        "top_species_prob":      top_species_prob,
        "krait_combined_prob":   round(krait_prob, 4),

        "severity_class":        severity_class,
        "severity_score":        round(severity_score, 1),

        "antivenom_required":    antivenom_required,
        "recommended_antivenom_name": antivenom_name,
        "referral_priority":     referral_priority,
        "estimated_time_to_hospital_minutes": round(tth_minutes, 1),

        "context": {
            "district": district, "state": state, "time_of_day": time_of_day,
            "season": season, "elapsed_hours": elapsed_hours,
        },
    }


# ── Demo / smoke test ──────────────────────────────────────────────────
if __name__ == "__main__":
    result = predict_am2_ml(
        am1_output={
            "venom_type": "neurotoxic", "urgency": "HIGH", "confidence": 0.93,
            "symptoms": ["ptosis", "dysphagia", "respiratory_distress", "paralysis"],
        },
        district="Khammam", state="Telangana", time_of_day="night", season="monsoon",
        elapsed_hours=3.5, patient_context={"age": 38},
        harmful_practices={"traditional_healer_visited": True},
    )
    for k, v in result.items():
        print(f"{k}: {v}")
