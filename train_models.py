"""Train all MarketSphere models. Run: ``python train_models.py``."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, precision_recall_fscore_support, r2_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from backend.data_validator import CAMPAIGN_FEATURES, CLV_FEATURES, SEGMENTATION_FEATURES

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "processed" / "marketing_campaign_cleaned.csv"
MODELS_DIR, REPORTS_DIR = ROOT / "models", ROOT / "reports"


def build_clv_target(df: pd.DataFrame) -> pd.Series:
    """Project CLV proxy; replace with observed future value when available."""
    return df["Total_Spending"] * df["Total_Purchases"] * ((100 - df["Recency"]) / 100)


def train() -> None:
    MODELS_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_PATH)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(df[SEGMENTATION_FEATURES])
    segment_model = KMeans(n_clusters=4, random_state=42, n_init=20)
    clusters = segment_model.fit_predict(scaled)
    joblib.dump(scaler, MODELS_DIR / "customer_segmentation_scaler.pkl")
    joblib.dump(segment_model, MODELS_DIR / "customer_segmentation_model.pkl")
    profile = df.assign(Cluster=clusters).groupby("Cluster").agg(spending=("Total_Spending", "mean"), recency=("Recency", "mean"))
    ranked = profile.assign(value=profile.spending - profile.recency * profile.spending.max() / 100).sort_values("value")
    labels = ["Dormant Customers", "Low-Value Customers", "Loyal Customers", "Premium VIP Customers"]
    (MODELS_DIR / "segment_mapping.json").write_text(json.dumps({str(k): v for k, v in zip(ranked.index, labels)}, indent=2), encoding="utf-8")

    x_train, x_test, y_train, y_test = train_test_split(df[CLV_FEATURES], build_clv_target(df), test_size=0.2, random_state=42)
    clv_model = GradientBoostingRegressor(random_state=42).fit(x_train, y_train)
    clv_pred = clv_model.predict(x_test)
    joblib.dump(clv_model, MODELS_DIR / "clv_model.pkl")
    pd.DataFrame([{"Model": "Gradient Boosting Regressor", "MAE": mean_absolute_error(y_test, clv_pred), "R2": r2_score(y_test, clv_pred)}]).to_csv(REPORTS_DIR / "clv_model_comparison.csv", index=False)

    x_train, x_test, y_train, y_test = train_test_split(df[CAMPAIGN_FEATURES], df.Response, test_size=0.2, random_state=42, stratify=df.Response)
    campaign_model = RandomForestClassifier(n_estimators=500, max_depth=10, min_samples_split=5, class_weight="balanced", random_state=42).fit(x_train, y_train)
    probability = campaign_model.predict_proba(x_test)[:, 1]
    predicted = campaign_model.predict(x_test)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, predicted, average="binary", zero_division=0)
    joblib.dump(campaign_model, MODELS_DIR / "campaign_response_model.pkl")
    pd.DataFrame([{"Model": "Random Forest Classifier", "ROC_AUC": roc_auc_score(y_test, probability), "Precision": precision, "Recall": recall, "F1": f1}]).to_csv(REPORTS_DIR / "classification_model_comparison.csv", index=False)
    print("Training complete. Models and reports saved.")


if __name__ == "__main__":
    train()
