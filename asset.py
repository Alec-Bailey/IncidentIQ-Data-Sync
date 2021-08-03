#!/usr/bin/env python
"""asset.py: Declaratively mapped Asset from IncidentIQ

Asset contains the methods nescessary to pull and transofrm
the data from the IncidentIQ to conform to declaratively mapped
object in SqlAlcemy. Asset can be instantiated with data from
IncidentIQ to insert into the specified database.
"""

from sqlalchemy import Column, String, Integer, Date, Boolean, Numeric
from sqlalchemy_utils.types.uuid import UUIDType as UNIQUEIDENTIFIER
import requests
from requests.models import HTTPError
from sqlalchemy.orm.mapper import validates
from base import Base, IIQ_Datatype as IIQ
from custom_fields import AssetCustomFields
import config


class Asset(Base, IIQ):
    """Asset is an instanciable class which holds all the information
    for one Asset in IncidentIQ. Asset also contains methods to make an
    API request to retreive an entire page of Assets as well as
    create an instance of the dynamic AssetCustomFields class.
    Asset is declaratively mapped in SqlAlchemy to the 'Assets' table 
    (by default, differs by configurable table names).
    On instantiation, Asset can be inserted into 'Assets' via an SqlAlchemy
    session."""

    __tablename__ = config.ASSETS_TABLE_NAME
    if config.SCHEMA is not None:
        __table_args__ = {'schema': config.SCHEMA}

    # Retrieve custom fields
    custom_fields = AssetCustomFields.parse_fields(
        AssetCustomFields.get_fields_request(0))

    AssetId = Column(UNIQUEIDENTIFIER(binary=False), primary_key=True)
    SiteId = Column(UNIQUEIDENTIFIER(binary=False))
    ProductId = Column(UNIQUEIDENTIFIER(binary=False))
    CreatedDate = Column(Date)
    ModifiedDate = Column(Date)
    AssetTypeId = Column(UNIQUEIDENTIFIER(binary=False))
    AssetTypeName = Column(String(length=config.STRING_LENGTH))
    IsDeleted = Column(Boolean)
    IsTraining = Column(Boolean)
    StatusTypeId = Column(UNIQUEIDENTIFIER(binary=False))
    StatusName = Column(String(length=config.STRING_LENGTH)) # Nested
    AssetTag = Column(String(length=config.STRING_LENGTH))
    SerialNumber = Column(String(length=config.STRING_LENGTH))
    ExternalId = Column(String(length=config.STRING_LENGTH))
    Name = Column(String(length=config.STRING_LENGTH))
    CanOwnerManage = Column(Boolean)
    CanSubmitTicket = Column(Boolean)
    IsFavorite = Column(Boolean)
    ModelId = Column(UNIQUEIDENTIFIER(binary=False))
    ModelName = Column(String(length=config.STRING_LENGTH))    # Nested
    CategoryId = Column(UNIQUEIDENTIFIER(binary=False))    # Nested
    CategoryName = Column(String(length=config.STRING_LENGTH))    # Nested
    OwnerId = Column(UNIQUEIDENTIFIER(binary=False))
    OwnerName = Column(String(length=config.STRING_LENGTH))    # Nested
    OwnerUsername = Column(String(length=config.STRING_LENGTH))    # Nested
    LocationId = Column(UNIQUEIDENTIFIER(binary=False))
    LocationName = Column(String(length=config.STRING_LENGTH))    # Nested
    LocationDetails = Column(String(length=config.STRING_LENGTH))
    LocationRoomId = Column(UNIQUEIDENTIFIER(binary=False))
    LocationRoomName = Column(String(length=config.STRING_LENGTH))    # Nested
    Notes = Column(String(length=config.STRING_LENGTH))
    HasOpenTicket = Column(Boolean)
    OpenTicket = Column(Integer)
    PurchasedDate = Column(Date)
    DeployedDate = Column(Date)
    RetiredDate = Column(Date)
    PurchasePrice = Column(Numeric)
    PurchasePoNumber = Column(String(length=config.STRING_LENGTH))
    WarrantyExpirationDate = Column(Date)
    WarrantyInfo = Column(String(length=config.STRING_LENGTH))
    LastInventoryDate = Column(Date)
    InvoiceNumber = Column(String(length=config.STRING_LENGTH))
    Vendor = Column(String(length=config.STRING_LENGTH))
    InsuranceExpirationDate = Column(Date)
    InsuranceInfo = Column(String(length=config.STRING_LENGTH))
    FundingSourceId = Column(UNIQUEIDENTIFIER(binary=False))
    IsReadOnly = Column(Boolean)
    StorageUnitNumber = Column(String(length=config.STRING_LENGTH))
    StorageSlotNumber = Column(Integer)
    StorageLocationId = Column(UNIQUEIDENTIFIER(binary=False))
    StorageLocationName = Column(String(length=config.STRING_LENGTH))

    # List of fields allows insertion via setattr() easily, as well as
    # validation without needless code
    fields = [
        'AssetId', 'AssetTag', 'AssetTypeId', 'AssetTypeName', 'CanOwnerManage',
        'CanSubmitTicket', 'CreatedDate', 'DeployedDate', 'ExternalId',
        'FundingSourceId', 'HasOpenTicket', 'InsuranceExpirationDate',
        'InsuranceInfo', 'InvoiceNumber', 'IsDeleted', 'IsFavorite',
        'IsReadOnly', 'IsTraining', 'LastInventoryDate', 'LocationDetails',
        'LocationId', 'LocationName', 'LocationRoomId', 'LocationRoomName',
        'ModelId', 'ModelName', 'ModifiedDate', 'CategoryName', 'CategoryId',
        'Name', 'Notes', 'OpenTicket', 'OwnerId', 'OwnerName', 'OwnerUsername',
        'ProductId', 'PurchasePoNumber', 'PurchasePrice', 'PurchasedDate',
        'RetiredDate', 'SerialNumber', 'SiteId', 'StatusName', 'StatusTypeId',
        'StorageLocationId', 'StorageLocationName', 'StorageSlotNumber',
        'StorageUnitNumber', 'Vendor', 'WarrantyExpirationDate', 'WarrantyInfo'
    ]

    # Validator ensures empty strings are entered as null
    @validates(*fields)
    def validate_inserts(self, key, value):
        return super().validate_inserts(key, value)

    def __init__(self, data):
        # Extract fields from the raw data, optional fields are retrieved
        # safely via find_element
        for field in self.fields:
            # For non-nested fields that exist at the first level of the JSON
            # we can use setattr to assign values, since the fields are
            # named exactly as they appear in the JSON. Convention over configuration
            # wins here. For example, an asset JSON response will have a field 'AssetId'
            # at the base level of that item. Thus, find_element can grab it simply by being
            # passed 'AssetId'. By design, the column is also named 'AssetId', so we can
            # iterate simply and set these fields.
            setattr(self, field, IIQ.find_element(data, field))

        # Nested fields are more complex, and thus are commented in the declaration
        # as Nested. We simply path these out by hand since there are only a few, and
        # often they are purposeful inclusions that aren't nescessary but useful to
        # end users. This is harmless even if they are optional fields in the API response,
        # since find_element will set them to None by default
        self.StatusName = IIQ.find_element(data, 'Status', 'Name')
        self.ModelName = IIQ.find_element(data, 'Model', 'Name')
        self.CategoryId = IIQ.find_element(data, 'Model', 'CategoryId')
        self.CategoryName = IIQ.find_element(data, 'Model', 'Category', 'Name')
        self.OwnerName = IIQ.find_element(data, 'Owner', 'Name')
        self.OwnerUsername = IIQ.find_element(data, 'Owner', 'Username')
        self.LocationName = IIQ.find_element(data, 'Location', 'Name')
        self.LocationRoomName = IIQ.find_element(data, 'LocationRoom', 'Name')

    @staticmethod
    def get_data_request(page):
        url = "https://" + config.IIQ_INSTANCE + "/api/v1.0/assets/?$p=" + str(
            page) + "&$s=" + config.PAGE_SIZE + "&$d=Ascending&$o=AssetTag"

        payload = "{\n    \"OnlyShowDeleted\": false,\n    \"Filters\": [\n        {\n            \"Facet\": \"AssetType\",\n            \"Id\": \"2a1561e5-34ff-4fcf-87de-2a146f0e1c01\"\n        }\n    ],\n    \"FilterByViewPermission\": true\n}"
        headers = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'Client': 'WebBrowser',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Authorization': 'Bearer ' + config.IIQ_TOKEN
        }

        response = requests.request("POST",
                                    url,
                                    headers=headers,
                                    data=payload,
                                    timeout=config.TIMEOUT)
        # Cause an exception if anything but success is returned
        if response.status_code != 200:
            print("ERROR: STATUS CODE NOT 200")
            raise HTTPError("""A request returned a status code other than 200\n
            Status Code: """ + str(response.status_code))

        # Cause an exception if for some reason the API returns nothing
        if response.json()['Paging']['PageSize'] <= 0:
            print("ERROR NO ELEMENTS WERE RETURNED")
            raise HTTPError("No elements were returned from a request")

        return response

    @staticmethod
    def get_num_pages():
        return Asset.get_data_request(0).json()['Paging']['PageCount']

    @classmethod
    def get_page(cls, page_number):
        return super().get_page(page_number)

    @staticmethod
    def get_custom_type():
        return AssetCustomFields

    @classmethod
    def _get_custom_fields(cls, item):
        return super()._get_custom_fields(item)
