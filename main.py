"""FastGeoPortal App"""

from fastapi import FastAPI, Request
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

import db
import config
from routers.authentication import authentication
from routers.tables import tables
from routers.imports import imports
from routers.analysis import analysis
from routers.collections import collections

DESCRIPTION = """A python api to create a geoportal."""

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

@app.get("/api/v1/", tags=["Landing Page"])
async def landing_page(request: Request):
    """
    Method to show landing page.
    """

    url = str(request.base_url)

    return {
        "links": [
            {
                "rel": "self",
                "type": "application/json",
                "title": "This document as JSON",
                "href": f"{url}api/v1/"
            },
            {
                "rel": "conformance",
                "type": "application/json",
                "title": "Conformance",
                "href": f"{url}api/v1/conformance"
            },
            {
                "rel": "data",
                "type": "application/json",
                "title": "Collections",
                "href": f"{url}api/v1/collections"
            },
            {
                "rel": "service-desc",
                "type": "application/vnd.oai.openapi+json;version=3.0",
                "title": "The OpenAPI definition as JSON",
                "href": f"{url}openapi.json"
            }
        ],
        "title": "FastGeoPortal",
        "description": DESCRIPTION
    }

@app.get("/api/v1/conformance", tags=["Conformance"])
async def conformance(request: Request):
    """
    Method to show conformance
    """

    url = str(request.base_url)

    return {
        "conformsTo": [
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
            "http://www.opengis.net/spec/ogcapi-tiles-1/1.0/conf/core"
        ]
    }

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