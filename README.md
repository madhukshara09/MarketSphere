# MarketSphere

MarketSphere is a marketing-decision intelligence application developed for a
Data Science Project-Based Learning course. It segments customers, estimates a
CLV proxy, predicts campaign response, and ranks customers by marketing
opportunity.

## Run the application

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-runtime.txt
python train_models.py
streamlit run app.py
```

Open the local URL displayed by Streamlit and sign in with `admin / admin123`
or `analyst / analyst123`.

## Data and models

The project uses `data/processed/marketing_campaign_cleaned.csv`. Running
`train_models.py` trains and saves:

- K-Means customer segmentation model and scaler
- Gradient Boosting CLV-proxy regressor
- Random Forest campaign-response classifier

Evaluation summaries are written to `reports/`. The CLV target is a documented
proxy based on spending, purchase count, and recency; it is not an observed
future-revenue label.
