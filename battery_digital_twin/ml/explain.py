import pandas as pd
import shap


def explain_prediction(model, feature_row, top_k=4):
    """
    Generate SHAP-based explanations for a battery prediction.

    Parameters
    ----------
    model : trained tree-based model
        The trained XGBoost model.

    feature_row : dict or pandas.DataFrame
        Feature values for one battery prediction.

    top_k : int
        Number of most important features to return.

    Returns
    -------
    dict
        {
            "reasons": [
                {
                    "feature": str,
                    "impact": float,
                    "plain_english": str
                }
            ]
        }
    """

    # Convert dictionary input into a DataFrame
    if isinstance(feature_row, dict):
        X = pd.DataFrame([feature_row])
    elif isinstance(feature_row, pd.DataFrame):
        X = feature_row.copy()
    else:
        raise TypeError("feature_row must be a dictionary or pandas DataFrame")

    # Create SHAP explainer for the tree-based model
    explainer = shap.TreeExplainer(model)

    # Calculate SHAP values
    shap_values = explainer.shap_values(X)

    # Handle different SHAP output formats
    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    shap_values = shap_values[0]

    # Rank features by absolute SHAP impact
    feature_importance = sorted(
        zip(X.columns, shap_values, X.iloc[0].values),
        key=lambda item: abs(item[1]),
        reverse=True
    )

    reasons = []

    for feature, impact, value in feature_importance[:top_k]:

        impact = float(impact)

        # Convert technical feature names into readable names
        readable_feature = feature.replace("_", " ")

        # Generate plain-English explanation
        if feature in ["temperature", "avg_temperature", "temperature_avg"]:
            if impact < 0:
                sentence = (
                    f"High average temperature ({value:.1f}°C) "
                    "is accelerating battery degradation."
                )
            else:
                sentence = (
                    f"Temperature conditions ({value:.1f}°C) "
                    "are currently having a positive effect on predicted battery life."
                )

        elif feature in ["fast_charge_freq", "fast_charge_ratio"]:
            if impact < 0:
                sentence = (
                    f"Frequent fast charging ({value:.1f}) "
                    "is contributing to faster battery degradation."
                )
            else:
                sentence = (
                    f"Fast-charging behaviour ({value:.1f}) "
                    "is currently having a limited negative effect on predicted life."
                )

        elif feature in ["cycle_count", "cumulative_cycle_count"]:
            if impact < 0:
                sentence = (
                    f"High cycle usage ({value:.1f}) "
                    "is reducing the battery's predicted remaining life."
                )
            else:
                sentence = (
                    f"Cycle usage ({value:.1f}) "
                    "is currently favourable for predicted battery life."
                )

        elif feature in ["depth_of_discharge", "dod"]:
            if impact < 0:
                sentence = (
                    f"Deep discharge behaviour ({value:.1f}) "
                    "is contributing to battery degradation."
                )
            else:
                sentence = (
                    f"Depth of discharge ({value:.1f}) "
                    "is currently having a positive effect on predicted battery life."
                )

        elif feature in ["voltage"]:
            if impact < 0:
                sentence = (
                    f"Voltage behaviour ({value:.2f}V) "
                    "is negatively affecting the predicted battery life."
                )
            else:
                sentence = (
                    f"Voltage behaviour ({value:.2f}V) "
                    "is supporting the predicted battery life."
                )

        elif feature in ["capacity_pct"]:
            if impact < 0:
                sentence = (
                    f"Reduced capacity ({value:.1f}%) "
                    "is contributing to lower predicted battery health."
                )
            else:
                sentence = (
                    f"Current capacity ({value:.1f}%) "
                    "is supporting the predicted battery health."
                )

        else:
            if impact < 0:
                sentence = (
                    f"Higher {readable_feature} ({value:.2f}) "
                    "is negatively affecting predicted battery life."
                )
            else:
                sentence = (
                    f"{readable_feature.capitalize()} ({value:.2f}) "
                    "is positively affecting predicted battery life."
                )

        reasons.append(
            {
                "feature": feature,
                "impact": round(impact, 4),
                "plain_english": sentence,
            }
        )

    return {"reasons": reasons}