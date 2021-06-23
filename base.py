import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from types import SimpleNamespace as Namespace
import config

engine = sqlalchemy.create_engine(config.DB_CONNECTION_STRING, pool_size=int(config.THREADS), max_overflow=0)

# Create a scoped session for thread safety, attempting to commit multiple sessions
# at once
Session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()


class IIQ_Datatype:

    # Validator ensures empty strings are entered as null
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value

    @staticmethod
    def get_data_request(page_number):
        raise NotImplementedError("__get_data_request API Request not implemented")

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
    def find_element(lookup_object : Namespace, *args):
        # Verify that the attribute exists at every level, moving
        # into the object as we find exising attributes
        for i in range (0, len(args) -1):
            if hasattr(lookup_object, args[i]):
                lookup_object = getattr(lookup_object, args[i])
            else:
                return None

        # If the outer most attributes exist, return the value
        if hasattr(lookup_object, args[len(args)-1]):
            return getattr(lookup_object, args[len(args)-1])
        # Return None if the attribute does not exist
        return None

    # Retrieves a page of elements from the API, and creates an appropriate
    # object of each type for all elements. Returns a list of these objects
    @classmethod
    def get_page(cls, page_number):
        # Create a list to hold all instantiated objects
        iiq_classes = []

        # Retreive the API data from the calling class
        response = cls.get_data_request(page_number)

        # Namespace hack of the response, nicely puts JSON data into objects so fields can be accessed
        # in the form user.Name user.LocationId etc etc intead of lame indexing Eg user['Name']
        response_types = response.json(object_hook = lambda d : Namespace(**d)).Items
    
        # Iterate over every returned elmeent in the response and instantiate
        # an instance of each respective class. Add that to a list so we can
        # later add this to a session & commit it to the database via 
        # SqlAlchemy
        for element in response_types:
            # Instantiation of the specified class cls
            # EG User(element) or Location(element)
            new_iiq_class = cls(element)
            iiq_classes.append(new_iiq_class)

        return iiq_classes
