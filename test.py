import sqlalchemy
import config

engine = sqlalchemy.create_engine(config.SQLALCHEMY)
