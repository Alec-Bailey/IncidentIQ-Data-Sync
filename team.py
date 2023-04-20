#!/usr/bin/env python
"""team.py: Declaratively mapped Team from IncidentIQ

Team contains the methods nescessary to pull and transofrm
the data from the IncidentIQ to conform to declaratively mapped
object in SqlAlcemy. Team can be instantiated with data from
IncidentIQ to insert into the specified database.
"""

from requests.models import HTTPError
from sqlalchemy import Column, String, Integer
from sqlalchemy_utils.types.uuid import UUIDType as UNIQUEIDENTIFIER
from sqlalchemy.orm import validates
from base import Base, IIQ_Datatype as IIQ
import config
import requests


class Team(Base, IIQ):
    """Team is an instanciable class which holds all the information
    for one Team in IncidentIQ. Team also contains methods to make an
    API request to retreive an entire page of Teams.
    Teams is declaratively mapped in SqlAlchemy to the 'Teams' table,
    (by default, differs by configurable table names).
    On instantiation, Room can be inserted into 'Teams' via an SqlAlchemy
    session."""

    __tablename__ = config.TEAMS_TABLE_NAME
    if config.SCHEMA is not None:
        __table_args__ = {'schema': config.SCHEMA}

    TeamId = Column(UNIQUEIDENTIFIER(binary=False), primary_key=True)
    SiteId = Column(UNIQUEIDENTIFIER(binary=False))
    TeamName = Column(String(length=config.STRING_LENGTH))
    MembersCount = Column(Integer)

    fields = ['TeamId', 'SiteId', 'TeamName', 'MembersCount']

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
        url = "https://" + config.IIQ_INSTANCE + "/api/v1.0/teams/all?$s=" + str(
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
        return Team.get_data_request(0).json()['Paging']['PageCount']

    @classmethod
    def get_page(cls, page_number):
        return super().get_page(page_number)
