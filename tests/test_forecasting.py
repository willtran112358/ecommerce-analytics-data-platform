"""Tests for sales forecasting module."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from forecasting import DemandForecaster, SalesForecastPipeline

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "samples" / "daily_sales_sample.csv"


def _synthetic_daily(rows: int = 20) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=rows, freq="D")
    return pd.DataFrame(
        {
            "date": list(dates) * 2,
            "store_id": ["WINMART_HCM_001"] * rows + ["WINMART_HCM_001"] * rows,
            "sku": ["WM_RICE_01"] * rows + ["WM_MILK_02"] * rows,
            "units_sold": np.random.default_rng(0).integers(20, 60, rows * 2),
            "promotion": [0] * (rows * 2),
            "competitor_price": [1.0] * (rows * 2),
        }
    )


def test_demand_forecaster_intervals():
    rng = np.random.default_rng(42)
    X = rng.random((30, 4))
    y = X[:, 0] * 10 + rng.random(30)
    f = DemandForecaster(backend="random_forest")
    f.train(X, y, "SKU_A")
    point, lower, upper = f.forecast_with_intervals(X[:3], "SKU_A")
    assert len(point) == 3
    assert (lower <= point).all()
    assert (point <= upper).all()


def test_sales_pipeline_fit_and_predict():
    daily = _synthetic_daily(21)
    pipe = SalesForecastPipeline(backend="random_forest")
    result = pipe.fit(daily)
    assert "WM_RICE_01" in result
    forecasts = pipe.predict_horizon(daily, horizon_days=3)
    assert len(forecasts) >= 2
    assert forecasts[0].lower_bound <= forecasts[0].predicted_units <= forecasts[0].upper_bound


def test_sample_csv_loads():
    assert SAMPLE.exists()
    df = pd.read_csv(SAMPLE)
    assert {"date", "store_id", "sku", "units_sold"}.issubset(df.columns)
