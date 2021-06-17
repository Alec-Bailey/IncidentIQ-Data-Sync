# User class respresents IncidentIQ users
from sqlalchemy import Column, String, Integer, Date, Boolean
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER as UNIQUEIDENTIFIER # TODO: we can use this import statement in a switch to support multiple dbs
from base import Base
import config
import requests
import json
from types import SimpleNamespace as Namespace

class User(Base):
    __tablename__ = 'Users'
    __table_args__ = {'schema': 'IQ'}

    #TODO: using UNIQUEIDENTIFER at all, especially as it's correct type and PK presents an interesting
    # challenge, SqlAlchemy doesn't support a database agnostic way of dealing with this
    # will have to create a case for other databases down the road and eventually test it
    # Dockerize some databases perhaps to test, for now this is the MsSql way of dealing with it
    UserId = Column(UNIQUEIDENTIFIER, primary_key=True)
    IsDeleted = Column(Boolean)
    SiteId = Column(String) # UUID TODO: figure out which UUID was causing issues & resolve
    CreatedDate = Column(Date)
    ModifiedDate = Column(Date)
    LocationId = Column(String) # UUID
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
    ExternalId = Column(String) # UUID
    InternalComments = Column(String)
    RoleId = Column(String) #UUID
    AuthenticatedBy = Column(String)
    AccountSetupProgress = Column(Integer)
    TrainingPercentComplete = Column(Integer)
    IsEmailVerified = Column(Boolean)
    IsWelcomeEmailSent = Column(Boolean)
    PreventProviderUpdates = Column(Boolean)
    IsOutOfOffice = Column(Boolean)
    Portal = Column(Integer)

    def __init__(self, data):
        # Extract fields from the raw data
        self.UserId = data.UserId
        self.IsDeleted = data.IsDeleted
        self.SiteId = data.SiteId
        self.CreatedDate = data.CreatedDate
        self.ModifiedDate = data.ModifiedDate
        self.LocationId = data.LocationId
        self.LocationName = data.LocationName
        self.IsActive = data.IsActive
        self.IsOnline = data.IsOnline
        self.IsOnlineLastUpdated = data.IsOnlineLastUpdated
        self.FirstName = data.FirstName
        self.LastName = data.LastName
        self.Email = data.Email
        self.Username = data.Username
        self.Phone = data.Phone
        self.SchoolIdNumber = data.SchoolIdNumber
        self.Grade = data.Grade
        self.Homeroom = data.Homeroom
        self.ExternalId = data.ExternalId
        self.InternalComments = data.InternalComments
        self.RoleId = data.RoleId
        self.AuthenticatedBy = data.AuthenticatedBy
        self.AccountSetupProgress = data.AccountSetupProgress
        self.TrainingPercentComplete = data.TrainingPercentComplete
        self.IsEmailVerified = data.IsEmailVerified
        self.IsWelcomeEmailSent = data.IsWelcomeEmailSent
        self.PreventProviderUpdates = data.PreventProviderUpdates
        self.IsOutOfOffice = data.IsOutOfOffice
        self.Portal = data.Portal

def __get_users_request(page):
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
    # Return response as JSON
    return requests.request("POST", url, headers=headers, data=payload, files=files)

# Retrieve the number of pages to iterate through
def get_num_pages():
    return __get_users_request(0).json()['Paging']['PageCount']

# Retreives all users from a request page and returns a list of all as User objects
def get_users_page(page):

    users = []

    response = __get_users_request(page)

    # Namespace hack of the response, nicely puts JSON data into objects so fields can be accessed
    # in the form user.Name user.LocationId etc etc intead of lame indexing Eg user['Name']
    response_users = response.json(object_hook = lambda d : Namespace(**d)).Items 

    # Create an instance of User for each returned user and append it to the list
    for u in response_users:
        # Create the user
        new_user = User(u)
        # Append the user
        users.append(new_user)

    return users


    


