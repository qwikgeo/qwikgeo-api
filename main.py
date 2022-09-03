"""FastGeoPortal App"""

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

import db
import config
from routers.authentication import authentication
from routers.tables import tables
from routers.tiles import tiles
from routers.imports import imports
from routers.analysis import analysis
from routers.collections import collections

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

app.include_router(
    tables.router,
    prefix="/api/v1/tables",
    tags=["Tables"],
)

app.include_router(
    tiles.router,
    prefix="/api/v1/tiles",
    tags=["Tiles"],
)

app.include_router(
    imports.router,
    prefix="/api/v1/imports",
    tags=["Imports"],
)

app.include_router(
    analysis.router,
    prefix="/api/v1/analysis",
    tags=["Analysis"],
)

app.include_router(
    collections.router,
    prefix="/api/v1/collections",
    tags=["Collections"],
)

# Register Start/Stop application event handler to setup/stop the database connection
@app.on_event("startup")
async def startup_event():
    """Application startup: register the database connection and create table list."""
    await db.connect_to_db(app)

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: de-register the database connection."""
    await db.close_db_connection(app)

@app.get("/api/v1/health_check", tags=["Health"])
async def health():
    """
    Method used to verify server is healthy.
    """

    return {"status": "UP"}

DB_CONFIG = {
    "connections": {
        "default": f"postgres://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_DATABASE}"
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