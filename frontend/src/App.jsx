import React, { useState, useEffect, createContext } from "react";
import { Routes, Route, Link, NavLink, Navigate, useLocation } from "react-router-dom";
import useAutoContext from "./useAutoContext.js";
import { getCases, createCase, updateCase } from "./api.js";

import Landing from "./pages/Landing.jsx";
import Triage from "./pages/Triage.jsx";
import CaseView from "./pages/CaseView.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import About from "./pages/About.jsx";
import Guide from "./pages/Guide.jsx";
import Settings from "./pages/Settings.jsx";

export const AppContext = createContext();

const INITIAL_CASES = [
  {
    id: 10482,
    time: "10:42 AM",
    transcript: "Patient bitten on ankle 2 hours ago while working in paddy field. Severe ptosis, difficulty swallowing, respiratory distress. Tourniquet applied above knee.",
    language: "en",
    venomType: "Neurotoxic",
    severity: "CRITICAL",
    status: "open",
    am1: { venom_type: "Neurotoxic", severity: "CRITICAL" },
    am2: {
      severity: "CRITICAL",
      severity_class: "CRITICAL",
      top_species: ["Common Krait (Bungarus caeruleus)", "Spectacled Cobra (Naja naja)"],
      mortality_risk: "High (75%)",
      antivenom_required: true,
      referral_priority: "IMMEDIATE (ICU / Ventilator Capable)"
    },
    am3: {
      primary_corrective_message: "Remove tourniquet immediately and transport to ICU facility."
    }
  },
  {
    id: 10481,
    time: "09:15 AM",
    transcript: "Saw viper in plantation. Severe swelling progressing past knee, continuous oozing from puncture wounds. Patient conscious, blood pressure dropping.",
    language: "kn",
    venomType: "Hemotoxic",
    severity: "HIGH",
    status: "open",
    am1: { venom_type: "Hemotoxic", severity: "HIGH" },
    am2: {
      severity: "HIGH",
      severity_class: "HIGH",
      top_species: ["Russell's Viper (Daboia russelii)"],
      mortality_risk: "Moderate (45%)",
      antivenom_required: true,
      referral_priority: "URGENT (District Hospital / Blood Bank)"
    },
    am3: {
      primary_corrective_message: "Do not attempt incision. Maintain limb at heart level during transport."
    }
  },
  {
    id: 10480,
    time: "08:30 AM",
    transcript: "Bitten on hand while clearing dry firewood. Mild localized pain and swelling around bite site. No systemic symptoms, coagulation normal.",
    language: "te",
    venomType: "Cytotoxic",
    severity: "MODERATE",
    status: "open",
    am1: { venom_type: "Cytotoxic", severity: "MODERATE" },
    am2: {
      severity: "MODERATE",
      severity_class: "MODERATE",
      top_species: ["Saw-scaled Viper (Echis carinatus)", "Bamboo Pit Viper (Trimeresurus gramineus)"],
      mortality_risk: "Low (<10%)",
      antivenom_required: false,
      referral_priority: "STANDARD (Primary Health Centre Observation)"
    },
    am3: {
      primary_corrective_message: "Keep patient calm. Observe for 24 hours for coagulopathy."
    }
  },
  {
    id: 10479,
    time: "07:10 AM",
    transcript: "Quick bite by non-venomous rat snake near barn. Slight scratch, no edema, patient asymptomatic after 4 hours observation.",
    language: "ta",
    venomType: "Non-venomous",
    severity: "LOW",
    status: "resolved",
    am1: { venom_type: "Non-venomous", severity: "LOW" },
    am2: {
      severity: "LOW",
      severity_class: "LOW",
      top_species: ["Indian Rat Snake (Ptyas mucosa)"],
      mortality_risk: "Negligible",
      antivenom_required: false,
      referral_priority: "DISCHARGE (Local Wound Care & Tetanus)"
    },
    am3: {
      primary_corrective_message: "Clean wound with antiseptic. Administer tetanus toxoid booster if needed."
    }
  }
];

