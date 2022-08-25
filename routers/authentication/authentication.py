import jwt
from passlib.hash import bcrypt
from tortoise.contrib.fastapi import HTTPNotFoundError
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from tortoise import exceptions

import db_models
import routers.authentication.models as models
import utilities

router = APIRouter()

@router.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await utilities.authenticate_user(form_data.username, form_data.password)
        
        user_obj = await models.User_Pydantic.from_tortoise_orm(user)

        token = jwt.encode({'username': user_obj.username}, utilities.SECRET_KEY)

        return {'access_token' : token, 'token_type' : 'bearer'}
    except exceptions.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

@router.post("/user/", response_model=models.User_Pydantic)
async def create_user(user: models.UserIn_Pydantic):
    try:
        user_obj = db_models.User(username=user.username, password_hash=bcrypt.hash(user.password_hash))
        await user_obj.save()
        return await models.User_Pydantic.from_tortoise_orm(user_obj)
    except exceptions.IntegrityError:
        raise HTTPException(status_code=400, detail=f"Username already exist.")

@router.get("/user/", response_model=models.User_Pydantic)
async def get_user(user_name: int=Depends(utilities.get_token_header)):
    try:
        user = await models.User_Pydantic.from_queryset_single(db_models.User.get(id=user_id))
        return user
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User not found")

@router.put("/user/", response_model=models.User_Pydantic, responses={404: {"model": HTTPNotFoundError}}, dependencies=[Depends(utilities.get_token_header)])
async def update_user(user: models.UserIn_Pydantic, user_name: int=Depends(utilities.get_token_header)):
    # TODO
    await db_models.User.filter(id=user_id).update(**user.dict(exclude_unset=True))
    return await models.User_Pydantic.from_queryset_single(db_models.User.get(id=user_id))

@router.delete("/user/", response_model=models.Status, responses={404: {"model": HTTPNotFoundError}}, dependencies=[Depends(utilities.get_token_header)])
async def delete_user(user_name: int=Depends(utilities.get_token_header)):
    deleted_count = await db_models.User.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return models.Status(message=f"Deleted user {user_id}")
