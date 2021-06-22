# A location class representing IncidentIQ Locaitons
from sqlalchemy import Column, String, Integer, Date, Boolean, Numeric
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER as UNIQUEIDENTIFIER # TODO: we can use this import statement in a switch to support multiple dbs
from sqlalchemy.orm import validates
from base import Base, IIQ_Datatype
import config
import requests
from types import SimpleNamespace as Namespace

class Location(Base, IIQ_Datatype):
    __tablename__ = 'Locations'
    __tableargs__ = {'schema': config.SCHEMA}

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
    

    @validates( 'LocationId', 'SiteId', 'Name', 'Abbreviation', 'CreatedDate',
     'ModifiedDate', 'AddressId', 'Street1', 'Street2', 'City', 'Zip', 
     'Country', 'Latitude', 'Longitude', 'LocationTypeId', 'LocationType')
    def empty_string_to_null(self, key, value):
         return super().empty_string_to_null(key, value)

    def __init__(self, data):
        self.LocationId = data.LocationId
        self.SiteId = data.SiteId
        self.Name = data.Name
        self.Abbreviation = data.Abbreviation
        self.CreatedDate = data.CreatedDate
        self.ModifiedDate = data.ModifiedDate
        self.AddressId = data.AddressId
        self.Street1 = data.Address.Street1
        self.Street2 = data.Address.Street2
        self.City = data.Address.City
        self.Zip = data.Address.Zip
        self.Country = data.Address.Country
        self.Latitude = data.Address.Latitude
        self.Longitude = data.Address.Longitude
        self.LocationTypeId = data.LocationTypeId
        self.LocationType = data.LocationType.Name

    @staticmethod
    def __get_data_request(page_number):
        url = "https://" + config.IIQ_INSTANCE + "/api/V1.0/locations?$p=" + str(page_number) +"&$s=" + str(config.PAGE_SIZE)

        payload={}
        headers = {
        'Connection': ' keep-alive',
        'Accept': ' application/json, text/plain, */*',
        'User-Agent': ' Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'Client': ' WebBrowser',
        'Sec-Fetch-Site': ' same-origin',
        'Sec-Fetch-Mode': ' cors',
        'Sec-Fetch-Dest': ' empty',
        'Accept-Encoding': ' gzip, deflate, br',
        'Accept-Language': ' en-US,en;q=0.9',
        'Authorization': 'Bearer ' + config.IIQ_TOKEN
        }

        return requests.request("GET", url, headers=headers, data=payload)

    @staticmethod
    def get_num_pages():
        return Location.__get_data_request(0).json()['Paging']['PageCount']

    @classmethod
    def get_page(page_number):
        return super().get_page(page_number)