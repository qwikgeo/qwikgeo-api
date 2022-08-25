from functools import reduce
from fastapi import Request, APIRouter, Depends, HTTPException, status
from pygeofilter.backends.sql import to_sql_where
from pygeofilter.parsers.ecql import parse
from tortoise.expressions import Q

import utilities
import db_models
import db

router = APIRouter()

@router.get("/", tags=["Collections"])
async def collections(request: Request, user_name: int=Depends(utilities.get_token_header)):
    """
    Method used to return a list of tables available to query.

    """

    db_tables = []

    user_groups = await utilities.get_user_groups(user_name)

    tables = await db_models.Table_Pydantic.from_queryset(db_models.Table.filter(reduce(lambda x, y: x | y, [Q(read_access_list__contains=[group]) for group in user_groups])))

    for table in tables:
        db_tables.append(
            {
                "name" : table.table_id,
                "schema" : "user_data",
                "type" : "table",
                "id" : f"user_data.{table.table_id}",
                "database" : db.DB_DATABASE
            }
        )

    return db_tables

@router.get("/{database}.{scheme}.{table}", tags=["Collections"])
async def collection(database: str, scheme: str, table: str, request: Request, user_name: int=Depends(utilities.get_token_header)):
    """
    Method used to return information about a collection.

    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app
    )

    url = str(request.base_url)

    return {
        "id": f"{database}.{scheme}.{table}",
        "title": f"{database}.{scheme}.{table}",
        "description": f"{database}.{scheme}.{table}",
        "keywords": [f"{database}.{scheme}.{table}"],
        "links": [
            {
                "type": "application/json",
                "rel": "self",
                "title": "Items as GeoJSON",
                "href": f"{url}api/v1/collections/{database}.{scheme}.{table}/items"
            }
        ],
        "extent": {
            "spatial": {
                "bbox": await utilities.get_table_bounds(
                    database=database,
                    scheme=scheme,
                    table=table,
                    app=request.app
                ),
                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            }
        },
        "itemType": "feature"
    }

@router.get("/{database}.{scheme}.{table}/items", tags=["Collections"])
async def items(database: str, scheme: str, table: str, request: Request,
    bbox: str=None, limit: int=200000, offset: int=0, properties: str="*",
    sortby :str="gid", filter :str=None, srid: int=4326, user_name: int=Depends(utilities.get_token_header)):
    """
    Method used to return geojson from a collection.

    """

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app
    )    

    blacklist_query_parameters = ["bbox","limit","offset","properties","sortby","filter"]

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
            WHERE table_name = '{table}'
            AND column_name != 'geom';
        """

        db_fields = await con.fetch(sql_field_query)

        if properties == '*':
            properties = ""
            for field in db_fields:
                column = field['column_name']
                properties += f'"{column}",'
            properties = properties[:-1]

        if new_query_parameters != []:

            for field in db_fields:
                if field['column_name'] in new_query_parameters:
                    if len(column_where_parameters) != 0:
                        column_where_parameters += " AND "
                    column_where_parameters += f" {field['column_name']} = '{request.query_params[field['column_name']]}' "

        if filter is not None:     

            field_mapping = {}  

            for field in db_fields:
                field_mapping[field['column_name']] = field['column_name']

            ast = parse(filter)
            filter = to_sql_where(ast, field_mapping)

            
    
        if filter is not None and column_where_parameters != "":
            filter += f" AND {column_where_parameters}"
        elif filter is None:
            filter = column_where_parameters
            
        results = await utilities.get_table_geojson(
            database=database,
            scheme=scheme,
            table=table,
            limit=limit,
            offset=offset,
            properties=properties,
            sort_by=sortby,
            bbox=bbox,
            filter=filter,
            srid=srid,
            app=request.app
        )

        return results

@router.get("/{database}.{scheme}.{table}/items/{id}", tags=["Collections"])
async def item(database: str, scheme: str, table: str, id:str, request: Request,
    properties: str="*", srid: int=4326, user_name: int=Depends(utilities.get_token_header)):
    """
    Method used to return geojson for one item of a collection.

    """    

    await utilities.validate_table_access(
        table=table,
        user_name=user_name,
        app=request.app
    )    

    pool = request.app.state.database

    async with pool.acquire() as con:

        sql_field_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table}'
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
            database=database,
            scheme=scheme,
            table=table,
            filter=f"gid = '{id}'",
            properties=properties,
            srid=srid,
            app=request.app
        )

        return results
