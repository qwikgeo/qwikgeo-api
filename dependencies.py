from fastapi import Header
import jwt

SECRET_KEY = "asdasasfakjh324fds876921vdas7tfv1uqw76fasd87g2q"

async def get_token_header(x_token: str = Header(default=None)):
    user = jwt.decode(x_token, SECRET_KEY, algorithm='sha256')
    return user['user_id']