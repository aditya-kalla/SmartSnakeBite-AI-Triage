import React, { useEffect } from "react";

export default function Guide() {
  useEffect(() => {
    window.location.replace("/assets/SmartSnakebite_KnowledgeBase.html");
  }, []);

  return (
    <div className="guide-page" style={{ textAlign: "center", padding: "4rem 2rem" }}>
      <p style={{ color: "var(--clinical-teal)", fontSize: "1.2rem", fontWeight: 500 }}>
        Loading Species Knowledge Base...
      </p>
    </div>
  );
}
