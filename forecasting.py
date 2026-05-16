"""Demand & sales forecasting for Winmart / VinMart store-SKU daily units."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

try:
    import lightgbm as lgb

    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False


ModelBackend = Literal["lightgbm", "random_forest"]


@dataclass
class ForecastPoint:
    store_id: str
    sku: str
    forecast_date: str
    predicted_units: float
    lower_bound: float
    upper_bound: float
    model_backend: str


class DemandForecaster:
    """Per-SKU demand model with optional confidence bands from residual spread."""

    def __init__(self, backend: ModelBackend = "lightgbm"):
        self.backend = backend if (backend != "lightgbm" or HAS_LIGHTGBM) else "random_forest"
        self.models: Dict[str, object] = {}
        self.residual_std: Dict[str, float] = {}
        self.is_trained = False

    def train(self, X_train: np.ndarray, y_train: np.ndarray, sku: str) -> Dict:
        model = self._build_model()
        model.fit(X_train, y_train)
        preds = model.predict(X_train)
        residuals = y_train - preds
        self.residual_std[sku] = float(np.std(residuals)) if len(residuals) > 1 else 0.0
        self.models[sku] = model
        self.is_trained = True
        return {
            "status": "trained",
            "sku": sku,
            "samples": len(X_train),
            "backend": self.backend,
            "residual_std": self.residual_std[sku],
        }

    def forecast(
        self,
        X: np.ndarray,
        sku: str,
        confidence: float = 0.9,
    ) -> np.ndarray:
        if sku not in self.models:
            raise ValueError(f"Model not trained for SKU {sku}")
        predictions = self.models[sku].predict(X)
        return np.maximum(predictions, 0)

    def forecast_with_intervals(
        self,
        X: np.ndarray,
        sku: str,
        confidence: float = 0.9,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        point = self.forecast(X, sku, confidence)
        z = 1.64 if confidence >= 0.9 else 1.28
        margin = z * self.residual_std.get(sku, 0.0)
        lower = np.maximum(point - margin, 0)
        upper = point + margin
        return point, lower, upper

    def get_feature_importance(self, sku: str) -> Dict[str, float]:
        if sku not in self.models:
            raise ValueError(f"Model not trained for SKU {sku}")
        model = self.models[sku]
        names = ["day_of_week", "seasonality", "promotion", "competitor_price"]
        if hasattr(model, "feature_importances_"):
            imp = model.feature_importances_
            return {names[i]: float(imp[i]) for i in range(min(len(names), len(imp)))}
        return {n: 0.0 for n in names}

    def _build_model(self):
        if self.backend == "lightgbm" and HAS_LIGHTGBM:
            return lgb.LGBMRegressor(
                n_estimators=120,
                learning_rate=0.08,
                max_depth=6,
                random_state=42,
                verbose=-1,
            )
        return RandomForestRegressor(n_estimators=100, random_state=42)


class SalesForecastPipeline:
    """
    Store × SKU daily sales forecasting from transaction history.
    Builds lag/seasonality features and trains one model per SKU.
    """

    FEATURE_COLUMNS = [
        "day_of_week",
        "seasonality",
        "promotion",
        "competitor_price",
    ]

    def __init__(self, backend: ModelBackend = "lightgbm"):
        self.forecaster = DemandForecaster(backend=backend)

    @staticmethod
    def build_features(daily_sales: pd.DataFrame) -> pd.DataFrame:
        """Expect columns: date, store_id, sku, units_sold, promotion, competitor_price."""
        df = daily_sales.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(["store_id", "sku", "date"])
        df["day_of_week"] = df["date"].dt.dayofweek
        df["seasonality"] = np.sin(2 * np.pi * df["date"].dt.dayofyear / 365.0)
        df["promotion"] = df.get("promotion", 0).fillna(0)
        df["competitor_price"] = df.get("competitor_price", 1.0).fillna(1.0)
        df["units_lag_7"] = df.groupby(["store_id", "sku"])["units_sold"].shift(7)
        df = df.dropna(subset=["units_lag_7"])
        return df

    def fit(self, daily_sales: pd.DataFrame) -> Dict[str, Dict]:
        featured = self.build_features(daily_sales)
        results: Dict[str, Dict] = {}
        for sku, grp in featured.groupby("sku"):
            X = grp[SalesForecastPipeline.FEATURE_COLUMNS].to_numpy()
            y = grp["units_sold"].to_numpy()
            results[sku] = self.forecaster.train(X, y, sku=str(sku))
        return results

    def predict_horizon(
        self,
        daily_sales: pd.DataFrame,
        horizon_days: int = 7,
        confidence: float = 0.9,
    ) -> List[ForecastPoint]:
        featured = self.build_features(daily_sales)
        if featured.empty:
            return []

        outputs: List[ForecastPoint] = []
        for (store_id, sku), grp in featured.groupby(["store_id", "sku"]):
            sku_key = str(sku)
            if sku_key not in self.forecaster.models:
                continue
            last = grp.iloc[-1]
            last_date = pd.to_datetime(last["date"])
            X_row = last[SalesForecastPipeline.FEATURE_COLUMNS].to_numpy().reshape(1, -1)
            for offset in range(1, horizon_days + 1):
                future_date = last_date + pd.Timedelta(days=offset)
                X_future = X_row.copy()
                X_future[0, 0] = future_date.dayofweek
                X_future[0, 1] = float(np.sin(2 * np.pi * future_date.dayofyear / 365.0))
                point, lower, upper = self.forecaster.forecast_with_intervals(
                    X_future, sku_key, confidence=confidence
                )
                outputs.append(
                    ForecastPoint(
                        store_id=str(store_id),
                        sku=sku_key,
                        forecast_date=future_date.date().isoformat(),
                        predicted_units=round(float(point[0]), 2),
                        lower_bound=round(float(lower[0]), 2),
                        upper_bound=round(float(upper[0]), 2),
                        model_backend=self.forecaster.backend,
                    )
                )
        return outputs

    def to_dataframe(self, points: List[ForecastPoint]) -> pd.DataFrame:
        return pd.DataFrame([p.__dict__ for p in points])
