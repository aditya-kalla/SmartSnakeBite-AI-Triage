import React, { useState, useEffect, useRef } from "react";
import ResultCard from "./ResultCard.jsx";
import FirstAidPanel from "./FirstAidPanel.jsx";
import { speakSummary, speakText } from "../api.js";

/**
 * ReportModal — a slide-over panel (from the right) that wraps ResultCard
 * and the emergency First Aid & Bite Timer checklist.
 * Props:
 *   open: boolean — whether the modal is visible
 *   onClose: () => void — callback to dismiss
 *   entry: { transcript, am1, am2, am3, language, id, time } — the case data
 *   initialTab: string — which tab to show by default ("report" or "firstAid")
 */
export default function ReportModal({ open, onClose, entry, initialTab = "report" }) {
  const panelRef = useRef(null);
  const audioRef = useRef(null);
  const abortControllerRef = useRef(null);
  const [speaking, setSpeaking] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(initialTab);

  // Sync activeTab when modal opens or initialTab changes
  useEffect(() => {
    if (open) {
      setActiveTab(entry ? initialTab : "firstAid");
    }
  }, [open, initialTab, entry]);

  // Close on Escape key
  useEffect(() => {
    if (!open) return;
    const handleKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [open, onClose]);

  // Prevent body scroll when open and clean up audio on close
  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      setLoading(false);
      setSpeaking(false);
    }
    return () => {
      document.body.style.overflow = "";
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, [open]);

  if (!open) return null;

  async function handleSpeakToggle() {
    if (!entry) return;

    if (speaking) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      setSpeaking(false);
      return;
    }

    if (loading) {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }
      setLoading(false);
      return;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setLoading(true);
    setSpeaking(false);

    // Unlock browser autoplay restrictions by creating audio synchronously during click
    const audio = new Audio();
    audioRef.current = audio;
    try {
      audio.src = "data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA";
      audio.volume = 0.01;
      audio.play().catch(() => {});
    } catch (e) {}

    try {
      const am2Severity = entry.am2?.severity_class || entry.am2?.severity || entry.am1?.severity || "MODERATE";
      const antivenomRequired = !!entry.am2?.antivenom_required;
      const lang = (entry.language === "auto" || !entry.language) ? "en" : entry.language;

      const audioBlob = await speakSummary(am2Severity, antivenomRequired, lang, controller.signal);

      if (controller.signal.aborted) return;

      const url = URL.createObjectURL(audioBlob);
      if (audioRef.current) {
        audioRef.current.src = url;
        audioRef.current.volume = 1.0;
        audioRef.current.loop = true;

        setLoading(false);
        setSpeaking(true);
        const playPromise = audioRef.current.play();
        if (playPromise !== undefined) {
          playPromise.catch((err) => {
            console.error("Audio playback error:", err);
            setSpeaking(false);
            audioRef.current = null;
          });
        }
      }
    } catch (err) {
      if (err.name === "AbortError") {
        console.log("TTS request aborted");
      } else {
        console.error("Speak error:", err);
      }
      setLoading(false);
      setSpeaking(false);
      audioRef.current = null;
    } finally {
      if (abortControllerRef.current === controller) {
        abortControllerRef.current = null;
      }
    }
  }

  return (
    <div className="report-modal__backdrop" onClick={onClose}>
      <div
        ref={panelRef}
        className="report-modal__panel"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Clinical Report & First Aid"
      >
        <div className="report-modal__header">
          <div>
            <h2 className="report-modal__title">
              {activeTab === "firstAid" ? "Emergency First Aid & Timer" : "Clinical Report"}
            </h2>
            {entry?.id && (
              <span className="report-modal__case-id">
                CASE #{entry.id} · {entry.time || "—"} · {entry.language?.toUpperCase() || "—"}
              </span>
            )}
          </div>
          <button
            className="report-modal__close"
            onClick={onClose}
            aria-label="Close report"
          >
            ×
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="report-modal__tab-bar">
          <button
            type="button"
            className={`report-modal__tab-btn ${activeTab === "firstAid" ? "active" : ""}`}
            onClick={() => setActiveTab("firstAid")}
          >
            🚨 First Aid &amp; Bite Timer
          </button>
          <button
            type="button"
            className={`report-modal__tab-btn ${activeTab === "report" ? "active" : ""}`}
            onClick={() => {
              if (entry) setActiveTab("report");
            }}
            disabled={!entry}
            title={!entry ? "Run diagnosis first to view clinical report" : ""}
            style={{ opacity: !entry ? 0.5 : 1, cursor: !entry ? "not-allowed" : "pointer" }}
          >
            📋 Diagnosis Report {!entry && "(Pending)"}
          </button>
        </div>

        <div className="report-modal__body">
          {activeTab === "firstAid" ? (
            <FirstAidPanel />
          ) : (
            <>
              <div className="report-modal__top-actions">
                <button
                  type="button"
                  className={`report-modal__speak-btn ${speaking ? "speaking" : ""} ${loading ? "loading" : ""}`}
                  onClick={handleSpeakToggle}
                  disabled={loading}
                >
                  {loading ? "⏳ Preparing audio..." : speaking ? "⏹ Stop Reading" : "🔊 Read Report Aloud"}
                </button>
              </div>
              {entry && (
                <ResultCard
                  transcript={entry.transcript}
                  am1={entry.am1}
                  am2={entry.am2}
                  am3={entry.am3}
                  language={entry.language}
                />
              )}
            </>
          )}
        </div>

        {entry && (
          <div className="report-modal__footer">
            <a
              href={`/case/${entry.id}`}
              className="report-modal__fullview-link"
            >
              Open full case view →
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
