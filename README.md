E-Commerce Sales Analysis & Dashboard

> A complete end-to-end data analysis project analyzing 2,000+ e-commerce transactions — from raw data cleaning to an interactive Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.15+-3F4F75?style=flat&logo=plotly&logoColor=white)

---

Project Overview

This project performs a full business intelligence analysis on e-commerce sales data across **5 product categories**, **5 regions**, and **3 sales channels** throughout 2023.

What It Does
- Cleans and validates raw transactional data
- Computes key business KPIs (Revenue, AOV, Return Rate, etc.)
- Generates 5 publication-quality visualisations
- Surfaces actionable insights automatically
- Provides an interactive dashboard for stakeholder exploration

---

Project Structure

```
project1_ecommerce_analysis/
│
├── data/
│   └── sales_data.csv          # Generated / replace with real data
│
├── src/
│   ├── analysis.py             # Core: cleaning, EDA, plots, insights
│   └── dashboard.py            # Streamlit interactive dashboard
│
├── outputs/                    # Auto-generated charts (PNG)
│   ├── monthly_revenue.png
│   ├── category_breakdown.png
│   ├── channel_region_heatmap.png
│   ├── cohort_analysis.png
│   └── discount_impact.png
│
├── tests/
│   └── test_analysis.py        # Unit tests
│
├── requirements.txt
└── README.md
```

---

Key Analyses

| Analysis | Description |
|---|---|
| **Monthly Revenue Trend** | Bar + line chart showing revenue seasonality across 12 months |
| **Category Breakdown** | Bar chart + pie chart showing revenue share per product category |
| **Region × Channel Heatmap** | Identify which region + channel combos drive most value |
| **Customer Cohort Analysis** | Track customer retention by acquisition quarter |
| **Discount Impact** | Dual-axis chart showing how discounts affect revenue and volume |

---


Sample Insights

The pipeline automatically generates insights such as:

Peak sales month — identifies when to stock up inventory
Mobile App share — quantifies mobile revenue contribution
Discount effectiveness — correlates promotions with order volume
Return rate health check — flags quality issues if > 10%
Top category & region — directs marketing budget

---

 Technical Highlights

- **Data Generation**: Realistic synthetic data with configurable seed for reproducibility
- **Vectorised Operations**: All pandas operations use vectorised methods (no Python loops on DataFrames)
- **Caching**: Streamlit `@st.cache_data` for fast dashboard loads
- **Dual-axis charts**: Plotly `go.Figure` with secondary Y-axis for overlay comparisons
- **Modular Design**: Each analysis step is a pure function — easy to test and extend

---

Running Tests
```bash
python -m pytest tests/ -v
```

---

Using Real Data

Replace the `generate_sample_data()` call in `analysis.py` with your CSV:

```python
# In src/analysis.py  →  main()
df_raw = pd.read_csv(DATA_DIR / "your_sales_file.csv", parse_dates=["date"])
```

Expected columns: `order_id`, `date`, `category`, `region`, `channel`, `unit_price`, `quantity`, `discount_pct`, `revenue`, `customer_id`, `is_returned`

---

Tech Stack

| Tool | Purpose |
|---|---|
| **Pandas / NumPy** | Data wrangling & computation |
| **Matplotlib / Seaborn** | Static publication charts |
| **Plotly** | Interactive dashboard charts |
| **Streamlit** | Web dashboard UI |

---

License
MIT — free to use, modify, and distribute.
