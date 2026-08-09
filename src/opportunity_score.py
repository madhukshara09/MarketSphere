def calculate_score(row):

    score = (

        row["Income"]*0.20 +

        row["Total_Spending"]*0.35 +

        row["Total_Purchases"]*0.25 +

        (100-row["Recency"])*0.20

    )

    return score
df["Opportunity_Score"] = df.apply(
    calculate_score,
    axis=1
)
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()

df["Opportunity_Score"] = scaler.fit_transform(
    df[["Opportunity_Score"]]
)*100