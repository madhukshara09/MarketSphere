import pandas as pd


# Features required by each MarketSphere ML module

SEGMENTATION_FEATURES = [
    "Income",
    "Age",
    "Total_Spending",
    "NumWebPurchases",
    "NumStorePurchases",
    "NumCatalogPurchases",
    "Recency",
]

CLV_FEATURES = [
    "Income",
    "Age",
    "Recency",
    "NumWebPurchases",
    "NumStorePurchases",
    "NumCatalogPurchases",
    "NumDealsPurchases",
    "NumWebVisitsMonth",
    "Kidhome",
    "Teenhome",
]

CAMPAIGN_FEATURES = [
    "Income",
    "Age",
    "Recency",
    "Kidhome",
    "Teenhome",
    "NumWebPurchases",
    "NumCatalogPurchases",
    "NumStorePurchases",
    "NumWebVisitsMonth",
    "NumDealsPurchases",
    "Total_Spending",
    "Total_Purchases",
]


def validate_columns(df: pd.DataFrame, required_columns: list[str]) -> dict:
    """
    Check whether a dataset contains all required columns.
    """

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    return {
        "valid": len(missing_columns) == 0,
        "missing_columns": missing_columns,
        "available_columns": list(df.columns),
    }


def validate_for_segmentation(df: pd.DataFrame) -> dict:
    """Validate dataset for Customer Segmentation."""

    return validate_columns(df, SEGMENTATION_FEATURES)


def validate_for_clv(df: pd.DataFrame) -> dict:
    """Validate dataset for CLV Prediction."""

    return validate_columns(df, CLV_FEATURES)


def validate_for_campaign(df: pd.DataFrame) -> dict:
    """Validate dataset for Campaign Response Prediction."""

    return validate_columns(df, CAMPAIGN_FEATURES)


def load_csv(file) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.

    `file` can be a Streamlit UploadedFile or a normal file path.
    """

    try:
        df = pd.read_csv(file)
    except Exception as e:
        raise ValueError(f"Unable to read CSV file: {e}")

    if df.empty:
        raise ValueError("The uploaded CSV is empty.")

    # Remove completely empty rows
    df = df.dropna(how="all")

    return df