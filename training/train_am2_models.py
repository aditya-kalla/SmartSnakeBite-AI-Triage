"""
SmartSnakebite — A-M2 Model Training
=====================================
Trains 3 XGBoost models on smartsnakebite_synthetic_dataset.csv:
  1. Species classifier   -> multi-class probability distribution (7 species)
  2. Severity regressor    -> severity_score (0-100)
  3. Time-to-hospital reg. -> estimated_time_to_hospital_minutes

Design choice: models predict the RULE ENGINE'S output (distillation), not
hidden_true_species/real outcomes. That's intentional — see chat notes.
Class imbalance (57% CRITICAL etc.) is handled via sample_weight, NOT by
touching thresholds.py.

Install once:
    pip install xgboost scikit-learn pandas joblib --break-system-packages
"""

import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import classification_report, mean_absolute_error, r2_score
import xgboost as xgb

DATA_PATH = "smartsnakebite_synthetic_dataset.csv"
OUT_DIR = Path("am2_models")
OUT_DIR.mkdir(exist_ok=True)

SPECIES = [
    "common_krait", "indian_cobra", "russells_viper", "saw_scaled_viper",
    "banded_krait", "bamboo_pit_viper", "slender_coral_snake",
]

# ── Load ──────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
print(f"Loaded {len(df)} rows, {df.shape[1]} cols")

# ── Feature engineering (shared across all 3 models) ─────────────────
def build_features(df: pd.DataFrame):
    X = pd.DataFrame(index=df.index)

    # Categorical -> one-hot
    for col in ["state", "district", "time_of_day", "season", "am1_venom_type", "am1_urgency"]:
        dummies = pd.get_dummies(df[col], prefix=col)
        X = pd.concat([X, dummies], axis=1)

    # Numeric, as-is
    for col in ["elapsed_hours", "age", "am1_confidence"]:
        X[col] = df[col]

    # Booleans -> int
    for col in ["tourniquet_applied", "incision_attempted",
                "traditional_healer_visited", "herbal_application"]:
        X[col] = df[col].astype(int)

    # Symptoms: multi-hot encode the comma-separated list
    symptom_lists = df["symptoms"].fillna("").apply(
        lambda s: [x.strip() for x in s.split(",") if x.strip()]
    )
    mlb = MultiLabelBinarizer()
    symptom_matrix = mlb.fit_transform(symptom_lists)
    symptom_df = pd.DataFrame(
        symptom_matrix, columns=[f"sym_{c}" for c in mlb.classes_], index=df.index
    )
    X = pd.concat([X, symptom_df], axis=1)

    return X, mlb


X, symptom_binarizer = build_features(df)
print(f"Feature matrix: {X.shape}")

X_train, X_test, idx_train, idx_test = train_test_split(
    X, df.index, test_size=0.15, random_state=42
)
df_train, df_test = df.loc[idx_train], df.loc[idx_test]

# =======================================================================
# MODEL 1 — Species classifier (predict which species engine ranked #1)
# =======================================================================
print("\n=== Training species classifier ===")

species_encoder = LabelEncoder()
species_encoder.fit(df["top_species_key"])
y_train_sp = species_encoder.transform(df_train["top_species_key"])
y_test_sp = species_encoder.transform(df_test["top_species_key"])

# handle class imbalance across species
sample_w = compute_sample_weight(class_weight="balanced", y=y_train_sp)

species_model = xgb.XGBClassifier(
    objective="multi:softprob",
    num_class=len(species_encoder.classes_),
    n_estimators=300,
    max_depth=6,
    learning_rate=0.08,
    subsample=0.85,
    colsample_bytree=0.85,
    eval_metric="mlogloss",
    n_jobs=-1,
)
species_model.fit(X_train, y_train_sp, sample_weight=sample_w)

pred_sp = species_model.predict(X_test)
print(classification_report(
    y_test_sp, pred_sp, target_names=species_encoder.classes_, zero_division=0
))

joblib.dump(species_model, OUT_DIR / "species_model.joblib")
joblib.dump(species_encoder, OUT_DIR / "species_label_encoder.joblib")

# =======================================================================
# MODEL 2 — Severity score regressor (0-100)
# =======================================================================
print("\n=== Training severity regressor ===")

y_train_sev = df_train["severity_score"]
y_test_sev = df_test["severity_score"]

# weight rare classes (LOW/MODERATE) higher so regressor doesn't ignore them
sev_class_w = compute_sample_weight(class_weight="balanced", y=df_train["severity_class"])

severity_model = xgb.XGBRegressor(
    objective="reg:squarederror",
    n_estimators=350,
    max_depth=6,
    learning_rate=0.06,
    subsample=0.85,
    colsample_bytree=0.85,
    n_jobs=-1,
)
severity_model.fit(X_train, y_train_sev, sample_weight=sev_class_w)

pred_sev = severity_model.predict(X_test)
print(f"MAE: {mean_absolute_error(y_test_sev, pred_sev):.2f}  R2: {r2_score(y_test_sev, pred_sev):.3f}")

joblib.dump(severity_model, OUT_DIR / "severity_model.joblib")

# =======================================================================
# MODEL 3 — Time-to-hospital regressor (minutes)
# =======================================================================
print("\n=== Training time-to-hospital regressor ===")

y_train_tth = df_train["estimated_time_to_hospital_minutes"]
y_test_tth = df_test["estimated_time_to_hospital_minutes"]

tth_model = xgb.XGBRegressor(
    objective="reg:squarederror",
    n_estimators=250,
    max_depth=5,
    learning_rate=0.08,
    subsample=0.85,
    colsample_bytree=0.85,
    n_jobs=-1,
)
tth_model.fit(X_train, y_train_tth)

pred_tth = tth_model.predict(X_test)
print(f"MAE: {mean_absolute_error(y_test_tth, pred_tth):.2f} min  R2: {r2_score(y_test_tth, pred_tth):.3f}")

joblib.dump(tth_model, OUT_DIR / "time_to_hospital_model.joblib")

# ── Save feature schema so inference code can rebuild X identically ──
schema = {
    "feature_columns": list(X.columns),
    "symptom_classes": list(symptom_binarizer.classes_),
    "species_classes": list(species_encoder.classes_),
}
with open(OUT_DIR / "feature_schema.json", "w") as f:
    json.dump(schema, f, indent=2)

print(f"\nAll models + schema saved to {OUT_DIR}/")
print("Files:", [p.name for p in OUT_DIR.iterdir()])
