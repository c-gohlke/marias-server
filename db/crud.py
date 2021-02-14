from logger import logger
from sqlalchemy import String
from .models import User, fake_hash_password

TAG = "db/crud"


def get_user(session, username: str):
    user = session.query(User).filter(User.username == username).first()
    return user


def get_users(session):
    users = session.query(User).all()
    logger.info(TAG + len(users))
    return users


def create_user(session, pwd: String, username: String, email: String):
    new_user = User(email=email,
                    pwd=pwd,
                    username=username,
                    hashed_password=fake_hash_password(pwd))

    session.add(new_user)
    session.commit()
    logger.info(TAG + "NEW USER CREATED")
    return new_user
