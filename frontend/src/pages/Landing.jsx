import React, { useRef } from "react";
import { Link } from "react-router-dom";
import ScaleField from "../components/ScaleField.jsx";
import ScrollCrawlSnake from "../components/ScrollCrawlSnake.jsx";

const LANGUAGES = [
  { label: "తెలుగు",   lang: "Telugu" },
  { label: "हिंदी",      lang: "Hindi" },
  { label: "தமிழ்",    lang: "Tamil" },
  { label: "ಕನ್ನಡ",    lang: "Kannada" },
  { label: "English", lang: "English" },
];

const ARC_POSITIONS = [
  { x: "-42%", y: "18px",  rotate: -4 },
  { x: "-21%", y: "-6px",  rotate: -2 },
  { x: "0%",   y: "-14px", rotate: 0  },
  { x: "21%",  y: "-6px",  rotate: 2  },
  { x: "42%",  y: "18px",  rotate: 4  },
];

export default function Landing() {
  return (
    <div className="landing">
      {/* ─── HERO ─── */}
      <section className="hero" aria-labelledby="hero-headline">
        {/* Scale-texture background: mouse-reactive glow */}
        <ScaleField
          mode="reactive"
          ctaSelector=".hero .btn-pill--solid"
          className="hero__scale-bg"
        />

        <div className="hero__content">
          <div className="lang-arc" aria-label="Supported languages">
            {LANGUAGES.map((l, i) => (
              <span
                key={l.lang}
                className="lang-badge"
                style={{
                  "--arc-x": ARC_POSITIONS[i].x,
                  "--arc-y": ARC_POSITIONS[i].y,
                  "--arc-rotate": `${ARC_POSITIONS[i].rotate}deg`,
                }}
                title={l.lang}
              >
                {l.label}
              </span>
            ))}
          </div>

          <h1 id="hero-headline" className="hero__headline">
            Voice-First Snakebite Diagnosis,{" "}
            <br className="hero-br" />
            Built for the <em>Last</em> Mile
          </h1>

          <p className="hero__sub">
            SmartSnakebite runs entirely offline on a phone, turning a patient's
            spoken symptoms into a clinically reasoned severity report — in Telugu,
            Hindi, Tamil, Kannada, or English.
          </p>

          <div className="hero__actions">
            <Link to="/diagnose" className="btn-pill btn-pill--solid">
              Start Diagnosis
            </Link>
            <Link to="/about" className="btn-pill btn-pill--ghost">
              Read Methodology
            </Link>
          </div>
        </div>

        {/* Scroll-synced bamboo viper crawl replaces static snake image */}
        <ScrollCrawlSnake
          sequenceFolder="bamboo_viper"
          frameCount={100}
          className="hero-snake-wrap"
          alt="Bamboo Viper crawl animation synced to scroll"
        />
      </section>

      {/* ─── WHY THIS MATTERS ─── */}
      <section className="why-section" aria-labelledby="why-heading">
        <ScaleField mode="ambient" className="section__scale-bg" />

        <div className="why-section__inner">
          <div className="why-stat" aria-label="46,000 deaths per year">
            <span className="why-stat__num">46,000</span>
            <span className="why-stat__caption">
              estimated snakebite deaths per year in India alone
            </span>
          </div>
          <div className="why-text">
            <h2 id="why-heading" className="why-text__heading">
              The gap that kills
            </h2>
            <p>
              Krait and cobra bites are frequently fatal not because antivenom
              doesn't exist, but because of <strong>delayed recognition</strong>.
              Families lose critical hours visiting traditional healers before
              reaching a hospital — by which time neurotoxic or hemotoxic damage
              is irreversible.
            </p>
            <p>
              SmartSnakebite exists to close that gap: giving a rural health
              worker or family member an immediate, spoken-language clinical
              assessment that says <em>"go to hospital now"</em> — before it's
              too late.
            </p>
          </div>
        </div>

        <ScrollCrawlSnake
          sequenceFolder="viper"
          frameCount={68}
          className="section-snake section-snake--why"
          alt="Russell's Viper crawl animation"
        />
      </section>

      {/* ─── HOW IT WORKS ─── */}
      <section className="steps-section" aria-labelledby="steps-heading">
        <ScaleField mode="ambient" className="section__scale-bg" />

        <h2 id="steps-heading" className="steps-section__heading">How It Works</h2>
        <div className="steps-grid">
          <article className="step-card">
            <span className="step-card__num">01</span>
            <h3 className="step-card__title">Speak naturally</h3>
            <p className="step-card__body">
              Describe the bite and symptoms in your own language — Telugu, Hindi,
              Tamil, Kannada, or English. No forms, no typing.
            </p>
          </article>
          <article className="step-card">
            <span className="step-card__num">02</span>
            <h3 className="step-card__title">Understood instantly</h3>
            <p className="step-card__body">
              Offline AI transcribes your voice and extracts symptoms,
              urgency signals, and any harmful first-aid practices.
            </p>
          </article>
          <article className="step-card">
            <span className="step-card__num">03</span>
            <h3 className="step-card__title">Clinically reasoned</h3>
            <p className="step-card__body">
              Your description is cross-checked against species data, district
              epidemiology, time of day, and season for a real risk assessment.
            </p>
          </article>
          <article className="step-card">
            <span className="step-card__num">04</span>
            <h3 className="step-card__title">Hospital-ready report</h3>
            <p className="step-card__body">
              A clear spoken and written severity report — antivenom guidance,
              referral priority — you can bring straight to a doctor.
            </p>
          </article>
        </div>

        <ScrollCrawlSnake
          sequenceFolder="krait"
          frameCount={100}
          className="section-snake section-snake--steps"
          alt="Common Krait crawl animation"
        />
      </section>

      {/* ─── CLOSING CTA ─── */}
      <section className="cta-band" aria-label="Explore the species guide">
        <div className="cta-band__inner">
          <div className="cta-band__text">
            <h2 className="cta-band__heading">
              Know the species. Recognise the symptoms. Save a life.
            </h2>
            <p className="cta-band__sub">
              The "Big Four" venomous snakes of India — what they look like, how their
              bites present clinically, and what to do (and what <em>not</em> to do)
              in the critical first hour.
            </p>
            <a href="/assets/SmartSnakebite_KnowledgeBase.html" className="btn-pill btn-pill--light">
              Explore the Species Guide
            </a>
          </div>
          <div className="cta-band__visual">
            <img
              src="/assets/gifs/medicine_in_hand.gif"
              alt="Medical assistance and antivenom administration"
              className="cta-band__gif"
            />
          </div>
        </div>
      </section>
    </div>
  );
}
