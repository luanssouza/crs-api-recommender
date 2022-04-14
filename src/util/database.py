from os import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

__db_connection = environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)

__engine = create_engine(__db_connection)

__Session = sessionmaker(bind=__engine)

Base = declarative_base()

def session_factory():
    Base.metadata.create_all(__engine)
    return __Session()
