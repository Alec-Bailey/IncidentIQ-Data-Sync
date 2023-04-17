#!/usr/bin/env python
"""room.py: Declaratively mapped Room from IncidentIQ

Room contains the methods nescessary to pull and transofrm
the data from the IncidentIQ to conform to declaratively mapped
object in SqlAlcemy. Room can be instantiated with data from
IncidentIQ to insert into the specified database.
"""

from requests.models import HTTPError
from sqlalchemy import Column, String, Integer, Date, Boolean, DateTime, VARCHAR
from sqlalchemy_utils.types.uuid import UUIDType as UNIQUEIDENTIFIER
from sqlalchemy.orm import validates
from base import Base, IIQ_Datatype as IIQ
import config
import requests


class Room(Base, IIQ):
    """Room is an instanciable class which holds all the information
    for one Room in IncidentIQ. Room also contains methods to make an
    API request to retreive an entire page of Rooms.
    Room is declaratively mapped in SqlAlchemy to the 'Rooms' table,
    (by default, differs by configurable table names).
    On instantiation, Room can be inserted into 'Rooms' via an SqlAlchemy
    session."""

    __tablename__ = config.ROOMS_TABLE_NAME
    if config.SCHEMA is not None:
        __table_args__ = {'schema': config.SCHEMA}

    LocationRoomId = Column(UNIQUEIDENTIFIER(binary=False), primary_key=True)
    SiteId = Column(UNIQUEIDENTIFIER(binary=False))
    Name = Column(String(length=config.STRING_LENGTH))
    LocationId = Column(UNIQUEIDENTIFIER(binary=False))
    LocationName = Column(String(length=config.STRING_LENGTH))
    LocationAbbreviation = Column(String(length=config.STRING_LENGTH))
    LocationRoomTypeId = Column(UNIQUEIDENTIFIER(binary=False))
    LocationRoomTypeName = Column(String(length=config.STRING_LENGTH))
    Description = Column(String(length=config.STRING_LENGTH))
    IsAvailable = Column(Boolean)
    IsExternallyAvailable = Column(Boolean)
    IsDeleted = Column(Boolean)

    fields = [
        'LocationRoomId', 'SiteId', 'Name', 'LocationId', 'LocationName',
        'LocationAbbreviation', 'LocationRoomTypeId', 'LocationRoomTypeName',
        'Description', 'IsAvailable', 'IsExternallyAvailable', 'IsDeleted'
    ]

    # Validator ensures empty strings are entered as null
    @validates(*fields)
    def validate_inserts(self, key, value):
        return super().validate_inserts(key, value)

    def __init__(self, data):
        # Extract fields from the raw data, optional nested fields
        # can be retrieved easily with find_element *args (See asset.py)
        for field in self.fields:
            # For non-nested fields that exist at the first level of the JSON
            # we can use setattr to assign values, since the fields are
            # named exactly as they appear in the JSON. For example, an asset
            # JSON response will have a field 'AssetId' at the base level of that item.
            # Thus, find_element can grab it simply by being passed 'AssetId'. By design,
            # the column is also named 'AssetId', so we can iterate simply and set these fields.
            setattr(self, field, IIQ.find_element(data, field))

    @staticmethod
    def get_data_request(page):
        url = "https://" + config.IIQ_INSTANCE + "/api/v1.0/locations/rooms?$s=" + str(
            config.PAGE_SIZE) + "&$d=Descending&$p=" + str(page)
        payload = {}
        files = {}
        headers = {
            'Client': 'WebBrowser',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Pragma': 'no-cache',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + config.IIQ_TOKEN
        }

        response = requests.request("GET",
                                    url,
                                    headers=headers,
                                    data=payload,
                                    files=files,
                                    timeout=config.TIMEOUT)

        # Cause an exception if anything but success is returned
        if response.status_code != 200:
            raise HTTPError("""A request returned a status code other than 200\n
            Status Code: """ + str(response.status_code))

        # Cause an exception if for some reason the API returns nothing
        if response.json()['Paging']['PageSize'] <= 0:
            raise HTTPError("No elements were returned from a request")

        # Return the response
        return response

    @staticmethod
    def get_num_pages():
        return Room.get_data_request(0).json()['Paging']['PageCount']

    @classmethod
    def get_page(cls, page_number):
        return super().get_page(page_number)
