import os
from db.models import fake_hash_password
from db.login import fake_encode_token
from db.crud import get_user
from db.database import connect_db
from fastapi import (
    APIRouter,
    Request,
    HTTPException,
)
from logger import logger
from param import DB_PATH

TAG = "routers/login"

router = APIRouter()
db_path_name = os.getcwd() + DB_PATH
SessionMaker = connect_db(db_path_name)


@router.post("/login")
async def login(request: Request):
    data = await request.json()

    session = SessionMaker()
    user_login = get_user(session, data['username'])

    session.close()

    if not user_login:
        raise HTTPException(status_code=400,
                            detail="Incorrect username or password")

    hashed_password = fake_hash_password(data["password"])
    if not hashed_password == user_login.hashed_password:
        raise HTTPException(status_code=400,
                            detail="Incorrect username or password")

    return {"access_token": fake_encode_token(user_login.username),
            "token_type": "bearer",
            "username": user_login.username}
