"""QwikGeo API - Collections"""

import os
import json
import shutil
import datetime
from typing import Optional
from fastapi import Request, APIRouter, Depends, status, Response, HTTPException
from starlette.responses import FileResponse
from pygeofilter.backends.sql import to_sql_where
from pygeofilter.parsers.ecql import parse
from tortoise.expressions import Q
import lark
import asyncpg

import routers.collections.models as models
import utilities
import config
import authentication_handler

router = APIRouter()

@router.get(
    path="/",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "collections": [
                            {
                                "id": "{table_id}",
                                "title": "string",
                                "description": "string",
                                "keywords": ["string"],
                                "links": [
                                    {
                                        "type": "application/json",
                                        "rel": "self",
                                        "title": "This document as JSON",
                                        "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}"
                                    }
                                ],
                                "geometry": "point",
                                "extent": {
                                    "spatial": {
                                        "bbox": [
                                            -180,
                                            -90,
                                            180,
                                            90
                                        ],
                                        "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                                    }
                                },
                                "itemType": "feature"
                            }
                        ]
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
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

async def collections(
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get a list of collections available to query.
    More information at https://docs.qwikgeo.com/collections/#collections
    """

    url = str(request.base_url)

    db_tables = []
    
    tables = await utilities.get_multiple_items_in_database(
        user_name=user_name,
        model_name="Table"
    )
    if len(tables) > 0:

        for table in tables:
            db_tables.append(
                {
                    "id" : f"{table.table_id}",
                    "title" : table.portal_id.title,
                    "description" : table.portal_id.description,
                    "keywords": table.portal_id.tags,
                    "links": [
                        {
                            "type": "application/json",
                            "rel": "self",
                            "title": "This document as JSON",
                            "href": f"{url}api/v1/collections/{table.table_id}"
                        },
                        {
                            "type": "application/geo+json",
                            "rel": "items",
                            "title": "Items as GeoJSON",
                            "href": f"{url}api/v1/collections/{table.table_id}/items"
                        },
                        {
                            "type": "application/json",
                            "rel": "queryables",
                            "title": "Queryables for this collection as JSON",
                            "href": f"{url}api/v1/collections/{table.table_id}/queryables"
                        },
                        {
                            "type": "application/json",
                            "rel": "tiles",
                            "title": "Tiles as JSON",
                            "href": f"{url}api/v1/collections/{table.table_id}/tiles"
                        }
                    ],
                    "geometry": await utilities.get_table_geometry_type(
                        table_id=table.table_id,
                        app=request.app
                    ),
                    "extent": {
                        "spatial": {
                            "bbox": await utilities.get_table_bounds(
                                table=table.table_id,
                                app=request.app
                            ),
                            "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                        }
                    },
                    "itemType": "feature"
                }
            )

    return {"collections": db_tables}

@router.get(
    path="/{table_id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "id": "{table_id}",
                        "title": "string",
                        "description": "string",
                        "keywords": ["string"],
                        "links": [
                            {
                                "type": "application/geo+json",
                                "rel": "self",
                                "title": "Items as GeoJSON",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}/items"
                            },
                            {
                                "type": "application/json",
                                "rel": "queryables",
                                "title": "Queryables for this collection as JSON",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}/queryables"
                            },
                            {
                                "type": "application/json",
                                "rel": "tiles",
                                "title": "Tiles as JSON",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}/tiles"
                            }
                        ],
                        "geometry": "point",
                        "extent": {
                            "spatial": {
                                "bbox": [
                                    -180,
                                    -90,
                                    180,
                                    90
                                ],
                                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                            }
                        },
                        "itemType": "feature"
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def collection(
    table_id: str,
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get information about a collection.
    More information at https://docs.qwikgeo.com/collections/#collection
    """

    print(user_name)

    item_metadata = await utilities.get_item_in_database(
        user_name=user_name,
        model_name="Table",
        query_filter=Q(table_id=table_id)
    )

    url = str(request.base_url)

    return {
        "id": f"{table_id}",
        "title" : item_metadata.portal_id.title,
        "description" : item_metadata.portal_id.description,
        "keywords": item_metadata.portal_id.tags,
        "links": [
            {
                "type": "application/json",
                "rel": "self",
                "title": "This document as JSON",
                "href": f"{url}api/v1/collections/{table_id}"
            },
            {
                "type": "application/geo+json",
                "rel": "items",
                "title": "Items as GeoJSON",
                "href": f"{url}api/v1/collections/{table_id}/items"
            },
            {
                "type": "application/json",
                "rel": "queryables",
                "title": "Queryables for this collection as JSON",
                "href": f"{url}api/v1/collections/{table_id}/queryables"
            },
            {
                "type": "application/json",
                "rel": "tiles",
                "title": "Tiles as JSON",
                "href": f"{url}api/v1/collections/{table_id}/tiles"
            }
        ],
        "geometry": await utilities.get_table_geometry_type(
            table_id=item_metadata.table_id,
            app=request.app
        ),
        "extent": {
            "spatial": {
                "bbox": await utilities.get_table_bounds(
                    table_id=table_id,
                    app=request.app
                ),
                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            }
        },
        "itemType": "feature"
    }

@router.get(
    path="/{table_id}/queryables",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "$id": "http://api.qwikgeo.com/api/v1/collections/{table_id}/queryables",
                        "title": "string",
                        "type": "object",
                        "$schema": "http://json-schema.org/draft/2019-09/schema",
                        "properties": {
                            "string": {
                                "title": "string",
                                "type": "numeric"
                            }
                        }
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def queryables(
    table_id: str,
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get queryable information about a collection.
    More information at https://docs.qwikgeo.com/collections/#queryables
    """

    item_metadata = await utilities.get_item_in_database(
        user_name=user_name,
        model_name="Table",
        query_filter=Q(table_id=table_id)
    )

    url = str(request.base_url)

    queryable = {
        "$id": f"{url}api/v1/collections/{table_id}/queryables",
        "title": item_metadata.portal_id.title,
        "type": "object",
        "$schema": "http://json-schema.org/draft/2019-09/schema",
        "properties": {}
    }

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table_id}'
            AND column_name != 'geom';
        """

        db_fields = await con.fetch(sql_field_query)

        for field in db_fields:
            data_type = 'string'
            if field['data_type'] in config.NUMERIC_FIELDS:
                data_type = 'numeric'
            queryable['properties'][field['column_name']] = {
                "title": field['column_name'],
                "type": data_type
            }

        return queryable

@router.get(
    path="/{table_id}/items",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [
                                        -88.8892,
                                        36.201015
                                    ]
                                },
                                "properties": {},
                                "id": 1
                            }
                        ],
                        "numberMatched": 56,
                        "numberReturned": 10,
                        "links": [
                            {
                                "type": "application/geo+json",
                                "rel": "self",
                                "title": "This document as GeoJSON",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}/items"
                            },
                            {
                                "type": "application/json",
                                "title": "{table_id}",
                                "rel": "collection",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}"
                            },
                            {
                                "type": "application/geo+json",
                                "rel": "next",
                                "title": "items (next)",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}/items?offset=10"
                            }
                        ]
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def items(
    table_id: str,
    request: Request,
    bbox: str=None,
    limit: int=10,
    offset: int=0,
    properties: str="*",
    sortby: str="gid",
    sortdesc: int=1,
    filter: str=None,
    srid: int=4326,
    return_geometry: bool=True,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get geojson from a collection.
    More information at https://docs.qwikgeo.com/collections/#items
    """

    url = str(request.base_url)

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name
    )

    blacklist_query_parameters = ["bbox","limit","offset","properties","sortby","sortdesc","filter","srid"]

    new_query_parameters = []

    for query in request.query_params:
        if query not in blacklist_query_parameters:
            new_query_parameters.append(query)

    column_where_parameters = ""

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table_id}'
            AND column_name != 'geom';
        """

        db_fields = await con.fetch(sql_field_query)

        fields = []

        for field in db_fields:
            fields.append(field['column_name'])

        if properties == '*':
            properties = ""
            for field in db_fields:
                column = field['column_name']
                properties += f'"{column}",'
            properties = properties[:-1]
        else:
            if len(properties) > 0:
                for property in properties.split(","):
                    if property not in fields:
                        raise HTTPException(
                            status_code=400,
                            detail=f"""Column: {property} is not a column for {table_id}."""
                        )

        if new_query_parameters:

            for field in db_fields:
                if field['column_name'] in new_query_parameters:
                    if len(column_where_parameters) != 0:
                        column_where_parameters += " AND "
                    column_where_parameters += f""" {field['column_name']} = '{request.query_params[field['column_name']]}' """

        if filter is not None:

            field_mapping = {}

            for field in db_fields:
                field_mapping[field['column_name']] = field['column_name']
            try:
                ast = parse(filter)
            except lark.exceptions.UnexpectedToken as exc:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid operator used in filter."
                ) from exc
            try:
                filter = to_sql_where(ast, field_mapping)
            except KeyError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=f"""Invalid column in filter parameter for {table_id}."""
                ) from exc


        if filter is not None and column_where_parameters != "":
            filter += f" AND {column_where_parameters}"
        elif filter is None:
            filter = column_where_parameters

        results = await utilities.get_table_geojson(
            table_id=table_id,
            limit=limit,
            offset=offset,
            properties=properties,
            sortby=sortby,
            sortdesc=sortdesc,
            bbox=bbox,
            filter=filter,
            srid=srid,
            return_geometry=return_geometry,
            app=request.app
        )

        results['timeStamp'] = f"{datetime.datetime.utcnow().isoformat()}Z"

        results['links'] = [
            {
                "type": "application/geo+json",
                "rel": "self",
                "title": "This document as GeoJSON",
                "href": request.url._url
            },
            {
                "type": "application/json",
                "title": f"{table_id}",
                "rel": "collection",
                "href": f"{url}api/v1/collections/{table_id}"
            }
        ]

        extra_params = ""

        for param in request.query_params:
            if param != 'offset':
                extra_params += f"&{param}={request.query_params[param]}"

        if (results['numberReturned'] + offset) < results['numberMatched']:
            href = f"{str(request.base_url)[:-1]}{request.url.path}?offset={offset+limit}"
            if len(extra_params)> 0:
                href += extra_params
            results['links'].append({
                "type": "application/geo+json",
                "rel": "next",
                "title": "items (next)",
                "href": href
            })

        if (offset - limit) > -1:
            href = f"{str(request.base_url)[:-1]}{request.url.path}?offset={offset-limit}"
            if len(extra_params)> 0:
                href += extra_params
            results['links'].append({
                "type": "application/geo+json",
                "rel": "prev",
                "title": "items (prev)",
                "href": href
            })

        return results

