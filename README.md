# LawAssistant

LawAssistant is a Vietnamese legal assistant application with:
- a FastAPI backend in `app/backend`
- a Flutter frontend in `app/frontend`
- an optional Celery worker for backend document-processing jobs

`src/` is kept as the original experimental codebase used during feature development. It is not the main production app surface.

## Main App Structure
```text
app/
  backend/    FastAPI backend
    routers/        API routes
    controllers/    request handling
    services/       business logic
    repositories/   data access
    models/         backend models
    dto/            request/response schemas
    core/           config, security, celery, shared runtime
    infrastructure/ concrete DB and processing implementations
    pipeline/       backend retrieval pipeline
    knowledge_graph/ backend ingestion and KG processing
    worker/         Celery worker and tasks
  frontend/   Flutter web/desktop client
src/          original experimental and research code
docs/         diagrams and documentation
data/         datasets and local artifacts
scripts/      one-off utilities and experiments
```

## Backend

### Requirements
- Python 3.10+
- MongoDB
- Redis
- Optional external services for worker flows:
  - OpenAI API key
  - Google Cloud service-account JSON
  - VNCoreNLP model directory
  - PhoNLP model directory

### Local Run
```bash
cd app/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Windows PowerShell:
```powershell
cd app\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Backend Environment
Create `app/backend/.env`:

```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=law_assistant

JWT_SECRET_KEY=change-me
JWT_REFRESH_SECRET_KEY=change-me-too
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_URL=redis://localhost:6379/0

OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket
VNCORENLP_MODEL_PATH=/absolute/path/to/VnCoreNLP-1.2
PHONLP_MODEL_PATH=/absolute/path/to/phonlp
```

### Backend Endpoints
When running locally:
- API root: `http://localhost:8000`
- OpenAPI schema: `http://localhost:8000/openapi.json`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Worker
Run the worker only if you need background document-processing tasks:

```bash
cd app/backend
python worker/worker.py
```

Optional Flower dashboard:
```bash
cd app/backend
celery --app=core.celery_app flower --port=5555
```

## Frontend

### Local Run
```bash
cd app/frontend
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

Useful commands:
```bash
flutter analyze
flutter test
flutter build web --dart-define=API_BASE_URL=https://api.yourdomain.com
```

### Frontend Environment
The frontend primarily reads `API_BASE_URL` from `--dart-define`.

If you use the local dotenv setup, create `app/frontend/.env`:

```env
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30000
```

## Docker

The root `docker-compose.yml` is the main local container setup for backend + frontend.

Start the stack:
```bash
docker compose up --build
```

This starts:
- MongoDB on `localhost:27017`
- Redis on `localhost:6379`
- Backend on `http://localhost:8000`
- Frontend on `http://localhost:3000`

Start the optional worker profile:
```bash
docker compose --profile worker up --build
```

Stop the stack:
```bash
docker compose down
```

## Experimental Code

`src/` contains the original experimental retrieval, extraction, and pipeline code used while developing features. Keep using `app/backend` and `app/frontend` as the main application entry points.

## Diagrams
### System Context
![System context diagram](docs/c4/System_context_diagram.png)

### Container
![Container diagram](docs/c4/Container_diagram.png)

### Backend Components
![Backend component diagram](docs/c4/Component_diagram_BE.svg)
