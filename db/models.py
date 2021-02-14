from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    pwd = Column(String)
    disabled = Column(Boolean, default=False)
    hashed_password = Column(String)


def fake_hash_password(password: str):
    return "fakehashed" + password