@router.post(
    path="/{table_id}/items",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                -88.8892,
                                36.201015
                            ]
                        },
                        "properties": {},
                        "id": 1
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def create_item(
    table_id: str,
    info: models.Geojson,
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Create a new item to a collection.
    More information at https://docs.qwikgeo.com/collections/#create-item
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table_id}'
        AND column_name != 'geom'
        AND column_name != 'gid';
        """

        db_fields = await con.fetch(sql_field_query)

        db_columns = []

        db_column_types = {}

        for field in db_fields:
            db_columns.append(field['column_name'])
            db_column_types[field['column_name']] = {
                "used": False,
                "type": field['data_type']
            }

        string_columns = ",".join(db_columns)

        input_columns = ""
        values = ""

        for column in info.properties:
            if column not in db_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"""Column: {column} is not a column for {table_id}.
                    Please use one of the following columns. {string_columns}"""
                )
            input_columns += f""""{column}","""
            if db_column_types[column]['type'] in config.NUMERIC_FIELDS:
                values += f"""{float(info.properties[column])},"""
            else:
                values += f"""'{info.properties[column]}',"""

            db_column_types[column]['used'] = True

        for column in db_column_types:
            if db_column_types[column]['used'] is False:
                raise HTTPException(
                    status_code=400,
                    detail=f"""Column {column} was not used. Add {column} to your properties."""
                )

        input_columns = input_columns[:-1]
        values = values[:-1]

        query = f"""
            INSERT INTO user_data."{table_id}" ({input_columns})
            VALUES ({values})
            RETURNING gid;
        """

        result = await con.fetch(query)

        geojson = {
            "type": info.geometry.type,
            "coordinates": json.loads(json.dumps(info.geometry.coordinates))
        }

        geom_query = f"""
            UPDATE user_data."{table_id}"
            SET geom = ST_GeomFromGeoJSON('{json.dumps(geojson)}')
            WHERE gid = {result[0]['gid']};
        """

        await con.fetch(geom_query)

        if os.path.exists(f'{os.getcwd()}/cache/user_data{table_id}'):
            shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table_id}')

        info.properties['gid'] = result[0]['gid']

        info.id = result[0]['gid']

        return info

@router.get(
    path="/{table_id}/items/{id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                -88.8892,
                                36.201015
                            ]
                        },
                        "properties": {},
                        "id": 1,
                        "links": [
                            {
                                "type": "application/geo+json",
                                "rel": "self",
                                "title": "This document as GeoJSON",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}/items/1"
                            },
                            {
                                "type": "application/geo+json",
                                "title": "items as GeoJSON",
                                "rel": "items",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}/items"
                            },
                            {
                                "type": "application/json",
                                "title": "{table_id}",
                                "rel": "collection",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}"
                            }
                        ]
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def item(
    table_id: str,
    id: str,
    request: Request,
    properties: str="*",
    return_geometry: bool=True,
    srid: int=4326,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get geojson for one item of a collection.
    More information at https://docs.qwikgeo.com/collections/#item
    """

    url = str(request.base_url)

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table_id}'
            AND column_name != 'geom';
        """

        db_fields = await con.fetch(sql_field_query)

        if properties == '*':
            properties = ""
            for field in db_fields:
                column = field['column_name']
                properties += f'"{column}",'
            properties = properties[:-1]

        results = await utilities.get_table_geojson(
            table_id=table_id,
            filter=f"gid = '{id}'",
            properties=properties,
            return_geometry=return_geometry,
            srid=srid,
            app=request.app
        )

        results['features'][0]['links'] = [
            {
                "type": "application/geo+json",
                "rel": "self",
                "title": "This document as GeoJSON",
                "href": request.url._url
            },
            {
                "type": "application/geo+json",
                "title": "items as GeoJSON",
                "rel": "items",
                "href": f"{url}api/v1/collections/{table_id}/items"
            },
            {
                "type": "application/json",
                "title": f"{table_id}",
                "rel": "collection",
                "href": f"{url}api/v1/collections/{table_id}"
            }
        ]

        return results['features'][0]

@router.put(
    path="/{table_id}/items/{id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                -88.8892,
                                36.201015
                            ]
                        },
                        "properties": {},
                        "id": 1
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def update_item(
    table_id: str,
    id: int,
    info: models.Geojson,
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Update an item in a collection.
    More information at https://docs.qwikgeo.com/collections/#update-item
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table_id}'
        AND column_name != 'geom'
        AND column_name != 'gid';
        """

        db_fields = await con.fetch(sql_field_query)

        db_columns = []

        db_column_types = {}

        for field in db_fields:
            db_columns.append(field['column_name'])
            db_column_types[field['column_name']] = {
                "type": field['data_type'],
                "used": False,
            }

        string_columns = ",".join(db_columns)

        exist_query = f"""
        SELECT count(*)
        FROM user_data."{table_id}"
        WHERE gid = {id}
        """

        exists = await con.fetchrow(exist_query)

        if exists['count'] == 0:
            raise HTTPException(
                    status_code=400,
                    detail=f"""Item {info.id} does not exist."""
                )

        query = f"""
            UPDATE user_data."{table_id}"
            SET 
        """

        for column in info.properties:
            if column not in db_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"""Column: {column} is not a column for {table_id}.
                    Please use one of the following columns. {string_columns}"""
                )
            if db_column_types[column]['type'] in config.NUMERIC_FIELDS:
                query += f"{column} = {info.properties[column]},"
            else:
                query += f"{column} = '{info.properties[column]}',"

            db_column_types[column]['used'] = True

        for column in db_column_types:
            if db_column_types[column]['used'] is False:
                raise HTTPException(
                    status_code=400,
                    detail=f"""Column {column} was not used. Add {column} to your properties."""
                )

        query = query[:-1]

        query += f" WHERE gid = {info.id};"

        await con.fetch(query)

        geojson = {
            "type": info.geometry.type,
            "coordinates": json.loads(json.dumps(info.geometry.coordinates))
        }

        geom_query = f"""
            UPDATE user_data."{table_id}"
            SET geom = ST_GeomFromGeoJSON('{json.dumps(geojson)}')
            WHERE gid = {id};
        """

        await con.fetch(geom_query)

        if os.path.exists(f'{os.getcwd()}/cache/user_data_{table_id}'):
            shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table_id}')

        return info

