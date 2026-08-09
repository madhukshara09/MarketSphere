"""Generate the realistic mock customer dataset used across MarketSphere AI.

Run directly to regenerate:  python data/generate_mock_data.py
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
from faker import Faker

CUSTOMER_COUNT = 300
SEED = 2026

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(DATA_DIR, "customers.csv")

EDUCATION = ["High School", "Bachelor", "Master", "PhD"]
EDUCATION_WEIGHTS = [0.22, 0.42, 0.26, 0.10]
OCCUPATION = ["Student", "Employed", "Self-Employed", "Manager", "Retired"]
OCCUPATION_WEIGHTS = [0.10, 0.44, 0.18, 0.20, 0.08]
MARITAL = ["Single", "Married", "Divorced", "Widowed"]
MARITAL_WEIGHTS = [0.34, 0.46, 0.14, 0.06]
GENDER = ["Male", "Female", "Other"]
GENDER_WEIGHTS = [0.48, 0.48, 0.04]


def _segment_for(frequency: int, recency: int, spending: float) -> str:
    """Assign an RFM style segment label."""
    score = (frequency / 30) * 0.4 + (1 - min(recency / 365, 1)) * 0.35 + (spending / 100) * 0.25
    if score >= 0.70:
        return "Champions"
    if score >= 0.55:
        return "Loyal"
    if score >= 0.40:
        return "Potential"
    if score >= 0.25:
        return "At Risk"
    return "Hibernating"


def _recommendation_for(segment: str, probability: float) -> str:
    """Human readable next-best-action per customer."""
    mapping = {
        "Champions": "Enrol in premium loyalty tier",
        "Loyal": "Cross-sell complementary bundle",
        "Potential": "Send targeted upgrade offer",
        "At Risk": "Trigger win-back discount",
        "Hibernating": "Move to low-cost email nurture",
    }
    base = mapping[segment]
    if probability >= 0.75:
        return f"{base} - prioritise"
    if probability <= 0.25:
        return f"{base} - low priority"
    return base


def generate_customers(count: int = CUSTOMER_COUNT, seed: int = SEED) -> pd.DataFrame:
    """Build a realistic customer table with all required columns."""
    faker = Faker()
    Faker.seed(seed)
    rng = np.random.default_rng(seed)

    ages = np.clip(rng.normal(43, 13, count).round(), 18, 82).astype(int)
    incomes = np.clip(rng.lognormal(np.log(58_000), 0.45, count).round(-2), 18_000, 320_000)
    frequency = np.clip(rng.poisson(9, count) + rng.integers(0, 8, count), 1, 40)
    recency = np.clip(rng.exponential(74, count).round(), 1, 365).astype(int)
    spending = np.clip(rng.normal(55, 21, count).round(1), 1, 100)

    rows = []
    for i in range(count):
        segment = _segment_for(int(frequency[i]), int(recency[i]), float(spending[i]))
        probability = float(np.clip(
            0.16
            + (frequency[i] / 40) * 0.26
            + (1 - recency[i] / 365) * 0.24
            + (spending[i] / 100) * 0.20
            + (incomes[i] / 320_000) * 0.14
            + rng.normal(0, 0.05),
            0.02, 0.98,
        ))
        avg_order = 42 + incomes[i] / 1_400 + spending[i] * 1.6
        years = float(np.clip(5.5 - recency[i] / 120, 0.8, 7.0))
        clv = round(float(avg_order * frequency[i] * years * 0.72), 2)

        rows.append({
            "Customer_ID": f"MS-{100000 + i}",
            "Customer_Name": faker.name(),
            "Age": int(ages[i]),
            "Gender": rng.choice(GENDER, p=GENDER_WEIGHTS),
            "Income": int(incomes[i]),
            "Education": rng.choice(EDUCATION, p=EDUCATION_WEIGHTS),
            "Occupation": rng.choice(OCCUPATION, p=OCCUPATION_WEIGHTS),
            "Marital_Status": rng.choice(MARITAL, p=MARITAL_WEIGHTS),
            "Purchase_Frequency": int(frequency[i]),
            "Recency": int(recency[i]),
            "Spending": float(spending[i]),
            "Customer_Segment": segment,
            "Predicted_CLV": clv,
            "Response_Probability": round(probability, 3),
            "Recommendation": _recommendation_for(segment, probability),
        })

    return pd.DataFrame(rows)


def save_customers(frame: pd.DataFrame, path: str = OUTPUT_PATH) -> str:
    """Persist the generated dataset to CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    frame.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    dataset = generate_customers()
    location = save_customers(dataset)
    print(f"Generated {len(dataset)} customers -> {location}")
