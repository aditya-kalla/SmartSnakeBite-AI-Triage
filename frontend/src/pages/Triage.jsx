import React, { useState, useEffect, useContext, useRef } from "react";
import { transcribeAudio, runFullPipeline, createCase } from "../api.js";
import { AppContext } from "../App.jsx";
import { MicButton, ContextChips } from "../components/VoiceRecorder.jsx";
import PipelineArc from "../components/PipelineArc.jsx";
import ReportModal from "../components/ReportModal.jsx";
import SnakeIdSection from "../components/SnakeIdSection.jsx";

const STAGE_LABELS = {
  idle: "Ready",
  transcribe: "Listening…",
  am1: "Understanding your words…",
  am3: "Checking safety…",
  am2: "Assessing clinical risk…",
  done: "Report ready",
};

export default function Triage() {
  const {
    autoContext, overrides, setOverrides,
    setCurrent, setLog, effectiveLanguage,
    effectiveDistrict, effectiveTime, effectiveSeason,
  } = useContext(AppContext);

  const [stage, setStage] = useState("idle");
  const [error, setError] = useState(null);
  const [recording, setRecording] = useState(false);
  const [transcriptText, setTranscriptText] = useState("");
  const [resultEntry, setResultEntry] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalTab, setModalTab] = useState("report");

  // Initialize bite timestamp on first mount of triage page if not already set
  useEffect(() => {
    if (!overrides.bite_timestamp && !overrides.elapsed_hours) {
      setOverrides((prev) => ({
        ...prev,
        bite_timestamp: Date.now(),
        elapsed_hours: "0.00",
      }));
    }
  }, [overrides.bite_timestamp, overrides.elapsed_hours, setOverrides]);

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  async function startRecording() {
    setError(null);
    setTranscriptText("");
    setResultEntry(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        stream.getTracks().forEach((t) => t.stop());
        handleRecordingComplete(blob);
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setRecording(true);
    } catch (err) {
      setError("Could not access microphone. Please check permissions.");
    }
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  }

  async function handleRecordingComplete(blob) {
    setError(null);
    try {
      setStage("transcribe");
      const transcription = await transcribeAudio(blob, effectiveLanguage);
      const transcript = transcription.transcript || "";
      const detectedLang = transcription.language || effectiveLanguage;
      setTranscriptText(transcript);

      setStage("am1");
      await new Promise((r) => setTimeout(r, 300));
      setStage("am3");
      await new Promise((r) => setTimeout(r, 300));
      setStage("am2");

      let computedElapsed = undefined;
      if (overrides.elapsed_hours !== undefined && overrides.elapsed_hours !== "") {
        computedElapsed = Number(overrides.elapsed_hours);
      } else if (overrides.bite_timestamp) {
        computedElapsed = Number(((Date.now() - overrides.bite_timestamp) / 3600000).toFixed(2));
      }

      const result = await runFullPipeline({
        text: transcript,
        district: effectiveDistrict,
        time_of_day: effectiveTime,
        season: effectiveSeason,
        language: detectedLang,
        lat: autoContext.lat,
        lng: autoContext.lng,
        patient_age: overrides.patient_age !== undefined && overrides.patient_age !== "" ? Number(overrides.patient_age) : undefined,
        elapsed_hours: computedElapsed,
        tourniquet_applied: Boolean(overrides.tourniquet_applied),
        incision_attempted: Boolean(overrides.incision_attempted),
        traditional_healer_visited: Boolean(overrides.traditional_healer_visited),
        herbal_application: Boolean(overrides.herbal_application),
      });

      setStage("done");
      const caseId = Date.now();

      const entry = {
        id: caseId,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        transcript,
        am1: result.am1,
        am3: result.am3,
        am2: result.am2,
        language: detectedLang,
        venomType: result.am1?.venom_type,
        severity: (result.am2?.severity || result.am2?.severity_class || result.am1?.severity || "MODERATE").toUpperCase(),
        status: "open",
        editing: false,
      };

      try {
        await createCase(entry);
      } catch (err) {
        console.error("Failed to persist case to backend:", err);
      }

      setCurrent(entry);
      setLog((prev) => [entry, ...prev]);
      setResultEntry(entry);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
      setStage("idle");
    }
  }

  return (
    <div className="triage-page">
      {/* ═══ SECTION 1: The Workspace ═══ */}
      <section className="triage-workspace">
        {/* LEFT ZONE — Interaction */}
        <div className="triage-left">
          <div className="triage-left__header">
            <h1>Voice Diagnosis</h1>
            <p className="text-muted">
              Speak the patient's symptoms. Context is auto-detected.
            </p>
          </div>

          {/* Persistent First Aid & Bite Timer Trigger Button */}
          <div className="triage-firstaid-trigger">
            <button
              type="button"
              className={`btn-pill--firstaid ${
                Number(overrides.elapsed_hours || 0) >= 4
                  ? ""
                  : Number(overrides.elapsed_hours || 0) >= 1
                  ? "timer-warn"
                  : "timer-normal"
              }`}
              onClick={() => {
                setModalTab("firstAid");
                setModalOpen(true);
              }}
            >
              <span role="img" aria-label="emergency">🚨</span> First Aid &amp; Bite Timer{" "}
              {overrides.elapsed_hours && overrides.elapsed_hours !== "0.00"
                ? `(${Number(overrides.elapsed_hours).toFixed(1)}h elapsed)`
                : "(Active Timer)"}
            </button>
          </div>

          {/* Mic Area */}
          <MicButton
            recording={recording}
            onStart={startRecording}
            onStop={stopRecording}
            stageLabel={STAGE_LABELS[stage]}
          />

          {/* Transcript Display */}
          {transcriptText && (
            <div className="triage-transcript">
              <span className="triage-transcript__label">Transcription</span>
              <p className="triage-transcript__text">&ldquo;{transcriptText}&rdquo;</p>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="warning-box">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Context Chips */}
          <ContextChips
            autoContext={autoContext}
            overrides={overrides}
            setOverrides={setOverrides}
          />

          {/* Multilingual Demo Cases for TTS / Testing */}
          {stage === "idle" && (
            <div style={{ display: "flex", gap: "0.5rem", justifyContent: "center", marginTop: "1rem", flexWrap: "wrap" }}>
              <button
                type="button"
                className="btn-pill"
                style={{ fontSize: "0.75rem", padding: "0.35rem 0.85rem", background: "var(--paper-raised)", border: "1px dashed var(--clinical-teal)", color: "var(--clinical-teal)", cursor: "pointer" }}
                onClick={() => {
                  const dummy = {
                    id: Date.now(),
                    time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                    transcript: "పాము కాటేసింది, కాలు వాచింది, స్పృహ కోల్పోతున్నాడు",
                    language: "te",
                    venomType: "Hemotoxic",
                    severity: "HIGH",
                    status: "open",
                    am1: { venom_type: "viper", severity: "HIGH", confidence: 0.89 },
                    am2: { severity_class: "HIGH", antivenom_required: true, referral_priority: "Urgent Hospital Transfer" },
                    am3: { primary_corrective_message: "Do not tie tourniquet." },
                  };
                  setCurrent(dummy);
                  setLog((prev) => [dummy, ...prev]);
                  setResultEntry(dummy);
                  setStage("done");
                  setModalTab("report");
                  setModalOpen(true);
                }}
              >
                ⚡ Demo Case (Telugu)
              </button>
              <button
                type="button"
                className="btn-pill"
                style={{ fontSize: "0.75rem", padding: "0.35rem 0.85rem", background: "var(--paper-raised)", border: "1px dashed var(--clinical-teal)", color: "var(--clinical-teal)", cursor: "pointer" }}
                onClick={() => {
                  const dummy = {
                    id: Date.now() + 1,
                    time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                    transcript: "सांप ने काट लिया है, बहुत दर्द हो रहा है और सूजन आ गई है",
                    language: "hi",
                    venomType: "Neurotoxic",
                    severity: "CRITICAL",
                    status: "open",
                    am1: { venom_type: "cobra", severity: "CRITICAL", confidence: 0.94 },
                    am2: { severity_class: "CRITICAL", antivenom_required: true, referral_priority: "Immediate ICU & Antivenom" },
                    am3: { primary_corrective_message: "Keep limb immobilized." },
                  };
                  setCurrent(dummy);
                  setLog((prev) => [dummy, ...prev]);
                  setResultEntry(dummy);
                  setStage("done");
                  setModalTab("report");
                  setModalOpen(true);
                }}
              >
                ⚡ Demo Case (Hindi)
              </button>
            </div>
          )}

          {/* View Clinical Report Button — appears after done */}
          {stage === "done" && resultEntry && (
            <button
              className="triage-report-btn"
              onClick={() => {
                setModalTab("report");
                setModalOpen(true);
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
              View Clinical Report &amp; First Aid
            </button>
          )}

          {/* New Triage button — reset after viewing result */}
          {stage === "done" && (
            <button
              className="triage-reset-btn"
              onClick={() => {
                setStage("idle");
                setTranscriptText("");
                setResultEntry(null);
                setError(null);
              }}
            >
              Start New Diagnosis
            </button>
          )}
        </div>

        {/* RIGHT ZONE — Pipeline Visualization Panel */}
        <div className="triage-right">
          <PipelineArc stage={stage} entry={resultEntry} />
        </div>
      </section>

      {/* ═══ SCROLL CUE BETWEEN SECTIONS ═══ */}
      <div className="section-scroll-cue">
        <span className="section-scroll-cue__label">Scroll to identify a snake by photo or description</span>
        <div className="section-scroll-cue__icon" aria-hidden="true">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
      </div>

      {/* ═══ SECTION 2: Snake Photo ID & Description Matching ═══ */}
      <SnakeIdSection
        onSelectSpecies={(symptomText) => {
          setTranscriptText((prev) => prev ? `${prev} ${symptomText}` : symptomText);
          window.scrollTo({ top: 0, behavior: "smooth" });
        }}
      />

      {/* Report Modal */}
      <ReportModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        entry={resultEntry}
        initialTab={modalTab}
      />
    </div>
  );
}
