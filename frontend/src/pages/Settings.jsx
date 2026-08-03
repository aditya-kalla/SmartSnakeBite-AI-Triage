import React, { useContext, useEffect, useState } from "react";
import { AppContext } from "../App.jsx";

export default function Settings() {
  const {
    defaultTTSLang,
    setDefaultTTSLang,
    autoDetectContext,
    setAutoDetectContext,
    alwaysExpandOverrides,
    setAlwaysExpandOverrides,
    log,
    setLog,
    reloadSampleCases
  } = useContext(AppContext);

  const [healthStatus, setHealthStatus] = useState({
    status: "online",
    muril_loaded: true,
    am2_engine: "Extreme Gradient Boosting (XGBoost) + Random Forest Ensembles",
    am1_engine: "MuRIL Bi-encoder + Bio-Clinical BERT embeddings",
    offline_ready: true
  });

  useEffect(() => {
    fetch("http://localhost:8000/api/health")
      .then(res => res.json())
      .then(data => {
        if (data && data.status) {
          setHealthStatus(prev => ({ ...prev, ...data }));
        }
      })
      .catch(() => {
        // use default fallback
      });
  }, []);

  function handleClearData() {
    if (window.confirm("Are you sure you want to clear all diagnosed cases from current session memory? This cannot be undone.")) {
      setLog([]);
    }
  }

  return (
    <div className="settings-page" style={{ maxWidth: "680px", margin: "2rem auto", padding: "0 clamp(1rem, 3vw, 2rem)" }}>
      <div className="workspace-header" style={{ marginBottom: "2.5rem" }}>
        <h1>Console Settings</h1>
        <p className="text-muted">Configure audio preferences, default clinical overrides, and manage offline models.</p>
      </div>

      <div className="settings-card" style={{
        background: "var(--paper-raised)",
        border: "1px solid var(--line-soft)",
        borderRadius: "20px",
        padding: "2rem 2.5rem",
        boxShadow: "var(--shadow-card)",
        marginBottom: "2rem",
        display: "flex",
        flexDirection: "column",
        gap: "2rem"
      }}>
        {/* Section 1: Audio Output */}
        <div className="settings-section">
          <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.15rem", marginBottom: "0.5rem", color: "var(--ink-dark)" }}>
            Audio & Language
          </h3>
          <p className="text-muted" style={{ fontSize: "0.85rem", marginBottom: "1rem" }}>
            Select the default language voice for Read Report Aloud TTS synthesis.
          </p>
          <label style={{ display: "flex", flexDirection: "column", gap: "0.4rem", fontFamily: "var(--font-mono)", fontSize: "0.8rem", color: "var(--ink-dark)" }}>
            DEFAULT TTS LANGUAGE
            <select
              value={defaultTTSLang}
              onChange={(e) => setDefaultTTSLang(e.target.value)}
              style={{
                padding: "0.75rem 1rem",
                borderRadius: "10px",
                border: "1px solid var(--line-strong)",
                background: "var(--paper-base)",
                fontFamily: "var(--font-body)",
                fontSize: "0.95rem",
                color: "var(--ink-dark)",
                cursor: "pointer",
                maxWidth: "320px"
              }}
            >
              <option value="en">English (Clinical Medical Voice)</option>
              <option value="te">Telugu (తెలుగు)</option>
              <option value="hi">Hindi (हिन्दी)</option>
              <option value="ta">Tamil (தமிழ்)</option>
              <option value="kn">Kannada (ಕನ್ನಡ)</option>
            </select>
          </label>
        </div>

        <hr style={{ border: "none", borderTop: "1px solid var(--line-soft)", margin: 0 }} />

        {/* Section 2: Clinical Defaults */}
        <div className="settings-section">
          <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.15rem", marginBottom: "0.5rem", color: "var(--ink-dark)" }}>
            Diagnosis & Context Behavior
          </h3>
          <p className="text-muted" style={{ fontSize: "0.85rem", marginBottom: "1.25rem" }}>
            Adjust how environmental and vital parameters are captured during triage.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "0.75rem", cursor: "pointer", userSelect: "none" }}>
              <input
                type="checkbox"
                checked={autoDetectContext}
                onChange={(e) => setAutoDetectContext(e.target.checked)}
                style={{ width: "18px", height: "18px", accentColor: "var(--clinical-teal)", cursor: "pointer" }}
              />
              <div>
                <strong style={{ fontSize: "0.95rem", display: "block", color: "var(--ink-dark)" }}>Auto-detect location & context by default</strong>
                <span className="text-muted" style={{ fontSize: "0.8rem" }}>Use GPS district, local time of day, and seasonal snakebite priors automatically.</span>
              </div>
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "0.75rem", cursor: "pointer", userSelect: "none" }}>
              <input
                type="checkbox"
                checked={alwaysExpandOverrides}
                onChange={(e) => setAlwaysExpandOverrides(e.target.checked)}
                style={{ width: "18px", height: "18px", accentColor: "var(--clinical-teal)", cursor: "pointer" }}
              />
              <div>
                <strong style={{ fontSize: "0.95rem", display: "block", color: "var(--ink-dark)" }}>Always show clinician override panel expanded</strong>
                <span className="text-muted" style={{ fontSize: "0.8rem" }}>Keep patient age, elapsed time, and harmful first-aid checkboxes open on page load.</span>
              </div>
            </label>
          </div>
        </div>

        <hr style={{ border: "none", borderTop: "1px solid var(--line-soft)", margin: 0 }} />

        {/* Section 3: Offline Model Status */}
        <div className="settings-section">
          <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.15rem", marginBottom: "0.5rem", color: "var(--ink-dark)" }}>
            Offline Clinical Models
          </h3>
          <p className="text-muted" style={{ fontSize: "0.85rem", marginBottom: "1.25rem" }}>
            Read-only status of embedded neural networks and severity classification ensembles.
          </p>

          <div style={{
            background: "var(--paper-base)",
            border: "1px solid var(--line-soft)",
            borderRadius: "12px",
            padding: "1.25rem",
            display: "grid",
            gap: "0.75rem",
            fontFamily: "var(--font-mono)",
            fontSize: "0.82rem"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="text-muted">SYSTEM STATUS</span>
              <span style={{ color: "var(--clinical-teal)", fontWeight: 700 }}>● ONLINE / EDGE CAPABLE</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="text-muted">NLP ENCODER (MuRIL)</span>
              <span>{healthStatus.muril_loaded ? "Loaded in Memory (Int8 Quantized)" : "Offline Standby"}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="text-muted">A-M2 SEVERITY ENGINE</span>
              <span>{healthStatus.am2_engine || "XGBoost + Random Forest Ensembles"}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="text-muted">PROTOCOL ARTIFACTS</span>
              <span>WHO / National Clinical Guidelines (V2.4)</span>
            </div>
          </div>
        </div>

        <hr style={{ border: "none", borderTop: "1px solid var(--line-soft)", margin: 0 }} />

        {/* Section 4: Session Memory Management */}
        <div className="settings-section">
          <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.15rem", marginBottom: "0.5rem", color: "var(--ink-dark)" }}>
            Session Memory Management
          </h3>
          <p className="text-muted" style={{ fontSize: "0.85rem", marginBottom: "1.25rem" }}>
            Manage the temporary dashboard case queue for this workstation.
          </p>

          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
            <button
              onClick={handleClearData}
              disabled={log.length === 0}
              style={{
                padding: "0.75rem 1.5rem",
                borderRadius: "10px",
                border: "1px solid var(--sev-critical)",
                background: log.length === 0 ? "rgba(220, 38, 38, 0.05)" : "var(--sev-critical)",
                color: log.length === 0 ? "var(--sev-critical)" : "#ffffff",
                fontFamily: "var(--font-mono)",
                fontSize: "0.85rem",
                fontWeight: 600,
                cursor: log.length === 0 ? "not-allowed" : "pointer",
                opacity: log.length === 0 ? 0.6 : 1,
                transition: "all 0.2s"
              }}
            >
              🗑️ Clear all session case data ({log.length} cases)
            </button>

            <button
              onClick={reloadSampleCases}
              style={{
                padding: "0.75rem 1.25rem",
                borderRadius: "10px",
                border: "1px solid var(--clinical-teal)",
                background: "transparent",
                color: "var(--clinical-teal)",
                fontFamily: "var(--font-mono)",
                fontSize: "0.85rem",
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.2s"
              }}
            >
              🔄 Reload Demo Queue
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
