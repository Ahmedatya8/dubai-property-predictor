# ── main.py ───────────────────────────────────────────────────────────────────
# FastAPI application — the public interface to the model.
# Responsibilities:
#   1. Validate incoming requests (Pydantic does this automatically)
#   2. Call predict_price() from src/predict.py
#   3. Return a structured JSON response
# The model logic lives in src/predict.py, not here.

import sys
from pathlib import Path

# ── Make src/ importable ──────────────────────────────────────────────────────
# When uvicorn runs api/main.py, Python doesn't know about the project root.
# We add it manually so 'from src.predict import predict_price' works.
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.predict import predict_price

# ── App definition ────────────────────────────────────────────────────────────
app = FastAPI(
    title='Dubai Property Price Predictor',
    description='Predicts Dubai residential unit sale prices using DLD transaction data.',
    version='1.0.0',
)


# ── Request schema ────────────────────────────────────────────────────────────
# Pydantic validates every incoming request automatically.
# If a field is missing or the wrong type, FastAPI returns a 422 error
# with a clear message — no validation code needed from us.
class PropertyInput(BaseModel):
    procedure_area:       float = Field(..., gt=0,   example=120.0,
                                        description='Property size in sqm')
    year:                 int   = Field(..., ge=2000, le=2030, example=2024)
    month:                int   = Field(..., ge=1,    le=12,   example=3)
    has_parking:          int   = Field(..., ge=0,    le=1,    example=1,
                                        description='1 = has parking, 0 = no parking')
    no_of_parties_role_1: float = Field(1.0, example=1.0)
    no_of_parties_role_2: float = Field(1.0, example=1.0)
    no_of_parties_role_3: float = Field(0.0, example=0.0)
    area_name_en:         str   = Field(..., example='Dubai Marina')
    rooms_en:             str   = Field(..., example='2 B/R')
    property_type_en:     str   = Field(..., example='Unit')
    property_usage_en:    str   = Field(..., example='Residential')
    nearest_metro_en:     str   = Field(..., example='DAMAC Properties')


# ── Response schema ───────────────────────────────────────────────────────────
class PredictionOutput(BaseModel):
    predicted_price_AED:           float
    predicted_price_AED_formatted: str
    price_per_sqm:                 float
    input_received:                dict


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get('/health')
def health():
    """
    Health check endpoint.
    Used by deployment platforms to verify the service is running.
    """
    return {'status': 'ok', 'model': 'dubai-property-predictor-v1'}


@app.post('/predict', response_model=PredictionOutput)
def predict(data: PropertyInput):
    """
    Predict the sale price of a Dubai residential property.

    - Accepts property features as JSON
    - Returns predicted price in AED with per-sqm breakdown
    - Unknown neighbourhoods or metro stations are handled gracefully
    """
    try:
        result = predict_price(
            procedure_area=data.procedure_area,
            year=data.year,
            month=data.month,
            has_parking=data.has_parking,
            no_of_parties_role_1=data.no_of_parties_role_1,
            no_of_parties_role_2=data.no_of_parties_role_2,
            no_of_parties_role_3=data.no_of_parties_role_3,
            area_name_en=data.area_name_en,
            rooms_en=data.rooms_en,
            property_type_en=data.property_type_en,
            property_usage_en=data.property_usage_en,
            nearest_metro_en=data.nearest_metro_en,
        )
    except Exception as e:
        # Return 500 with the error message — useful for debugging
        raise HTTPException(status_code=500, detail=str(e))

    return {
        **result,
        'input_received': data.model_dump(),
    }