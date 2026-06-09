"""
E-Commerce Sales Analysis
Core analysis module - loads data, cleans it, and runs all analyses.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Style ──────────────────────────────────────────────────────────────────
PALETTE = ["#2563EB", "#7C3AED", "#DB2777", "#059669", "#D97706"]
sns.set_theme(style="whitegrid", palette=PALETTE)
plt.rcParams.update({"figure.dpi": 150, "font.family": "DejaVu Sans"})


# ══════════════════════════════════════════════════════════════════════════
# 1.  DATA GENERATION  (replace with pd.read_csv() for real data)
# ══════════════════════════════════════════════════════════════════════════

def generate_sample_data(n: int = 2000, seed: int = 42) -> pd.DataFrame:
    """
    Generate realistic synthetic e-commerce transactions.
    In production replace this with:  pd.read_csv(DATA_DIR / 'sales.csv')
    """
    rng = np.random.default_rng(seed)

    categories  = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books"]
    regions     = ["North", "South", "East", "West", "Central"]
    channels    = ["Online", "Mobile App", "In-Store"]
    pay_methods = ["Credit Card", "PayPal", "Debit Card", "Crypto"]

    dates = pd.date_range("2023-01-01", "2023-12-31", periods=n)

    category_arr = rng.choice(categories, n, p=[0.30, 0.25, 0.20, 0.15, 0.10])

    base_price = {"Electronics": 250, "Clothing": 60, "Home & Garden": 90,
                  "Sports": 80, "Books": 20}
    prices = np.array([base_price[c] * (1 + rng.normal(0, 0.3)) for c in category_arr])
    prices = np.clip(prices, 5, 1500).round(2)

    quantities = rng.integers(1, 6, n)

    discount_pct = rng.choice([0, 5, 10, 15, 20, 25], n,
                               p=[0.40, 0.20, 0.18, 0.10, 0.07, 0.05])

    revenue = (prices * quantities * (1 - discount_pct / 100)).round(2)

    df = pd.DataFrame({
        "order_id":      [f"ORD-{i:05d}" for i in range(n)],
        "date":          dates,
        "category":      category_arr,
        "region":        rng.choice(regions, n),
        "channel":       rng.choice(channels, n, p=[0.55, 0.30, 0.15]),
        "payment":       rng.choice(pay_methods, n),
        "unit_price":    prices,
        "quantity":      quantities,
        "discount_pct":  discount_pct,
        "revenue":       revenue,
        "customer_id":   rng.integers(1000, 5000, n),
        "is_returned":   rng.choice([0, 1], n, p=[0.92, 0.08]),
    })
    df["month"]    = df["date"].dt.month_name()
    df["month_num"]= df["date"].dt.month
    df["weekday"]  = df["date"].dt.day_name()
    df["quarter"]  = df["date"].dt.quarter.map({1:"Q1",2:"Q2",3:"Q3",4:"Q4"})

    # Save for reproducibility
    df.to_csv(DATA_DIR / "sales_data.csv", index=False)
    print(f"[data] {len(df):,} rows saved to data/sales_data.csv")
    return df


# ══════════════════════════════════════════════════════════════════════════
# 2.  DATA CLEANING & VALIDATION
# ══════════════════════════════════════════════════════════════════════════

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate the raw dataframe."""
    original_len = len(df)

    # Drop full duplicates
    df = df.drop_duplicates()

    # Remove negative or zero revenue
    df = df[df["revenue"] > 0]

    # Fill any missing categories
    df["category"] = df["category"].fillna("Unknown")

    # Clip outlier unit prices (beyond 3 std)
    mean_p, std_p = df["unit_price"].mean(), df["unit_price"].std()
    df = df[df["unit_price"].between(mean_p - 3 * std_p, mean_p + 3 * std_p)]

    print(f"[clean] Removed {original_len - len(df):,} rows  →  {len(df):,} remain")
    return df.reset_index(drop=True)


# ══════════════════════════════════════════════════════════════════════════
# 3.  EXPLORATORY DATA ANALYSIS  (returns dict of key metrics)
# ══════════════════════════════════════════════════════════════════════════

