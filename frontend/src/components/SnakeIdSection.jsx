import React, { useState, useRef, useContext } from "react";
import { identifySnakeByPhoto, identifySnakeByDescription, transcribeAudio } from "../api.js";
import { AppContext } from "../App.jsx";

const CLINICAL_PROFILES = {
  indian_cobra: {
    name: "Spectacled / Monocled Cobra",
    venom: "Neurotoxic & Necrotoxic",
    symptoms: [
      "Drooping eyelids (Ptosis) — earliest sign of neurotoxicity",
      "Difficulty speaking, swallowing, or opening mouth",
      "Progressive muscle weakness and respiratory paralysis",
      "Severe pain, blistering, and tissue necrosis around the bite site"
    ],
    action: "Immediate polyvalent antivenom administration required. Ventilatory support may be needed if breathing is compromised.",
    defaultText: "Patient bitten by a Cobra. Shows drooping eyelids, difficulty speaking, and local swelling around bite mark."
  },
  saw_scaled_viper: {
    name: "Saw-scaled Viper",
    venom: "Hemotoxic & Coagulopathic",
    symptoms: [
      "Incoagulable blood — continuous bleeding from bite wound",
      "Spontaneous bleeding from gums, nose, or old scars",
      "Severe localized swelling, blistering, and intense pain",
      "Signs of acute kidney injury or fall in urine output"
    ],
    action: "Rapid antivenom required. Do not give aspirin or NSAIDs. Monitor whole blood clotting test (20WBCT) closely.",
    defaultText: "Bite by Saw-scaled Viper. Severe localized pain, swelling, and bleeding from the bite site."
  },
  russells_viper: {
    name: "Russell's Viper",
    venom: "Hemotoxic, Myotoxic & Nephrotoxic",
    symptoms: [
      "Rapidly spreading swelling and blistering from bite site",
      "Systemic bleeding (gums, hematuria/blood in urine, vomiting blood)",
      "Severe lower back pain indicating acute renal damage",
      "Dropping blood pressure and signs of shock"
    ],
    action: "Urgent hospital ICU admission. Requires polyvalent antivenom and continuous renal function monitoring.",
    defaultText: "Bitten by Russell's Viper. Rapid swelling, bleeding from wound, and abdominal pain."
  },
  common_krait: {
    name: "Common Krait",
    venom: "Potently Neurotoxic",
    symptoms: [
      "Often painless bite with minimal or invisible local bite marks",
      "Severe abdominal cramps occurring within hours of bite in sleep",
      "Drooping eyelids (Ptosis), facial paralysis, and blurred vision",
      "Rapid onset of respiratory arrest and complete paralysis"
    ],
    action: "CRITICAL MEDICAL EMERGENCY. Treat immediately with antivenom even if the bite wound looks minor. Prepare for mechanical ventilation.",
    defaultText: "Suspected Krait bite while sleeping. Patient experiencing abdominal cramps, drooping eyelids, and difficulty breathing."
  }
};

