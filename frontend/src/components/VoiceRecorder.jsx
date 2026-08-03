import { useRef, useState } from "react";

const LANG_LABELS = {
  auto: "Auto detect", en: "English", te: "Telugu",
  hi: "Hindi", ta: "Tamil", kn: "Kannada",
};

const TIME_LABELS = { morning: "Morning", afternoon: "Afternoon", evening: "Evening", night: "Night" };
const SEASON_LABELS = { monsoon: "Monsoon", post_monsoon: "Post-monsoon", summer: "Summer", winter: "Winter" };

/**
 * MicButton — the large tappable microphone button + status text.
 * Separated out so Triage can place it in its own visual zone.
 */
export function MicButton({ recording, onStart, onStop, stageLabel }) {
  return (
    <div className="mic-area">
      <button
        className={`mic-btn ${recording ? "recording" : ""}`}
        onClick={recording ? onStop : onStart}
        aria-label={recording ? "Stop recording" : "Start recording"}
      >
        {recording ? (
          <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="6" width="12" height="12" rx="2" />
          </svg>
        ) : (
          <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
          </svg>
        )}
      </button>
      <div className="mic-status">
        <span className="mic-status__state">{recording ? "Recording…" : stageLabel}</span>
        <span className="mic-status__hint">
          {recording
            ? "Tap to stop"
            : "Tap the mic and describe the symptoms — any language"}
        </span>
      </div>
    </div>
  );
}

/**
 * ContextChips — auto-detected context as read-only pills + clinician override toggle.
 */
export function ContextChips({ autoContext, overrides, setOverrides }) {
  const [showOverride, setShowOverride] = useState(false);

  const effectiveTime = overrides.time_of_day || autoContext.time_of_day;
  const effectiveSeason = overrides.season || autoContext.season;
  const effectiveLang = overrides.language || "auto";

  const locationLabel =
    autoContext.locationStatus === "granted"
      ? `${autoContext.lat.toFixed(3)}, ${autoContext.lng.toFixed(3)}`
      : autoContext.locationStatus === "requesting"
      ? "Locating…"
      : "Location unavailable";

  return (
    <div className="context-group">
      <div className="context-group__chips">
        <span className="ctx-chip">📍 {locationLabel}</span>
        <span className="ctx-chip">🕐 {TIME_LABELS[effectiveTime]}</span>
        <span className="ctx-chip">🌦 {SEASON_LABELS[effectiveSeason]}</span>
        <span className="ctx-chip">🗣 {LANG_LABELS[effectiveLang]}</span>
      </div>

      <button
        className="ctx-override-toggle"
        onClick={() => setShowOverride((v) => !v)}
      >
        {showOverride ? "Hide overrides" : "Clinician override"}
      </button>

      {showOverride && (
        <div className="context-group__overrides">
          <div className="ctx-field">
            <label>Language</label>
            <select
              value={effectiveLang}
              onChange={(e) => setOverrides({ ...overrides, language: e.target.value })}
            >
              {Object.entries(LANG_LABELS).map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </div>
          <div className="ctx-field">
            <label>District</label>
            <input
              value={overrides.district || ""}
              placeholder="Auto (pending GPS module)"
              onChange={(e) => setOverrides({ ...overrides, district: e.target.value })}
            />
          </div>
          <div className="ctx-field">
            <label>Time of day</label>
            <select
              value={effectiveTime}
              onChange={(e) => setOverrides({ ...overrides, time_of_day: e.target.value })}
            >
              {Object.entries(TIME_LABELS).map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </div>
          <div className="ctx-field">
            <label>Season</label>
            <select
              value={effectiveSeason}
              onChange={(e) => setOverrides({ ...overrides, season: e.target.value })}
            >
              {Object.entries(SEASON_LABELS).map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </div>

          <div className="ctx-section-title">Patient & Timing</div>
          <div className="ctx-field">
            <label>Patient Age (yrs)</label>
            <input
              type="number"
              min="0"
              max="120"
              placeholder="e.g. 35"
              value={overrides.patient_age || ""}
              onChange={(e) => setOverrides({ ...overrides, patient_age: e.target.value })}
            />
          </div>
          <div className="ctx-field">
            <label>Elapsed Time (hrs)</label>
            <input
              type="number"
              min="0"
              step="0.5"
              placeholder="e.g. 2.5"
              value={overrides.elapsed_hours || ""}
              onChange={(e) => {
                const val = e.target.value;
                const hrs = parseFloat(val);
                const newTs = !isNaN(hrs) && hrs >= 0 ? Date.now() - hrs * 3600 * 1000 : undefined;
                setOverrides({ ...overrides, elapsed_hours: val, ...(newTs ? { bite_timestamp: newTs } : {}) });
              }}
            />
          </div>

          <div className="ctx-section-title">Harmful First-Aid Practices</div>
          <div className="ctx-checkbox-group">
            <label className="ctx-checkbox-label">
              <input
                type="checkbox"
                checked={!!overrides.tourniquet_applied}
                onChange={(e) => setOverrides({ ...overrides, tourniquet_applied: e.target.checked })}
              />
              Tourniquet applied
            </label>
            <label className="ctx-checkbox-label">
              <input
                type="checkbox"
                checked={!!overrides.incision_attempted}
                onChange={(e) => setOverrides({ ...overrides, incision_attempted: e.target.checked })}
              />
              Incision / cutting attempted
            </label>
            <label className="ctx-checkbox-label">
              <input
                type="checkbox"
                checked={!!overrides.traditional_healer_visited}
                onChange={(e) => setOverrides({ ...overrides, traditional_healer_visited: e.target.checked })}
              />
              Visited traditional healer before this
            </label>
            <label className="ctx-checkbox-label">
              <input
                type="checkbox"
                checked={!!overrides.herbal_application}
                onChange={(e) => setOverrides({ ...overrides, herbal_application: e.target.checked })}
              />
              Herbal / topical application
            </label>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * VoiceRecorder — the original combined component, kept for backward compat.
 * New Triage page uses MicButton + ContextChips separately instead.
 */
export default function VoiceRecorder({ autoContext, overrides, setOverrides, onRecordingComplete, stageLabel }) {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    chunksRef.current = [];

    recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      stream.getTracks().forEach((t) => t.stop());
      onRecordingComplete(blob);
    };

    recorder.start();
    mediaRecorderRef.current = recorder;
    setRecording(true);
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  }

  return (
    <div className="recorder-panel">
      <MicButton
        recording={recording}
        onStart={startRecording}
        onStop={stopRecording}
        stageLabel={stageLabel}
      />
      <ContextChips
        autoContext={autoContext}
        overrides={overrides}
        setOverrides={setOverrides}
      />
    </div>
  );
}
