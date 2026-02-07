from fastapi import FastAPI

from src.api.students import router as students_router

app = FastAPI(
    title="Simple Student CRUD API",
    description="Learning FastAPI + PostgreSQL without dependency injection",
    version="0.1.0",
)

app.include_router(students_router)


@app.get("/health")
async def health():
    return {"status": "ok"}