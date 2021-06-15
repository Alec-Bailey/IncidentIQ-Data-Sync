from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from base import Base

class Asset(Base):
    __tablename__ = 'IiqAssets'
    __table_args__ = {'schema': 'IQ'}

    id = Column(UNIQUEIDENTIFIER, primary_key=True)
    assetTag = Column(String)
    createdDate = Column(Date)


    def __init__(self, id, assetTag, createdDate):
        self.id = id
        self.assetTag = assetTag
        self.createdDate = createdDate