def run_eda(df: pd.DataFrame) -> dict:
    """Compute and print summary statistics."""
    metrics = {
        "total_revenue":   df["revenue"].sum(),
        "total_orders":    len(df),
        "avg_order_value": df["revenue"].mean(),
        "unique_customers":df["customer_id"].nunique(),
        "return_rate":     df["is_returned"].mean() * 100,
        "top_category":    df.groupby("category")["revenue"].sum().idxmax(),
        "top_region":      df.groupby("region")["revenue"].sum().idxmax(),
        "top_channel":     df.groupby("channel")["revenue"].sum().idxmax(),
    }

    print("\n" + "="*50)
    print("  KEY BUSINESS METRICS")
    print("="*50)
    print(f"  Total Revenue      : ${metrics['total_revenue']:>12,.2f}")
    print(f"  Total Orders       : {metrics['total_orders']:>12,}")
    print(f"  Avg Order Value    : ${metrics['avg_order_value']:>12,.2f}")
    print(f"  Unique Customers   : {metrics['unique_customers']:>12,}")
    print(f"  Return Rate        : {metrics['return_rate']:>11.1f}%")
    print(f"  Top Category       : {metrics['top_category']:>14}")
    print(f"  Top Region         : {metrics['top_region']:>14}")
    print(f"  Top Channel        : {metrics['top_channel']:>14}")
    print("="*50 + "\n")
    return metrics


# ══════════════════════════════════════════════════════════════════════════
# 4.  VISUALISATIONS
# ══════════════════════════════════════════════════════════════════════════

def _save(name: str):
    path = OUTPUT_DIR / name
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"[plot] saved → {path}")


