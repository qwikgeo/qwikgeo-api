"""FastGeoPortal App"""

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from routers import authentication

DESCRIPTION = """
A python api to create a geoportal.
"""

app = FastAPI(
    title="FastGeoportal",
    description=DESCRIPTION,
    version="0.0.1",
    contact={
        "name": "Michael Keller",
        "email": "michaelkeller03@gmail.com",
    },
    license_info={
        "name": "The MIT License (MIT)",
        "url": "https://mit-license.org/",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    authentication.router,
    prefix="/api/v1/authentication",
    tags=["Authentication"],
)

@app.get("/api/v1/health_check", tags=["Health"])
async def health():
    """
    Method used to verify server is healthy.
    """

    return {"status": "UP"}

DB_CONFIG = {
    "connections": {
        "default": "postgres://postgres:postgres@localhost:5432/geoportal"
    },
    "apps": {
        "models": {
            "models": ["db_models", "aerich.models"],
            "default_connection": "default",
        },
    }
}

register_tortoise(
    app,
    config=DB_CONFIG
)

Instrumentator().instrument(app).expose(app)