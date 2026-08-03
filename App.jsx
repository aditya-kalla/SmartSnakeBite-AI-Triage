import { useState } from "react";
import PipelineRail from "./components/PipelineRail.jsx";
import VoiceRecorder from "./components/VoiceRecorder.jsx";
import ResultCard from "./components/ResultCard.jsx";
import DashboardLog from "./components/DashboardLog.jsx";
import useAutoContext from "./useAutoContext.js";
import { transcribeAudio, runFullPipeline } from "./api.js";

const STAGE_LABELS = {
  idle: "Ready",
  transcribe: "Transcribing…",
  am1: "Classifying symptoms…",
  am3: "Checking for harmful practices…",
  am2: "Running clinical reasoning…",
  done: "Complete",
};

export default function App() {
  const [tab, setTab] = useState("triage"); // "triage" | "dashboard"
  const [stage, setStage] = useState("idle");
  const autoContext = useAutoContext();
  const [overrides, setOverrides] = useState({});
  const [current, setCurrent] = useState(null);
  const [log, setLog] = useState([]);
  const [error, setError] = useState(null);

  const effectiveLanguage = overrides.language || "auto";
  const effectiveDistrict = overrides.district || "Unknown";
  const effectiveTime = overrides.time_of_day || autoContext.time_of_day;
  const effectiveSeason = overrides.season || autoContext.season;

  async function handleRecordingComplete(blob) {
    setError(null);
    setCurrent(null);
    try {
      setStage("transcribe");
      const transcription = await transcribeAudio(blob, effectiveLanguage);
      const transcript = transcription.transcript || "";
      const detectedLang = transcription.language || effectiveLanguage;

      setStage("am1");
      await new Promise((r) => setTimeout(r, 300));
      setStage("am3");
      await new Promise((r) => setTimeout(r, 300));
      setStage("am2");

      const result = await runFullPipeline({
        text: transcript,
        district: effectiveDistrict,
        time_of_day: effectiveTime,
        season: effectiveSeason,
        language: detectedLang,
        lat: autoContext.lat,
        lng: autoContext.lng,
      });

      setStage("done");
      const entry = { transcript, am1: result.am1, am3: result.am3, am2: result.am2, language: detectedLang };
      setCurrent(entry);

      setLog((prev) => [
        {
          id: Date.now(),
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          transcript,
          venomType: result.am1?.venom_type,
          severity: result.am2?.severity || result.am2?.severity_class || result.am1?.severity,
          status: "open",
          editing: false,
        },
        ...prev,
      ]);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
      setStage("idle");
    }
  }

  function handleClose(id) {
    setLog((prev) =>
      prev.map((e) => (e.id === id ? { ...e, status: e.status === "closed" ? "open" : "closed" } : e))
    );
  }

  function handleEdit(id, newTranscript, toggleEditMode) {
    setLog((prev) =>
      prev.map((e) => {
        if (e.id !== id) return e;
        if (toggleEditMode) return { ...e, editing: true };
        return { ...e, transcript: newTranscript ?? e.transcript, editing: false };
      })
    );
  }

  const openCount = log.filter((e) => e.status !== "closed").length;
  const closedCount = log.length - openCount;

  return (
    <div className="app-shell">
      <PipelineRail currentStage={stage} />

      <main className="main">
        <nav className="tab-nav">
          <button className={tab === "triage" ? "active" : ""} onClick={() => setTab("triage")}>
            Voice Triage
          </button>
          <button className={tab === "dashboard" ? "active" : ""} onClick={() => setTab("dashboard")}>
            Dashboard
          </button>
        </nav>

        {tab === "triage" && (
          <>
            <div className="page-header">
              <h1>Voice Triage</h1>
              <p>Speak the patient's symptoms in any of five languages — context is detected automatically.</p>
            </div>

            <VoiceRecorder
              autoContext={autoContext}
              overrides={overrides}
              setOverrides={setOverrides}
              onRecordingComplete={handleRecordingComplete}
              stageLabel={STAGE_LABELS[stage]}
            />

            {error && <div className="warning-banner">⚠ <span>{error}</span></div>}

            <ResultCard
              transcript={current?.transcript}
              am1={current?.am1}
              am3={current?.am3}
              am2={current?.am2}
              language={current?.language}
            />
          </>
        )}

        {tab === "dashboard" && (
          <>
            <div className="page-header">
              <h1>Dashboard</h1>
              <p>All recorded cases this session.</p>
            </div>

            <div className="stat-row">
              <div className="stat-card">
                <span className="stat-num">{log.length}</span>
                <span className="stat-label">Total cases</span>
              </div>
              <div className="stat-card">
                <span className="stat-num">{openCount}</span>
                <span className="stat-label">Open</span>
              </div>
              <div className="stat-card">
                <span className="stat-num">{closedCount}</span>
                <span className="stat-label">Closed</span>
              </div>
            </div>
          </>
        )}

        <DashboardLog entries={log} onClose={handleClose} onEdit={handleEdit} />
      </main>
    </div>
  );
}
