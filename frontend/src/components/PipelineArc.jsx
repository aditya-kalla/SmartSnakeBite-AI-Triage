import React from "react";

const STAGES = [
  { key: "idle",       label: "Ready",                    short: "Ready" },
  { key: "transcribe", label: "Listening…",               short: "Listen" },
  { key: "am1",        label: "Understanding your words",  short: "Understand" },
  { key: "am3",        label: "Checking safety",           short: "Safety" },
  { key: "am2",        label: "Assessing risk",            short: "Risk" },
  { key: "done",       label: "Report ready",              short: "Done" },
];

function stageIndex(stage) {
  const idx = STAGES.findIndex((s) => s.key === stage);
  return idx === -1 ? 0 : idx;
}

/**
 * PipelineArc — a semicircular arc with dot markers for each pipeline stage.
 * Props: stage (string) — one of the STAGES keys.
 */
export default function PipelineArc({ stage = "idle" }) {
  const activeIdx = stageIndex(stage);
  const activeStage = STAGES[activeIdx];

  // Arc geometry: semicircle from 180° to 0° (left to right, top half)
  const cx = 160;
  const cy = 155;
  const r = 120;
  const dotCount = STAGES.length;

  // Distribute dots evenly along a 180° arc (π radians, from left to right)
  const dots = STAGES.map((s, i) => {
    const angle = Math.PI - (i / (dotCount - 1)) * Math.PI; // π to 0
    return {
      ...s,
      x: cx + r * Math.cos(angle),
      y: cy - r * Math.sin(angle),
      index: i,
    };
  });

  // Arc path for the track (semicircle, left to right)
  const arcPath = `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`;

  // Active arc: from dot 0 to the active dot
  const activeAngle = Math.PI - (activeIdx / (dotCount - 1)) * Math.PI;
  const activeEndX = cx + r * Math.cos(activeAngle);
  const activeEndY = cy - r * Math.sin(activeAngle);
  // Determine if arc sweep is > 180° (it won't be for a semicircle with ≤6 stages)
  const largeArcFlag = activeIdx > (dotCount - 1) / 2 ? 1 : 0;

  return (
    <div className="pipeline-arc" aria-label={`Pipeline stage: ${activeStage.label}`}>
      <svg viewBox="0 0 320 195" className="pipeline-arc__svg">
        {/* Track arc (background) */}
        <path
          d={arcPath}
          fill="none"
          stroke="var(--line-soft)"
          strokeWidth="2"
          strokeLinecap="round"
        />

        {/* Active arc (filled portion) */}
        {activeIdx > 0 && (
          <path
            d={`M ${cx - r} ${cy} A ${r} ${r} 0 ${largeArcFlag} 1 ${activeEndX} ${activeEndY}`}
            fill="none"
            stroke="var(--clinical-teal)"
            strokeWidth="3"
            strokeLinecap="round"
            className="pipeline-arc__active-path"
          />
        )}

        {/* Dot markers */}
        {dots.map((dot) => {
          const isActive = dot.index === activeIdx;
          const isCompleted = dot.index < activeIdx;
          const isFuture = dot.index > activeIdx;

          return (
            <g key={dot.key}>
              {/* Outer ring for active dot */}
              {isActive && (
                <circle
                  cx={dot.x}
                  cy={dot.y}
                  r="14"
                  fill="none"
                  stroke="var(--clinical-teal)"
                  strokeWidth="2"
                  opacity="0.3"
                  className="pipeline-arc__pulse"
                />
              )}
              <circle
                cx={dot.x}
                cy={dot.y}
                r={isActive ? 8 : 5}
                fill={isFuture ? "var(--paper-base)" : "var(--clinical-teal)"}
                stroke={isFuture ? "var(--line-strong)" : "var(--clinical-teal)"}
                strokeWidth={isFuture ? 1.5 : 0}
                className={`pipeline-arc__dot ${isActive ? "pipeline-arc__dot--active" : ""}`}
              />
              {/* Small label beneath each dot */}
              <text
                x={dot.x}
                y={dot.y + (dot.y > cy - 20 ? 22 : -16)}
                textAnchor="middle"
                className={`pipeline-arc__dot-label ${isActive ? "pipeline-arc__dot-label--active" : ""}`}
                fill={isFuture ? "var(--ink-muted)" : "var(--clinical-teal)"}
                fontSize="9"
                fontFamily="var(--font-mono)"
              >
                {dot.short}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Central number and label */}
      <div className="pipeline-arc__center">
        <span className="pipeline-arc__step-num">
          {activeIdx === 0 ? "—" : String(activeIdx).padStart(2, "0")}
        </span>
        <span className="pipeline-arc__step-label">{activeStage.label}</span>
      </div>
    </div>
  );
}

export { STAGES, stageIndex };
