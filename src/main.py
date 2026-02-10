from fastapi import FastAPI

from src.api import students_router, items_router, register_router, auth_router, test_supa_router


app = FastAPI(
    title="Simple CRUD API",
    description="Learning FastAPI + PostgreSQL by sooooookrat",
)

app.include_router(students_router)
app.include_router(items_router)
app.include_router(register_router)
app.include_router(auth_router)
app.include_router(test_supa_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
