# User class respresents IncidentIQ users
from sqlalchemy import Column, String, Integer, Date, Boolean
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from base import Base
import config
import requests
import json
from types import SimpleNamespace as Namespace

class User(Base):
    __tablename__ = 'Users'
    __table_args__ = {'schema': 'IQtesting'}

    #TODO: using UUID at all, especially as it's correct type and PK presents an interesting
    # challenge, SqlAlchemy doesn't support a database agnostic way of dealing with this
    # will have to create a case for other databases down the road and eventually test it
    # Dockerize some databases perhaps, for now this is the MsSql way of dealing with it
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
    SchoolIdNumber = Column(Integer)
    Grade = Column(String)
    Homeroom = Column(String)
    ExternalId = Column(UNIQUEIDENTIFIER)
    InternalComments = Column(String)
    RoleId = Column(UNIQUEIDENTIFIER)
    AuthenticatedBy = Column(String)
    AccountSetupProgress = Column(Integer)
    TrainingPercentComplete = Column(Integer)
    IsEmailVerified = Column(Boolean)
    IsWelcomeEmailSent = Column(Boolean)
    PreventProviderUpdates = Column(Boolean)
    IsOutOfOffice = Column(Boolean)
    Portal = Column(Integer)

    def __init__(self, UserId, IsDeleted, SiteId, CreatedDate, ModifiedDate, LocationId,
    LocationName, IsActive, IsOnline, IsOnlineLastUpdated, FirstName, LastName,
    Email, Username, Phone, SchoolIdNumber, Grade, Homeroom, ExternalId, InternalComments,
    RoleId, AuthenticatedBy, AccountSetupProgress, TrainingPercentComplete, IsEmailVerified,
    IsWelcomeEmailSent, PreventProviderUpdates, IsOutOfOffice, Portal):
        self.UserId = UserId
        self.IsDeleted = IsDeleted
        self.SiteId = SiteId
        self.CreatedDate = CreatedDate
        self.ModifiedDate = ModifiedDate
        self.LocationId = LocationId
        self.LocationName = LocationName
        self.IsActive = IsActive
        self.IsOnline = IsOnline
        self.IsOnlineLastUpdated = IsOnlineLastUpdated
        self.FirstName = FirstName
        self.LastName = LastName
        self.Email = Email
        self.Username = Username
        self.Phone = Phone
        self.SchoolIdNumber = SchoolIdNumber
        self.Grade = Grade
        self.Homeroom = Homeroom
        self.ExternalId = ExternalId
        self.InternalComments = InternalComments
        self.RoleId = RoleId
        self.AuthenticatedBy = AuthenticatedBy
        self.AccountSetupProgress = AccountSetupProgress
        self.TrainingPercentComplete = TrainingPercentComplete
        self.IsEmailVerified = IsEmailVerified
        self.IsWelcomeEmailSent = IsWelcomeEmailSent
        self.PreventProviderUpdates = PreventProviderUpdates
        self.IsOutOfOffice = IsOutOfOffice
        self.Portal = Portal

def get_users_request(page):
    url = "http://" + config.IIQ_INSTANCE + "/services/users?$o=FullName&$d=Ascending&$s=" + str(config.PAGE_SIZE) + "$p=" + str(page)
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
    # Return response as JSON
    return requests.request("POST", url, headers=headers, data=payload, files=files)

# Retrieve the number of pages to iterate through
def get_num_pages():
    return get_users_request(0).json()['Paging']['PageCount']

# Retreives all users from a request page and returns a list of all as User objects
def get_users_page(page):

    users = []

    response = get_users_request(page)

    # Create an instance of User for each returned user and append it to the list
    for user in response.json(object_hook = lambda d : Namespace(**d))['Items']:
        new_user = User()


    