@router.patch(
    path="/{table_id}/items/{id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                -88.8892,
                                36.201015
                            ]
                        },
                        "properties": {},
                        "id": 1
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def modify_item(
    table_id: str,
    id: int,
    info: models.Geojson,
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Modify an item in a collection.
    More information at https://docs.qwikgeo.com/collections/#modify-item
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table_id}'
        AND column_name != 'geom'
        AND column_name != 'gid';
        """

        db_fields = await con.fetch(sql_field_query)

        db_columns = []

        db_column_types = {}

        for field in db_fields:
            db_columns.append(field['column_name'])
            db_column_types[field['column_name']] = {
                "type": field['data_type']
            }

        string_columns = ",".join(db_columns)

        exist_query = f"""
        SELECT count(*)
        FROM user_data."{table_id}"
        WHERE gid = {id}
        """

        exists = await con.fetchrow(exist_query)

        if exists['count'] == 0:
            raise HTTPException(
                    status_code=400,
                    detail=f"""Item {info.id} does not exist."""
                )

        query = f"""
            UPDATE user_data."{table_id}"
            SET 
        """

        for column in info.properties:
            if column not in db_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"""Column: {column} is not a column for {table_id}.
                    Please use one of the following columns. {string_columns}"""
                )
            if db_column_types[column]['type'] in config.NUMERIC_FIELDS:
                query += f"{column} = {info.properties[column]},"
            else:
                query += f"{column} = '{info.properties[column]}',"

        query = query[:-1]

        query += f" WHERE gid = {id};"

        await con.fetch(query)

        geojson = {
            "type": info.geometry.type,
            "coordinates": json.loads(json.dumps(info.geometry.coordinates))
        }

        geom_query = f"""
            UPDATE user_data."{table_id}"
            SET geom = ST_GeomFromGeoJSON('{json.dumps(geojson)}')
            WHERE gid = {id};
        """

        await con.fetch(geom_query)

        if os.path.exists(f'{os.getcwd()}/cache/user_data_{table_id}'):
            shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table_id}')

        return info

@router.delete(
    path="/{table_id}/items/{id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "status": True
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def delete_item(
    table_id: str,
    id: int,
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Delete an item in a collection.
    More information at https://docs.qwikgeo.com/collections/#delete-item
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name,
        write_access=True
    )

    pool = request.app.state.database

    async with pool.acquire() as con:
        query = f"""
            DELETE FROM user_data."{table_id}"
            WHERE gid = {id};
        """

        await con.fetch(query)

        if os.path.exists(f'{os.getcwd()}/cache/user_data_{table_id}'):
            shutil.rmtree(f'{os.getcwd()}/cache/user_data_{table_id}')

        return {"status": True}

@router.get(
    path="/{table_id}/tiles",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "id": "{table_id}",
                        "title": "string",
                        "description": "string",
                        "links": [
                            {
                                "type": "application/json",
                                "rel": "self",
                                "title": "This document as JSON",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}/tiles"
                            },
                            {
                                "type": "application/vnd.mapbox-vector-tile",
                                "rel": "item",
                                "title": "This collection as Mapbox vector tiles",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}",
                                "templated": True
                            },
                            {
                                "type": "application/json",
                                "rel": "describedby",
                                "title": "Metadata for this collection in the TileJSON format",
                                "href": "http://api.qwikgeo.com/api/v1/collections/{table_id}/tiles/{tile_matrix_set_id}/metadata",
                                "templated": True
                            }
                        ],
                        "tileMatrixSetLinks": [
                            {
                                "tileMatrixSet": "WorldCRS84Quad",
                                "tileMatrixSetURI": "http://schemas.opengis.net/tms/1.0/json/examples/WorldCRS84Quad.json"
                            }
                        ]
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def tiles(
    table_id: str,
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get tile information about a collection.
    More information at https://docs.qwikgeo.com/collections/#tiles
    """

    item_metadata = await utilities.get_item_in_database(
        user_name=user_name,
        model_name="Table",
        query_filter=Q(table_id=table_id)
    )

    url = str(request.base_url)

    mvt_path = "{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}"

    tile_info = {
        "id": f"{table_id}",
        "title": item_metadata.portal_id.title,
        "description": item_metadata.portal_id.description,
        "links": [
            {
                "type": "application/json",
                "rel": "self",
                "title": "This document as JSON",
                "href": f"{url}api/v1/collections/{table_id}/tiles",
            },
            {
                "type": "application/vnd.mapbox-vector-tile",
                "rel": "item",
                "title": "This collection as Mapbox vector tiles",
                "href": f"{url}api/v1/collections/{table_id}/tiles/{mvt_path}",
                "templated": True
            },
            {
                "type": "application/json",
                "rel": "describedby",
                "title": "Metadata for this collection in the TileJSON format",
                "href": f"{url}api/v1/collections/{table_id}/tiles/{{tile_matrix_set_id}}/metadata",
                "templated": True
            }
        ],
        "tileMatrixSetLinks": [
            {
                "tileMatrixSet": "WorldCRS84Quad",
                "tileMatrixSetURI": "http://schemas.opengis.net/tms/1.0/json/examples/WorldCRS84Quad.json"
            }
        ]
    }

    return tile_info

