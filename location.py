# A location class representing IncidentIQ Locaitons
from sqlalchemy import Column, String, Integer, Date, Boolean, Numeric
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER as UNIQUEIDENTIFIER # TODO: we can use this import statement in a switch to support multiple dbs
from sqlalchemy.orm import validates
from base import Base, IIQ_Datatype as IIQ
import config
import requests
from types import SimpleNamespace as Namespace

class Location(Base, IIQ):
    __tablename__ = 'Locations'
    __table_args__ = {'schema': config.SCHEMA}

    LocationId = Column(UNIQUEIDENTIFIER, primary_key=True)
    SiteId = Column(UNIQUEIDENTIFIER)
    Name = Column(String)
    Abbreviation = Column(String)
    CreatedDate = Column(Date)
    ModifiedDate = Column(Date)
    AddressId = Column(UNIQUEIDENTIFIER)
    Street1 = Column(String)
    Street2 = Column(String)
    City = Column(String)
    Zip = Column(String)
    Country = Column(String)
    Latitude = Column(Numeric)
    Longitude = Column(Numeric)
    LocationTypeId = Column(UNIQUEIDENTIFIER)
    LocationType = Column(String) #LocationType.Name
    

    @validates('LocationId', 'SiteId', 'Name', 'Abbreviation', 'CreatedDate',
     'ModifiedDate', 'AddressId', 'Street1', 'Street2', 'City', 'Zip', 
     'Country', 'Latitude', 'Longitude', 'LocationTypeId', 'LocationType')
    def empty_string_to_null(self, key, value):
         return super().empty_string_to_null(key, value)

    def __init__(self, data):
        # Call find_element on fields which are marked optional to be returned by the
        # IncidentIQ API. This is especially important to note for nested fields, the
        # parent of which can be optional even though when included there can
        # be required fields
        self.LocationId = data.LocationId
        self.SiteId = data.SiteId
        self.Name = IIQ.find_element(data, 'Name')
        self.Abbreviation = IIQ.find_element(data, 'Abbreviation')
        self.CreatedDate = data.CreatedDate
        self.ModifiedDate = data.ModifiedDate
        self.AddressId = data.AddressId
        self.Street1 = IIQ.find_element(data, 'Address', 'Street1')
        self.Street2 = IIQ.find_element(data, 'Address', 'Street2')
        self.City = IIQ.find_element(data, 'Address', 'City')
        self.Zip = IIQ.find_element(data, 'Address', 'Zip')
        self.Country = IIQ.find_element(data, 'Address' ,'Country') 
        self.Latitude = IIQ.find_element(data, 'Address', 'Latitude')
        self.Longitude = IIQ.find_element(data, 'Address', 'Longitude')
        self.LocationTypeId = data.LocationTypeId
        self.LocationType = IIQ.find_element(data, 'LocationType', 'Name')

    @staticmethod
    def get_data_request(page_number):
        url = "https://" + config.IIQ_INSTANCE + "/api/V1.0/locations?$p=" + str(page_number) +"&$s=" + str(config.PAGE_SIZE)

        payload={}
        headers = {
        'Connection': 'keep-alive',
        'Client': 'WebBrowser',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Authorization': 'Bearer ' + config.IIQ_TOKEN
        }

        return requests.request("GET", url, headers=headers, data=payload)

    @staticmethod
    def get_num_pages():
        return Location.get_data_request(0).json()['Paging']['PageCount']

    @classmethod
    def get_page(cls, page_number):
        return super().get_page(page_number)