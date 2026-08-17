# PFM Mobile App

Flutter client for the AI-Based Personal Financial Management System. Talks
to the Node.js backend (`../backend`), which in turn proxies ML requests to
the Python service (`../ml-service`).

## Screens

- **Login / Register** — JWT auth against `/api/auth`.
- **Home** — monthly income/spend summary and the AI spend forecast.
- **Expenses** — transaction history, search, and "Add Transaction" with an
  AI auto-categorize toggle (calls the ML service via the backend).
- **Budget** — per-category monthly budgets with spend progress, and a link
  into Savings Goals.
- **Profile** — account info, AI/automation preferences, sign out.

## Setup

```bash
flutter pub get
```

The API base URL defaults to `http://10.0.2.2:4000/api` (the Android
emulator's alias for the host machine's localhost). Override it for a real
device or iOS simulator:

```bash
flutter run --dart-define=API_BASE_URL=http://<your-machine-ip>:4000/api
```

## Test

```bash
flutter test
```
