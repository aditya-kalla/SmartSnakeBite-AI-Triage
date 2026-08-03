# SmartSnakebite Synthetic Dataset — Data Dictionary

**File:** `smartsnakebite_synthetic_dataset.csv`
**Rows:** 15,000 | **Columns:** 47
**Generation method:** Randomly sampled inputs run through the actual A-M2 engines
(`syndrome_engine.py`, `species_engine.py`, `severity_engine.py`, `mortality_engine.py`,
`clinical_decision.py`) from `smartsnakebite.zip`. No clinical thresholds, weights, or
decision logic were invented — every label column is the real return value of your
functions. Two purely-arithmetic derived fields were added exactly as you specified.

## ⚠️ Two things I added that weren't in your original field list

Your engines require two inputs your sampling spec didn't cover. I built simple,
documented samplers for both rather than leaving them undefined — flagging them here
since they materially affect severity distribution:

1. **`am1_urgency`** — required by `severity_engine.compute_severity()`. Sampled from
   an invented `hidden_envenomation_level` (dry/mild/moderate/severe, see below), not
   from your knowledge base. This is the single biggest driver of severity_class, so
   if you have real A-M1 urgency-label statistics, swap this sampler out.
2. **`hidden_envenomation_level`** — a dry-bite/mild/moderate/severe layer controlling
   how many (and which) symptoms are sampled. Without it, every case had a full
   venom symptom profile and the dataset was ~94% CRITICAL / 99% antivenom-required
   (see Sanity Check Notes below for the before/after). This field is ground truth
   only — never passed to any engine — same treatment as `hidden_true_species`.

## Input / Sampled Feature Columns

