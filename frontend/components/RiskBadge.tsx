interface Props {
  risk: number;
}

export default function RiskBadge({ risk }: Props) {
  let label = "LOW";
  let className = "risk-low";

  if (risk >= 70) {
    label = "HIGH";
    className = "risk-high";
  } else if (risk >= 40) {
    label = "MEDIUM";
    className = "risk-medium";
  }

  return (
    <span className={`risk-badge ${className}`}>
      {label} · {risk}%
    </span>
  );
}