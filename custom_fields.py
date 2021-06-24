from sqlalchemy import Column, String, Integer, Date, Table
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import mapper
import requests
import json

from sqlalchemy.sql.expression import all_
from base import Base, IIQ_Datatype
import config

# A custom fields metaclass which allows for the dynamic deffinition
# of fields given the API response
class IIQ_CustomFields(object):
    
    @staticmethod
    def get_fields_request(page_number):
        raise NotImplementedError("get_fields_request API Request not implementd")

    # Parse out all returned custom field types from the API
    # This should be the same for all types of custom fields
    @classmethod
    def parse_fields(cls):
        response = cls.get_fields_request(0)
        # Dict storing all parsed custom fields
        # formatted 'Field UUID' -> 'Field Name'
        all_fields = {}

        # Iterate over all returned fields and add to dict
        for item in response.json()['Items']:
            # Remove any spaces from name
            name = item['CustomFieldType']['Name'].replace(" ", "")
            all_fields[item['CustomFieldId']] = name

        return all_fields

    # Create and map the custom field type table to the ORM.
    # After the creation of this table, the base class [Users/Assets/etc]CustomFields can
    # be populated with the API fields data
    @classmethod
    def create_table(cls, table_name, primarykey_name):
        response = cls.get_fields_request(0)
        all_fields = cls.parse_fields(response)
        t = Table(table_name, Base.metadata, Column(primarykey_name, UNIQUEIDENTIFIER, primary_key=True),
        *(Column(field_name, String) for field_name in list(all_fields.values())), schema=config.SCHEMA)
        mapper(cls, t)


class UserCustomFields(IIQ_CustomFields):

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

        response = requests.request("POST", url, headers=headers, data=payload)

        return response

class AssetCustomFields(IIQ_CustomFields):

    @staticmethod
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

        response = requests.request("POST", url, headers=headers, data=payload)

        return response
