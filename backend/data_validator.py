from datetime import date

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
        df = pd.read_csv(file, sep=None, engine="python")
    except Exception as e:
        raise ValueError(f"Unable to read CSV file: {e}")

    if df.empty:
        raise ValueError("The uploaded CSV is empty.")

    # Remove completely empty rows
    df = df.dropna(how="all")

    return df


def prepare_marketing_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Convert a common raw marketing-campaign CSV to model-ready features.

    The saved models require a known set of behavioural and demographic
    columns. This adapter accepts either the already-processed project schema
    or the original marketing-campaign schema that contains ``Mnt*`` and
    ``Num*Purchases`` columns.
    """
    result = df.copy()
    # A CSV opened with pandas' comma default may arrive as one semicolon-
    # separated column. Recover it so direct API callers are supported too.
    if len(result.columns) == 1 and ";" in str(result.columns[0]):
        header = str(result.columns[0]).split(";")
        result = result.iloc[:, 0].astype(str).str.split(";", expand=True)
        result.columns = header

    if "Age" not in result and "Year_Birth" in result:
        result["Age"] = date.today().year - pd.to_numeric(result["Year_Birth"], errors="coerce")

    spend_columns = [
        "MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
        "MntSweetProducts", "MntGoldProds",
    ]
    if "Total_Spending" not in result and set(spend_columns).issubset(result.columns):
        result["Total_Spending"] = result[spend_columns].apply(pd.to_numeric, errors="coerce").sum(axis=1)

    purchase_columns = ["NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases"]
    if "Total_Purchases" not in result and set(purchase_columns).issubset(result.columns):
        result["Total_Purchases"] = result[purchase_columns].apply(pd.to_numeric, errors="coerce").sum(axis=1)

    required = sorted(set(SEGMENTATION_FEATURES + CLV_FEATURES + CAMPAIGN_FEATURES))
    missing = [column for column in required if column not in result.columns]
    if missing:
        raise ValueError(
            "This CSV cannot be scored because it is missing: " + ", ".join(missing)
            + ". Upload a dataset with the documented marketing feature columns."
        )

    for column in required:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    if result[required].isna().any().any():
        reference = pd.read_csv(
            pd.io.common.stringify_path(
                __import__("pathlib").Path(__file__).resolve().parents[1]
                / "data" / "processed" / "marketing_campaign_cleaned.csv"
            )
        )
        for column in required:
            result[column] = result[column].fillna(reference[column].median())

    return result
