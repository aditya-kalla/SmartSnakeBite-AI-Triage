import React, { useContext, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../App.jsx";

function getSevRank(sev) {
  const s = (sev || "").toUpperCase();
  if (s === "CRITICAL") return 4;
  if (s === "HIGH") return 3;
  if (s === "MODERATE" || s === "MEDIUM") return 2;
  if (s === "LOW") return 1;
  return 0;
}

function getSevClass(sev) {
  const s = (sev || "").toUpperCase();
  if (["CRITICAL", "HIGH", "MODERATE", "LOW"].includes(s)) return s.toLowerCase();
  if (s === "MEDIUM") return "moderate";
  return "moderate";
}

export default function Dashboard() {
  const { log, updateCaseStatus, deleteCases, setOverrides } = useContext(AppContext);
  const navigate = useNavigate();

  const [searchTerm, setSearchTerm] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [sortBy, setSortBy] = useState("SEVERE_FIRST");
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [activeMenuId, setActiveMenuId] = useState(null);

  // Stat calculations
  const totalCases = log.length;
  const criticalCases = log.filter(c => (c.severity || "").toUpperCase() === "CRITICAL").length;
  const awaitingReferral = log.filter(c => c.status !== "resolved").length;
  const resolvedCases = log.filter(c => c.status === "resolved").length;

  // Filtered and Sorted Queue
  const queue = useMemo(() => {
    return log
      .filter(item => {
        // Severity filter
        if (severityFilter !== "ALL") {
          const s = (item.severity || "").toUpperCase();
          if (s !== severityFilter) return false;
        }
        // Search filter
        if (searchTerm.trim() !== "") {
          const q = searchTerm.toLowerCase();
          const idMatch = String(item.id).includes(q);
          const transcriptMatch = (item.transcript || "").toLowerCase().includes(q);
          const speciesMatch = (item.am2?.top_species || []).some(sp => sp.toLowerCase().includes(q));
          const venomMatch = (item.venomType || "").toLowerCase().includes(q);
          return idMatch || transcriptMatch || speciesMatch || venomMatch;
        }
        return true;
      })
      .sort((a, b) => {
        if (sortBy === "SEVERE_FIRST") {
          const diff = getSevRank(b.severity) - getSevRank(a.severity);
          if (diff !== 0) return diff;
          return b.id - a.id; // secondary sort newest first
        }
        if (sortBy === "RECENT_FIRST") {
          return b.id - a.id;
        }
        if (sortBy === "OLDEST_FIRST") {
          return a.id - b.id;
        }
        return 0;
      });
  }, [log, severityFilter, searchTerm, sortBy]);

  // Checkbox handlers
  function toggleSelectAll() {
    if (selectedIds.size === queue.length && queue.length > 0) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(queue.map(item => item.id)));
    }
  }

  function toggleSelectOne(id, e) {
    e.stopPropagation();
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  // Row navigation
  function handleRowClick(id) {
    navigate(`/case/${id}`);
  }

  // Row actions
  function handleReopenInDiagnose(item, e) {
    e.stopPropagation();
    setActiveMenuId(null);
    setOverrides(prev => ({
      ...prev,
      transcriptText: item.transcript
    }));
    navigate("/diagnose");
  }

  function handleStatusToggle(id, currentStatus, e) {
    e.stopPropagation();
    setActiveMenuId(null);
    updateCaseStatus(id, currentStatus === "resolved" ? "open" : "resolved");
  }

  function handleDeleteSingle(id, e) {
    e.stopPropagation();
    setActiveMenuId(null);
    deleteCases(id);
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  }

  // Bulk actions
  function handleBulkResolve() {
    updateCaseStatus(Array.from(selectedIds), "resolved");
    setSelectedIds(new Set());
  }

  function handleBulkReopen() {
    updateCaseStatus(Array.from(selectedIds), "open");
    setSelectedIds(new Set());
  }

  function handleBulkDelete() {
    if (window.confirm(`Delete ${selectedIds.size} selected case(s)?`)) {
      deleteCases(Array.from(selectedIds));
      setSelectedIds(new Set());
    }
  }

  // Export CSV
  function handleExportCSV() {
    const headers = ["ID", "Time", "Severity", "Status", "Venom Type", "Top Species", "Referral Priority", "Transcript"];
    const rows = queue.map(c => [
      c.id,
      c.time || "",
      c.severity || "UNKNOWN",
      c.status || "open",
      c.venomType || "",
      (c.am2?.top_species || []).join("; "),
      c.am2?.referral_priority || "",
      `"${(c.transcript || "").replace(/"/g, '""')}"`
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `smartsnakebite_session_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  const allSelected = queue.length > 0 && selectedIds.size === queue.length;

  return (
    <div className="dashboard-page" style={{ paddingBottom: "5rem" }}>
      {/* 1. Page Header */}
      <div className="workspace-header" style={{ marginBottom: "2rem" }}>
        <h1>Case Queue</h1>
        <p className="text-muted">Real-time clinical prioritization and session log of snakebite diagnostics.</p>
      </div>

      {/* 2. Stat Cards Row (4 cards) */}
      <div className="stat-row" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.25rem", marginBottom: "2.5rem" }}>
        <div className="stat-card" style={{ background: "var(--paper-raised)", padding: "1.5rem", borderRadius: "16px", border: "1px solid var(--line-soft)", boxShadow: "var(--shadow-card)" }}>
          <span className="stat-num" style={{ fontSize: "2rem", fontWeight: 700, fontFamily: "var(--font-display)", display: "block", color: "var(--ink-dark)" }}>
            {totalCases}
          </span>
          <span className="stat-label" style={{ fontSize: "0.85rem", color: "var(--ink-muted)", fontFamily: "var(--font-mono)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Total Cases
          </span>
        </div>

        <div className="stat-card" style={{ background: "var(--paper-raised)", padding: "1.5rem", borderRadius: "16px", border: "1px solid var(--line-soft)", boxShadow: "var(--shadow-card)", borderLeft: "4px solid var(--sev-critical)" }}>
          <span className="stat-num color-critical" style={{ fontSize: "2rem", fontWeight: 700, fontFamily: "var(--font-display)", display: "block", color: "var(--sev-critical)" }}>
            {criticalCases}
          </span>
          <span className="stat-label" style={{ fontSize: "0.85rem", color: "var(--ink-muted)", fontFamily: "var(--font-mono)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Critical
          </span>
        </div>

        <div className="stat-card" style={{ background: "var(--paper-raised)", padding: "1.5rem", borderRadius: "16px", border: "1px solid var(--line-soft)", boxShadow: "var(--shadow-card)" }}>
          <span className="stat-num" style={{ fontSize: "2rem", fontWeight: 700, fontFamily: "var(--font-display)", display: "block", color: "var(--sev-high)" }}>
            {awaitingReferral}
          </span>
          <span className="stat-label" style={{ fontSize: "0.85rem", color: "var(--ink-muted)", fontFamily: "var(--font-mono)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Awaiting Referral
          </span>
        </div>

        <div className="stat-card" style={{ background: "var(--paper-raised)", padding: "1.5rem", borderRadius: "16px", border: "1px solid var(--line-soft)", boxShadow: "var(--shadow-card)" }}>
          <span className="stat-num" style={{ fontSize: "2rem", fontWeight: 700, fontFamily: "var(--font-display)", display: "block", color: "var(--clinical-teal)" }}>
            {resolvedCases}
          </span>
          <span className="stat-label" style={{ fontSize: "0.85rem", color: "var(--ink-muted)", fontFamily: "var(--font-mono)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Resolved
          </span>
        </div>
      </div>

      {/* 3. Toolbar Row */}
      <div className="toolbar-row" style={{
        display: "flex",
        flexWrap: "wrap",
        gap: "1rem",
        justifyContent: "space-between",
        alignItems: "center",
        background: "var(--paper-raised)",
        padding: "1rem 1.5rem",
        borderRadius: "16px",
        border: "1px solid var(--line-soft)",
        boxShadow: "var(--shadow-card)",
        marginBottom: "1.5rem"
      }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", flex: 1, minWidth: "280px" }}>
          {/* Search */}
          <div style={{ position: "relative", flex: "1 1 220px" }}>
            <input
              type="text"
              placeholder="Search patient, ID, or species..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: "100%",
                padding: "0.6rem 1rem 0.6rem 2.25rem",
                borderRadius: "10px",
                border: "1px solid var(--line-strong)",
                background: "var(--paper-base)",
                fontFamily: "var(--font-body)",
                fontSize: "0.85rem",
                color: "var(--ink-dark)"
              }}
            />
            <span style={{ position: "absolute", left: "0.75rem", top: "50%", transform: "translateY(-50%)", color: "var(--ink-muted)", fontSize: "0.9rem" }}>
              🔍
            </span>
          </div>

          {/* Severity Filter */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            style={{
              padding: "0.6rem 1rem",
              borderRadius: "10px",
              border: "1px solid var(--line-strong)",
              background: "var(--paper-base)",
              fontFamily: "var(--font-mono)",
              fontSize: "0.8rem",
              color: "var(--ink-dark)",
              cursor: "pointer"
            }}
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical Only</option>
            <option value="HIGH">High Only</option>
            <option value="MODERATE">Moderate Only</option>
            <option value="LOW">Low Only</option>
          </select>

          {/* Sort Control */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{
              padding: "0.6rem 1rem",
              borderRadius: "10px",
              border: "1px solid var(--line-strong)",
              background: "var(--paper-base)",
              fontFamily: "var(--font-mono)",
              fontSize: "0.8rem",
              color: "var(--ink-dark)",
              cursor: "pointer"
            }}
          >
            <option value="SEVERE_FIRST">Sort: Most Severe First</option>
            <option value="RECENT_FIRST">Sort: Most Recent</option>
            <option value="OLDEST_FIRST">Sort: Oldest First</option>
          </select>
        </div>

        {/* Export CSV Button */}
        <button
          onClick={handleExportCSV}
          disabled={queue.length === 0}
          style={{
            padding: "0.6rem 1.25rem",
            borderRadius: "10px",
            border: "1px solid var(--clinical-teal)",
            background: "transparent",
            color: "var(--clinical-teal)",
            fontFamily: "var(--font-mono)",
            fontSize: "0.8rem",
            fontWeight: 600,
            cursor: queue.length === 0 ? "not-allowed" : "pointer",
            opacity: queue.length === 0 ? 0.6 : 1,
            transition: "all 0.2s",
            display: "inline-flex",
            alignItems: "center",
            gap: "0.4rem"
          }}
        >
          📥 Export session as CSV
        </button>
      </div>

      {/* Bulk Action Bar (when 1+ selected) */}
      {selectedIds.size > 0 && (
        <div className="bulk-action-bar" style={{
          background: "var(--clinical-teal)",
          color: "#ffffff",
          padding: "0.75rem 1.5rem",
          borderRadius: "12px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.5rem",
          boxShadow: "0 4px 12px rgba(31, 74, 68, 0.2)",
          fontFamily: "var(--font-mono)",
          fontSize: "0.85rem",
          animation: "fadeIn 0.2s ease"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <span style={{ fontWeight: 700 }}>✓ {selectedIds.size} case(s) selected</span>
            <button
              onClick={() => setSelectedIds(new Set())}
              style={{ background: "transparent", border: "none", color: "rgba(255,255,255,0.7)", cursor: "pointer", fontSize: "0.8rem", textDecoration: "underline" }}
            >
              Clear
            </button>
          </div>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button
              onClick={handleBulkResolve}
              style={{ padding: "0.4rem 0.8rem", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.3)", background: "rgba(255,255,255,0.15)", color: "#fff", cursor: "pointer", fontWeight: 600 }}
            >
              ✅ Mark Resolved
            </button>
            <button
              onClick={handleBulkReopen}
              style={{ padding: "0.4rem 0.8rem", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.3)", background: "rgba(255,255,255,0.15)", color: "#fff", cursor: "pointer", fontWeight: 600 }}
            >
              🟢 Re-open
            </button>
            <button
              onClick={handleBulkDelete}
              style={{ padding: "0.4rem 0.8rem", borderRadius: "8px", border: "1px solid rgba(255,100,100,0.5)", background: "rgba(220, 38, 38, 0.8)", color: "#fff", cursor: "pointer", fontWeight: 600 }}
            >
              🗑️ Delete
            </button>
          </div>
        </div>
      )}

      {/* 4. The Queue Table */}
      {queue.length === 0 ? (
        <div className="empty-state" style={{
          background: "var(--paper-raised)",
          padding: "4rem 2rem",
          borderRadius: "20px",
          border: "1px dashed var(--line-strong)",
          textAlign: "center",
          color: "var(--ink-muted)"
        }}>
          <p style={{ fontSize: "1.1rem", marginBottom: "0.5rem", color: "var(--ink-dark)", fontFamily: "var(--font-display)" }}>
            No matching cases in queue
          </p>
          <p style={{ fontSize: "0.9rem" }}>
            {log.length === 0 ? "Start a new diagnosis session or reload the demo queue from settings." : "Try adjusting your search or filter criteria."}
          </p>
        </div>
      ) : (
        <div className="table-container" style={{
          background: "var(--paper-raised)",
          borderRadius: "20px",
          border: "1px solid var(--line-soft)",
          boxShadow: "var(--shadow-card)",
          overflow: "visible"
        }}>
          <table className="data-table" style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
            <thead>
              <tr style={{ background: "rgba(31, 74, 68, 0.04)", borderBottom: "2px solid var(--line-strong)", fontFamily: "var(--font-mono)", fontSize: "0.75rem", color: "var(--ink-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                <th style={{ padding: "1rem 1rem", width: "40px" }}>
                  <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={toggleSelectAll}
                    style={{ width: "16px", height: "16px", accentColor: "var(--clinical-teal)", cursor: "pointer" }}
                  />
                </th>
                <th style={{ padding: "1rem 0.5rem", width: "50px" }}>PRIORITY</th>
                <th style={{ padding: "1rem 1rem" }}>CASE ID · TIME</th>
                <th style={{ padding: "1rem 1rem" }}>TOP SPECIES / CLASS</th>
                <th style={{ padding: "1rem 1rem" }}>SEVERITY</th>
                <th style={{ padding: "1rem 1rem" }}>REFERRAL PRIORITY</th>
                <th style={{ padding: "1rem 1rem" }}>STATUS</th>
                <th style={{ padding: "1rem 1rem", width: "60px", textAlign: "center" }}>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {queue.map((item, idx) => {
                const sClass = getSevClass(item.severity);
                const isSelected = selectedIds.has(item.id);
                const isResolved = item.status === "resolved";
                const speciesList = item.am2?.top_species || item.am2?.probable_species || [];
                const primarySpecies = speciesList.length > 0 ? speciesList[0] : (item.venomType || "Unspecified Snakebite");
                const referralText = item.am2?.referral_priority || item.am3?.primary_corrective_message || "Standard Observation";

                return (
                  <tr
                    key={item.id}
                    onClick={() => handleRowClick(item.id)}
                    style={{
                      borderBottom: "1px solid var(--line-soft)",
                      cursor: "pointer",
                      background: isSelected ? "rgba(31, 74, 68, 0.05)" : isResolved ? "rgba(0,0,0,0.015)" : "transparent",
                      opacity: isResolved ? 0.75 : 1,
                      transition: "background 0.15s ease"
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = isSelected ? "rgba(31, 74, 68, 0.08)" : "rgba(31, 74, 68, 0.025)"}
                    onMouseLeave={(e) => e.currentTarget.style.background = isSelected ? "rgba(31, 74, 68, 0.05)" : isResolved ? "rgba(0,0,0,0.015)" : "transparent"}
                  >
                    {/* 1. Checkbox */}
                    <td style={{ padding: "1.1rem 1rem" }} onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => toggleSelectOne(item.id, e)}
                        style={{ width: "16px", height: "16px", accentColor: "var(--clinical-teal)", cursor: "pointer" }}
                      />
                    </td>

                    {/* 2. Priority # */}
                    <td style={{ padding: "1.1rem 0.5rem", fontFamily: "var(--font-mono)", fontWeight: 700, fontSize: "0.85rem", color: idx === 0 && !isResolved ? "var(--sev-critical)" : "var(--ink-muted)" }}>
                      #{idx + 1}
                    </td>

                    {/* 3. Case ID & Time */}
                    <td style={{ padding: "1.1rem 1rem" }}>
                      <div style={{ fontFamily: "var(--font-mono)", fontWeight: 600, fontSize: "0.9rem", color: "var(--ink-dark)" }}>
                        #{item.id}
                      </div>
                      <div style={{ fontSize: "0.75rem", color: "var(--ink-muted)", fontFamily: "var(--font-mono)" }}>
                        {item.time || "—"} · {(item.language || "EN").toUpperCase()}
                      </div>
                    </td>

                    {/* 4. Top Species */}
                    <td style={{ padding: "1.1rem 1rem", maxWidth: "240px" }}>
                      <div style={{ fontWeight: 600, fontSize: "0.9rem", color: "var(--ink-dark)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                        {primarySpecies}
                      </div>
                      {speciesList.length > 1 && (
                        <div style={{ fontSize: "0.75rem", color: "var(--ink-muted)" }}>
                          +{speciesList.length - 1} other probable
                        </div>
                      )}
                    </td>

                    {/* 5. Severity Badge */}
                    <td style={{ padding: "1.1rem 1rem" }}>
                      <span style={{
                        display: "inline-block",
                        padding: "4px 10px",
                        borderRadius: "99px",
                        fontSize: "0.75rem",
                        fontFamily: "var(--font-mono)",
                        fontWeight: 700,
                        textTransform: "uppercase",
                        letterSpacing: "0.04em",
                        background: `var(--sev-${sClass}-soft, rgba(0,0,0,0.05))`,
                        color: `var(--sev-${sClass}, var(--ink-dark))`,
                        border: `1px solid var(--sev-${sClass}, var(--line-strong))`
                      }}>
                        {item.severity || "UNKNOWN"}
                      </span>
                    </td>

                    {/* 6. Referral Priority */}
                    <td style={{ padding: "1.1rem 1rem", maxWidth: "260px" }}>
                      <div style={{ fontSize: "0.85rem", color: "var(--ink-dark)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                        {referralText}
                      </div>
                    </td>

                    {/* 7. Status */}
                    <td style={{ padding: "1.1rem 1rem" }}>
                      <span style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.3rem",
                        fontSize: "0.78rem",
                        fontFamily: "var(--font-mono)",
                        fontWeight: 600,
                        color: isResolved ? "var(--clinical-teal)" : "var(--sev-high)"
                      }}>
                        <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: isResolved ? "var(--clinical-teal)" : "var(--sev-high)" }} />
                        {isResolved ? "RESOLVED" : "OPEN"}
                      </span>
                    </td>

                    {/* 8. Actions (...) Menu */}
                    <td style={{ padding: "1.1rem 1rem", textAlign: "center", position: "relative" }} onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setActiveMenuId(activeMenuId === item.id ? null : item.id);
                        }}
                        style={{
                          background: "transparent",
                          border: "1px solid var(--line-soft)",
                          borderRadius: "6px",
                          padding: "0.3rem 0.6rem",
                          cursor: "pointer",
                          color: "var(--ink-dark)",
                          fontWeight: 700,
                          fontSize: "0.9rem"
                        }}
                        title="Row Actions"
                      >
                        •••
                      </button>

                      {activeMenuId === item.id && (
                        <div style={{
                          position: "absolute",
                          right: "1rem",
                          top: "2.8rem",
                          background: "var(--paper-raised)",
                          border: "1px solid var(--line-strong)",
                          borderRadius: "12px",
                          boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
                          padding: "0.5rem",
                          zIndex: 10,
                          minWidth: "180px",
                          display: "flex",
                          flexDirection: "column",
                          gap: "0.25rem",
                          textAlign: "left"
                        }}>
                          <button
                            onClick={() => navigate(`/case/${item.id}`)}
                            style={{ background: "transparent", border: "none", padding: "0.5rem 0.75rem", borderRadius: "6px", cursor: "pointer", textAlign: "left", fontSize: "0.82rem", color: "var(--ink-dark)", display: "flex", alignItems: "center", gap: "0.5rem" }}
                            onMouseEnter={(e) => e.currentTarget.style.background = "var(--paper-base)"}
                            onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                          >
                            👁️ View full case
                          </button>

                          <button
                            onClick={(e) => handleReopenInDiagnose(item, e)}
                            style={{ background: "transparent", border: "none", padding: "0.5rem 0.75rem", borderRadius: "6px", cursor: "pointer", textAlign: "left", fontSize: "0.82rem", color: "var(--ink-dark)", display: "flex", alignItems: "center", gap: "0.5rem" }}
                            onMouseEnter={(e) => e.currentTarget.style.background = "var(--paper-base)"}
                            onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                          >
                            🔄 Re-open in Diagnose
                          </button>

                          <button
                            onClick={(e) => handleStatusToggle(item.id, item.status, e)}
                            style={{ background: "transparent", border: "none", padding: "0.5rem 0.75rem", borderRadius: "6px", cursor: "pointer", textAlign: "left", fontSize: "0.82rem", color: "var(--ink-dark)", display: "flex", alignItems: "center", gap: "0.5rem" }}
                            onMouseEnter={(e) => e.currentTarget.style.background = "var(--paper-base)"}
                            onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                          >
                            {isResolved ? "🟢 Mark Open" : "✅ Mark Resolved"}
                          </button>

                          <hr style={{ border: "none", borderTop: "1px solid var(--line-soft)", margin: "0.25rem 0" }} />

                          <button
                            onClick={(e) => handleDeleteSingle(item.id, e)}
                            style={{ background: "transparent", border: "none", padding: "0.5rem 0.75rem", borderRadius: "6px", cursor: "pointer", textAlign: "left", fontSize: "0.82rem", color: "var(--sev-critical)", display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: 600 }}
                            onMouseEnter={(e) => e.currentTarget.style.background = "rgba(220, 38, 38, 0.08)"}
                            onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                          >
                            🗑️ Delete case
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