export default function App() {
  const autoContext = useAutoContext();
  const [overrides, setOverrides] = useState({});
  const [current, setCurrent] = useState(null);
  const [log, setLog] = useState([]);

  useEffect(() => {
    getCases().then(setLog).catch(e => console.error("Failed to load cases from backend:", e));
  }, []);
  
  // Settings state
  const [defaultTTSLang, setDefaultTTSLang] = useState("en");
  const [autoDetectContext, setAutoDetectContext] = useState(true);
  const [alwaysExpandOverrides, setAlwaysExpandOverrides] = useState(false);

  const location = useLocation();

  const effectiveLanguage = overrides.language || "auto";
  const effectiveDistrict = overrides.district || "Unknown";
  const effectiveTime = overrides.time_of_day || autoContext.time_of_day;
  const effectiveSeason = overrides.season || autoContext.season;

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
        const updated = { ...e, transcript: newTranscript ?? e.transcript, editing: false };
        updateCase(id, updated).catch(err => console.error(err));
        return updated;
      })
    );
  }

  function updateCaseStatus(ids, newStatus) {
    const idSet = new Set(Array.isArray(ids) ? ids : [ids]);
    setLog((prev) =>
      prev.map((e) => {
        if (idSet.has(e.id)) {
          const updated = { ...e, status: newStatus };
          updateCase(e.id, updated).catch(err => console.error(err));
          return updated;
        }
        return e;
      })
    );
  }

  function deleteCases(ids) {
    const idSet = new Set(Array.isArray(ids) ? ids : [ids]);
    // NOTE: Need backend DELETE endpoint for true deletion. For now just removing from state.
    // fetch(`${BASE}/cases/${id}`, {method: 'DELETE'})
    setLog((prev) => prev.filter((e) => !idSet.has(e.id)));
  }

  function reloadSampleCases() {
    // Deprecated with real backend database
  }

  const contextValue = {
    autoContext,
    overrides,
    setOverrides,
    current,
    setCurrent,
    log,
    setLog,
    effectiveLanguage,
    effectiveDistrict,
    effectiveTime,
    effectiveSeason,
    handleClose,
    handleEdit,
    updateCaseStatus,
    deleteCases,
    reloadSampleCases,
    defaultTTSLang,
    setDefaultTTSLang,
    autoDetectContext,
    setAutoDetectContext,
    alwaysExpandOverrides,
    setAlwaysExpandOverrides
  };

  const isLanding = location.pathname === "/";

  return (
    <AppContext.Provider value={contextValue}>
      <div className="app-container">
        {/* Global Floating Pill Nav matching Landing Page */}
        <nav className="landing-nav" role="navigation" aria-label="Main navigation">
          <Link to="/" className="landing-nav__brand" aria-label="SmartSnakebite home">
            SmartSnakebite
          </Link>
          <div className="landing-nav__links">
            <NavLink to="/diagnose" className="landing-nav__link">Diagnose</NavLink>
            <NavLink to="/dashboard" className="landing-nav__link">Dashboard</NavLink>
            <a href="/assets/SmartSnakebite_KnowledgeBase.html" className="landing-nav__link">Guide</a>
            <NavLink to="/about" className="landing-nav__link">About</NavLink>
            <NavLink to="/settings" className="landing-nav__link">Settings</NavLink>
          </div>
          <Link to="/diagnose" className="landing-nav__cta">Start Diagnosis</Link>
        </nav>

        {isLanding ? (
          <Routes>
            <Route path="/" element={<Landing />} />
          </Routes>
        ) : (
          <main className="main-content">
            <Routes>
              <Route path="/diagnose" element={<Triage />} />
              <Route path="/triage" element={<Navigate to="/diagnose" replace />} />
              <Route path="/case/:id" element={<CaseView />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/about" element={<About />} />
              <Route path="/guide" element={<Guide />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        )}
      </div>
    </AppContext.Provider>
  );
}