| Column | Type | Description |
|---|---|---|
| `case_id` | int | Row identifier, 1–15000 |
| `bite_timestamp` | ISO datetime | Randomly sampled Jan 2024–Dec 2025 |
| `state` | str | `Telangana` or `Andhra Pradesh` |
| `district` | str | District key (underscore form matches `district_priors.json`) |
| `time_of_day` | str | Derived from timestamp hour: night 20–05, morning 05–12, afternoon 12–17, evening 17–20 |
| `season` | str | Derived from month: monsoon (Jun–Sep), post_monsoon (Oct–Nov), winter (Dec–Feb), summer (Mar–May) |
| `elapsed_hours` | float | Hours since bite. Exponential distribution (scale 2.2), clipped to [0.1, 24] |
| `age` | int | Mixture: 8% pediatric (~N(8,3)), 77% adult (~N(38,13)), 15% elderly (~N(72,6)) |
| `symptoms` | str | Comma-separated symptom keys extracted for this case (see envenomation-level logic above) |
| `am1_venom_type` | str | Simulated A-M1 venom-type output. Correct ~90% of the time (matches true species' `venom_syndrome`, weighted toward first component for mixed-syndrome species); wrong ~10% (random other single-syndrome label) |
| `am1_confidence` | float | 0.4–0.99. Higher (~N(0.85,0.10)) when `am1_venom_type` is correct, lower (~N(0.60,0.12)) when wrong |
| `am1_urgency` | str | LOW/MEDIUM/HIGH/CRITICAL — see note above |
| `tourniquet_applied`, `incision_attempted`, `traditional_healer_visited`, `herbal_application` | bool | Independent booleans. Rural (non-urban) districts get higher base probability (e.g. tourniquet 28% rural vs 10% urban) |
| `hidden_true_species` | str | **Ground truth only** — never fed to any engine. One of the 7 species keys, sampled from that district's prior in `district_priors.json` |
| `hidden_envenomation_level` | str | **Ground truth only** — dry / mild / moderate / severe. Drives symptom sampling |

## Output Columns — direct engine returns

| Column | Source function | Description |
|---|---|---|
| `primary_syndrome`, `syndrome_label`, `is_mixed_syndrome` | `syndrome_engine.compute_syndrome()` | Top syndrome, display label, mixed-syndrome flag |
| `syndrome_score_neurotoxic/hemotoxic/cytotoxic/myotoxic` | same | The 4 raw syndrome scores (0–1) |
| `has_critical_symptom` | same | Whether any symptom is in the ontology's critical-symptom list |
| `top_species_key`, `top_species_name`, `top_species_probability` | `species_engine.compute_species_probabilities()` | Model's top-ranked species and its probability |
| `species_prob_<species>` (×7) | same | Full probability distribution across all 7 species (`all_probabilities`) |
| `krait_escalation` | same | True if combined krait probability ≥0.35 and primary syndrome is neurotoxic |
| `top_species_correct` | derived by me | `top_species_key == hidden_true_species`, for model-accuracy sanity checking only — not an engine output |
| `severity_score`, `severity_class` | `severity_engine.compute_severity()` | 0–100 score and LOW/MODERATE/HIGH/CRITICAL class |
| `mortality_risk_score`, `mortality_risk_class` | `mortality_engine.compute_mortality_risk()` | 0–100 score and LOW/MODERATE/HIGH/VERY_HIGH class |
| `antivenom_required`, `antivenom_priority`, `referral_priority` | `clinical_decision.compute_clinical_decision()` | Whether ASV is indicated, urgency bucket, and the referral-priority sentence |

## Output Columns — derived by me (arithmetic only, per your spec)

| Column | Logic |
|---|---|
| `recommended_antivenom_name` | If `top_species_key` ∈ {russells_viper, saw_scaled_viper, indian_cobra, common_krait} → `"Polyvalent ASV (Big Four coverage)"`; else → `"Polyvalent ASV (limited/uncertain efficacy — species not in standard antivenom coverage)"`. Appends `(est. X-Y vials)` from `species_db.json` |
| `estimated_time_to_hospital_minutes` | Base by referral priority word (EMERGENCY=15, URGENT=30, REQUIRED=120, ADVISORY=240) × jitter(0.8–1.2), +15–45 min extra if district ∉ {Hyderabad, Visakhapatnam, Vijayawada, Warangal} |

## Sanity Check Notes (read before training on this)

- **Species distribution** roughly tracks district priors: common_krait (4,226 hidden / 4,846 predicted) and indian_cobra (3,648 / 5,229) dominate, matching the knowledge base's krait/cobra-heavy priors for most districts. slender_coral_snake is correctly rare (180 hidden cases) since it has the lowest district priors everywhere.
- **Top-species prediction accuracy** (`top_species_correct` mean) is **52%** — i.e., even with a hidden hand-generated ground truth and the district's own prior, the species engine's top pick matches the "true" species just over half the time. This is expected given only 7 overlapping-symptom species and real evidentiary ambiguity — it is *not* a bug in the simulator, it's an honest reflection of how ambiguous species ID is from symptoms+location alone in your current engine design.
- **Severity/mortality skew toward CRITICAL/VERY_HIGH remains even after rebalancing** (57% CRITICAL severity, 88% VERY_HIGH mortality). I traced this to your engines' own base constants, not the sampler: `SYNDROME_MORTALITY_BASE` alone gives 45–55 points before anything else is added, and `URGENCY_BASE_SCORES["HIGH"]=60` / `["CRITICAL"]=85` in severity_engine dominate the 100-point scale. Even "dry bite" cases (0–1 symptoms) can land in HIGH/CRITICAL severity if a tourniquet + traditional healer + elderly age stack up — which is plausible (pre-hospital harm without envenomation) but worth knowing before you train a classifier on this, since the label distribution reflects your rule thresholds, not epidemiological base rates. If you want a more balanced training distribution, the fix belongs in `thresholds.py`/`severity_engine.py`, not in the sampler.
- **District row counts** are even (511–588 per district across 27 districts) — sampling is uniform over districts, not population-weighted. Let me know if you'd rather weight by real population/bite-incidence.
- **Antivenom required** in 97.3% of rows — follows directly from the severity/mortality skew above.
- `elapsed_hours`: median 1.5h, 75th percentile 3.0h, max ~20h — matches your "many <2h, long tail to 24h" spec.
- `age`: median 39, IQR 27–52 — matches "skew toward working-age adults" spec.
