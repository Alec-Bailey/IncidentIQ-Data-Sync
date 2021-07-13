#!/usr/bin/env python
"""base.py: Creates the Base and IIQ_Datatype

Base and IIQ_Datatype are the foundation on which declaratively
mapped SqlAlchemy classes in this program are built on. Methods
to retrieve data from the API are included, as well as classmethods
which allow for type to be deteremind at runtime for objects.
This allows for the modular code to insert User objects into the
database as well as Assets etc.
"""

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, String, Integer, Date, Table
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import mapper    # 'Unused' imports needed for pyinstaller
from sqlalchemy.sql import default_comparator
from sqlalchemy.ext import baked
from sqlalchemy.dialects.mysql import mysqldb
import sqlalchemy
from types import SimpleNamespace as Namespace
import config

# Create nescessary SqlAlchemy binds
engine = sqlalchemy.create_engine(config.DB_CONNECTION_STRING,
                                  pool_size=int(config.THREADS),
                                  max_overflow=0,
                                  pool_timeout=120)
# Create a scoped session for thread safety, attempting to commit multiple sessions
# at once
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


class IIQ_Datatype:
    """IIQ_Datatype is the base class from which all created
    IncidentIQ datatypes inherit from. It defines methods 
    which are nescessary for each type to retrieve, parse,
    and transform data from the IncidentIQ API.
    """

    # Validator ensures empty strings are entered as null and
    # strings never exceed the capacity imposed by multi-database support.
    # The smallest VARCHAR type we support is 4,000 characters due to
    # ORACLE DB. There is probably no good reason for any asset to have a
    # string this long in the database
    def validate_inserts(self, key, value):
        if isinstance(value, str) and value == '':
            return None    # Set empty string to None (Null in databases)
        elif isinstance(value, str) and len(value) >= config.STRING_LENGTH:
            return value[0:config.STRING_LENGTH - 1]    # Truncate the string
        else:
            return value

    # Given a page number, returns the entire page response from the API
    @staticmethod
    def get_data_request(page_number):
        raise NotImplementedError(
            "__get_data_request API Request not implemented")

    # Returns the number of pages the API has for the calling type
    @staticmethod
    def get_num_pages():
        raise NotImplementedError("get_num_pages not impelmeneted")

    # Safely Checks if the API response contains an element at the specified path.
    # Takes an unlimited number of arguments, each successive argument
    # corrosponding to a successive level of nesting in the returned JSON
    # Eg. _lookup_api_contents(data, 'Address', 'Street1')
    # If data.Address.Street1 does exist, return the value. Otherwise
    # return None
    @staticmethod
    def find_element(lookup_object: Namespace, *args):
        # Verify that the attribute exists at every level, moving
        # into the object as we find exising attributes
        for i in range(0, len(args) - 1):
            if hasattr(lookup_object, args[i]):
                lookup_object = getattr(lookup_object, args[i])
            else:
                return None

        # If the outer most attributes exist, return the value
        if hasattr(lookup_object, args[len(args) - 1]):
            return getattr(lookup_object, args[len(args) - 1])
        # Return None if the attribute does not exist
        return None

    # Retrieves a page of items from the API, and creates an appropriate mapped
    # instance for all items. Returns a list of created objects.
    @classmethod
    def get_page(cls, page_number):
        iiq_classes = []
        # Retreive the API data from the calling class
        response = cls.get_data_request(page_number)

        # Namespace hack of the response, nicely puts JSON data into objects so fields can be accessed
        # in the form user.Name user.LocationId etc etc intead of lame indexing Eg user['Name']
        response_types = response.json(
            object_hook=lambda d: Namespace(**d)).Items

        # Iterate over every returned elmeent in the response and instantiate
        # an instance of each respective class. Add the instance to a list so we can
        # later add this to a session & commit it to the database via
        # SqlAlchemy
        for item in response_types:
            # Instantiation of the specified class cls to represent one item
            # EG User(item) or Asset(item)
            new_iiq_class = cls(item)
            iiq_classes.append(new_iiq_class)

            # If the given class has custom fields create an instance of the
            # appropraite IIQ_CustomFields object, and add it to the list
            customs = cls._get_custom_fields(item)
            if customs is not None:
                iiq_classes.append(customs)

        return iiq_classes

    # Retrieve the sublcass of IIQ_CustomFields (in custom_fields.py)
    # which corrosponds to the type of the calling class.
    # EG Asset.get_custom_type() returns AssetCustomFields
    @staticmethod
    def get_custom_type():
        raise NotImplementedError("get_custom_type not implemeneted")

    # Retrieves the custom field values from an 'Item' of the API response Namespace
    # Returns an instance of the appropriate custom_field type for the Item or None
    # if the Item had no custom fields
    @classmethod
    def _get_custom_fields(cls, item):
        if hasattr(cls, 'custom_fields') and hasattr(item, 'CustomFieldValues'):

            # A list of attributes to set in the form ['Name'] -> ['Value']
            attributes = {}
            returned_fields = item.CustomFieldValues    # Nest into custom field values

            # Iterate over every returned custom field for the object
            # When a custom filed type id is in the defined custom_fields
            # for the class, add it to the attributes dict [FieldName] -> [Value]
            for f in returned_fields:
                if f.CustomFieldTypeId in cls.custom_fields:
                    attributes[cls.custom_fields[f.CustomFieldTypeId]] = f.Value
            # Create an object consisting of the datatype
            Custom_Type = cls.get_custom_type()
            new_custom = Custom_Type(getattr(item, Custom_Type.primarykey_name),
                                     cls.custom_fields, attributes)

            return new_custom
        else:
            return None
