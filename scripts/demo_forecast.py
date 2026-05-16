"""Demo: VinMart / Winmart store-SKU sales forecast with confidence intervals."""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from forecasting import SalesForecastPipeline

SAMPLE = ROOT / "data" / "samples" / "daily_sales_sample.csv"


def main() -> None:
    daily = pd.read_csv(SAMPLE, parse_dates=["date"])
    pipeline = SalesForecastPipeline(backend="lightgbm")
    train_info = pipeline.fit(daily)
    print("--- Training ---")
    for sku, info in train_info.items():
        print(f"  {sku}: {info['samples']} samples via {info['backend']}")

    points = pipeline.predict_horizon(daily, horizon_days=7, confidence=0.9)
    df = pipeline.to_dataframe(points)
    print("\n--- 7-day forecast (90% interval) ---")
    print(df.to_string(index=False))
    print(f"\nTotal forecast rows: {len(df)}")


if __name__ == "__main__":
    main()
