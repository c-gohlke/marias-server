# -*- coding: utf-8 -*-
import os
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer
from db.database import connect_db
from db.models import User
from db.crud import get_user
from param import DB_PATH
from logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
TAG = "db/login"

db_path_name = os.getcwd() + DB_PATH
SessionMaker = connect_db(db_path_name)


def fake_decode_token(token):
    logger.info(TAG + "in fake decode token")

    # for now token is just the "token"+username
    username = token[5:]
    session = SessionMaker()

    # if there is a valid user
    if(get_user(session, username)):
        return username
    else:
        return None


def fake_encode_token(username):
    logger.info(TAG + "in fake encode token")
    # for now token is just the username
    return "token"+username


async def get_current_user(username: str):
    logger.info(TAG + "in get_current_user")
    logger.info(TAG + "token is:")
    logger.info(TAG + username)

    session = SessionMaker()
    user = get_user(session, username)
    session.close()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)):
    logger.info(TAG + "in get_current_active_user")

    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
