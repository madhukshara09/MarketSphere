import os
import joblib
import pandas as pd

from .data_validator import (
    SEGMENTATION_FEATURES,
    CLV_FEATURES,
    CAMPAIGN_FEATURES,
    validate_for_segmentation,
    validate_for_clv,
    validate_for_campaign,
)


# Project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODELS_DIR = os.path.join(BASE_DIR, "models")

SEGMENTATION_MODEL_PATH = os.path.join(
    MODELS_DIR, "customer_segmentation_model.pkl"
)

SEGMENTATION_SCALER_PATH = os.path.join(
    MODELS_DIR, "customer_segmentation_scaler.pkl"
)

CLV_MODEL_PATH = os.path.join(
    MODELS_DIR, "clv_model.pkl"
)

CAMPAIGN_MODEL_PATH = os.path.join(
    MODELS_DIR, "campaign_response_model.pkl"
)


# Business-friendly segment names
SEGMENT_MAPPING = {
    0: "Low-Value Customers",
    1: "Loyal Customers",
    2: "Dormant Customers",
    3: "Premium VIP Customers",
}


def load_models():
    """Load all trained MarketSphere models."""

    segmentation_model = joblib.load(SEGMENTATION_MODEL_PATH)
    segmentation_scaler = joblib.load(SEGMENTATION_SCALER_PATH)
    clv_model = joblib.load(CLV_MODEL_PATH)
    campaign_model = joblib.load(CAMPAIGN_MODEL_PATH)

    return (
        segmentation_model,
        segmentation_scaler,
        clv_model,
        campaign_model,
    )


def run_segmentation(df):
    """Predict customer segments."""

    validation = validate_for_segmentation(df)

    if not validation["valid"]:
        raise ValueError(
            "Missing segmentation columns: "
            + ", ".join(validation["missing_columns"])
        )

    model, scaler, _, _ = load_models()

    X = df[SEGMENTATION_FEATURES]

    X_scaled = scaler.transform(X)

    clusters = model.predict(X_scaled)

    result = df.copy()

    result["Cluster"] = clusters
    result["Customer_Segment"] = [
        SEGMENT_MAPPING.get(int(cluster), "Unknown")
        for cluster in clusters
    ]

    return result


def run_clv_prediction(df):
    """Predict Customer Lifetime Value."""

    validation = validate_for_clv(df)

    if not validation["valid"]:
        raise ValueError(
            "Missing CLV columns: "
            + ", ".join(validation["missing_columns"])
        )

    _, _, model, _ = load_models()

    X = df[CLV_FEATURES]

    predictions = model.predict(X)

    result = df.copy()
    result["Predicted_CLV"] = predictions

    return result


def run_campaign_prediction(df):
    """Predict campaign response."""

    validation = validate_for_campaign(df)

    if not validation["valid"]:
        raise ValueError(
            "Missing campaign columns: "
            + ", ".join(validation["missing_columns"])
        )

    _, _, _, model = load_models()

    X = df[CAMPAIGN_FEATURES]

    probabilities = model.predict_proba(X)[:, 1]
    predictions = model.predict(X)

    result = df.copy()

    result["Response_Probability"] = probabilities
    result["Predicted_Response"] = predictions

    return result


def analyze_dataset(df):
    """
    Run all available MarketSphere ML models
    on the uploaded dataset.
    """

    result = run_segmentation(df)

    # Run CLV using the original dataframe
    clv_result = run_clv_prediction(result)

    # Run campaign prediction
    final_result = run_campaign_prediction(clv_result)

    return final_result