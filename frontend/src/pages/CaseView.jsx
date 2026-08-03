import React, { useContext, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { AppContext } from "../App.jsx";
import { speakText } from "../api.js";

function sevClass(sev) {
  const s = (sev || "").toUpperCase();
  if (["CRITICAL", "HIGH", "MODERATE", "LOW"].includes(s)) return s.toLowerCase();
  if (s === "MEDIUM") return "moderate";
  return "moderate";
}

function getSevPercentage(sev) {
  const s = sevClass(sev);
  if (s === "critical") return "95%";
  if (s === "high") return "75%";
  if (s === "moderate") return "45%";
  if (s === "low") return "15%";
  return "0%";
}

function formatExplanation(explanation) {
  if (!explanation) return "";
  if (Array.isArray(explanation)) {
    return explanation.join("\n").replace(/\\n/g, "\n");
  }
  return String(explanation);
}

export default function CaseView() {
  const { id } = useParams();
  const { log } = useContext(AppContext);
  const [speaking, setSpeaking] = useState(false);
  
  const caseId = parseInt(id, 10);
  const entry = log.find(e => e.id === caseId);

  if (!entry) {
    return (
      <div className="empty-state" style={{ marginTop: '4rem' }}>
        <h2>Case Not Found</h2>
        <p>The case ID {id} does not exist or has been removed from session memory.</p>
        <Link to="/diagnose" className="btn btn-outline" style={{ marginTop: '1rem' }}>Return to Diagnosis</Link>
      </div>
    );
  }

  const { am1, am2, am3, transcript, language } = entry;
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

  const sClass = sevClass(am2Severity);

  return (
    <div className="case-view">
      <div className="case-header">
        <div>
          <h1>Clinical Report</h1>
          <span className="case-id">CASE #{caseId} · {entry.time} · {language?.toUpperCase()}</span>
        </div>
        <button className="btn btn-outline" onClick={handlePlay} disabled={speaking}>
          {speaking ? "🔊 Playing…" : "🔊 Speak Report"}
        </button>
      </div>

      <div className="transcript-preview" style={{ marginBottom: '2rem' }}>
        &ldquo;{transcript}&rdquo;
      </div>

      {am3?.critical_alert && (
        <div className="warning-box">
          <strong>CRITICAL SAFETY ALERT:</strong> {am3.primary_corrective_message || "Harmful first-aid practice detected."}
        </div>
      )}

      {/* Vitals Strip */}
      <div className={`vitals-strip-container bg-${sClass}-soft border-${sClass}`}>
        <div className="vitals-header">
          <span>Overall Severity</span>
          <span className={`color-${sClass}`}>{am2Severity?.toUpperCase() || "UNKNOWN"} RISK</span>
        </div>
        <div className="vitals-gauge">
          <div className="vitals-ticks"></div>
          <div className={`gauge-segment sev-${sClass}`} style={{ width: getSevPercentage(am2Severity) }}></div>
        </div>
        <div className="vitals-labels">
          <span>Low</span>
          <span>Moderate</span>
          <span>High</span>
          <span>Critical</span>
        </div>
      </div>

      <div className="clinical-grid">
        <div className="clinical-card">
          <h3>Diagnosis Decision</h3>
          <div className="species-list">
            <div className="species-row">
              <span className="text-muted">Mortality Risk</span>
              <span className="color-critical">{am2?.mortality_risk || "—"}</span>
            </div>
            <div className="species-row">
              <span className="text-muted">Antivenom Required</span>
              <span>{am2?.antivenom_required ? "Yes" : "No"}</span>
            </div>
            <div className="species-row">
              <span className="text-muted">Priority</span>
              <span>{am2?.referral_priority || "—"}</span>
            </div>
            <div className="species-row">
              <span className="text-muted">Est. Delay</span>
              <span>{am3?.am2_total_delay_hours ?? am3?.delay_analysis?.total_estimated_delay_hours ?? 0} hours</span>
            </div>
          </div>
        </div>

        <div className="clinical-card">
          <h3>Probable Species</h3>
          <div className="species-list">
            {Array.isArray(topSpecies) && topSpecies.length > 0 ? (
              topSpecies.map((sp, idx) => (
                <div key={idx} className="species-row">
                  <span>{sp}</span>
                  <span className="text-muted text-mono">#{idx + 1}</span>
                </div>
              ))
            ) : (
              <span className="text-muted">No specific species identified</span>
            )}
            
            <div className="species-row" style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--line-soft)' }}>
              <span className="text-muted">Symptom Class</span>
              <span>{am1?.venom_type || "—"}</span>
            </div>
          </div>
        </div>
      </div>

      {explanationText && (
        <div className="collapsible-summary">
          <details open>
            <summary>Clinical Reasoning Log</summary>
            <pre style={{ marginTop: '1rem', whiteSpace: 'pre-wrap', fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
              {explanationText}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}
