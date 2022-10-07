from fastapi import APIRouter, HTTPException, Depends
from tortoise import exceptions
from tortoise.query_utils import Prefetch

import routers.groups.models as models
import db_models
import utilities

router = APIRouter()

@router.get("/", response_model=models.Groups, description="Return a list of all groups.")
async def groups(user_name: int=Depends(utilities.get_token_header)):
    groups = (
        await db_models.Group.all()
        .prefetch_related(Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name)))
    )

    return {"groups": groups}

@router.get("/search", response_model=models.Groups, description="Return a list of groups based off of searching via the name of the group.")
async def group_search(name: str, user_name: int=Depends(utilities.get_token_header)):
    groups = (
        await db_models.Group.filter(name__search=name)
        .prefetch_related(Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name)))
    )

    return {"groups": groups}


@router.post("/group", response_model=models.Group_Pydantic, description="Create a new group.", responses={
    400: {
        "description": "Group name already exist.",
        "content": {
            "application/json": {
                "example": {"detail": "Group name already exist."}
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

@router.get("/group/{group_id}", response_model=models.Group_Pydantic, description="Get a group via the group id.", responses={
    404: {
        "description": "Group not found.",
        "content": {
            "application/json": {
                "example": {"detail": "Group not found."}
            }
        }
    }
})
async def get_group(group_id: str, user_name: int=Depends(utilities.get_token_header)):
    try:
        group = await models.Group_Pydantic.from_queryset_single(db_models.Group.get(group_id=group_id).prefetch_related(Prefetch("group_users", queryset=db_models.GroupUser.filter(username=user_name))))
        return group
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Group not found.")

# @router.put("/group", response_model=models.Group_Pydantic)
# async def update_user(group: models.Group_Pydantic, user_name: int=Depends(utilities.get_token_header)):
#     # TODO
#     await db_models.User.filter(username=user_name).update(**user.dict(exclude_unset=True))
#     return await models.User_Pydantic.from_queryset_single(db_models.User.get(username=user_name))

# @router.delete("/group", response_model=models.Status, responses={404: {"model": HTTPNotFoundError}}, dependencies=[Depends(utilities.get_token_header)])
# async def delete_user(user_name: int=Depends(utilities.get_token_header)):
#     deleted_count = await db_models.User.filter(username=user_name).delete()
#     if not deleted_count:
#         raise HTTPException(status_code=404, detail=f"User {user_name} not found")
#     return models.Status(message=f"Deleted user {user_name}")