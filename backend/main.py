"""
SmartSnakebite — FastAPI Orchestrator
Pipeline: text -> AM1 (venom/severity) -> AM3 (harmful practices/delay) -> AM2 (clinical decision)
"""

import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from stt import transcribe_audio
from tts import speak as tts_speak
from speech_templates import build_spoken_summary

MODULES = Path(__file__).parent / "modules"
sys.path.insert(0, str(MODULES / "am1"))
sys.path.insert(0, str(MODULES / "am2"))
sys.path.insert(0, str(MODULES / "am3"))
sys.path.insert(0, str(MODULES / "snake_id"))

from predictor import predict as predict_am1
from symptom_extractor import extract_symptoms
from am2_predictor import predict_am2
from am3_predictor import predict_am3
try:
    from snake_id_inference import classify_photo, match_description
except Exception as e:
    print(f"[SNAKE ID WARNING] Could not import snake_id_inference: {e}")
    classify_photo = None
    match_description = None

import json
try:
    with open(MODULES / "snake_id" / "species_id_clinical_mapping.json", encoding="utf-8") as f:
        SPECIES_MAPPING = json.load(f)
except Exception as e:
    print(f"[SNAKE ID WARNING] Could not load species_id_clinical_mapping.json: {e}")
    SPECIES_MAPPING = {}

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="SmartSnakebite API")

SNAKE_ID_MODELS_DIR = MODULES / "snake_id" / "snake_id_models"
app.mount("/snake-id-images", StaticFiles(directory=str(SNAKE_ID_MODELS_DIR), check_dir=False), name="snake-id-images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    language: str = Form("auto")
):
    audio_bytes = await audio.read()
    return transcribe_audio(audio_bytes, language)


class PipelineRequest(BaseModel):
    text: str
    district: str = "Unknown"
    state: Optional[str] = None
    time_of_day: str = "evening"
    season: str = "monsoon"
    elapsed_hours: Optional[float] = None
    patient_age: Optional[int] = None
    patient_occupation: Optional[str] = None
    language: str = "auto"
    lat: Optional[float] = None
    lng: Optional[float] = None
    tourniquet_applied: Optional[bool] = None
    incision_attempted: Optional[bool] = None
    traditional_healer_visited: Optional[bool] = None
    herbal_application: Optional[bool] = None


@app.get("/api/health")
def health():
    return {"status": "ok"}


class SpeakRequest(BaseModel):
    text: str
    language: str = "en"


@app.post("/api/speak")
def speak_endpoint(req: SpeakRequest):
    audio_bytes = tts_speak(req.text, req.language)
    return Response(content=audio_bytes, media_type="audio/wav")


class SpeakSummaryRequest(BaseModel):
    severity_class: str
    antivenom_required: bool
    language: str = "en"


@app.post("/api/speak-summary")
def speak_summary_endpoint(req: SpeakSummaryRequest):
    text = build_spoken_summary(req.severity_class, req.antivenom_required, req.language)
    audio_bytes = tts_speak(text, req.language)
    return Response(content=audio_bytes, media_type="audio/wav")


