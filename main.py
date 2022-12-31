"""QwikGeo API"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from prometheus_fastapi_instrumentator import Instrumentator

import db
import config
from routers.authentication import router as authentication_router
from routers.groups import router as groups_router
from routers.users import router as users_router
from routers.items import router as items_router
from routers.tables import router as tables_router
from routers.imports import router as imports_router
from routers.analysis import router as analysis_router
from routers.collections import router as collections_router
from routers.maps import router as maps_router

DESCRIPTION = """A python api to create a geoportal."""

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

app = FastAPI(
    title="QwikGeo API",
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
    authentication_router.router,
    prefix="/api/v1/authentication",
    tags=["Authentication"],
)

app.include_router(
    groups_router.router,
    prefix="/api/v1/groups",
    tags=["Groups"],
)

app.include_router(
    users_router.router,
    prefix="/api/v1/users",
    tags=["Users"],
)

app.include_router(
    items_router.router,
    prefix="/api/v1/items",
    tags=["Items"],
)

app.include_router(
    tables_router.router,
    prefix="/api/v1/tables",
    tags=["Tables"],
)

app.include_router(
    imports_router.router,
    prefix="/api/v1/imports",
    tags=["Imports"],
)

app.include_router(
    analysis_router.router,
    prefix="/api/v1/analysis",
    tags=["Analysis"],
)

app.include_router(
    collections_router.router,
    prefix="/api/v1/collections",
    tags=["Collections"],
)

app.include_router(
    maps_router.router,
    prefix="/api/v1/maps",
    tags=["Maps"],
)

@app.on_event("startup")
async def startup_event():
    """Application startup: register the database connection and create table list."""
    await db.connect_to_db(app)

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown: de-register the database connection."""

    await db.close_db_connection(app)

@app.get(
    path="/api/v1/",
    tags=["Landing Page"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "links": [
                            {
                                "rel": "self",
                                "type": "application/json",
                                "title": "This document as JSON",
                                "href": "https://api.qwikgeo.com/api/v1/"
                            },
                            {
                                "rel": "conformance",
                                "type": "application/json",
                                "title": "Conformance",
                                "href": "https://api.qwikgeo.com/api/v1/conformance"
                            },
                            {
                                "rel": "data",
                                "type": "application/json",
                                "title": "Collections",
                                "href": "https://api.qwikgeo.com/api/v1/collections"
                            },
                            {
                                "rel": "service-desc",
                                "type": "application/vnd.oai.openapi+json;version=3.0",
                                "title": "The OpenAPI definition as JSON",
                                "href": "https://api.qwikgeo.com/openapi.json"
                            }
                        ],
                        "title": "QwikGeo API",
                        "description": DESCRIPTION
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def landing_page(
    request: Request
):
    """Get landing page."""

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
        "title": "QwikGeo API",
        "description": DESCRIPTION
    }

@app.get(
    path="/api/v1/conformance",
    tags=["Conformance"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "conformsTo": [
                            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
                            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
                            "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/filter",
                            "http://www.opengis.net/spec/ogcapi-features-4/1.0/req/features",
                            "http://www.opengis.net/spec/ogcapi-tiles-1/1.0/conf/core"
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def conformance():
    """Get conformance of api."""

    return {
        "conformsTo": [
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
            "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/filter",
            "http://www.opengis.net/spec/ogcapi-features-4/1.0/req/features",
            "http://www.opengis.net/spec/ogcapi-tiles-1/1.0/conf/core"
        ]
    }

@app.get(
    path="/api/v1/health_check",
    tags=["Health"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {"status": "UP"}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "Internal Server Error"
                }
            }
        }
    }
)
async def health():
    """Method used to verify server is healthy."""

    return {"status": "UP"}

register_tortoise(
    app,
    config=DB_CONFIG,
    generate_schemas=True,
    add_exception_handlers=True
)


Instrumentator().instrument(app).expose(app)
