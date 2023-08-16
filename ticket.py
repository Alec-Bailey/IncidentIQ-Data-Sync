#!/usr/bin/env python
"""ticket.py: Declaratively mapped Ticket from IncidentIQ

Ticket contains the methods nescessary to pull and transofrm
the data from the IncidentIQ to conform to declaratively mapped
object in SqlAlcemy. Ticket can be instantiated with data from
IncidentIQ to insert into the specified database.
"""

from requests.models import HTTPError
from sqlalchemy import Column, String, Integer, Date, Boolean, DateTime, VARCHAR
from sqlalchemy_utils.types.uuid import UUIDType as UNIQUEIDENTIFIER
from sqlalchemy.orm import validates
from base import Base, IIQ_Datatype as IIQ
from custom_fields import TicketCustomFields
import config
import requests
import uuid
import json


class Ticket(Base, IIQ):
    """Ticket is an instanciable class which holds all the information
    for one Ticket in IncidentIQ. Ticket also contains methods to make an
    API request to retreive an entire page of Tickets as well as
    create an instance of the dynamic TicketCustomFields class.
    Ticket is declaratively mapped in SqlAlchemy to the 'Tickets' table,
    (by default, differs by configurable table names).
    On instantiation, Ticket can be inserted into 'Tickets' via an SqlAlchemy
    session."""

    __tablename__ = config.TICKETS_TABLE_NAME
    if config.SCHEMA is not None:
        __table_args__ = {'schema': config.SCHEMA}

    # Retreive custom fields
    custom_fields = TicketCustomFields.parse_fields(
        TicketCustomFields.get_fields_request(0))

    TicketId = Column(UNIQUEIDENTIFIER(binary=False), primary_key=True)
    SiteId = Column(UNIQUEIDENTIFIER(binary=False))
    IsDeleted = Column(Boolean)
    TicketNumber = Column(String(length=config.STRING_LENGTH))
    Subject = Column(String(length=config.STRING_LENGTH))
    CreatedDate = Column(DateTime)
    ModifiedDate = Column(DateTime)
    StartedDate = Column(DateTime)
    ClosedDate = Column(DateTime)
    IsPastDue = Column(Boolean)
    OwnerId = Column(UNIQUEIDENTIFIER(binary=False))
    OwnerName = Column(String(length=config.STRING_LENGTH))    # Nested
    ForId = Column(UNIQUEIDENTIFIER(binary=False))
    ForName = Column(String(length=config.STRING_LENGTH))    # Nested
    Username = Column(String(length=config.STRING_LENGTH))
    LocationId = Column(UNIQUEIDENTIFIER(binary=False))
    LocationName = Column(String(length=config.STRING_LENGTH))    # Nested
    IssueId = Column(UNIQUEIDENTIFIER(binary=False))
    IssueName = Column(String(length=config.STRING_LENGTH))    # Nested
    IsIssueConfirmed = Column(Boolean)
    TeamId = Column(UNIQUEIDENTIFIER(binary=False))
    TeamName = Column(String(length=config.STRING_LENGTH))    # Nested
    AssignedToUserId = Column(UNIQUEIDENTIFIER(binary=False))    # Nested
    AssignedToUserName = Column(String(length=config.STRING_LENGTH))    # Nested
    IsClosed = Column(Boolean)
    WorkflowStepId = Column(UNIQUEIDENTIFIER(binary=False))
    Priority = Column(String(length=config.STRING_LENGTH))
    Subject = Column(String(length=config.STRING_LENGTH))
    IssueDescription = Column(VARCHAR(None))
    Status = Column(String(length=config.STRING_LENGTH))    # Nested

    fields = [
        'TicketId', 'TicketNumber', 'CreatedDate', 'StartedDate', 'ClosedDate',
        'IsPastDue', 'OwnerId', 'ForId', 'IssueId', 'IsIssueConfirmed',
        'IsDeleted', 'AssignedToUserId', 'IsClosed', 'WorkflowStepId',
        'LocationId', 'LocationName', 'ModifiedDate', 'SiteId', 'UserId',
        'Username', 'Priority', 'Subject', 'IssueDescription', 'Status',
        'TeamId', 'TeamName'
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

        # Nested fields are more complex, and thus are commented in the declaration
        # as Nested. We simply path these out by hand since there are only a few, and
        # often they are purposeful inclusions that aren't nescessary but useful to
        # end users. This is harmless even if they are optional fields in the API response,
        # since find_element will set them to None by default
        self.OwnerName = IIQ.find_element(data, 'Owner', 'Name')
        self.ForName = IIQ.find_element(data, 'For', 'Name')
        self.LocationName = IIQ.find_element(data, 'Location', 'Name')
        self.IssueName = IIQ.find_element(data, 'Issue', 'Name')
        self.AssignedToUserName = IIQ.find_element(data, 'AssignedToUser', 'Name')
        self.Status = IIQ.find_element(data, 'WorkflowStep', 'StepName')
        self.TeamId = IIQ.find_element(data, 'AssignedToTeam', 'TeamId')
        self.TeamName = IIQ.find_element(data, 'AssignedToTeam', 'TeamName')

    @staticmethod
    def get_data_request(page):
        url = "https://" + config.IIQ_INSTANCE + "/api/v1.0/tickets?$p=" + str(page) + "&$s=" + config.PAGE_SIZE + "&$d=Descending&$o=TicketCreatedDate"
        payload = "{\n    \"OnlyShowDeleted\": false,\n    \"FilterByViewPermission\": true\n}"
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

        response = requests.request("POST",
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
        return Ticket.get_data_request(0).json()['Paging']['PageCount']

    @staticmethod
    def get_custom_type():
        return TicketCustomFields

    @classmethod
    def _get_custom_fields(cls, item):
        return super()._get_custom_fields(item)
