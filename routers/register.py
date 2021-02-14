import os
from db.crud import get_user, create_user
from db.database import connect_db
from fastapi import (
    APIRouter,
    HTTPException,
    Request
)
from logger import logger
from param import DB_PATH
from routers.login import login

router = APIRouter()
db_path_name = os.getcwd() + DB_PATH
SessionMaker = connect_db(db_path_name)

TAG = "routers/register"


@router.post("/register")
async def register(request: Request):
    logger.info(TAG + "register request received")
    data = await request.json()
    session = SessionMaker()
    user_login = get_user(session, data["username"])

    if user_login:
        raise HTTPException(status_code=403,
                            detail="Username already in use")
    else:
        create_user(session,
                    data["password"],
                    data["username"],
                    data["email"])

        session.close()
        return await login(request)
