import React from "react";

export default function About() {
  return (
    <div className="about-page">
      <div className="workspace-header">
        <h1>Clinical Methodology</h1>
        <p className="text-muted">Understanding the SmartSnakebite reasoning pipeline.</p>
      </div>

      <div className="content-container" style={{ background: 'var(--paper-raised)', padding: '2rem', border: '1px solid var(--line-strong)', borderRadius: '4px', maxWidth: '800px' }}>
        
        <h2 style={{ color: 'var(--clinical-teal)' }}>Core Objective</h2>
        <p>
          In rural Andhra Pradesh and Telangana, the delay between a venomous snakebite and the administration of antivenom is the primary driver of mortality. SmartSnakebite is designed to bridge the gap between initial symptoms and hospital admission.
        </p>

        <h3 style={{ marginTop: '2rem' }}>The "Big Four" Species</h3>
        <p>
          Our reasoning engine specifically targets the four most medically significant venomous snakes in the Indian subcontinent:
        </p>
        <ul style={{ lineHeight: '1.8' }}>
          <li><strong>Indian Cobra (Naja naja)</strong> - Neurotoxic and locally necrotizing.</li>
          <li><strong>Common Krait (Bungarus caeruleus)</strong> - Highly neurotoxic, often bites at night indoors.</li>
          <li><strong>Russell's Viper (Daboia russelii)</strong> - Hemotoxic, causing severe coagulopathy and acute kidney injury.</li>
          <li><strong>Saw-scaled Viper (Echis carinatus)</strong> - Hemotoxic, causing local pain and bleeding disorders.</li>
        </ul>

        <h3 style={{ marginTop: '2rem' }}>Reasoning Pipeline</h3>
        <div style={{ paddingLeft: '1rem', borderLeft: '3px solid var(--clinical-teal-light)' }}>
          <p><strong>A-M1 (Symptom Classification):</strong> Maps raw voice transcriptions to standardized venom typologies (Neurotoxic, Hemotoxic, Cytotoxic).</p>
          <p><strong>A-M3 (Safety Check):</strong> Identifies dangerous first-aid practices such as tourniquets or incision and suction, generating critical warnings to prevent further harm.</p>
          <p><strong>A-M2 (Clinical Decision):</strong> The core engine that evaluates symptom presentation against regional epidemiological data, time of day, and season to produce a species probability matrix, mortality risk, and antivenom requirement.</p>
        </div>

        <h3 style={{ marginTop: '2rem' }}>Languages Supported</h3>
        <p>
          The system's ASR (Automatic Speech Recognition) automatically detects and transcribes Telugu, Hindi, Tamil, Kannada, and English, allowing patients and rural health workers to describe symptoms naturally.
        </p>

      </div>
    </div>
  );
}