@router.get(
    path="/{table_id}/tiles/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/vnd.mapbox-vector-tile": {}
            }
        },
        204: {
            "description": "No Content",
            "content": {
                "application/vnd.mapbox-vector-tile": {}
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def tile(
    table_id: str,
    tile_matrix_set_id: str,
    tile_matrix: int,
    tile_row: int,
    tile_col: int,
    request: Request,
    fields: Optional[str] = None,
    cql_filter: Optional[str] = None,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get a vector tile for a given table.
    More information at https://docs.qwikgeo.com/collections/#tile
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name
    )

    pbf, tile_cache = await utilities.get_tile(
        table_id=table_id,
        tile_matrix_set_id=tile_matrix_set_id,
        z=tile_matrix,
        x=tile_row,
        y=tile_col,
        fields=fields,
        cql_filter=cql_filter,
        app=request.app
    )

    response_code = status.HTTP_200_OK

    max_cache_age = config.CACHE_AGE_IN_SECONDS

    if fields is not None and cql_filter is not None:
        max_cache_age = 0

    if tile_cache:
        return FileResponse(
            path=f'{os.getcwd()}/cache/user_data_{table_id}/{tile_matrix_set_id}/{tile_matrix}/{tile_row}/{tile_col}',
            media_type="application/vnd.mapbox-vector-tile",
            status_code=response_code,
            headers = {
                "Cache-Control": f"max-age={max_cache_age}",
                "tile-cache": 'true'
            }
        )

    if pbf == b"":
        response_code = status.HTTP_204_NO_CONTENT

    return Response(
        content=bytes(pbf),
        media_type="application/vnd.mapbox-vector-tile",
        status_code=response_code,
        headers = {
            "Cache-Control": f"max-age={max_cache_age}",
            "tile-cache": 'false'
        }
    )

@router.get(
    path="/{table_id}/tiles/{tile_matrix_set_id}/metadata",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "tilejson": "3.0.0",
                        "name": "{table_id}",
                        "tiles": "http://api.qwikgeo.com/api/v1/collections/{table_id}/tiles/WorldCRS84Quad/{tile_matrix}/{tile_row}/{tile_col}?f=mvt",
                        "minzoom": "0",
                        "maxzoom": "22",
                        "attribution": "string",
                        "description": "string",
                        "vector_layers": [
                            {
                                "id": "{table_id}",
                                "description": "string",
                                "minzoom": 0,
                                "maxzoom": 22,
                                "fields": {}
                            }
                        ]
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def tiles_metadata(
    table_id: str,
    tile_matrix_set_id: str,
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get tile metadata for a given table.
    More information at https://docs.qwikgeo.com/collections/#tiles-metadata
    """

    item_metadata = await utilities.get_item_in_database(
        user_name=user_name,
        model_name="Table",
        query_filter=Q(table_id=table_id)
    )

    url = str(request.base_url)

    mvt_path = f"{tile_matrix_set_id}/{{tile_matrix}}/{{tile_row}}/{{tile_col}}?f=mvt"

    metadata = {
        "tilejson": "3.0.0",
        "name": f"{table_id}",
        "tiles": f"{url}api/v1/collections/{table_id}/tiles/{mvt_path}",
        "minzoom": "0",
        "maxzoom": "22",
        # "bounds": "-124.953634,-16.536406,109.929807,66.969298",
        # "center": "-84.375000,44.951199,5",
        "attribution": None,
        "description": item_metadata.portal_id.description,
        "vector_layers": [
            {
                "id": f"{table_id}",
                "description": item_metadata.portal_id.description,
                "minzoom": 0,
                "maxzoom": 22,
                "fields": {}
            }
        ]
    }

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table_id}'
            AND column_name != 'geom';
        """

        db_fields = await con.fetch(sql_field_query)

        for field in db_fields:
            data_type = 'string'
            if field['data_type'] in config.NUMERIC_FIELDS:
                data_type = 'numeric'
            metadata['vector_layers'][0]['fields'][field['column_name']] = data_type

        return metadata

@router.get(
    path="/{table_id}/tiles/cache_size",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "size_in_gigabytes": 0
                    }
                }
            }
        }
    }
)
async def get_tile_cache_size(
    table_id: str,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get size of cache for table.
    More information at https://docs.qwikgeo.com/collections/#cache-size
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name
    )

    size = 0

    cache_path = f'{os.getcwd()}/cache/user_data_{table_id}'

    if os.path.exists(cache_path):
        for path, dirs, files in os.walk(cache_path):
            for file in files:
                file_path = os.path.join(path, file)
                size += os.path.getsize(file_path)

    return {"size_in_gigabytes": size*.000000001}

