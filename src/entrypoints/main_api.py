from fastapi import FastAPI
from src.api.router import router

app = FastAPI(
    title="LLM Engine Verifier",
    description="API for automating judicial process analysis using LLM.",
    version="1.0.0"
)

app.include_router(router)

# NOTE: To run this application locally for testing:
# uvicorn app.entrypoints.main_api:app --reload --port 8000