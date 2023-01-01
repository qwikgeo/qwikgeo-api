"""QwikGeo API - Groups"""

import uuid
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from tortoise import exceptions
from tortoise.query_utils import Prefetch
from tortoise.expressions import Q

from qwikgeo_api import db_models
from qwikgeo_api import utilities
from qwikgeo_api import authentication_handler

router = APIRouter()

@router.get(
    path="/",
    response_model=List[db_models.Group_Pydantic],
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
async def groups(
    q: str="",
    limit: int=10,
    offset: int=0,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """Return a list of all groups."""

    query_filter = ""

    if q != "":
        query_filter = Q(name__icontains=q)

    items = await utilities.get_multiple_items_in_database(
        user_name=user_name,
        model_name="Group",
        query_filter=query_filter,
        limit=limit,
        offset=offset
    )

    return items

@router.post(
    path="/",
    response_model=db_models.Group_Pydantic,
    responses={
        400: {
            "description": "Group name already exist",
            "content": {
                "application/json": {
                    "example": {"detail": "Group name already exist."}
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
async def create_group(
    group: db_models.Group_Pydantic,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """Create a group."""

    try:
        user_in_group_users = False
        user_in_group_admins = False

        for name in group.group_users:
            if name.username == user_name:
                user_in_group_users = True
            try:
                await db_models.User.get(username=name.username)
            except exceptions.DoesNotExist as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Username: {name.username} does not exist.'
                ) from exc
        
        for name in group.group_admins:
            if name.username == user_name:
                user_in_group_admins = True
        
        if user_in_group_users is False:
            raise HTTPException(status_code=400, detail="User is not in group_users.")
        
        if user_in_group_admins is False:
            raise HTTPException(status_code=400, detail="User is not in group_admins.")
        
        new_group = await db_models.Group.create(
            name=group.name
        )

        for name in group.group_users:
            await db_models.GroupUser.create(username=name.username, group_id_id=new_group.group_id)
        
        for name in group.group_admins:
            await db_models.GroupAdmin.create(username=name.username, group_id_id=new_group.group_id)

        return await db_models.Group_Pydantic.from_tortoise_orm(new_group)
    except exceptions.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Group name already exist.") from exc

@router.get(
    path="/{group_id}",
    response_model=db_models.Group_Pydantic,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "You do not have access to this group."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Group not found."}
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
async def get_group(
    group_id: str,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """Retrieve a group."""

    try:
        group = await db_models.Group_Pydantic.from_queryset_single(
            db_models.Group.get(group_id=group_id)
        )
        access = False
        for user in group.group_users:
            if user.username == user_name:
                access = True
        if access is False:
            raise HTTPException(status_code=403, detail="You do not have access to this group.")
        return group
    except exceptions.DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="Group not found.") from exc

@router.put(
    path="/{group_id}",
    response_model=db_models.Group_Pydantic,
    responses={
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "You do not have access to this group."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Group not found."}
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
async def update_group(
    group_id: uuid.UUID,
    new_group: db_models.Group_Pydantic,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """Update a group."""

    try:
        group = await db_models.Group_Pydantic.from_queryset_single(
            db_models.Group.get(group_id=group_id)
        )
        access = False
        for user in group.group_admins:
            if user.username == user_name:
                access = True
        if access is False:
            raise HTTPException(status_code=403, detail="You do not have admin access to this group.")
        await db_models.Group.filter(group_id=group_id).update(name=new_group.name)
        for name in new_group.group_users:
            await db_models.GroupUser.filter(
                id=name.id, group_id_id=group_id
            ).update(username=name.username)
        return await db_models.Group_Pydantic.from_queryset_single(
            db_models.Group.get(group_id=group_id)
        )
    except exceptions.DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="Group not found.") from exc

@router.delete(
    path="/{group_id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {"status": True}
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "You do not have access to this group."}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Group not found."}
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
async def delete_group(
    group_id: uuid.UUID,
    user_name: int=Depends(authentication_handler.JWTBearer())
):
    """Delete a group."""

    try:
        group = await db_models.Group_Pydantic.from_queryset_single(
            db_models.Group.get(group_id=group_id)
        )
        access = False
        for user in group.group_admins:
            if user.username == user_name:
                access = True
        if access is False:
            raise HTTPException(status_code=403, detail="You do not have admin access to this group.")
        deleted_count = await db_models.Group.filter(group_id=group_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=404, detail="Group not found")
        return {"status": True}
    except exceptions.DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="Group not found.") from exc
