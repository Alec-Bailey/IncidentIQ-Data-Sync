import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config

engine = sqlalchemy.create_engine(config.DB_CONNECTION_STRING, pool_size=config.THREADS, max_overflow=0)

Session = sessionmaker(bind=engine)

Base = declarative_base()