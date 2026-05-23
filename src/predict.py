# ── predict.py ────────────────────────────────────────────────────────────────
# Prediction logic isolated from the API layer.
# The API imports predict_price() — it never touches the model directly.
# This separation means you can swap models without touching api/main.py.

import numpy as np
import joblib
import json
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / 'models' / 'model.joblib'
META_PATH  = ROOT / 'models' / 'model_meta.json'

# ── Lazy loading ──────────────────────────────────────────────────────────────
# Load model once when first prediction is made, not on every request.
# _pipeline and _meta stay None until predict_price() is called the first time.
_pipeline = None
_meta     = None


def _load():
    """Load model and metadata from disk if not already loaded."""
    global _pipeline, _meta
    if _pipeline is None:
        _pipeline = joblib.load(MODEL_PATH)
        with open(META_PATH) as f:
            _meta = json.load(f)


def predict_price(
    procedure_area: float,
    year: int,
    month: int,
    has_parking: int,
    no_of_parties_role_1: float,
    no_of_parties_role_2: float,
    no_of_parties_role_3: float,
    area_name_en: str,
    rooms_en: str,
    property_type_en: str,
    property_usage_en: str,
    nearest_metro_en: str,
) -> dict:
    """
    Accept raw property features, run them through the saved pipeline,
    and return the predicted price in AED.
    """
    _load()

    import pandas as pd

    # Build a single-row DataFrame — must match training feature order exactly
    X = pd.DataFrame([{
        'procedure_area':       procedure_area,
        'year':                 year,
        'month':                month,
        'has_parking':          has_parking,
        'no_of_parties_role_1': no_of_parties_role_1,
        'no_of_parties_role_2': no_of_parties_role_2,
        'no_of_parties_role_3': no_of_parties_role_3,
        'area_name_en':         area_name_en,
        'rooms_en':             rooms_en,
        'property_type_en':     property_type_en,
        'property_usage_en':    property_usage_en,
        'nearest_metro_en':     nearest_metro_en,
    }])

    # Model predicts in log scale — reverse with expm1 to get AED
    log_pred = _pipeline.predict(X)[0]
    price    = float(np.expm1(log_pred))

    return {
        'predicted_price_AED':           round(price, 2),
        'predicted_price_AED_formatted': f'AED {price:,.0f}',
        'price_per_sqm':                 round(price / procedure_area, 2),
    }