export default function SnakeIdSection({ onSelectSpecies }) {
  const { effectiveLanguage } = useContext(AppContext);
  const [mode, setMode] = useState("photo"); // "photo" | "describe"

  // Photo mode state
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  // Describe mode state
  const [describeText, setDescribeText] = useState("");
  const [recording, setRecording] = useState(false);
  const [recordError, setRecordError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  // Results state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [resultsData, setResultsData] = useState(null);

  // Modal state
  const [activeProfile, setActiveProfile] = useState(null);

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
    }
  }

  async function handlePhotoSubmit(e) {
    e.preventDefault();
    if (!selectedFile) {
      setError("Please select an image first.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await identifySnakeByPhoto(selectedFile);
      setResultsData(data);
    } catch (err) {
      setError(err.message || "Failed to analyze photo.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDescribeSubmit(e) {
    e.preventDefault();
    if (!describeText.trim()) {
      setError("Please enter a description first.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await identifySnakeByDescription(describeText);
      setResultsData(data);
    } catch (err) {
      setError(err.message || "Failed to analyze description.");
    } finally {
      setLoading(false);
    }
  }

  async function startRecording() {
    setRecordError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        stream.getTracks().forEach((t) => t.stop());
        try {
          setLoading(true);
          const transcription = await transcribeAudio(blob, effectiveLanguage);
          if (transcription.transcript) {
            setDescribeText((prev) => (prev ? `${prev} ${transcription.transcript}` : transcription.transcript));
          }
        } catch (err) {
          setRecordError("Voice transcription failed. Try typing instead.");
        } finally {
          setLoading(false);
        }
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setRecording(true);
    } catch (err) {
      setRecordError("Could not access microphone. Please check permissions.");
    }
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  }

  return (
    <section className="snake-id-container">
      <div className="snake-id-header">
        <h2>AI Snake Species &amp; Risk Identification</h2>
        <p className="text-muted">
          Upload a photo or describe appearance to identify the species using our fine-tuned vision &amp; cross-modal CLIP engines.
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="snake-id-toggles">
        <button
          type="button"
          className={`snake-id-toggle-btn ${mode === "photo" ? "active" : ""}`}
          onClick={() => { setMode("photo"); setError(null); }}
        >
          <span role="img" aria-label="camera">📷</span> Upload Photo Mode
        </button>
        <button
          type="button"
          className={`snake-id-toggle-btn ${mode === "describe" ? "active" : ""}`}
          onClick={() => { setMode("describe"); setError(null); }}
        >
          <span role="img" aria-label="speech">💬</span> Describe Snake Mode
        </button>
      </div>

      {/* Input Area */}
      <div className="snake-id-input-box">
        {mode === "photo" ? (
          <form onSubmit={handlePhotoSubmit} className="snake-id-form">
            <div
              className="snake-id-dropzone"
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => document.getElementById("snake-photo-input").click()}
            >
              {previewUrl ? (
                <div className="snake-id-preview-wrapper">
                  <img src={previewUrl} alt="Snake preview" className="snake-id-preview-img" />
                  <span className="snake-id-preview-hint">Click or drag to change image</span>
                </div>
              ) : (
                <div className="snake-id-dropzone-content">
                  <span className="drop-icon">📸</span>
                  <h4>Drag &amp; drop snake photo here</h4>
                  <p className="text-muted">or click to browse from device</p>
                </div>
              )}
              <input
                id="snake-photo-input"
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={handleFileChange}
              />
            </div>
            <button
              type="submit"
              disabled={loading || !selectedFile}
              className="btn-primary snake-id-submit-btn"
            >
              {loading ? "Analyzing Photo..." : "Identify Species by Photo"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleDescribeSubmit} className="snake-id-form">
            <div className="snake-id-describe-wrapper">
              <textarea
                className="snake-id-textarea"
                rows="4"
                placeholder="Describe color, pattern, head shape, scales, sound (hissing/rubbing scales), or habitat (e.g. 'thin green snake with yellow belly found in bush' or 'large brown snake with diamond chains on back producing loud hissing sound')..."
                value={describeText}
                onChange={(e) => setDescribeText(e.target.value)}
              />
              <div className="snake-id-voice-controls">
                <button
                  type="button"
                  className={`btn-pill ${recording ? "recording-pulse" : ""}`}
                  style={{ background: recording ? "var(--clinical-coral)" : "var(--paper-raised)", color: recording ? "#fff" : "var(--text-main)" }}
                  onClick={recording ? stopRecording : startRecording}
                >
                  {recording ? "⏹️ Stop Recording" : "🎤 Use Voice to Describe"}
                </button>
                {recordError && <span className="text-coral" style={{ fontSize: "0.85rem" }}>{recordError}</span>}
              </div>
            </div>
            <button
              type="submit"
              disabled={loading || !describeText.trim()}
              className="btn-primary snake-id-submit-btn"
            >
              {loading ? "Matching Description..." : "Match Species by Description"}
            </button>
          </form>
        )}

        {error && (
          <div className="warning-box" style={{ marginTop: "1rem" }}>
            <strong>Notice:</strong> {error}
          </div>
        )}
      </div>

      {/* Results Area */}
      {resultsData && (
        <div className="snake-id-results">
          {resultsData.show_venom_caution && (
            <div className="snake-id-caution-banner">
              <div className="caution-icon">⚠️</div>
              <div className="caution-text">
                <strong>VENOMOUS SPECIES DETECTED IN TOP MATCHES</strong>
                <p>
                  Treat immediately as a potential medical emergency. Do not wait for severe symptoms to appear before seeking hospital care or emergency transport.
                </p>
              </div>
            </div>
          )}

          <h3 className="results-title">Top Identified Species Matches</h3>
          <div className="snake-id-cards-grid">
            {resultsData.results.map((card, idx) => (
              <div key={idx} className={`snake-id-card ${card.venomous ? "card-venomous" : "card-safe"}`}>
                <div className="card-img-wrapper">
                  <img
                    src={card.sample_image}
                    alt={card.species}
                    className="card-img"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = "/assets/snakes-static/saw_scaledviper-Photoroom.png";
                    }}
                  />
                  <span className={`card-badge ${card.venomous ? "badge-red" : "badge-green"}`}>
                    {card.venomous ? "🚨 Venomous" : "🛡️ Non-Venomous"}
                  </span>
                </div>
                <div className="card-body">
                  <div className="card-header-row">
                    <h4>{card.species}</h4>
                    <span className="card-confidence">{(card.confidence * 100).toFixed(1)}% Match</span>
                  </div>
                  <div className="confidence-bar-bg">
                    <div
                      className="confidence-bar-fill"
                      style={{
                        width: `${Math.min(100, Math.max(5, card.confidence * 100))}%`,
                        background: card.venomous ? "var(--clinical-coral)" : "var(--clinical-teal)"
                      }}
                    />
                  </div>
                  <p className="card-note">{card.note}</p>

                  {card.clinical_key && CLINICAL_PROFILES[card.clinical_key] ? (
                    <button
                      type="button"
                      className="btn-clinical-hint"
                      onClick={() => setActiveProfile(CLINICAL_PROFILES[card.clinical_key])}
                    >
                      View clinical severity profile &amp; first aid ➔
                    </button>
                  ) : (
                    <div className="card-hint-text text-muted">
                      Identification only — no direct A-M2 clinical severity mapping.
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Clinical Profile Info Modal */}
      {activeProfile && (
        <div className="snake-modal-backdrop" onClick={() => setActiveProfile(null)}>
          <div className="snake-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="snake-modal-header">
              <div>
                <span className="badge-red" style={{ fontSize: "0.75rem", padding: "0.2rem 0.6rem", borderRadius: "12px" }}>
                  🚨 Big Four Medically Significant
                </span>
                <h3 style={{ marginTop: "0.5rem", marginBottom: "0.2rem" }}>{activeProfile.name}</h3>
                <p className="text-muted" style={{ margin: 0 }}>Venom Type: <strong>{activeProfile.venom}</strong></p>
              </div>
              <button className="snake-modal-close" onClick={() => setActiveProfile(null)}>✕</button>
            </div>

            <div className="snake-modal-body">
              <h4>Key Symptoms to Watch For:</h4>
              <ul className="snake-modal-symptoms">
                {activeProfile.symptoms.map((sym, i) => (
                  <li key={i}>{sym}</li>
                ))}
              </ul>

              <div className="warning-box" style={{ marginTop: "1rem", marginBottom: "1.5rem" }}>
                <strong>Clinical Protocol:</strong> {activeProfile.action}
              </div>

              <div className="snake-modal-actions">
                <button
                  type="button"
                  className="btn-primary"
                  style={{ width: "100%", padding: "0.75rem" }}
                  onClick={() => {
                    if (onSelectSpecies) {
                      onSelectSpecies(activeProfile.defaultText);
                    }
                    setActiveProfile(null);
                  }}
                >
                  ⚡ Use this Species in Symptom Checker (Section 1)
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
