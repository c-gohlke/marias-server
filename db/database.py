import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .seed import seed


def connect_db(db_path_name):
    SQLALCHEMY_DATABASE_URL = "sqlite:///" + db_path_name
    # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

    engine = create_engine(SQLALCHEMY_DATABASE_URL,
                           connect_args={"check_same_thread": False})

    SessionMaker = sessionmaker(bind=engine)

    # if db file doesn't exist, initialize it
    if not os.path.exists(db_path_name):
        # create all tables that don't exist yet
        Base.metadata.create_all(engine)

        session = SessionMaker()
        seed(session)
        session.close()

    return SessionMaker
