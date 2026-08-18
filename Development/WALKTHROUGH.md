# Walkthrough: Deploy & Run a Live Inference

Fastest path to a real prediction from the trained model. ~5 minutes.

## 1. Set up the ML service

```bash
cd Development/ml-service
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Train the classifier

```bash
python train.py
```

Generates synthetic training data, trains Logistic Regression and Random
Forest, picks the better one by F1 score, and saves it to `models/`.

## 3. Serve it

```bash
uvicorn app.main:app --port 8000
```

## 4. Run a live inference

In another terminal:

```bash
curl -X POST http://localhost:8000/predict/category \
  -H "Content-Type: application/json" \
  -d '{"merchant":"Netflix","description":"Monthly subscription","amount":14.0}'
```

Expected response — a real prediction from the model you just trained:

```json
{"category":"Entertainment","confidence":0.86}
```

Try `/predict/forecast` too:

```bash
curl -X POST http://localhost:8000/predict/forecast \
  -H "Content-Type: application/json" \
  -d '{"history":[{"month":"2026-06","total":100},{"month":"2026-07","total":150},{"month":"2026-08","total":210}]}'
```

## 5. (Optional) See it wired into the full app

The backend proxies these same endpoints and the Flutter app calls the
backend. To run the full stack:

```bash
# PostgreSQL must be running and reachable — see backend/.env.example
cd Development/backend
npm install && cp .env.example .env && npm run seed && npm run dev   # :4000

cd Development/mobile
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:4000/api      # Android emulator
```

Register a user in the app, add a transaction with "Auto-categorize with
AI" on, and watch the same model above categorize it live.