@router.delete(
    path="/{table_id}/tiles/cache",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "status": "deleted"
                    }
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def delete_tile_cache(
    table_id: str,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Delete cache for a table.
    More information at https://docs.qwikgeo.com/collections/#delete-cache
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name
    )

    utilities.delete_user_tile_cache(table_id)

    return {"status": "deleted"}

@router.post(
    path="/{table_id}/statistics",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "results": {
                            "count_gid": 19,
                            "avg_deed_ac": 64.28666666666666,
                            "distinct_first_name_count_first_name": [
                                {
                                    "first_name": "",
                                    "count": 3
                                },
                                {
                                    "first_name": "COLE",
                                    "count": 3
                                },
                                {
                                    "first_name": "% BAS",
                                    "count": 2
                                }
                            ]
                        },
                        "status": "SUCCESS"
                    }
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "One of the columns used does not exist for {table_id}."}
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def statistics(
    table_id: str,
    info: models.StatisticsModel,
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Retrieve statistics for a table.
    More information at https://docs.qwikgeo.com/tables/#statistics
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name
    )
    pool = request.app.state.database

    async with pool.acquire() as con:

        final_results= {}
        cols = []
        col_names = []
        distinct = False
        general_stats = False

        for aggregate in info.aggregate_columns:
            if aggregate.type == 'distinct':
                distinct = True
            else:
                general_stats = True
                cols.append(f"""
                {aggregate.type }("{aggregate.column}") as {aggregate.type}_{aggregate.column}
                """)
                col_names.append(f"{aggregate.type}_{aggregate.column}")

        if general_stats:
            formatted_columns = ','.join(cols)
            query = f"""
                SELECT {formatted_columns}
                FROM user_data."{table_id}"
            """

            query += await utilities.generate_where_clause(info, con)

            try:
                data = await con.fetchrow(query)
            
            except asyncpg.exceptions.UndefinedColumnError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'One of the columns used does not exist for {table_id}.'
                )

            for col in col_names:
                final_results[col] = data[col]

        if distinct:
            for aggregate in info.aggregate_columns:
                if aggregate.type == 'distinct':
                    query = f"""
                    SELECT DISTINCT("{aggregate.column}"), {aggregate.group_method}("{aggregate.group_column}") 
                    FROM user_data."{table_id}" """

                    query += await utilities.generate_where_clause(info, con)

                    query += f"""
                    GROUP BY "{aggregate.column}"
                    ORDER BY "{aggregate.group_method}" DESC"""

                    try:
                        data = await con.fetchrow(query)
                    
                    except asyncpg.exceptions.UndefinedColumnError:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'One of the columns used does not exist for {table_id}.'
                        )

                    final_results[
                        f"""distinct_{aggregate.column}_{aggregate.group_method}_{aggregate.group_column}"""
                    ] = data

        return {
            "results": final_results,
            "status": "SUCCESS"
        }