def plot_monthly_revenue(df: pd.DataFrame):
    monthly = (df.groupby("month_num")["revenue"]
                 .sum()
                 .reset_index()
                 .rename(columns={"month_num": "Month"}))
    monthly["Month Label"] = pd.to_datetime(monthly["Month"], format="%m").dt.strftime("%b")

    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(monthly["Month Label"], monthly["revenue"],
                  color=PALETTE[0], alpha=0.85, edgecolor="white", linewidth=0.8)
    ax.plot(monthly["Month Label"], monthly["revenue"],
            color=PALETTE[1], marker="o", linewidth=2, markersize=6, label="Trend")

    # Annotate bars
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 500,
                f"${bar.get_height()/1000:.0f}K",
                ha="center", va="bottom", fontsize=8, color="#374151")

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    ax.set_title("Monthly Revenue — 2023", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Month"); ax.set_ylabel("Revenue (USD)")
    ax.legend()
    _save("monthly_revenue.png")


def plot_category_breakdown(df: pd.DataFrame):
    cat = df.groupby("category")["revenue"].sum().sort_values(ascending=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Bar chart
    ax1.barh(cat.index, cat.values, color=PALETTE[:len(cat)])
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    ax1.set_title("Revenue by Category", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Revenue (USD)")
    for i, v in enumerate(cat.values):
        ax1.text(v + 500, i, f"${v/1000:.0f}K", va="center", fontsize=9)

    # Pie chart
    ax2.pie(cat.values, labels=cat.index, autopct="%1.1f%%",
            colors=PALETTE, startangle=140,
            wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    ax2.set_title("Category Share", fontsize=13, fontweight="bold")

    _save("category_breakdown.png")


def plot_channel_region_heatmap(df: pd.DataFrame):
    pivot = df.pivot_table(values="revenue", index="region",
                           columns="channel", aggfunc="sum")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt=",.0f", cmap="Blues",
                linewidths=0.5, linecolor="#E5E7EB",
                annot_kws={"size": 10}, ax=ax)
    ax.set_title("Revenue Heatmap: Region × Channel", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Sales Channel"); ax.set_ylabel("Region")
    _save("channel_region_heatmap.png")


def plot_cohort_analysis(df: pd.DataFrame):
    """Simple quarterly cohort by first-purchase quarter."""
    first_q = df.groupby("customer_id")["quarter"].min().rename("cohort")
    df2 = df.merge(first_q, on="customer_id")
    cohort_data = (df2.groupby(["cohort", "quarter"])["customer_id"]
                      .nunique()
                      .reset_index(name="customers"))

    pivot = cohort_data.pivot(index="cohort", columns="quarter", values="customers").fillna(0)

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.heatmap(pivot.astype(int), annot=True, fmt="d", cmap="YlOrRd",
                linewidths=0.4, ax=ax)
    ax.set_title("Customer Cohort Analysis (by Quarter)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Active Quarter"); ax.set_ylabel("Acquisition Quarter")
    _save("cohort_analysis.png")


def plot_discount_impact(df: pd.DataFrame):
    """Show how discount levels affect average order value."""
    disc = (df.groupby("discount_pct")
             .agg(avg_revenue=("revenue", "mean"),
                  order_count=("order_id", "count"))
             .reset_index())

    fig, ax1 = plt.subplots(figsize=(10, 5))
    color_bar = PALETTE[3]
    color_line = PALETTE[2]

    ax1.bar(disc["discount_pct"].astype(str) + "%", disc["avg_revenue"],
            color=color_bar, alpha=0.8, label="Avg Order Value")
    ax1.set_ylabel("Avg Order Value ($)", color=color_bar)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}"))

    ax2 = ax1.twinx()
    ax2.plot(disc["discount_pct"].astype(str) + "%", disc["order_count"],
             color=color_line, marker="s", linewidth=2, label="Order Count")
    ax2.set_ylabel("Order Count", color=color_line)

    ax1.set_title("Discount Level vs. Avg Order Value & Volume", fontsize=13,
                  fontweight="bold", pad=12)
    ax1.set_xlabel("Discount Percentage")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    _save("discount_impact.png")


# ══════════════════════════════════════════════════════════════════════════
# 5.  INSIGHTS  (simple rule-based)
# ══════════════════════════════════════════════════════════════════════════

def generate_insights(df: pd.DataFrame, metrics: dict) -> list[str]:
    insights = []

    # Revenue peak month
    monthly = df.groupby("month_num")["revenue"].sum()
    peak_month = pd.to_datetime(str(monthly.idxmax()), format="%m").strftime("%B")
    insights.append(f"Peak sales month is {peak_month} — consider stocking up inventory beforehand.")

    # Best category
    insights.append(f"{metrics['top_category']} drives the highest revenue; prioritize ads here.")

    # Return rate flag
    if metrics["return_rate"] > 10:
        insights.append(f"Return rate is {metrics['return_rate']:.1f}% — investigate product quality.")
    else:
        insights.append(f"Healthy return rate of {metrics['return_rate']:.1f}%.")

    # Channel insight
    channel_rev = df.groupby("channel")["revenue"].sum()
    mobile_share = channel_rev.get("Mobile App", 0) / channel_rev.sum() * 100
    insights.append(f"Mobile App generates {mobile_share:.1f}% of revenue — optimize mobile UX.")

    # Discount insight
    disc_corr = df[["discount_pct", "revenue"]].corr().iloc[0, 1]
    if disc_corr > 0:
        insights.append("Higher discounts correlate with higher revenue — promotions are effective.")
    else:
        insights.append("Discounts show negative correlation with revenue — review pricing strategy.")

    print("\n[insights]")
    for i, ins in enumerate(insights, 1):
        print(f"  {i}. {ins}")
    return insights


# ══════════════════════════════════════════════════════════════════════════
# 6.  MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    print("\n🛒  E-Commerce Sales Analysis  🛒\n")

    df_raw = generate_sample_data()
    df     = clean_data(df_raw)
    metrics = run_eda(df)

    print("[plots] generating visualisations …")
    plot_monthly_revenue(df)
    plot_category_breakdown(df)
    plot_channel_region_heatmap(df)
    plot_cohort_analysis(df)
    plot_discount_impact(df)

    generate_insights(df, metrics)
    print("\n✅  All outputs saved to /outputs/")


if __name__ == "__main__":
    main()
