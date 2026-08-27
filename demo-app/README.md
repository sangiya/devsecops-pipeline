# demo-app

A minimal FastAPI service (`/healthz`, `/greet`, `/version`) used purely as
the target the `devsecops-pipeline` reusable workflows build, test, and
scan. Not itself a portfolio deliverable — see the root README.

```bash
pip install -e ".[dev]"
pytest --cov
uvicorn demo_app:create_app --factory --reload
```
