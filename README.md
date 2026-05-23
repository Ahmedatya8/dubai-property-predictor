# Dubai Property Price Predictor

> ML service that predicts Dubai residential apartment sale prices using 
> real Dubai Land Department (DLD) transaction data.  
> Served via REST API — deployed on Render.

🔗 **Live API:** https://dubai-property-predictor.onrender.com/docs

---

## Problem

Dubai's property market generates hundreds of thousands of transactions per year
with high price variance across neighbourhoods, property types, and sizes.
This service predicts residential unit sale prices to help buyers, sellers,
and agents get a data-driven price estimate instantly.

---

## Dataset

- **Source:** Dubai Land Department (DLD) public transaction records
- **Size:** ~460,000 transactions after filtering
- **Scope:** Residential unit sales only (apartments)
- **Period:** 2001–2024

---

## Features Used

| Feature | Type | Rationale |
|---|---|---|
| `procedure_area` | Numeric | Size in sqm — strongest price correlator |
| `year` / `month` | Numeric | Captures market trends and seasonality |
| `has_parking` | Numeric | Parking adds measurable value in Dubai |
| `no_of_parties_role_1/2/3` | Numeric | Transaction complexity signals |
| `area_name_en` | Categorical | Neighbourhood — #1 price driver |
| `rooms_en` | Categorical | Bedroom count determines price tier |
| `property_type_en` | Categorical | Unit / Villa / Land |
| `property_usage_en` | Categorical | Residential vs Commercial |
| `nearest_metro_en` | Categorical | Metro proximity signal |

---

## Model & Results

5 models compared via 5-fold cross-validation:

| Model | CV R² |
|---|---|
| Linear Regression | ~0.53 |
| Ridge | ~0.53 |
| Decision Tree | ~0.87 |
| Random Forest | ~0.93 |
| **XGBoost** | **~0.92** |


---

## API Usage

**Base URL:** `https://dubai-property-predictor.onrender.com`

### Health check
```bash
curl https://dubai-property-predictor.onrender.com/health
```

### Predict price
```bash
curl -X POST https://dubai-property-predictor.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "procedure_area": 120,
    "year": 2024,
    "month": 3,
    "has_parking": 1,
    "no_of_parties_role_1": 1,
    "no_of_parties_role_2": 1,
    "no_of_parties_role_3": 0,
    "area_name_en": "Dubai Marina",
    "rooms_en": "2 B/R",
    "property_type_en": "Unit",
    "property_usage_en": "Residential",
    "nearest_metro_en": "DAMAC Properties"
  }'
```

### Response
```json
{
  "predicted_price_AED": 1842300.0,
  "predicted_price_AED_formatted": "AED 1,842,300",
  "price_per_sqm": 15352.5,
  "input_received": { ... }
}
```

---

## How to Run Locally

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/dubai-property-predictor
cd dubai-property-predictor

# Install
pip install -r requirements.txt

# Run API
uvicorn api.main:app --reload

# Open docs
http://127.0.0.1:8000/docs
```

---

## Run with Docker

```bash
docker build -t dubai-property-predictor .
docker run -p 8000:8000 dubai-property-predictor
```

---

## Project Structure
dubai-property-predictor/
├── notebooks/
│   ├── dubai_property_predictor.ipynb   # EDA + training
│   └── 02_api_test.ipynb                # API testing
├── src/
│   └── predict.py                       # prediction logic
├── api/
│   └── main.py                          # FastAPI app
├── models/
│   └── model_meta.json                  # metrics & feature info
├── Dockerfile
└── requirements.txt

---

## Tech Stack

`Python` · `scikit-learn` · `XGBoost` · `FastAPI` · `Docker` · `Render`