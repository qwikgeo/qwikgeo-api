from passlib.hash import bcrypt
from tortoise.contrib.fastapi import HTTPNotFoundError
from fastapi import APIRouter, HTTPException, Depends, Request
from tortoise import exceptions
from starlette.config import Config
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
import jwt
from datetime import datetime, timedelta

import db_models
import routers.authentication.models as models
import utilities
import config

env_config = Config('.env')
oauth = OAuth(env_config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

router = APIRouter()

@router.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

@router.get('/authenticate')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
        request.session['test'] = 'nice'

    expire = datetime.utcnow() + timedelta(minutes=1)
    token = jwt.encode({
        "username": user['email'],
        "exp": expire
        }, config.SECRET_KEY)

    return {'access_token' : token, 'token_type' : 'bearer'}

@router.post("/user/", response_model=models.User_Pydantic)
async def create_user(user: models.UserIn_Pydantic):
    try:
        user_obj = db_models.User(username=user.username, password_hash=bcrypt.hash(user.password_hash))
        await user_obj.save()
        return await models.User_Pydantic.from_tortoise_orm(user_obj)
    except exceptions.IntegrityError:
        raise HTTPException(status_code=400, detail=f"Username already exist.")

@router.get("/user/")
async def get_user(user_name: int=Depends(utilities.get_token_header)):
    # try:
    #     user = await models.User_Pydantic.from_queryset_single(db_models.User.get(id=user_id))
    #     return user
    # except exceptions.DoesNotExist:
    #     raise HTTPException(status_code=404, detail=f"User not found")
    # user = request.session.get('user')
    # data = json.dumps(user)
    # return json.loads(data)
    # print(user_name)
    return {"user_name": user_name}

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
