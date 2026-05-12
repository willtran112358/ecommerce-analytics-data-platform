"""Demand forecasting for retail"""

from typing import List

import numpy as np
from sklearn.ensemble import RandomForestRegressor


class DemandForecaster:
    """Forecast demand for SKUs"""

    def __init__(self):
        self.models = {}
        self.is_trained = False

    def train(self, X_train: np.ndarray, y_train: np.ndarray, sku: str) -> Dict:
        """Train demand forecast model"""
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        self.models[sku] = model
        return {"status": "trained", "sku": sku, "samples": len(X_train)}

    def forecast(self, X: np.ndarray, sku: str) -> np.ndarray:
        """Forecast demand for SKU"""
        if sku not in self.models:
            raise ValueError(f"Model not trained for SKU {sku}")

        predictions = self.models[sku].predict(X)
        return np.maximum(predictions, 0)  # Demand cannot be negative

    def get_feature_importance(self, sku: str) -> Dict:
        """Get feature importance for model"""
        if sku not in self.models:
            raise ValueError(f"Model not trained for SKU {sku}")

        model = self.models[sku]
        features = {
            "day_of_week": model.feature_importances_[0],
            "seasonality": model.feature_importances_[1],
            "promotion": model.feature_importances_[2],
            "competitor_price": model.feature_importances_[3],
        }

        return features