@router.post(
    path="/{table_id}/bins",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "min": 0.0,
                                "max": 145.158,
                                "count": 15993
                            },
                            {
                                "min": 145.158,
                                "max": 290.316,
                                "count": 1088
                            },
                        ],
                        "status": "SUCCESS"
                    }
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Column: {column} does not exists for {table_id}."}
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def bins(
    table_id: str,
    info: models.BinsModel,
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Retrieve a numerical column's bins for a table.
    More information at https://docs.qwikgeo.com/tables/#bins
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name
    )

    pool = request.app.state.database

    async with pool.acquire() as con:
        results = [

        ]
        query = f"""
            SELECT MIN("{info.column}"),MAX("{info.column}")
            FROM user_data."{table_id}"
        """

        query += await utilities.generate_where_clause(info, con)        

        try:
            data = await con.fetchrow(query)
        
        except asyncpg.exceptions.UndefinedColumnError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Column: {info.column} does not exist for {table_id}.'
            ) from exc

        group_size = (data['max'] - data['min']) / info.number_of_bins

        for group in range(info.number_of_bins):
            if group == 0:
                minimum = data['min']
                maximum = group_size
            else:
                minimum = group*group_size
                maximum = (group+1)*group_size
            query = f"""
                SELECT COUNT(*)
                FROM user_data."{table_id}"
                WHERE "{info.column}" > {minimum}
                AND "{info.column}" <= {maximum}
            """

            query += await utilities.generate_where_clause(info, con, True)

            data = await con.fetchrow(query)

            results.append({
                "min": minimum,
                "max": maximum,
                "count": data['count']
            })

        return {
            "results": results,
            "status": "SUCCESS"
        }

