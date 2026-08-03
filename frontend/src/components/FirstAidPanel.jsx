import React, { useState, useEffect, useContext } from "react";
import { AppContext } from "../App.jsx";
import checklistData from "../data/first_aid_checklist.json";

/**
 * FirstAidPanel — Emergency interactive first-aid guide and elapsed bite timer.
 * Designed for high stress, mobile use: large tap targets, clear visual hierarchy,
 * and single-source-of-truth syncing with clinical override fields.
 */
export default function FirstAidPanel() {
  const { overrides, setOverrides } = useContext(AppContext);
  const [now, setNow] = useState(Date.now());
  const [checkedSteps, setCheckedSteps] = useState({});

  // Live ticking timer every second
  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, []);

  // Ensure bite_timestamp is initialized if not present
  useEffect(() => {
    if (!overrides.bite_timestamp && !overrides.elapsed_hours) {
      const initTime = Date.now();
      setOverrides((prev) => ({
        ...prev,
        bite_timestamp: initTime,
        elapsed_hours: "0.00",
      }));
    } else if (!overrides.bite_timestamp && overrides.elapsed_hours) {
      // If elapsed_hours exists (e.g. entered manually elsewhere), back-calculate timestamp
      const hrs = parseFloat(overrides.elapsed_hours) || 0;
      const initTime = Date.now() - hrs * 3600 * 1000;
      setOverrides((prev) => ({ ...prev, bite_timestamp: initTime }));
    }
  }, [overrides.bite_timestamp, overrides.elapsed_hours, setOverrides]);

  const timestamp = overrides.bite_timestamp || now;
  const totalSeconds = Math.max(0, Math.floor((now - timestamp) / 1000));
  const elapsedHrs = totalSeconds / 3600;

  // Determine visual escalation state based on clinical thresholds
  let statusClass = "status-normal";
  let statusLabel = "⚡ WITHIN GOLDEN HOUR (< 1 HR) — BEST PROGNOSIS";
  let statusColor = "#059669"; // teal/green

  if (elapsedHrs >= 4) {
    statusClass = "status-critical";
    statusLabel = "🚨 CRITICAL DELAY (> 4 HRS) — HIGH RISK OF COAGULOPATHY / NECROSIS";
    statusColor = "#DC2626"; // red
  } else if (elapsedHrs >= 1) {
    statusClass = "status-warning";
    statusLabel = "⚠️ EXTENDED DELAY (> 1 HR) — URGENT TRANSPORT NEEDED";
    statusColor = "#D97706"; // amber
  }

  // Format HH:MM:SS
  const formatHHMMSS = (secs) => {
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    const s = secs % 60;
    return [h, m, s].map((v) => String(v).padStart(2, "0")).join(":");
  };

  // Quick adjust bite time
  const adjustMinutesAgo = (mins) => {
    const newTs = Date.now() - mins * 60 * 1000;
    const hrs = (mins / 60).toFixed(2);
    setOverrides((prev) => ({
      ...prev,
      bite_timestamp: newTs,
      elapsed_hours: hrs,
    }));
  };

  // Fine tune +/- 15 mins
  const shiftTime = (deltaMins) => {
    const currentTs = overrides.bite_timestamp || Date.now();
    const newTs = currentTs - deltaMins * 60 * 1000; // negative delta means earlier bite
    const newSecs = Math.max(0, (Date.now() - newTs) / 1000);
    const hrs = (newSecs / 3600).toFixed(2);
    setOverrides((prev) => ({
      ...prev,
      bite_timestamp: newTs,
      elapsed_hours: hrs,
    }));
  };

  const handleManualHoursChange = (val) => {
    const numHrs = parseFloat(val);
    if (!isNaN(numHrs) && numHrs >= 0) {
      const newTs = Date.now() - numHrs * 3600 * 1000;
      setOverrides((prev) => ({
        ...prev,
        bite_timestamp: newTs,
        elapsed_hours: val,
      }));
    } else {
      setOverrides((prev) => ({ ...prev, elapsed_hours: val }));
    }
  };

  const toggleStep = (id) => {
    setCheckedSteps((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const { do_protocol, dont_practices } = checklistData;

  return (
    <div className="firstaid-panel">
      {/* ─── ELAPSED BITE TIMER ─── */}
      <div className={`firstaid-timer-card ${statusClass}`} style={{ borderColor: statusColor }}>
        <div className="firstaid-timer-card__header">
          <div className="firstaid-timer-card__title">⏱️ ELAPSED BITE TIMER</div>
          <div className="firstaid-timer-card__badge" style={{ backgroundColor: statusColor }}>
            {statusLabel}
          </div>
        </div>

        <div className="firstaid-timer-card__clock" role="timer" aria-live="polite">
          {formatHHMMSS(totalSeconds)}
        </div>

        <div className="firstaid-timer-card__controls">
          <div className="firstaid-timer-card__controls-label">When did the bite occur? Quick adjust:</div>
          <div className="firstaid-timer-card__quick-btns">
            <button type="button" onClick={() => adjustMinutesAgo(0)} className="quick-btn">Just Now</button>
            <button type="button" onClick={() => adjustMinutesAgo(15)} className="quick-btn">15m ago</button>
            <button type="button" onClick={() => adjustMinutesAgo(30)} className="quick-btn">30m ago</button>
            <button type="button" onClick={() => adjustMinutesAgo(60)} className="quick-btn">1 hr ago</button>
            <button type="button" onClick={() => adjustMinutesAgo(120)} className="quick-btn">2 hrs ago</button>
            <button type="button" onClick={() => adjustMinutesAgo(240)} className="quick-btn">4 hrs ago</button>
          </div>

          <div className="firstaid-timer-card__fine-controls">
            <div className="fine-adjust-group">
              <button type="button" onClick={() => shiftTime(-15)} className="fine-btn" title="Add 15 minutes to elapsed time">
                + 15m Elapsed
              </button>
              <button type="button" onClick={() => shiftTime(15)} className="fine-btn" title="Subtract 15 minutes from elapsed time">
                - 15m Elapsed
              </button>
            </div>

            <div className="manual-hours-group">
              <label htmlFor="manual-elapsed">Exact hours:</label>
              <input
                id="manual-elapsed"
                type="number"
                min="0"
                step="0.25"
                placeholder="0.0"
                value={overrides.elapsed_hours || ""}
                onChange={(e) => handleManualHoursChange(e.target.value)}
                className="manual-hours-input"
              />
            </div>
          </div>
        </div>

        <div className="firstaid-timer-card__sync-info">
          🔄 Syncs automatically with diagnosis pipeline &amp; clinician console (Elapsed: {Number(overrides.elapsed_hours || 0).toFixed(2)} hrs)
        </div>
      </div>

      {/* ─── RICE PROTOCOL (DO THIS) ─── */}
      <div className="firstaid-section">
        <div className="firstaid-section__header">
          <h3 className="firstaid-section__title">✅ DO THIS — {do_protocol.title}</h3>
          <p className="firstaid-section__sub">
            Follow these steps immediately while awaiting transport. Check items off for reassurance while waiting.
          </p>
        </div>

        <div className="firstaid-rice-list">
          {do_protocol.steps.map((step) => {
            const isChecked = !!checkedSteps[step.id];
            return (
              <label
                key={step.id}
                className={`firstaid-step-card ${isChecked ? "checked" : ""}`}
              >
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => toggleStep(step.id)}
                  className="firstaid-step-card__checkbox"
                />
                <div className="firstaid-step-card__content">
                  <div className="firstaid-step-card__label">
                    {step.label}
                    {isChecked && <span className="step-checked-tag">✓ Confirmed</span>}
                  </div>
                  <div className="firstaid-step-card__detail">{step.detail}</div>
                </div>
              </label>
            );
          })}
        </div>
      </div>

      {/* ─── HARMFUL PRACTICES (AVOID THIS) ─── */}
      <div className="firstaid-section firstaid-section--hazard">
        <div className="firstaid-section__header">
          <h3 className="firstaid-section__title hazard-title">⚠️ AVOID THIS — REPORT PAST EVENTS</h3>
          <p className="firstaid-section__sub">
            <strong>Check any harmful practices that have already occurred.</strong> This information feeds directly into the AI diagnostic pipeline to warn doctors of potential amputation, necrosis, or infection risks.
          </p>
        </div>

        <div className="firstaid-hazard-list">
          {dont_practices.map((item) => {
            // Determine backend override field name
            const overrideKey = item.feeds_backend_field
              ? item.feeds_backend_field.replace("harmful_practices.", "")
              : `local_dont_${item.id}`;

            const isChecked = !!overrides[overrideKey];

            const handleHazardToggle = () => {
              setOverrides((prev) => ({
                ...prev,
                [overrideKey]: !isChecked,
              }));
            };

            return (
              <label
                key={item.id}
                className={`firstaid-hazard-card ${isChecked ? "flagged" : ""}`}
              >
                <div className="firstaid-hazard-card__indicator" aria-hidden="true">⚠️</div>
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={handleHazardToggle}
                  className="firstaid-hazard-card__checkbox"
                />
                <div className="firstaid-hazard-card__content">
                  <div className="firstaid-hazard-card__label">
                    {item.label}
                    {item.feeds_backend_field && (
                      <span className="sync-badge">📡 Feeds AI Pipeline</span>
                    )}
                    {isChecked && <span className="flagged-tag">🚨 REPORTED</span>}
                  </div>
                  <div className="firstaid-hazard-card__detail">{item.detail}</div>
                </div>
              </label>
            );
          })}
        </div>
      </div>
    </div>
  );
}
