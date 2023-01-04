"""QwikGeo API - Maps"""

from fastapi import APIRouter, Depends
from tortoise.expressions import Q

# import routers.tables.models as models
from qwikgeo_api import utilities
from qwikgeo_api import db_models
from qwikgeo_api import authentication_handler

router = APIRouter()

@router.get(
    path="/{map_id}",
    response_model=db_models.Map_Pydantic,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "No access to item."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Item does not exist."}
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
async def get_map(
    map_id: str,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get a map.
    More information at https://docs.qwikgeo.com/maps/#map
    """

    map_information = await utilities.get_item_in_database(
        username=username,
        model_name="Map",
        query_filter=Q(map_id=map_id)
    )

    return map_information

@router.post(
    path="/",
    response_model=db_models.Map_Pydantic,
    responses={
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
async def create_map(
    item: db_models.Map_Pydantic,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Create a new map.
    More information at https://docs.qwikgeo.com/maps/#create-map
    """

    

    utilities.check_if_username_in_access_list(username, item.read_access_list, "read")

    utilities.check_if_username_in_access_list(username, item.write_access_list, "write")

    new_map = await utilities.create_single_item_in_database(
        item=item,
        model_name="Map"
    )

    return new_map