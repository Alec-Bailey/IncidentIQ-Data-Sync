from datetime import date

from sqlalchemy.sql.sqltypes import DateTime
from asset import Asset
from base import Session, engine, Base

import configparser

config = configparser.ConfigParser()
config.read('config.ini')
print(config.sections())
print(config.options('Database'))
print(config.get('Database', 'database'))