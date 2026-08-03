import { sevClass } from "./ResultCard.jsx";

export default function DashboardLog({ entries, onClose, onEdit }) {
  return (
    <section className="dashboard-section">
      <h2>Case Log</h2>
      {entries.length === 0 ? (
        <div className="empty-state">
          No cases yet. Record a symptom narrative above to begin.
        </div>
      ) : (
        <div className="log-list">
          {entries.map((e) => (
            <div key={e.id} className={`log-row ${e.status === "closed" ? "closed" : ""}`}>
              <span className="time">{e.time}</span>
              <span className="snippet">
                {e.editing ? (
                  <input
                    className="inline-edit"
                    defaultValue={e.transcript}
                    autoFocus
                    onBlur={(ev) => onEdit(e.id, ev.target.value)}
                    onKeyDown={(ev) => ev.key === "Enter" && ev.target.blur()}
                  />
                ) : (
                  e.transcript || "(no transcript)"
                )}
              </span>
              <span className="snippet" style={{ color: "var(--ink-soft)" }}>
                {e.venomType || "—"}
              </span>
              <span className={`badge sev-${sevClass(e.severity)}`}>
                {e.severity || "N/A"}
              </span>
              <span className="row-actions">
                <button
                  className="row-action-btn"
                  onClick={() => onEdit(e.id, undefined, true)}
                  title="Edit transcript"
                >
                  ✎
                </button>
                <button
                  className="row-action-btn"
                  onClick={() => onClose(e.id)}
                  title={e.status === "closed" ? "Reopen case" : "Close case"}
                >
                  {e.status === "closed" ? "↺" : "✓"}
                </button>
              </span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
