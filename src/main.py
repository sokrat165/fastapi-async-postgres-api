from fastapi import FastAPI

from src.api import students_router
# from src.mongo import connect_to_mongo, close_mongo_connection


app = FastAPI(
    title="Simple  CRUD API",
    description="Learning FastAPI + PostgreSQL  by sooooookrat",
)

app.include_router(students_router)


# @app.on_event("startup")
# async def on_startup():
#     await connect_to_mongo(app)


# @app.on_event("shutdown")
# async def on_shutdown():
#     await close_mongo_connection(app)


# @app.get("/health")
# async def health():
#     return {"status": "ok"}