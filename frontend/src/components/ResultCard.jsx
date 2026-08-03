import { useState } from "react";
import { speakText } from "../api.js";

function sevClass(sev) {
  const s = (sev || "").toUpperCase();
  if (["CRITICAL", "HIGH", "MODERATE", "LOW"].includes(s)) return s;
  if (s === "MEDIUM") return "MODERATE";
  return "MODERATE";
}

function formatExplanation(explanation) {
  if (!explanation) return "";
  if (Array.isArray(explanation)) {
    return explanation.join("\n").replace(/\\n/g, "\n");
  }
  return String(explanation);
}

export default function ResultCard({ transcript, am1, am3, am2, language }) {
  const [showReasoning, setShowReasoning] = useState(false);
  const [speaking, setSpeaking] = useState(false);

  if (!am1 && !am2 && !am3) return null;

  const am2Severity = am2?.severity || am2?.severity_class || am1?.severity;
  const topSpecies = am2?.top_species || am2?.probable_species || [];
  const explanationRaw = am2?.clinical_explanation || am2?.explanation;
  const explanationText = formatExplanation(explanationRaw);

  const spokenSummary =
    am3?.primary_corrective_message ||
    `Severity ${am2Severity || "unknown"}. ${am2?.antivenom_required ? "Antivenom required." : ""} ${am2?.referral_priority || ""}`.trim();

  async function handlePlay() {
    setSpeaking(true);
    try {
      const audioBlob = await speakText(spokenSummary, language === "auto" ? "en" : language);
      const url = URL.createObjectURL(audioBlob);
      const audio = new Audio(url);
      audio.onended = () => setSpeaking(false);
      await audio.play();
    } catch (err) {
      console.error(err);
      setSpeaking(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {transcript && (
        <div className="transcript-preview">&ldquo;{transcript}&rdquo;</div>
      )}

      {am3?.critical_alert && (
        <div className="warning-banner">
          ⚠ <span>{am3.primary_corrective_message || "Harmful first-aid practice detected."}</span>
        </div>
      )}

      <div className="result-grid">
        <div className={`result-card sev-${sevClass(am1?.severity)}`}>
          <span className="eyebrow">A-M1 · Symptom Classification</span>
          <span className="headline">{am1?.venom_type || "—"}</span>
          <div className="detail-row">
            <span className="k">Urgency</span>
            <span className="v">{am1?.severity || "—"}</span>
          </div>
          <div className="detail-row">
            <span className="k">Confidence</span>
            <span className="v">{am1?.confidence ? `${Math.round(am1.confidence * 100)}%` : "—"}</span>
          </div>
        </div>

        <div className={`result-card sev-${sevClass(am2Severity)}`}>
          <span className="eyebrow">A-M2 · Clinical Decision</span>
          <span className="headline">{am2Severity || "—"}</span>
          <div className="detail-row">
            <span className="k">Mortality risk</span>
            <span className="v">{am2?.mortality_risk || "—"}</span>
          </div>
          <div className="detail-row">
            <span className="k">Antivenom</span>
            <span className="v">{am2?.antivenom_required ? "Required" : "—"}</span>
          </div>
          {topSpecies.length > 0 && (
            <div className="detail-row">
              <span className="k">Top species</span>
              <span className="v">
                {Array.isArray(topSpecies) ? topSpecies.slice(0, 2).join(", ") : String(topSpecies)}
              </span>
            </div>
          )}
        </div>

        <div className={`result-card sev-${am3?.harmful_practices?.count > 0 ? "HIGH" : "LOW"}`}>
          <span className="eyebrow">A-M3 · Safety Check</span>
          <span className="headline">
            {am3?.harmful_practices?.count > 0 ? "Practices flagged" : "No harmful practices"}
          </span>
          <div className="detail-row">
            <span className="k">Delay estimate</span>
            <span className="v">{am3?.am2_total_delay_hours ?? am3?.delay_analysis?.total_estimated_delay_hours ?? 0}h</span>
          </div>
          <div className="detail-row">
            <span className="k">Delay risk</span>
            <span className="v">{am3?.delay_analysis?.delay_risk || "—"}</span>
          </div>
        </div>
      </div>

      <div className="reasoning-toggle-row">
        <button className="override-toggle" onClick={() => setShowReasoning((v) => !v)}>
          {showReasoning ? "Hide clinical reasoning" : "View clinical reasoning"}
        </button>
        <button className="speak-btn" onClick={handlePlay} disabled={speaking}>
          {speaking ? "🔊 Playing…" : "🔊 Read result aloud"}
        </button>
      </div>

      {showReasoning && explanationText && (
        <div className="reasoning-panel">
          <pre>{explanationText}</pre>
        </div>
      )}
    </div>
  );
}

export { sevClass };
