#!/usr/bin/env python
"""user.py: Declaratively mapped User from IncidentIQ

User contains the methods nescessary to pull and transofrm
the data from the IncidentIQ to conform to declaratively mapped
object in SqlAlcemy. User can be instantiated with data from
IncidentIQ to insert into the specified database.
"""

from requests.models import HTTPError
from sqlalchemy import Column, String, Integer, Date, Boolean
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER as UNIQUEIDENTIFIER # TODO: we can use this import statement in a switch to support multiple dbs
from sqlalchemy.orm import validates
from base import Base, IIQ_Datatype as IIQ
from custom_fields import UserCustomFields
import config
import requests
from types import SimpleNamespace as Namespace

class User(Base, IIQ):
    """User is an instanciable class which holds all the information
    for one User in IncidentIQ. User also contains methods to make an
    API request to retreive an entire page of Users as well as
    create an instance of the dynamic UserCustomFields class.
    User is declaratively mapped in SqlAlchemy to the 'Users' table,
    on instantiation Asset can be inserted into 'Users' via an SqlAlchemy
    session."""

    __tablename__ = 'Users'
    __table_args__ = {'schema': config.SCHEMA}

    # Retreive custom fields
    custom_fields = UserCustomFields.parse_fields(UserCustomFields.get_fields_request(0))

    #TODO: using UNIQUEIDENTIFER at all, especially as it's correct type and PK presents an interesting
    # challenge, SqlAlchemy doesn't support a database agnostic way of dealing with this
    # will have to create a case for other databases down the road and eventually test it
    # Dockerize some databases perhaps to test, for now this is the MsSql way of dealing with it
    UserId = Column(UNIQUEIDENTIFIER, primary_key=True)
    IsDeleted = Column(Boolean)
    SiteId = Column(UNIQUEIDENTIFIER)
    CreatedDate = Column(Date)
    ModifiedDate = Column(Date)
    LocationId = Column(UNIQUEIDENTIFIER)
    LocationName = Column(String)
    IsActive = Column(Boolean)
    IsOnline = Column(Boolean)
    IsOnlineLastUpdated = Column(Date)
    FirstName = Column(String)
    LastName = Column(String)
    Email = Column(String)
    Username = Column(String)
    Phone = Column(String)
    SchoolIdNumber = Column(String)
    Grade = Column(String)
    Homeroom = Column(String)
    ExternalId = Column(UNIQUEIDENTIFIER)
    InternalComments = Column(String)
    RoleId = Column(String)
    AuthenticatedBy = Column(String)
    AccountSetupProgress = Column(Integer)
    TrainingPercentComplete = Column(Integer)
    IsEmailVerified = Column(Boolean)
    IsWelcomeEmailSent = Column(Boolean)
    PreventProviderUpdates = Column(Boolean)
    IsOutOfOffice = Column(Boolean)
    Portal = Column(Integer)

    fields = ['AccountSetupProgress', 'AuthenticatedBy', 'CreatedDate', 
    'Email', 'ExternalId', 'FirstName', 'Grade', 'Homeroom', 
    'InternalComments', 'IsActive', 'IsDeleted', 'IsEmailVerified',
     'IsOnline', 'IsOnlineLastUpdated', 'IsOutOfOffice', 'IsWelcomeEmailSent',
      'LastName', 'LocationId', 'LocationName', 'ModifiedDate', 'Phone',
       'Portal', 'PreventProviderUpdates', 'RoleId', 'SchoolIdNumber', 
       'SiteId', 'TrainingPercentComplete', 'UserId', 'Username']

    # Validator ensures empty strings are entered as null
    @validates(*fields)
    def empty_string_to_null(self, key, value):
        return super().empty_string_to_null(key, value)

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
        url = "http://" + config.IIQ_INSTANCE + "/services/users?$o=FullName&$s=" + str(config.PAGE_SIZE) + "&$d=Ascending&$p=" + str(page)
        print(url)
        payload={}
        files={}
        headers = {
        'Client': 'WebBrowser',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + config.IIQ_TOKEN
        }
        
        response =  requests.request("POST", url, headers=headers, data=payload, files=files)
        
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
        return User.get_data_request(0).json()['Paging']['PageCount']

    @classmethod
    def get_page(cls, page_number):
        return super().get_page(page_number)

    @staticmethod
    def get_custom_type():
        return UserCustomFields

    @classmethod
    def _get_custom_fields(cls, item):
        return super()._get_custom_fields(item)