@router.post(
    path="/{table_id}/numeric_breaks",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "min": 0.0,
                                "max": 145.158,
                                "count": 15993
                            },
                            {
                                "min": 145.158,
                                "max": 290.316,
                                "count": 1088
                            },
                        ],
                        "status": "SUCCESS"
                    }
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Column: {column} does not exists for {table_id}."}
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def numeric_breaks(
    table_id: str,
    info: models.NumericBreaksModel,
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Retrieve a numerical column's breaks for a table.
    More information at https://docs.qwikgeo.com/tables/#numeric-breaks
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name
    )

    pool = request.app.state.database

    async with pool.acquire() as con:
        results = [

        ]

        if info.break_type == "quantile":
            query = f"""
                SELECT {info.break_type}_bins(array_agg(CAST("{info.column}" AS integer)), {info.number_of_breaks}) 
                FROM user_data."{table_id}"
            """
        else:
            query = f"""
                SELECT {info.break_type}_bins(array_agg("{info.column}"), {info.number_of_breaks}) 
                FROM user_data."{table_id}"
            """

        query += await utilities.generate_where_clause(info, con)

        try:
            break_points = await con.fetchrow(query)
        
        except asyncpg.exceptions.UndefinedColumnError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Column: {info.column} does not exist for {table_id}.'
            ) from exc

        min_query = f"""
            SELECT MIN("{info.column}")
            FROM user_data."{table_id}"
        """

        min_query += await utilities.generate_where_clause(info, con)

        min_number = await con.fetchrow(min_query)

        for index, max_number in enumerate(break_points[f"{info.break_type}_bins"]):
            if index == 0:
                minimum = min_number['min']
                maximum = max_number
            else:
                minimum = break_points[f"{info.break_type}_bins"][index-1]
                maximum = max_number
            query = f"""
                SELECT COUNT(*)
                FROM user_data."{table_id}"
                WHERE "{info.column}" > {minimum}
                AND "{info.column}" <= {maximum}
            """

            query += await utilities.generate_where_clause(info, con, True)

            data = await con.fetchrow(query)

            results.append({
                "min": minimum,
                "max": maximum,
                "count": data['count']
            })

        return {
            "results": results,
            "status": "SUCCESS"
        }

