# MarketSphere AI

Polished Streamlit interface for the root MarketSphere ML pipeline. The interface displays
predictions from the trained segmentation, CLV-proxy and campaign-response models stored in
the repository root.

## Quick start

```bash
cd ../..
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements-runtime.txt
python train_models.py
streamlit run app.py
```

Open http://localhost:8501

### Demonstration accounts

| Username | Password    |
| -------- | ----------- |
| admin    | admin123    |
| analyst  | analyst123  |

## Project structure

```
MarketSphereAI/
  app.py                      Auth gate, custom sidebar, page router
  requirements.txt
  README.md
  assets/
    style.css                 Complete visual override of Streamlit
    logo.png
    banner.png
  pages/
    Dashboard.py
    Customer_Segmentation.py
    Response_Prediction.py
    CLV_Prediction.py
    Decision_Impact.py
    Reports.py
    Settings.py
  utils/
    components.py             Metric cards, section headers, tables, badges, sidebar, callouts
    charts.py                 Plotly factory: pie, donut, bar, line, area, scatter, gauge, histogram
    helpers.py                Formatting, mock data access, heuristic prediction logic
  data/
    generate_mock_data.py     300 realistic customers via Faker + NumPy
    customers.csv             Generated on first run
  images/
```

## Pages

- **Dashboard** — four premium KPI cards, segmentation pie, campaign performance bars, monthly
  revenue line, retention area chart, recent customer table, business insights, AI recommendations
  and an activity feed.
- **Customer Segmentation** — CSV upload, analysis trigger, cluster scatter, donut distribution,
  per-segment cards, customer statistics and a styled data table.
- **Campaign Response Prediction** — full profile form, probability card, gauge, driver progress
  bars and a business recommendation.
- **CLV Prediction** — valuation form, tier assignment, churn risk score, health gauge and a
  cumulative value projection.
- **Decision Impact Engine** — scenario configuration, projected revenue/ROI/profit, three gauges,
  weekly projection, budget allocation donut, discount sensitivity, risk analysis and an
  executive summary.
- **Reports** — customer, campaign and executive templates with generate, PDF and CSV actions plus
  a live preview.
- **Settings** — theme, notifications, profile, application defaults and about information.

## Design system

Defined once in `assets/style.css`.

| Token          | Value     |
| -------------- | --------- |
| Background     | `#0F172A` |
| Sidebar        | `#111827` |
| Cards          | `#1E293B` |
| Primary        | `#2563EB` |
| Success        | `#10B981` |
| Warning        | `#F59E0B` |
| Danger         | `#EF4444` |
| Text           | `#FFFFFF` |
| Secondary text | `#CBD5E1` |
| Borders        | `#334155` |

Glassmorphism surfaces, rounded cards, soft shadows, hover elevation, smooth transitions, Inter
typography, responsive breakpoints and inline SVG icons. No emojis anywhere in the product.

## Mock data

`data/generate_mock_data.py` produces 300 customers with the columns `Customer_ID`,
`Customer_Name`, `Age`, `Gender`, `Income`, `Education`, `Occupation`, `Marital_Status`,
`Purchase_Frequency`, `Recency`, `Spending`, `Customer_Segment`, `Predicted_CLV`,
`Response_Probability` and `Recommendation`. Distributions are seeded so charts stay stable
between reloads.

## Future backend integration

Every prediction surface carries a placeholder in the exact call position:

```python
# Future FastAPI Integration
# response = requests.post("/predict", json=input_data)
# prediction = response.json()
```

Swap the heuristic call in `utils/helpers.py` for the HTTP call and the interface needs no other
change. A service endpoint field already exists in Settings > Application.
