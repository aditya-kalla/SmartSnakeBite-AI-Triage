"""
A-M2 Configurable Thresholds
SmartSnakebite — Aditya Module 2
All decision boundaries stored here. Never hardcode in engine files.
"""

# ── Severity Score → Severity Class ──────────────────────────────────────
SEVERITY_THRESHOLDS = {
    "CRITICAL": 80,
    "HIGH":     60,
    "MODERATE": 35,
    "LOW":      0
}

# ── Mortality Risk Score → Mortality Class ────────────────────────────────
MORTALITY_THRESHOLDS = {
    "VERY_HIGH": 75,
    "HIGH":      55,
    "MODERATE":  30,
    "LOW":       0
}

# ── Syndrome Score Thresholds (minimum to declare syndrome active) ─────────
SYNDROME_ACTIVATION_THRESHOLD = 0.30
MIXED_SYNDROME_THRESHOLD       = 0.20   # if 2+ syndromes cross this, declare mixed

# ── Species Probability Minimum to Report ────────────────────────────────
MIN_SPECIES_PROBABILITY = 0.05   # species below this not shown in output
TOP_N_SPECIES           = 3      # number of top species to return

# ── Elapsed Time Risk Escalation (hours) ─────────────────────────────────
ELAPSED_TIME_WEIGHTS = {
    "within_1h":   0,
    "1_to_3h":     10,
    "3_to_6h":     20,
    "6_to_12h":    30,
    "over_12h":    40
}

# ── A-M1 Confidence Penalty (low confidence adds uncertainty) ─────────────
AM1_CONFIDENCE_PENALTY = {
    "high":    0,       # confidence >= 0.85: no penalty
    "medium": 5,        # confidence 0.60–0.84: small penalty
    "low":    15        # confidence < 0.60: larger penalty
}

# ── Harmful Practice Risk Additions ───────────────────────────────────────
HARMFUL_PRACTICE_WEIGHTS = {
    "tourniquet_applied":         15,
    "incision_attempted":         10,
    "traditional_healer_visited": 20,
    "herbal_application":         8,
    "delay_before_treatment_h":   5    # per hour of delay
}

# ── Patient Risk Factor Weights ───────────────────────────────────────────
PATIENT_RISK_WEIGHTS = {
    "age_pediatric":   15,    # age < 12
    "age_elderly":     10,    # age > 65
    "occupation_farm": 0      # no additional risk
}

# ── Critical Symptom Instant Escalation ───────────────────────────────────
# Any of these symptoms automatically escalates severity to CRITICAL minimum
CRITICAL_SYMPTOM_ESCALATION_THRESHOLD = "HIGH"

# ── Krait Special Override ─────────────────────────────────────────────────
# If krait probability > this AND neurotoxic AND night bite → escalate to HIGH minimum
KRAIT_PROBABILITY_ESCALATION = 0.35

# ── Antivenom Urgency Map ─────────────────────────────────────────────────
ANTIVENOM_PRIORITY = {
    "CRITICAL": "EMERGENCY_IMMEDIATE",
    "HIGH":     "URGENT_WITHIN_30MIN",
    "MODERATE": "REQUIRED_SOON",
    "LOW":      "OBSERVE_MAY_NEED"
}
