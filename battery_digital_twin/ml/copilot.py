import os
from typing import Any

try:
    from groq import Groq
except ImportError:
    Groq = None


def _template_fallback(analysis: dict[str, Any]) -> dict[str, str]:
    """
    Fallback explanation when Groq is unavailable or the API call fails.
    """

    bhi = analysis.get("bhi")
    rul_days = analysis.get("rul_days")
    failure_risk = analysis.get("failure_risk_pct")
    reasons = analysis.get("reasons", [])

    if reasons:
        main_reason = reasons[0].get(
            "plain_english",
            "The model identified factors affecting battery health."
        )
    else:
        main_reason = "The model identified several factors affecting battery health."

    summary = (
        f"Battery health is currently {bhi}% with an estimated "
        f"remaining useful life of {rul_days} days and a "
        f"{failure_risk}% estimated failure risk."
    )

    recommendation = (
        f"The main factor currently affecting the battery is: {main_reason} "
        "Consider reducing the identified stress factor and continue monitoring "
        "battery health."
    )

    return {
        "summary": summary,
        "recommendation": recommendation
    }


def generate_copilot_response(analysis: dict[str, Any]) -> dict[str, str]:
    """
    Generate a battery-health summary and recommendation.

    The LLM receives structured ML outputs only:
    - BHI
    - RUL
    - failure risk
    - SHAP reasons

    Raw telemetry is NOT sent to the LLM.
    """

    required_fields = [
        "bhi",
        "rul_days",
        "failure_risk_pct",
        "reasons"
    ]

    for field in required_fields:
        if field not in analysis:
            raise ValueError(f"Missing required field: {field}")

    api_key = os.getenv("GROQ_API_KEY")

    # If Groq is not configured, use deterministic fallback.
    if not api_key or Groq is None:
        return _template_fallback(analysis)

    client = Groq(api_key=api_key)

    prompt = f"""
You are a battery digital twin assistant.

Explain the battery condition clearly to a non-expert.

Use ONLY the structured information provided below.
Do not invent telemetry values, causes, or statistics.

Battery Health Index: {analysis["bhi"]}
Estimated Remaining Useful Life: {analysis["rul_days"]} days
Estimated Failure Risk: {analysis["failure_risk_pct"]}%

Model-derived reasons:
{analysis["reasons"]}

Return exactly two sections:

SUMMARY:
A concise explanation of the current battery condition.

RECOMMENDATION:
One practical recommendation based only on the model-derived reasons.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise battery health assistant. "
                        "Never invent information."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=300,
        )

        content = response.choices[0].message.content.strip()

        # Parse the two expected sections.
        summary = content
        recommendation = ""

        if "RECOMMENDATION:" in content:
            summary_part, recommendation = content.split(
                "RECOMMENDATION:",
                1
            )

            summary = summary_part.replace("SUMMARY:", "").strip()
            recommendation = recommendation.strip()

        return {
            "summary": summary,
            "recommendation": recommendation
        }

    except Exception:
        # Never let an LLM/API failure break the battery dashboard.
        return _template_fallback(analysis)