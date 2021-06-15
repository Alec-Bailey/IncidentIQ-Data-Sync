from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from base import Base

def CustomFields(Base):
    __tablename__ = ''
    __table_args__ = {'schema': 'IQ'}