# LawAssistant

End-to-end legal document assistant with a FastAPI backend (MongoDB + Redis + Celery) and a Flutter web frontend.

## Prerequisites
- Python 3.10+, MongoDB, Redis
- Flutter 3+ with Chrome/Web support
- Google Cloud service account JSON (Vision + Storage), OpenAI API key, VNCoreNLP & PhoNLP model folders

## Backend (app\backend)
```powershell
cd app\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in `app\backend`:
```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=lawassistant
JWT_SECRET_KEY=change-me
JWT_REFRESH_SECRET_KEY=change-me-too
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\gcp.json
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket
VNCORENLP_MODEL_PATH=C:\path\to\vncorenlp
PHONLP_MODEL_PATH=C:\path\to\phonlp
REDIS_URL=redis://localhost:6379/0
```

Run API:
```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Background workers (require Redis + env):
```powershell
python worker\worker.py                  # Celery worker (queue: documents)
celery --app=core.celery_app flower --port=5555   # Monitoring (optional)
```

Full stack via Docker (requires Docker, docker-compose):
```powershell
docker-compose up --build
```

## Frontend (app\frontend)
```powershell
cd app\frontend
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

Other useful commands:
```powershell
flutter analyze
flutter test
flutter build web --dart-define=API_BASE_URL=https://api.yourdomain.com
```