@app.post("/api/full-pipeline")
def full_pipeline(req: PipelineRequest):
    # NOTE: req.lat / req.lng are captured from the browser's GPS but not
    # yet resolved to a district — that resolution arrives with Hasini's
    # hospital-routing module. For now district falls back to req.district
    # (defaults to "Unknown") until that integration lands.

    # ── AM1 ──────────────────────────────────────────────────────────────
    am1_result = predict_am1(req.text)

    urgency_map = {
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW",
    }

    am1_urgency = urgency_map.get(
        am1_result.get("severity", "MEDIUM"),
        "MEDIUM"
    )

    extracted_symptoms = extract_symptoms(req.text)

    am1_output_for_am2 = {
        "venom_type": am1_result.get("venom_type", "unknown"),
        "urgency": am1_urgency,
        "confidence": am1_result.get("confidence", 0.7),
        "symptoms": extracted_symptoms,
    }

    # ── AM3 ──────────────────────────────────────────────────────────────
    am3_result = predict_am3(
        narrative=req.text,
        language=req.language,
        elapsed_hours=req.elapsed_hours,
    )

    am3_out = am3_result["am3_output"]

    harmful_practices = {
        flag: True for flag in am3_out["am2_harmful_flags"]
    }
    if req.tourniquet_applied:
        harmful_practices["tourniquet_applied"] = True
    if req.incision_attempted:
        harmful_practices["incision_attempted"] = True
    if req.traditional_healer_visited:
        harmful_practices["traditional_healer_visited"] = True
    if req.herbal_application:
        harmful_practices["herbal_application"] = True

    effective_elapsed = (
        req.elapsed_hours
        if req.elapsed_hours is not None
        else am3_out["am2_total_delay_hours"]
    )

    patient_context = {}

    if req.patient_age is not None:
        patient_context["age"] = req.patient_age

    if req.patient_occupation:
        patient_context["occupation"] = req.patient_occupation

    # ── AM2 ──────────────────────────────────────────────────────────────
    am2_result = predict_am2(
        am1_output=am1_output_for_am2,
        district=req.district,
        state=req.state,
        time_of_day=req.time_of_day,
        season=req.season,
        elapsed_hours=effective_elapsed,
        patient_context=patient_context,
        harmful_practices=harmful_practices,
    )

    return {
        "am1": am1_result,
        "am1_extracted_symptoms": extracted_symptoms,
        "am3": am3_out,
        "am2": am2_result,
    }


@app.post("/api/predict")
def predict(req: PipelineRequest):
    return full_pipeline(req)


def enrich_snake_id_results(results: list[dict]) -> dict:
    show_venom_caution = False
    for item in results:
        species_name = item.get("species", "")
        mapping_val = SPECIES_MAPPING.get(species_name)
        if not mapping_val:
            normalized = species_name.replace(" ", "_").replace("-", "_").replace("'", "")
            mapping_val = SPECIES_MAPPING.get(normalized)
        if not mapping_val:
            for k, val in SPECIES_MAPPING.items():
                if k.lower().replace("_", "") == species_name.lower().replace(" ", "").replace("-", "").replace("'", ""):
                    mapping_val = val
                    break
        
        if mapping_val:
            item["clinical_key"] = mapping_val.get("clinical_key")
            item["venomous"] = mapping_val.get("venomous", False)
            item["medical_significance"] = mapping_val.get("medical_significance", "none")
            item["note"] = mapping_val.get("note", "")
        else:
            item["clinical_key"] = None
            item["venomous"] = False
            item["medical_significance"] = "none"
            item["note"] = "Identification only."

        if item.get("medical_significance", "none") != "none":
            show_venom_caution = True

        if item.get("sample_image"):
            clean_path = str(item["sample_image"]).replace("\\", "/").replace("//", "/").lstrip("/")
            item["sample_image"] = f"/snake-id-images/{clean_path}"

    return {
        "results": results,
        "show_venom_caution": show_venom_caution
    }


@app.post("/api/snake-id/photo")
async def snake_id_photo(image: UploadFile = File(...)):
    if classify_photo is None:
        raise HTTPException(status_code=503, detail="Snake ID service unavailable: module not loaded")
    try:
        image_bytes = await image.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to read image upload")
    
    try:
        results = classify_photo(image_bytes)
    except RuntimeError as e:
        if "unavailable" in str(e).lower() or "not available" in str(e).lower():
            raise HTTPException(status_code=503, detail=str(e))
        raise HTTPException(status_code=400, detail="Invalid or corrupt image upload")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid or corrupt image upload")

    return enrich_snake_id_results(results)


class DescribeRequest(BaseModel):
    text: str


@app.post("/api/snake-id/describe")
def snake_id_describe(req: DescribeRequest):
    if match_description is None:
        raise HTTPException(status_code=503, detail="Snake ID service unavailable: module not loaded")
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Description text is required")
    try:
        results = match_description(req.text)
    except RuntimeError as e:
        if "unavailable" in str(e).lower() or "not available" in str(e).lower():
            raise HTTPException(status_code=503, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return enrich_snake_id_results(results)