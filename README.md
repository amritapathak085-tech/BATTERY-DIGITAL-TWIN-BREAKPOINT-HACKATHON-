# Battery Digital Twin

A full-stack Battery Digital Twin platform combining a Next.js
dashboard, FastAPI backend, XGBoost machine-learning models, SHAP
explainability, what-if simulation, and an optional AI copilot.

## Overview

The platform is designed to answer four questions:

-   **How healthy is the battery?** --- Battery Health Index (BHI),
    Remaining Useful Life (RUL), and failure risk.
-   **What is happening?** --- Battery telemetry and health/degradation
    trends.
-   **Why is it happening?** --- SHAP-based explanations converted into
    plain English.
-   **What if operating conditions change?** --- Before/after
    predictions and estimated cost, downtime, and CO2 savings.

## Architecture

``` text
Next.js Frontend
       |
       | REST API
       v
FastAPI Backend
   |         |
   v         v
Supabase   ML Layer
Database   XGBoost RUL + Failure Risk
               |
               +--> SHAP Explainability
               +--> What-if Simulation
               +--> AI Copilot
```

## Project Structure

``` text
/
├── frontend/              # Next.js dashboard
├── backend/               # FastAPI application
│   ├── main.py
│   ├── db.py
│   ├── schemas.py
│   └── routers/
│       └── batteries.py
├── ml/                    # ML, explainability and simulation
│   ├── model_rul.json
│   ├── model_failure.json
│   ├── predict.py
│   ├── explain.py
│   ├── simulate.py
│   └── copilot.py
├── data/                  # Battery datasets
│   ├── battery_telemetry.csv
│   └── battery_metadata.csv
├── docs/                  # API contract and environment example
├── schema.sql
├── seed.py
├── requirements.txt
└── README.md
```

## Frontend

### Stack

-   Next.js 14
-   App Router
-   TypeScript
-   Tailwind CSS
-   Recharts

### Features

**Fleet Overview** - Battery cards - Battery Health Index (0--100) - RUL
in days - Failure risk percentage

**Battery Detail** - Health trend charts - Telemetry history - Risk
visualization - Battery information

**Explainability** - Plain-English root-cause reasons - Top contributing
features from SHAP

**What-if Simulation** - Modify operating conditions such as fast-charge
frequency - Compare before/after BHI, RUL, and risk - Show estimated
INR, downtime, and CO2 savings

The frontend can initially run against mock JSON data matching the
shared API contract and later switch to the real backend.

## Backend

### Stack

-   Python
-   FastAPI
-   Supabase PostgreSQL

### Database

`batteries`

``` text
id, vehicle_type, install_date
```

`telemetry`

``` text
battery_id, day, voltage, temperature, cycle_count,
depth_of_discharge, fast_charge_freq, capacity_pct
```

`predictions`

``` text
battery_id, bhi, rul_days, failure_risk_pct, computed_at
```

### API

  Method   Endpoint                    Purpose
  -------- --------------------------- ---------------------------------------
  GET      `/batteries`                Latest BHI/RUL/risk for batteries
  GET      `/batteries/{id}`           Battery details and telemetry history
  GET      `/batteries/{id}/predict`   Generate and store prediction
  GET      `/batteries/{id}/explain`   Return model explanation
  POST     `/batteries/{id}/whatif`    Run modified-condition simulation

## Machine Learning

The build plan specifies a synthetic dataset representing **20
industrial EV batteries over 365 days**. Telemetry includes voltage,
temperature, cycle count, depth of discharge, ambient temperature,
fast-charge frequency, and capacity percentage.

Higher heat exposure and increased fast charging are modeled as
accelerating degradation, with some batteries trending toward failure.

### Feature Engineering

-   7-day rolling averages
-   30-day rolling averages
-   Cumulative cycle count
-   Temperature exposure index
-   Fast-charge ratio

### RUL Model

An **XGBoost regressor** predicts Remaining Useful Life in days.

``` text
ml/model_rul.json
```

### Failure Model

An **XGBoost classifier** predicts 90-day failure probability.

``` text
ml/model_failure.json
```

### Prediction Output

`ml/predict.py` exposes:

