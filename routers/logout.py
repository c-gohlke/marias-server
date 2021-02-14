import logging
import os
from db.database import connect_db
from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import OAuth2PasswordRequestForm
from param import DB_PATH

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()
db_path_name = os.getcwd() + DB_PATH
SessionMaker = connect_db(db_path_name)


@router.post("/logout")  # TODO: check if works
async def logout(form_data: OAuth2PasswordRequestForm = Depends()):
    return {"access_token": "", "token_type": ""}
