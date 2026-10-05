# ACEest Fitness & Gym - DevOps CI/CD Project

Flask web service for gym management (programs, clients, calorie estimation),
converted from the original Tkinter desktop versions, with a full CI/CD pipeline
using Git/GitHub, Pytest, Docker, GitHub Actions and Jenkins.

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service status |
| GET | `/health` | Health check |
| GET | `/programs` | List programs (FL, MG, BG) |
| GET | `/programs/<code>` | Workout, diet, calorie factor |
| POST | `/calories` | `{"weight": 70, "program": "FL"}` -> estimated calories |
| GET/POST | `/clients` | List / add client |
| GET/DELETE | `/clients/<name>` | Get / delete client |

## Local Setup
```bash
git clone https://github.com/YOUR_USERNAME/aceest-fitness.git
cd aceest-fitness
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py                   # runs on http://localhost:5000
```

## Run Tests Manually
```bash
pytest -v
flake8 . --max-line-length=100 --exclude=venv
```

## Docker
```bash
docker build -t aceest-fitness .
docker run -p 5000:5000 aceest-fitness
docker run --rm aceest-fitness pytest -v     # tests inside container
```

## CI/CD Overview
**GitHub Actions** (`.github/workflows/main.yml`) runs on every push / pull request:
1. **Build & Lint** - installs dependencies, syntax check (`py_compile`), `flake8`.
2. **Docker Build & Test** - builds the image and runs `pytest` inside the container.

**Jenkins** (`Jenkinsfile`) acts as the secondary build/quality gate: pulls the latest
code from GitHub, creates a clean virtualenv, installs dependencies, compiles, runs
tests and builds the Docker image.

## Branching & Commits
`main` is stable; work is done on `feature/*`, `bugfix/*`, `infra/*` branches and merged via PR.
