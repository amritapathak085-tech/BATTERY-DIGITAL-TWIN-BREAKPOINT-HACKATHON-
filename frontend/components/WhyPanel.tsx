import { ExplanationResponse } from "@/lib/types";

export default function WhyPanel({
  explanation,
}: {
  explanation: ExplanationResponse;
}) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">EXPLAINABLE AI</span>
          <h3>Why is this battery degrading?</h3>
        </div>
      </div>

      <div className="reason-list">
        {explanation.reasons.map((reason, index) => (
          <div className="reason" key={reason.feature}>
            <div className="reason-number">
              {index + 1}
            </div>

            <div className="reason-content">
              <div className="reason-title">
                {reason.feature}

                <span>
                  {Math.round(reason.impact * 100)}%
                </span>
              </div>

              <p>{reason.plain_english}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}