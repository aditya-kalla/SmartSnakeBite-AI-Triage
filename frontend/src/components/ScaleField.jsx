import React, { useRef, useEffect, useCallback, useState } from "react";

/**
 * ScaleField — bio-luminescent reptile-scale background effect.
 *
 * Props:
 *   mode: "reactive" (follows cursor, hero) | "ambient" (auto-drift, body sections)
 *   glowColor: CSS color for the radial glow (default: emerald)
 *   className: additional CSS class
 *   ctaSelector: CSS selector for the CTA button that triggers amber glow shift
 */

/* SVG scale pattern as a data-URI. Overlapping shield/leaf shapes with subtle ridge. */
const SCALE_SVG = `
<svg xmlns="http://www.w3.org/2000/svg" width="48" height="40" viewBox="0 0 48 40">
  <defs>
    <filter id="ds" x="-10%" y="-10%" width="130%" height="140%">
      <feDropShadow dx="0" dy="1.5" stdDeviation="1.2" flood-color="rgba(0,0,0,0.07)"/>
    </filter>
  </defs>
  <!-- row 1 -->
  <ellipse cx="12" cy="10" rx="13" ry="16" fill="rgba(31,74,68,0.035)" filter="url(#ds)" />
  <ellipse cx="36" cy="10" rx="13" ry="16" fill="rgba(31,74,68,0.03)" filter="url(#ds)" />
  <!-- row 2, offset -->
  <ellipse cx="0" cy="30" rx="13" ry="16" fill="rgba(31,74,68,0.025)" filter="url(#ds)" />
  <ellipse cx="24" cy="30" rx="13" ry="16" fill="rgba(31,74,68,0.035)" filter="url(#ds)" />
  <ellipse cx="48" cy="30" rx="13" ry="16" fill="rgba(31,74,68,0.025)" filter="url(#ds)" />
  <!-- ridges -->
  <line x1="12" y1="2" x2="12" y2="18" stroke="rgba(31,74,68,0.03)" stroke-width="0.6"/>
  <line x1="36" y1="2" x2="36" y2="18" stroke="rgba(31,74,68,0.03)" stroke-width="0.6"/>
  <line x1="24" y1="22" x2="24" y2="38" stroke="rgba(31,74,68,0.03)" stroke-width="0.6"/>
</svg>`;

const SCALE_PATTERN_URI = `url("data:image/svg+xml,${encodeURIComponent(SCALE_SVG.trim())}")`;

const GLOW_EMERALD = "rgba(16, 185, 129, 0.18)";
const GLOW_AMBER   = "rgba(245, 158, 11, 0.22)";

export default function ScaleField({ mode = "reactive", ctaSelector, className = "" }) {
  const containerRef = useRef(null);
  const mouseRef = useRef({ x: 50, y: 50 });         // target (percent)
  const currentRef = useRef({ x: 50, y: 50 });        // lerp'd current
  const rafRef = useRef(null);
  const [glowColor, setGlowColor] = useState(GLOW_EMERALD);

  /* ── Reactive mode: track mouse with spring-damped lerp ── */
  const updatePosition = useCallback(() => {
    if (mode !== "reactive" || !containerRef.current) return;
    const lerp = 0.06; // spring damping factor
    currentRef.current.x += (mouseRef.current.x - currentRef.current.x) * lerp;
    currentRef.current.y += (mouseRef.current.y - currentRef.current.y) * lerp;

    containerRef.current.style.setProperty("--glow-x", `${currentRef.current.x}%`);
    containerRef.current.style.setProperty("--glow-y", `${currentRef.current.y}%`);
    rafRef.current = requestAnimationFrame(updatePosition);
  }, [mode]);

  useEffect(() => {
    if (mode !== "reactive") return;

    const el = containerRef.current;
    if (!el) return;

    const onMove = (e) => {
      mouseRef.current.x = (e.clientX / window.innerWidth) * 100;
      mouseRef.current.y = (e.clientY / window.innerHeight) * 100;
    };

    window.addEventListener("mousemove", onMove, { passive: true });
    rafRef.current = requestAnimationFrame(updatePosition);

    return () => {
      window.removeEventListener("mousemove", onMove);
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [mode, updatePosition]);

  /* ── CTA hover → amber glow shift ── */
  useEffect(() => {
    if (mode !== "reactive" || !ctaSelector) return;
    const cta = document.querySelector(ctaSelector);
    if (!cta) return;

    const onEnter = () => setGlowColor(GLOW_AMBER);
    const onLeave = () => setGlowColor(GLOW_EMERALD);
    cta.addEventListener("mouseenter", onEnter);
    cta.addEventListener("mouseleave", onLeave);
    return () => {
      cta.removeEventListener("mouseenter", onEnter);
      cta.removeEventListener("mouseleave", onLeave);
    };
  }, [mode, ctaSelector]);

  const isReactive = mode === "reactive";

  return (
    <div
      ref={containerRef}
      className={`scale-field ${isReactive ? "scale-field--reactive" : "scale-field--ambient"} ${className}`}
      aria-hidden="true"
      style={{
        "--glow-color": glowColor,
        "--glow-x": "50%",
        "--glow-y": "50%",
      }}
    />
  );
}
