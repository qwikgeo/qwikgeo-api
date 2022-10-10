"""QwikGeo API - Groups"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from tortoise import exceptions
from tortoise.query_utils import Prefetch

import routers.groups.models as models
import db_models
import utilities

router = APIRouter()

@router.get(
    path="/",
    response_model=models.Groups,
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
    user_name: int=Depends(utilities.get_token_header)
):
    """Return a list of all groups."""

    user_groups = (
        await db_models.Group.all()
        .prefetch_related(
            Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name))
        )
    )

    return {"groups": user_groups}

@router.get(
    path="/search",
    response_model=models.Groups,
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
async def group_search(
    name: str,
    user_name: int=Depends(utilities.get_token_header)
):
    """Return a list of groups based off of searching via the name of the group."""

    user_groups = (
        await db_models.Group.filter(name__search=name)
        .prefetch_related(
            Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name))
        )
    )

    return {"groups": user_groups}


@router.post(
    path="/group",
    response_model=models.Group_Pydantic,
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
    group: models.Group
):
    """Create a group."""

    try:
        new_group = await db_models.Group.create(
            name=group.name
        )

        for name in group.group_users:
            await db_models.GroupUser.create(username=name.username, group_id_id=new_group.group_id)

        return await models.Group_Pydantic.from_tortoise_orm(new_group)
    except exceptions.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Group name already exist.") from exc

@router.get(
    path="/group/{group_id}",
    response_model=models.Group_Pydantic,
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
    user_name: int=Depends(utilities.get_token_header)
):
    """Retrieve a group."""

    try:
        group = await models.Group_Pydantic.from_queryset_single(
            db_models.Group.get(group_id=group_id).prefetch_related(
                Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name))
            )
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
    path="/group/{group_id}",
    response_model=models.Group_Pydantic,
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
    new_group: models.Group_Pydantic,
    user_name: int=Depends(utilities.get_token_header)
):
    """Update a group."""

    try:
        group = await models.Group_Pydantic.from_queryset_single(
            db_models.Group.get(group_id=group_id).prefetch_related(
                Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name))
            )
        )
        access = False
        for user in group.group_users:
            if user.username == user_name:
                access = True
        if access is False:
            raise HTTPException(status_code=403, detail="You do not have access to this group.")
        await db_models.Group.filter(group_id=group_id).update(name=new_group.name)
        for name in new_group.group_users:
            await db_models.GroupUser.filter(
                id=name.id, group_id_id=group_id
            ).update(username=name.username)
        return await models.Group_Pydantic.from_queryset_single(
            db_models.Group.get(group_id=group_id)
        )
    except exceptions.DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="Group not found.") from exc

@router.delete(
    path="/group/{group_id}",
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {"message": "Deleted group."}
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
    user_name: int=Depends(utilities.get_token_header)
):
    """Delete a group."""

    try:
        group = await models.Group_Pydantic.from_queryset_single(
            db_models.Group.get(group_id=group_id).prefetch_related(
                Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name))
            )
        )
        access = False
        for user in group.group_users:
            if user.username == user_name:
                access = True
        if access is False:
            raise HTTPException(status_code=403, detail="You do not have access to this group.")
        deleted_count = await db_models.Group.filter(group_id=group_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=404, detail="Group not found")
        return models.Status(message="Deleted group.")
    except exceptions.DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="Group not found.") from exc
