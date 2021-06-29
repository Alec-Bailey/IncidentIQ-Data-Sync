#!/usr/bin/env python
"""custom_fields.py: Mapped custom_fields from IncidentIQ

Contains the IIQ_CustomFields class which serves as the base from which
all other [Type]CustomFields classes inherit. Contains methods to parse
custom fields from data and instantaite objects of the appropriate type
with the provided API data. The subclasses of IIQ_CustomFields are
mapped dynamically with create_table based on an API call which retreives
the custom fields for each IncidentIQ type. Once mapped, subclasses of
IIQ_CustomFields operate just like an other IncidentIQ type, objects are
instantiated and inserted into a database with an SqlAlchemy Session.
"""

from sqlalchemy import Column, String, Integer, Date, Table
#from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy_utils.types.uuid import UUIDType as UNIQUEIDENTIFIER
from sqlalchemy.orm import mapper
import requests
from requests.models import HTTPError
import json

from sqlalchemy.sql.expression import all_
from base import Base, IIQ_Datatype
import config

# A custom fields metaclass which allows for the dynamic deffinition
# of fields given the API response
class IIQ_CustomFields(object):

    # Parse out all returned custom field types from the API
    # This should be the same for all types of custom fields
    def parse_fields(response):
        # Dict storing all parsed custom fields
        # formatted 'Field UUID' -> 'Field Name'
        all_fields = {}

        # Iterate over all returned fields and add to dict
        for item in response.json()['Items']:
            # Remove any spaces from name
            name = item['CustomFieldType']['Name'].replace(" ", "")
            all_fields[item['CustomFieldTypeId']] = name

        return all_fields

    # Set all passed in attributes as fields of the class
    def __init__(self, primarykey_name, primarykey_id, custom_fields, attributes):

        # Set the primary key
        setattr(self, primarykey_name, primarykey_id)

        # Set all fields to None so there exists a value for all
        for field in custom_fields.values():
            setattr(self, field, None)

        # For each field which is passed, set the corrosponding value
        for key in attributes:
            setattr(self, key, attributes[key])

    # Create and map the custom field type table to the ORM.
    # After the creation of this table, the base class [Users/Assets/etc]CustomFields can
    # be populated with the API fields data
    @classmethod
    def create_table(cls, table_name, primarykey_name):
        #response = cls.get_fields_request(0)
        all_fields = cls.parse_fields(cls.get_fields_request(0))
        t = Table(table_name, Base.metadata, Column(primarykey_name, UNIQUEIDENTIFIER(binary=False), primary_key=True),
        *(Column(field_name, String(length=config.STRING_LENGTH)) for field_name in list(all_fields.values())), schema=config.SCHEMA)
        mapper(cls, t)


class UserCustomFields(IIQ_CustomFields):

    primarykey_name = 'UserId'

    @staticmethod
    def get_fields_request(page_number):
        url = "https://" + str(config.IIQ_INSTANCE) + "/api/v1.0/custom-fields?$p=" + str(page_number) + "&$s=999999"

        payload = json.dumps({
        "SiteScope": "Aggregate",
        "Strategy": "AggregateUser"
        })
        headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
        'content-type': 'application/json',
        'accept': 'application/json, text/plain, */*',
        'Authorization': 'Bearer ' + config.IIQ_TOKEN
        }

        response = requests.request("POST", url, headers=headers, data=payload, timeout=config.TIMEOUT)
        # Cause an exception if anything but success is returned
        if response.status_code != 200:
            raise HTTPError("""A request returned a status code other than 200\n
            Status Code: """ + str(response.status_code))

        return response

    def __init__(self, asset_id, fields, attributes):
        super().__init__(self.primarykey_name, asset_id, fields, attributes)

class AssetCustomFields(IIQ_CustomFields):

    primarykey_name = 'AssetId'
    
    def get_fields_request(page_number):
        url = "https://" + str(config.IIQ_INSTANCE) + "/api/v1.0/custom-fields?$p=" + str(page_number) + "&$s=999999"

        payload = json.dumps({
        "SiteScope": "Aggregate",
        "Strategy": "AggregateAsset"
        })
        headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
        'content-type': 'application/json',
        'accept': 'application/json, text/plain, */*',
        'Authorization': 'Bearer ' + config.IIQ_TOKEN
        }

        response = requests.request("POST", url, headers=headers, data=payload, timeout=config.TIMEOUT)
        # Cause an exception if anything but success is returned
        if response.status_code != 200:
            raise HTTPError("""A request returned a status code other than 200\n
            Status Code: """ + str(response.status_code))

        return response


    def __init__(self, asset_id, fields, attributes):
        super().__init__(self.primarykey_name, asset_id, fields, attributes)
