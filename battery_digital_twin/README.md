# Battery Digital Twin — FastAPI Backend

## Structure

```text
battery_digital_twin/
├── backend/
│   ├── main.py
│   ├── db.py
│   ├── schemas.py
│   └── routers/
│       └── batteries.py
├── ml/
│   ├── predict.py   # provide Amrita's module
│   ├── explain.py   # provide Amrita's module
│   └── simulate.py  # provide Amrita's module
├── data/
│   ├── battery_metadata.csv
│   └── battery_telemetry.csv
├── schema.sql
├── seed.py
├── requirements.txt
└── .env.example
```

## 1. Environment

Copy `.env.example` to `.env` and set:

- `SUPABASE_URL` — Supabase project URL
- `SUPABASE_KEY` — Supabase anon/publishable key (or another key appropriate for the backend)
- `VERCEL_FRONTEND_URL` — deployed Vercel frontend origin, e.g. `https://your-app.vercel.app`

Never commit `.env`.

## 2. Create the Supabase tables

Run `schema.sql` in the Supabase SQL Editor. The Python Supabase client uses `SUPABASE_URL` and `SUPABASE_KEY` for all application CRUD operations; the SQL Editor is used for DDL because the public Supabase client API does not provide arbitrary SQL execution.

## 3. Add data

Put the two CSV files at:

```text
data/battery_telemetry.csv
data/battery_metadata.csv
```

Expected metadata columns:

```text
id,vehicle_type,install_date
```

Expected telemetry columns:

```text
battery_id,day,voltage,temperature,cycle_count,depth_of_discharge,fast_charge_freq,capacity_pct
```

Then run:

```bash
python seed.py
```

## 4. Amrita's ML modules

The backend expects these callables:

- `ml/predict.py` → `predict_battery(payload)`
- `ml/explain.py` → `explain_battery(payload)`
- `ml/simulate.py` → `simulate_battery(payload)`

`predict_battery()` must return a dictionary containing `bhi`, `rul_days`, and `failure_risk_pct`.

The payloads are JSON-like Python dictionaries. See `backend/routers/batteries.py` for the exact payload shape.

## 5. Run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Load environment variables from .env in your shell or use python-dotenv in your entrypoint.
uvicorn backend.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

## Endpoints

- `GET /batteries` — all batteries with their latest stored BHI/RUL/risk
- `GET /batteries/{id}` — full telemetry history
- `GET /batteries/{id}/predict` — run prediction, store it, return it
- `GET /batteries/{id}/explain` — call Amrita's explanation module
- `POST /batteries/{id}/whatif` — simulate modified latest telemetry inputs
- `GET /health` — health check

### What-if example

```json
{
  "temperature": 38.5,
  "depth_of_discharge": 0.85,
  "fast_charge_freq": 4
}
```

Only supplied fields are changed; unspecified fields remain at the latest telemetry values.
