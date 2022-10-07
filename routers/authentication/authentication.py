from passlib.hash import bcrypt
from tortoise.contrib.fastapi import HTTPNotFoundError
from fastapi import APIRouter, HTTPException, Depends, status
from tortoise import exceptions
import jwt
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport import requests

import db_models
import routers.authentication.models as models
import utilities
import config

router = APIRouter()

@router.post('/token')
async def generate_token(form_data: models.Login):
    user = await utilities.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )
    user_obj = await models.User_Pydantic.from_tortoise_orm(user)

    expire = datetime.utcnow() + timedelta(minutes=int(config.JWT_TOKEN_EXPIRE_IN_MINUTES))
    token = jwt.encode(
        {
            "username": user_obj.username,
            "exp": expire
        }, 
        config.SECRET_KEY
    )

    return {'access_token' : token, 'token_type' : 'bearer'}

@router.post('/google_token_authenticate')
async def google_token_authenticate(info: models.GoogleTokenAuthenticate):
    try:
        user = id_token.verify_oauth2_token(info.token, requests.Request(), config.GOOGLE_CLIENT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        user_obj = db_models.User(
            username=user['email'].split("@")[0],
            first_name=user['given_name'],
            last_name=user['family_name'],
            photo_url=user['picture'],
            email=user['email']
        )
        await user_obj.save()

    except exceptions.IntegrityError:
        pass

    expire = datetime.utcnow() + timedelta(minutes=int(config.JWT_TOKEN_EXPIRE_IN_MINUTES))
    token = jwt.encode({
        "username": user['email'].split("@")[0],
        "exp": expire
        }, config.SECRET_KEY
    )

    return {'access_token' : token, 'token_type' : 'bearer'}

@router.post("/user", response_model=models.User_Pydantic)
async def create_user(user: models.UserIn_Pydantic):
    try:
        user_obj = db_models.User(
            username=user.username,
            password_hash=bcrypt.hash(user.password_hash),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )
        await user_obj.save()
        return await models.User_Pydantic.from_tortoise_orm(user_obj)
    except exceptions.IntegrityError:
        raise HTTPException(status_code=400, detail=f"Username already exist.")

@router.get("/user")
async def get_user(user_name: int=Depends(utilities.get_token_header)):
    try:
        user = await models.User_Pydantic.from_queryset_single(db_models.User.get(username=user_name))
        return user
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User not found")

@router.put("/user", response_model=models.User_Pydantic, responses={404: {"model": HTTPNotFoundError}}, dependencies=[Depends(utilities.get_token_header)])
async def update_user(user: models.UserIn_Pydantic, user_name: int=Depends(utilities.get_token_header)):
    # TODO
    await db_models.User.filter(username=user_name).update(**user.dict(exclude_unset=True))
    return await models.User_Pydantic.from_queryset_single(db_models.User.get(username=user_name))

@router.delete("/user", response_model=models.Status, responses={404: {"model": HTTPNotFoundError}}, dependencies=[Depends(utilities.get_token_header)])
async def delete_user(user_name: int=Depends(utilities.get_token_header)):
    deleted_count = await db_models.User.filter(username=user_name).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_name} not found")
    return models.Status(message=f"Deleted user {user_name}")
