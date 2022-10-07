import uuid
from fastapi import APIRouter, HTTPException, Depends
from tortoise import exceptions
from tortoise.query_utils import Prefetch

import routers.groups.models as models
import db_models
import utilities

router = APIRouter()

@router.get("/", response_model=models.Groups, description="Return a list of all groups.", responses={
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "Internal Server Error"
            }
        }
    }
})
async def groups(user_name: int=Depends(utilities.get_token_header)):
    groups = (
        await db_models.Group.all()
        .prefetch_related(Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name)))
    )

    return {"groups": groups}

@router.get("/search", response_model=models.Groups, description="Return a list of groups based off of searching via the name of the group.", responses={
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "Internal Server Error"
            }
        }
    }
})
async def group_search(name: str, user_name: int=Depends(utilities.get_token_header)):
    groups = (
        await db_models.Group.filter(name__search=name)
        .prefetch_related(Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name)))
    )

    return {"groups": groups}


@router.post("/group", response_model=models.Group_Pydantic, description="Create a group.", responses={
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
})
async def create_group(group: models.Group):
    try:
        new_group = await db_models.Group.create(
            name=group.name
        )

        for name in group.group_users:
            await db_models.GroupUser.create(username=name.username, group_id_id=new_group.group_id)

        return await models.Group_Pydantic.from_tortoise_orm(new_group)
    except exceptions.IntegrityError:
        raise HTTPException(status_code=400, detail=f"Group name already exist.")

@router.get("/group/{group_id}", response_model=models.Group_Pydantic, description="Retrieve a group.", responses={
    403: {
        "description": "No access",
        "content": {
            "application/json": {
                "example": {"detail": "You do not have access to this group."}
            }
        }
    },
    404: {
        "description": "Group not found",
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
})
async def get_group(group_id: str, user_name: int=Depends(utilities.get_token_header)):
    try:
        group = await models.Group_Pydantic.from_queryset_single(db_models.Group.get(group_id=group_id).prefetch_related(Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name))))
        access = False
        for user in group.group_users:
            if user.username == user_name:
                access = True
        if access == False:
            raise HTTPException(status_code=403, detail=f"You do not have access to this group.")
        return group
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Group not found.")

@router.put("/group/{group_id}", response_model=models.Group_Pydantic, description="Update a group.", responses={
    403: {
        "description": "No access",
        "content": {
            "application/json": {
                "example": {"detail": "You do not have access to this group."}
            }
        }
    },
    404: {
        "description": "Group not found",
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
})
async def update_group(group_id: uuid.UUID, new_group: models.Group_Pydantic, user_name: int=Depends(utilities.get_token_header)):
    try:
        group = await models.Group_Pydantic.from_queryset_single(db_models.Group.get(group_id=group_id).prefetch_related(Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name))))
        access = False
        for user in group.group_users:
            if user.username == user_name:
                access = True
        if access == False:
            raise HTTPException(status_code=403, detail=f"You do not have access to this group.")
        await db_models.Group.filter(group_id=group_id).update(name=new_group.name)
        for name in new_group.group_users:
            await db_models.GroupUser.filter(id=name.id, group_id_id=group_id).update(username=name.username)
        return await models.Group_Pydantic.from_queryset_single(db_models.Group.get(group_id=group_id))
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Group not found.")

@router.delete("/group/{group_id}", description="Delete a group.", responses={
    200: {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {"message": "Deleted group."}
            }
        }
    },
    403: {
        "description": "No access",
        "content": {
            "application/json": {
                "example": {"detail": "You do not have access to this group."}
            }
        }
    },
    404: {
        "description": "Group not found",
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
})
async def delete_group(group_id: uuid.UUID, user_name: int=Depends(utilities.get_token_header)):
    try:
        group = await models.Group_Pydantic.from_queryset_single(db_models.Group.get(group_id=group_id).prefetch_related(Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name))))
        access = False
        for user in group.group_users:
            if user.username == user_name:
                access = True
        if access == False:
            raise HTTPException(status_code=403, detail=f"You do not have access to this group.")
        deleted_count = await db_models.Group.filter(group_id=group_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=404, detail=f"Group not found")
        return models.Status(message=f"Deleted group.")
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Group not found.")