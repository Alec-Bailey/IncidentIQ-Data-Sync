# A location class representing IncidentIQ Locaitons
from sqlalchemy import Column, String, Integer, Date, Boolean, Numeric
from sqlalchemy_utils.types.uuid import UUIDType as UNIQUEIDENTIFIER
from sqlalchemy.orm import validates
from base import Base, IIQ_Datatype as IIQ
import config
import requests


class Location(Base, IIQ):
    """Location is an instanciable class which holds all the information
    for one Location in IncidentIQ. Location also contains methods to make an
    API request to retreive an entire page of Locations. Location is declaratively 
    mapped in SqlAlchemy to the 'Locations' table.
    (by default, differs by configurable table names).
    On instantiation Location can be inserted into 'Locations' via an SqlAlchemy
    session."""
    __tablename__ = config.LOCATIONS_TABLE_NAME
    if config.SCHEMA is not None:
        __table_args__ = {'schema': config.SCHEMA}

    LocationId = Column(UNIQUEIDENTIFIER(binary=False), primary_key=True)
    SiteId = Column(UNIQUEIDENTIFIER(binary=False))
    Name = Column(String(length=config.STRING_LENGTH))
    Abbreviation = Column(String(length=config.STRING_LENGTH))
    CreatedDate = Column(Date)
    ModifiedDate = Column(Date)
    AddressId = Column(UNIQUEIDENTIFIER(binary=False))
    Street1 = Column(String(length=config.STRING_LENGTH))
    Street2 = Column(String(length=config.STRING_LENGTH))
    City = Column(String(length=config.STRING_LENGTH))
    State = Column(String(length=config.STRING_LENGTH))
    Zip = Column(String(length=config.STRING_LENGTH))
    Country = Column(String(length=config.STRING_LENGTH))
    Latitude = Column(Numeric)
    Longitude = Column(Numeric)
    LocationTypeId = Column(UNIQUEIDENTIFIER(binary=False))
    LocationType = Column(
        String(length=config.STRING_LENGTH))    #LocationType.Name

    fields = [
        'LocationId', 'SiteId', 'Name', 'Abbreviation', 'CreatedDate',
        'ModifiedDate', 'AddressId', 'Street1', 'Street2', 'City', 'State', 
        'Zip', 'Country', 'Latitude', 'Longitude', 'LocationTypeId',
        'LocationType'
    ]

    @validates(*fields)
    def validate_inserts(self, key, value):
        return super().validate_inserts(key, value)

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
        self.State = IIQ.find_element(data, 'Address', 'State')
        self.Zip = IIQ.find_element(data, 'Address', 'Zip')
        self.Country = IIQ.find_element(data, 'Address', 'Country')
        self.Latitude = IIQ.find_element(data, 'Address', 'Latitude')
        self.Longitude = IIQ.find_element(data, 'Address', 'Longitude')
        self.LocationTypeId = data.LocationTypeId
        self.LocationType = IIQ.find_element(data, 'LocationType', 'Name')

    @staticmethod
    def get_data_request(page_number):
        url = "https://" + config.IIQ_INSTANCE + "/api/V1.0/locations?$p=" + str(
            page_number) + "&$s=" + str(config.PAGE_SIZE)

        payload = {}
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

        return requests.request("GET",
                                url,
                                headers=headers,
                                data=payload,
                                timeout=config.TIMEOUT)

    @staticmethod
    def get_num_pages():
        return Location.get_data_request(0).json()['Paging']['PageCount']

    @classmethod
    def get_page(cls, page_number):
        return super().get_page(page_number)