@router.post(
    path="/{table_id}/custom_break_values",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "min": 0.0,
                                "max": 145.158,
                                "count": 15993
                            },
                            {
                                "min": 145.158,
                                "max": 290.316,
                                "count": 1088
                            },
                        ],
                        "status": "SUCCESS"
                    }
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Column: {column} does not exists for {table_id}."}
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def custom_break_values(
    table_id: str,
    info: models.CustomBreaksModel,
    request: Request,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """
    Retrieve custom break values for a column for a table.
    More information at https://docs.qwikgeo.com/tables/#numeric-breaks
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name
    )

    pool = request.app.state.database

    async with pool.acquire() as con:
        results = [

        ]

        for break_range in info.breaks:
            minimum = break_range.min
            maximum = break_range.max

            query = f"""
                SELECT COUNT(*)
                FROM user_data."{table_id}"
                WHERE "{info.column}" > {minimum}
                AND "{info.column}" <= {maximum}
            """

            query += await utilities.generate_where_clause(info, con, True)

            try:
                data = await con.fetchrow(query)
            
            except asyncpg.exceptions.UndefinedColumnError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Column: {info.column} does not exist for {table_id}.'
                ) from exc

            results.append({
                "min": minimum,
                "max": maximum,
                "count": data['count']
            })

        return {
            "results": results,
            "status": "SUCCESS"
        }

@router.get(
    path="/{table_id}/autocomplete/",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": ["str","str"]
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Column: {column} does not exists for {table_id}."}
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to table."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Table does not exist."}
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
async def autocomplete(
    table_id: str,
    column: str,
    q: str,
    request: Request,
    limit: int=10,
    user_name: int=Depends(authentication_handler.JWTBearer()),

):
    """
    Retrieve distinct values for a column in a table.
    More information at https://docs.qwikgeo.com/tables/#table-autocomplete
    """

    await utilities.validate_item_access(
        model_name="Table",
        query_filter=Q(table_id=table_id),
        user_name=user_name
    )

    pool = request.app.state.database

    async with pool.acquire() as con:

        results = []

        query = f"""
            SELECT distinct("{column}")
            FROM user_data.{table_id}
            WHERE "{column}" ILIKE '%{q}%'
            ORDER BY "{column}"
            LIMIT {limit}
        """

        try:
            data = await con.fetch(query)
        
        except asyncpg.exceptions.UndefinedColumnError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Column: {column} does not exist for {table_id}.'
            )

        for row in data:
            results.append(row[column])

        return results