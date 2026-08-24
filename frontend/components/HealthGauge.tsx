interface Props {
  value: number;
}

export default function HealthGauge({ value }: Props) {
  const rotation = -90 + (value / 100) * 180;

  return (
    <div className="gauge-wrapper">
      <div className="gauge">
        <div
          className="gauge-needle"
          style={{
            transform: `rotate(${rotation}deg)`,
          }}
        />

        <div className="gauge-center">
          <strong>{value}</strong>
          <span>BHI</span>
        </div>
      </div>

      <div className="gauge-labels">
        <span>0</span>
        <span>50</span>
        <span>100</span>
      </div>
    </div>
  );
}