``` python
predict(battery_id_or_features)
```

with:

``` json
{
  "bhi": 0,
  "rul_days": 0,
  "failure_risk_pct": 0
}
```

The BHI combines the RUL and failure-risk outputs into a 0--100 health
score; the exact formula is maintained in the ML implementation.

## Explainability

`ml/explain.py` uses SHAP values to identify the most influential
features behind an XGBoost prediction and converts the top contributors
into plain-English explanations.

Example output:

``` json
{
  "reasons": [
    {
      "feature": "temperature",
      "impact": "...",
      "plain_english": "High average temperature is accelerating degradation."
    }
  ]
}
```

## What-if Simulation

`ml/simulate.py` accepts modified inputs, reruns the prediction, and
compares the result with the original state.

Example:

``` text
Reduce fast-charge frequency by 30%
        ↓
Modify inputs
        ↓
Run prediction
        ↓
Compare before vs after
        ↓
Estimate INR / downtime / CO2 impact
```

The conversion multipliers are kept as named constants so their
assumptions can be explained during the demo.

## AI Copilot

`ml/copilot.py` receives only structured outputs:

-   BHI
-   RUL
-   Failure risk
-   SHAP reason list

It does not receive raw telemetry. The copilot generates a
natural-language summary and recommendation. If the LLM API is
unavailable, a template-based fallback keeps the demo functional.

The planned implementation uses the Groq Python SDK with an
OpenAI-compatible interface.

## Data Flow

``` text
Battery Telemetry
       ↓
Synthetic Dataset
       ↓
Feature Engineering
       ↓
XGBoost RUL + Failure Models
       ↓
BHI / RUL / Failure Risk
       ├──→ FastAPI
       ├──→ SHAP Explanation
       └──→ What-if Simulation
                    ↓
               Next.js UI
```

## Local Development

### Backend

``` bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Backend:

``` text
http://localhost:8000
```

### Frontend

``` bash
cd frontend
npm install
npm run dev
```

Frontend:

``` text
http://localhost:3000
```

Set:

``` text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Environment Variables

``` text
SUPABASE_URL=
SUPABASE_KEY=
GROQ_API_KEY=
NEXT_PUBLIC_API_URL=
```

Never commit real API keys or `.env` files. Use `.env.example` files
instead.

## Deployment

  Component    Planned Platform
  ------------ ------------------
  Frontend     Vercel
  Backend      Render
  Database     Supabase
  AI Copilot   Groq

The frontend uses `NEXT_PUBLIC_API_URL` to connect to the deployed
backend. Backend secrets are configured through the hosting platform's
environment variables.

## Git Workflow

``` text
feature/<name> → dev → main
```

Recommended workflow:

``` bash
git checkout -b feature/<your-name>
git add .
git commit -m "short descriptive message"
git push origin feature/<your-name>
```

Open a pull request into `dev`. After integration and demo testing,
merge `dev` into `main`.

## End-to-End Demo

``` text
Select an unhealthy battery
        ↓
View BHI / RUL / failure risk
        ↓
Inspect health trend
        ↓
Open "Why?"
        ↓
See SHAP-based reasons
        ↓
Open What-if
        ↓
Change an operating condition
        ↓
Compare before vs after
        ↓
View estimated cost / downtime / CO2 savings
```

## Team Tracks

  Area                                      Responsibility
  ----------------------------------------- ----------------
  Synthetic data & ML models                Kavya
  Backend & APIs                            Aadya
  Frontend & dashboard                      Diya
  Explainability, simulation & AI copilot   Amrita

## Key Technologies

``` text
Frontend:  Next.js 14, TypeScript, Tailwind CSS, Recharts
Backend:   Python, FastAPI, Supabase PostgreSQL
ML:        XGBoost, scikit-learn, Pandas, SHAP
AI:        Groq / LLM Copilot
Deploy:    Vercel, Render, Supabase
```

## Project Goal

The Battery Digital Twin combines **battery telemetry, predictive ML,
explainable AI, and scenario simulation** in one platform.

Instead of only showing that a battery is unhealthy, the system aims to
show:

**How healthy it is → how long it may last → why it is degrading → and
what could happen if operating conditions change.**
