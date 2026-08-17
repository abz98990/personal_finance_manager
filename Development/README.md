# AI-Based Personal Financial Management System

Three-tier implementation matching the architecture described in the IPR
(section 3.1): a Flutter mobile client, a Node.js/Express/PostgreSQL API,
and a Python/FastAPI machine-learning microservice.

```
mobile/       Flutter app (auth, dashboard, expenses, budgets, savings goals)
backend/      Express + Sequelize + PostgreSQL REST API, JWT auth
ml-service/   FastAPI service: expense categorization (Logistic Regression
              vs Random Forest) + spend forecasting (linear trend)
```

## Running the stack locally

1. **ML service** (port 8000)
   ```bash
   cd ml-service
   python -m venv .venv && .venv\Scripts\activate
   pip install -r requirements.txt
   python train.py            # trains + saves the category classifier
   uvicorn app.main:app --port 8000
   ```

2. **Backend** (port 4000) — needs PostgreSQL running and a `pfm_dev` database
   ```bash
   cd backend
   npm install
   cp .env.example .env       # set DB_* and ML_SERVICE_URL
   npm run seed                # default categories
   npm run dev
   ```

3. **Mobile app**
   ```bash
   cd mobile
   flutter pub get
   flutter run --dart-define=API_BASE_URL=http://10.0.2.2:4000/api
   ```

Each service has its own README and test suite (`npm test` / `python -m
pytest` / `flutter test`).

## Status

- Backend: 14/14 tests passing, verified live against PostgreSQL and the ML
  service (register → auto-categorized transaction → budget → forecast).
- ML service: 13/13 tests passing; classifier trained and served over HTTP.
- Mobile: screens implemented (auth, dashboard, expenses + add-transaction,
  budgets, savings goals, profile) wired to the backend API.
