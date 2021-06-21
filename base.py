import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import config

engine = sqlalchemy.create_engine(config.DB_CONNECTION_STRING, pool_size=int(config.THREADS), max_overflow=0)

# Create a scoped session for thread safety, attempting to commit multiple sessions
# at once
Session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()


class IIQ_Datatype:

    @staticmethod
    def __get_data_request(page_number):
        raise NotImplementedError("__get_data_request API Request not implemented")

    @staticmethod
    def get_num_pages():
        raise NotImplementedError("get_num_pages not impelmeneted")

    @staticmethod
    def get_page(page_number):
        raise NotImplementedError("get_page not implemented")
