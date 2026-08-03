import torch
import torch.nn as nn
import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModel
from langdetect import detect

MODEL_DIR = Path(__file__).parent / "model"
MAX_LEN = 128
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

with open(MODEL_DIR / "label_maps.json") as f:
    label_maps = json.load(f)

VENOM_LABELS = label_maps["venom"]
SEVERITY_LABELS = label_maps["severity"]


class MuRILClassifier(nn.Module):
    def __init__(self, n_venom, n_severity):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(MODEL_DIR)
        hidden = self.encoder.config.hidden_size
        self.drop = nn.Dropout(0.3)
        self.venom_head = nn.Linear(hidden, n_venom)
        self.severity_head = nn.Linear(hidden, n_severity)

    def forward(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled = out.last_hidden_state[:, 0, :]
        pooled = self.drop(pooled)
        return self.venom_head(pooled), self.severity_head(pooled)


tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = MuRILClassifier(len(VENOM_LABELS), len(SEVERITY_LABELS)).to(DEVICE)
model.load_state_dict(torch.load(MODEL_DIR / "classifier_heads.pt", map_location=DEVICE))
model.eval()


def predict(text: str) -> dict:
    if not text or not text.strip():
        return {"venom_type": "Unknown", "severity": "LOW",
                "confidence": 0.0, "language_detected": "unknown"}

    try:
        lang = detect(text)
    except Exception:
        lang = "unknown"

    enc = tokenizer(
        text, max_length=MAX_LEN,
        padding="max_length", truncation=True, return_tensors="pt"
    )
    input_ids = enc["input_ids"].to(DEVICE)
    attention_mask = enc["attention_mask"].to(DEVICE)

    with torch.no_grad():
        venom_logits, severity_logits = model(input_ids, attention_mask)

    venom_probs = torch.softmax(venom_logits, dim=1).cpu().numpy()[0]
    severity_probs = torch.softmax(severity_logits, dim=1).cpu().numpy()[0]

    venom_idx = venom_probs.argmax()
    severity_idx = severity_probs.argmax()

    return {
        "venom_type": VENOM_LABELS[venom_idx],
        "severity": SEVERITY_LABELS[severity_idx],
        "confidence": round(float(venom_probs[venom_idx]), 4),
        "severity_confidence": round(float(severity_probs[severity_idx]), 4),
        "language_detected": lang,
        "all_venom_probs": {VENOM_LABELS[i]: round(float(p), 4) for i, p in enumerate(venom_probs)}
    }