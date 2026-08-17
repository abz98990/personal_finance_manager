# PFM Backend

Express + PostgreSQL API for the AI-Based Personal Financial Management
System. Handles auth, transactions, categories, budgets and savings goals,
and proxies categorization/forecasting requests to the ML microservice.

## Setup

```bash
npm install
cp .env.example .env   # then fill in DB credentials, JWT secret, ML_SERVICE_URL
npm run seed            # inserts default expense/income categories
npm run dev              # starts on http://localhost:4000 with auto-reload
```

## API

- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `GET/POST /api/categories`, `DELETE /api/categories/:id`
- `GET/POST /api/transactions`, `PUT/DELETE /api/transactions/:id`, `GET /api/transactions/summary?month=YYYY-MM`
  - `POST` with `autoCategorize: true` and no `categoryId` calls the ML service to predict a category.
- `GET/POST /api/budgets`, `DELETE /api/budgets/:id`
- `GET/POST /api/savings-goals`, `PUT/DELETE /api/savings-goals/:id`
- `POST /api/ml/predict/category` — one-off category prediction (proxied)
- `GET /api/ml/predict/forecast` — next-month spend forecast from this user's history (proxied)

All routes except `/api/auth/register` and `/api/auth/login` require
`Authorization: Bearer <token>`.

## Test

```bash
npm test
```

Tests run against the `pfm_test` database (see `.env` `DB_NAME`, overridden
to `pfm_test` in `tests/setup.js`) and `sequelize.sync({ force: true })` on
each suite, so point it at a disposable database.
