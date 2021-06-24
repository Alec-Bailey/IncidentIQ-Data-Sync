# User class respresents IncidentIQ users
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
    __tablename__ = 'Users'
    __table_args__ = {'schema': config.SCHEMA}

    # Retreive custom fields
    custom_fields = UserCustomFields.parse_fields()

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

    fields = ['UserId','IsDeleted','SiteId','CreatedDate','ModifiedDate',
    'LocationId','LocationName','IsActive','IsOnline','IsOnlineLastUpdated',
    'FirstName','LastName','Email','Username','Phone','SchoolIdNumber','Grade',
    'Homeroom','ExternalId','InternalComments','RoleId','AuthenticatedBy',
    'AccountSetupProgress','TrainingPercentComplete','IsEmailVerified',
    'IsWelcomeEmailSent','PreventProviderUpdates','IsOutOfOffice','Portal']

    # Validator ensures empty strings are entered as null
    @validates(fields.__hash__)
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value

    def __init__(self, data):
        # Extract fields from the raw data, optional fields are retrieved
        # safely via find_element
        self.UserId = data.UserId
        self.IsDeleted = IIQ.find_element(data, 'IsDeleted')
        self.SiteId = data.SiteId
        self.CreatedDate = data.CreatedDate
        self.ModifiedDate = data.ModifiedDate
        self.LocationId = data.LocationId
        self.LocationName = IIQ.find_element(data, 'LocationName')
        self.IsActive = data.IsActive
        self.IsOnline = IIQ.find_element(data, 'IsOnline')
        self.IsOnlineLastUpdated = IIQ.find_element(data, 'IsOnlineLastUpdated')
        self.FirstName = IIQ.find_element(data, 'FirstName')
        self.LastName = IIQ.find_element(data, 'LastName')
        self.Email = IIQ.find_element(data, 'Email')
        self.Username = IIQ.find_element(data, 'Username')
        self.Phone = IIQ.find_element(data, 'Phone')
        self.SchoolIdNumber = IIQ.find_element(data, 'SchoolIdNumber')
        self.Grade = IIQ.find_element(data, 'Grade')
        self.Homeroom = IIQ.find_element(data, 'Homeroom')
        self.ExternalId = IIQ.find_element(data, 'ExternalId')
        self.InternalComments = IIQ.find_element(data, 'InternalComments')
        self.RoleId = data.RoleId
        self.AuthenticatedBy = IIQ.find_element(data, 'AuthenticatedBy')
        self.AccountSetupProgress = data.AccountSetupProgress
        self.TrainingPercentComplete = data.TrainingPercentComplete
        self.IsEmailVerified = data.IsEmailVerified
        self.IsWelcomeEmailSent = IIQ.find_element(data, 'IsWelcomeEmailSent')
        self.PreventProviderUpdates = data.PreventProviderUpdates
        self.IsOutOfOffice = IIQ.find_element(data, 'IsOutOfOffice')
        self.Portal = data.Portal

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

    # Retrieve the number of pages to iterate through
    @staticmethod
    def get_num_pages():
        return User.get_data_request(0).json()['Paging']['PageCount']

    # Retreives all users from a request page and returns a list of all as User objects
    @classmethod
    def get_page(cls, page_number):
        return super().get_page(page_number)
