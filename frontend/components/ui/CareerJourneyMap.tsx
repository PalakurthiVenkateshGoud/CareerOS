type CareerJourneyMapProps = {
  activeStage?: string;
};

export default function CareerJourneyMap({
  activeStage = "upload",
}: CareerJourneyMapProps) {
  const stages = [
    "upload",
    "target",
    "skills",
    "roadmap",
    "interview",
  ];

  return (
    <div
      style={{
        padding: "24px",
        border: "1px solid #e2e8f0",
        borderRadius: "12px",
        background: "#ffffff",
      }}
    >
      <h3 style={{ marginBottom: "16px", fontWeight: "bold" }}>
        Career Journey
      </h3>

      <div
        style={{
          display: "flex",
          gap: "12px",
          flexWrap: "wrap",
        }}
      >
        {stages.map((stage) => (
          <div
            key={stage}
            style={{
              padding: "8px 12px",
              borderRadius: "8px",
              background:
                stage === activeStage ? "#2563eb" : "#e5e7eb",
              color:
                stage === activeStage ? "#ffffff" : "#111827",
            }}
          >
            {stage}
          </div>
        ))}
      </div>
    </div>
  );
}