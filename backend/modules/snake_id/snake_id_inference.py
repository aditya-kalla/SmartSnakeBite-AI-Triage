"""
SmartSnakebite — Snake ID Inference Wrapper
=============================================
Combines the fine-tuned photo classifier + the CLIP description-matching
gallery into one module with two entry points:

    classify_photo(image_bytes)   -> top-k species from an uploaded photo
    match_description(text)       -> top-k species from a typed/spoken description

Both return the same schema so the frontend can render one result-card UI
regardless of which input mode the user used.

Expects these files (produced by train_snake_classifier.py and
build_clip_gallery.py) in ./snake_id_models/:
    snake_classifier_best.pt
    class_names.json
    clip_gallery.npz
    clip_species_list.json
"""

import json
import io
from pathlib import Path

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from torchvision import transforms, models
import open_clip

MODEL_DIR = Path(__file__).parent / "snake_id_models"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TOP_K = 3

_SNAKE_ID_AVAILABLE = False
_SNAKE_ID_ERROR = None
_classifier = None
_photo_transform = None
_clip_model = None
_clip_tokenizer = None
_gallery_embeddings = None
_gallery_labels = None
_gallery_paths = None
CLASS_NAMES = []

try:
    with open(MODEL_DIR / "class_names.json") as f:
        CLASS_NAMES = json.load(f)

    _classifier = models.efficientnet_b0(weights=None)
    _in_features = _classifier.classifier[1].in_features
    _classifier.classifier[1] = torch.nn.Linear(_in_features, len(CLASS_NAMES))
    _classifier.load_state_dict(torch.load(MODEL_DIR / "snake_classifier_best.pt", map_location=DEVICE))
    _classifier = _classifier.to(DEVICE).eval()

    _photo_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    _clip_model, _, _clip_preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained="openai"
    )
    _clip_model = _clip_model.to(DEVICE).eval()
    _clip_tokenizer = open_clip.get_tokenizer("ViT-B-32")

    _gallery = np.load(MODEL_DIR / "clip_gallery.npz", allow_pickle=True)
    _gallery_embeddings = torch.tensor(_gallery["embeddings"]).to(DEVICE)  # (N, 512), pre-normalized
    _gallery_labels = _gallery["labels"]
    _gallery_paths = _gallery["paths"]

    # Ensure sample images physically exist on disk in MODEL_DIR for static serving
    try:
        import shutil
        static_dir = MODEL_DIR.parent.parent.parent.parent / "frontend" / "public" / "assets" / "snakes-static"
        if static_dir.exists():
            src_map = {
                "Common Krait": "common krait-Photoroom.png",
                "Spectacled Cobra": "indian-cobra-Photoroom.png",
                "Monocled Cobra": "monocled_cobra.png",
                "King Cobra": "king_cobra.png",
                "Saw-scaled Viper": "saw_scaledviper-Photoroom.png",
                "Russell's Viper": "russells_viper.png",
                "Checkered Keelback": "keelback.png",
                "Common Rat Snake": "rat_snake.png",
                "Indian Rock Python": "rock_python.png",
                "Common Sand Boa": "sand_boa.png",
                "Common Trinket": "trinket.png",
                "Banded Racer": "banded_racer.png",
                "Green Tree Vine": "green_vine_snake.png",
            }
            default_src = "saw_scaledviper-Photoroom.png"
            for species in set(_gallery_labels):
                matches = [p for p, l in zip(_gallery_paths, _gallery_labels) if l == species]
                if matches:
                    target_file = MODEL_DIR / str(matches[0])
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    src_img = static_dir / src_map.get(str(species), default_src)
                    if src_img.exists():
                        shutil.copy(src_img, target_file)
    except Exception as img_err:
        print(f"[SNAKE ID WARNING] Could not populate sample images: {img_err}")

    _SNAKE_ID_AVAILABLE = True
except Exception as e:
    _SNAKE_ID_AVAILABLE = False
    _SNAKE_ID_ERROR = str(e)
    print(f"[SNAKE ID WARNING] Failed to load Snake ID models: {e}")


def _sample_image_for_species(species_name: str) -> str:
    """Returns one representative gallery image path for a species (for the
    frontend's result cards)."""
    matches = [p for p, l in zip(_gallery_paths, _gallery_labels) if l == species_name]
    return str(matches[0]) if matches else None


def classify_photo(image_bytes: bytes, top_k: int = TOP_K) -> list[dict]:
    """Primary input mode — user uploads a photo of the snake."""
    if not _SNAKE_ID_AVAILABLE:
        raise RuntimeError(f"Snake ID service unavailable: {_SNAKE_ID_ERROR}")
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = _photo_transform(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = _classifier(tensor)
        probs = F.softmax(logits, dim=1)[0]

    top_probs, top_idx = torch.topk(probs, k=min(top_k, len(CLASS_NAMES)))

    results = []
    for prob, idx in zip(top_probs.tolist(), top_idx.tolist()):
        species = str(CLASS_NAMES[idx])
        results.append({
            "species": species,
            "confidence": round(prob, 4),
            "sample_image": _sample_image_for_species(species),
            "source": "photo_classifier",
        })
    return results


def match_description(text: str, top_k: int = TOP_K) -> list[dict]:
    """Secondary input mode — user describes the snake in words (typed or
    transcribed from voice). Matches against the CLIP image gallery via
    cross-modal (text-to-image) cosine similarity, averaged per species."""
    if not _SNAKE_ID_AVAILABLE:
        raise RuntimeError(f"Snake ID service unavailable: {_SNAKE_ID_ERROR}")
    tokens = _clip_tokenizer([text]).to(DEVICE)

    with torch.no_grad():
        text_emb = _clip_model.encode_text(tokens)
        text_emb = text_emb / text_emb.norm(dim=-1, keepdim=True)

        similarities = (_gallery_embeddings @ text_emb.T).squeeze(1)  # (N,)

    # average similarity per species (more robust than single best-matching image)
    species_scores = {}
    for species, sim in zip(_gallery_labels, similarities.cpu().tolist()):
        species_scores.setdefault(species, []).append(sim)
    species_avg = {sp: sum(v) / len(v) for sp, v in species_scores.items()}

    ranked = sorted(species_avg.items(), key=lambda kv: -kv[1])[:top_k]

    # CLIP cosine similarities for text-vs-image are typically in a narrow
    # band (~0.15-0.30) rather than 0-1 like softmax — rescale for a more
    # intuitive "confidence" display without claiming false precision
    scores_only = [s for _, s in ranked]
    lo, hi = min(scores_only), max(scores_only + [scores_only[0] + 0.05])
    results = []
    for species, score in ranked:
        rescaled = (score - lo) / (hi - lo) if hi > lo else 1.0
        results.append({
            "species": str(species),
            "confidence": round(rescaled, 4),
            "raw_clip_similarity": round(score, 4),
            "sample_image": _sample_image_for_species(species),
            "source": "clip_description_match",
        })
    return results


if __name__ == "__main__":
    # quick manual smoke test
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "text":
        print(match_description(" ".join(sys.argv[2:]) or "green snake with yellow eyes"))
    else:
        print("Usage: python snake_id_inference.py text <description...>")
