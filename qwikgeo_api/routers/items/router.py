"""QwikGeo API - Items"""

from typing import List
from fastapi import APIRouter, Depends
from tortoise.expressions import Q

from qwikgeo_api import utilities
from qwikgeo_api import db_models
from qwikgeo_api import authentication_handler

router = APIRouter()

@router.get(
    path="/",
    response_model=List[db_models.Item_Pydantic],
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
async def items(
    username: int=Depends(authentication_handler.JWTBearer()),
    q: str="",
    limit: int=10,
    offset: int=0,
    item_type: str="",
):
    """
    List all items.
    More information at https://docs.qwikgeo.com/items/#items
    """

    if q == "":
        if item_type:
            portal_items = await utilities.get_multiple_items_in_database(
                username=username,
                model_name=item_type,
                limit=limit,
                offset=offset
            )
        else:
            portal_items = await utilities.get_multiple_items_in_database(
                username=username,
                model_name="Item",
                limit=limit,
                offset=offset
            )

    else:
        if item_type:
            portal_items = await utilities.get_multiple_items_in_database(
                username=username,
                model_name=item_type,
                query_filter=Q(Q(title__icontains=q) | Q(description__icontains=q)),
                limit=limit,
                offset=offset
            )
        else:
            portal_items = await utilities.get_multiple_items_in_database(
                username=username,
                model_name="Item",
                query_filter=Q(Q(title__icontains=q) | Q(description__icontains=q)),
                limit=limit,
                offset=offset
            )

    return portal_items

@router.get(
    path="/{portal_id}",
    response_model=db_models.Item_Pydantic,
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
async def item(
    portal_id: str,
    username: int=Depends(authentication_handler.JWTBearer())
):
    """
    Get an item.
    More information at https://docs.qwikgeo.com/items/#item
    """

    return await utilities.get_item_in_database(
        username=username,
        model_name="Item",
        query_filter=Q(portal_id=portal_id)
    )
