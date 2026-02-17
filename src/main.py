from fastapi import FastAPI

from src.api import (students_router, items_router, register_router, auth_router,
                      qanda_router_ai,qanda_router, chat_router, files_router,
                      file_prompt)


app = FastAPI(
    title="Simple CRUD API",
    description="Learning FastAPI + PostgreSQL by sooooookrat",
)

app.include_router(students_router)
app.include_router(items_router)
app.include_router(register_router)
app.include_router(auth_router)
app.include_router(qanda_router_ai)
app.include_router(qanda_router)
app.include_router(chat_router)
app.include_router(files_router)
app.include_router(file_prompt)

@app.get("/health")
async def health():
    return {"status": "ok"}
