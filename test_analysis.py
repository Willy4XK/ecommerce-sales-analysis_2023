"""
Unit tests for the e-commerce analysis module.
Run:  pytest tests/test_analysis.py -v
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from analysis import generate_sample_data, clean_data, run_eda, generate_insights


@pytest.fixture(scope="module")
def raw_df():
    return generate_sample_data(n=500, seed=42)


@pytest.fixture(scope="module")
def clean_df(raw_df):
    return clean_data(raw_df)


class TestDataGeneration:
    def test_row_count(self, raw_df):
        assert len(raw_df) == 500

    def test_required_columns(self, raw_df):
        required = ["order_id", "date", "category", "region",
                    "channel", "revenue", "customer_id"]
        for col in required:
            assert col in raw_df.columns, f"Missing column: {col}"

    def test_revenue_positive(self, raw_df):
        assert (raw_df["revenue"] > 0).all()

    def test_discount_range(self, raw_df):
        assert raw_df["discount_pct"].between(0, 100).all()

    def test_date_range(self, raw_df):
        assert raw_df["date"].min() >= pd.Timestamp("2023-01-01")
        assert raw_df["date"].max() <= pd.Timestamp("2023-12-31")


class TestDataCleaning:
    def test_no_negative_revenue(self, clean_df):
        assert (clean_df["revenue"] > 0).all()

    def test_no_null_category(self, clean_df):
        assert clean_df["category"].notna().all()

    def test_cleaned_leq_raw(self, raw_df, clean_df):
        assert len(clean_df) <= len(raw_df)


class TestEDA:
    def test_metrics_keys(self, clean_df):
        metrics = run_eda(clean_df)
        expected_keys = ["total_revenue", "total_orders", "avg_order_value",
                         "unique_customers", "return_rate", "top_category"]
        for k in expected_keys:
            assert k in metrics

    def test_total_revenue_positive(self, clean_df):
        metrics = run_eda(clean_df)
        assert metrics["total_revenue"] > 0

    def test_return_rate_range(self, clean_df):
        metrics = run_eda(clean_df)
        assert 0 <= metrics["return_rate"] <= 100


class TestInsights:
    def test_returns_list(self, clean_df):
        metrics = run_eda(clean_df)
        insights = generate_insights(clean_df, metrics)
        assert isinstance(insights, list)
        assert len(insights) >= 3

    def test_insights_are_strings(self, clean_df):
        metrics = run_eda(clean_df)
        insights = generate_insights(clean_df, metrics)
        assert all(isinstance(i, str) for i in insights)
