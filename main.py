#!/usr/bin/env python
"""main.py: Runs a sync to pull IncidentIQ information into a user 
   configured database

This execution script implements a ThreadPoolExecutor to spawn a
configurable number of worker threads which make API calls to
the IncidentIQ API. Inventory data recieved from the IncidentIQ
API is inserted into the configured database via SqlAlchemy ORM mappings.    
"""

from configparser import ConfigParser
import time
import concurrent.futures
from concurrent.futures import Future
from threading import Lock
from sqlalchemy.sql.sqltypes import DateTime
from base import Session, engine, Base, IIQ_Datatype
from user import User
from location import Location
from custom_fields import UserCustomFields, AssetCustomFields
import config

__author__ = "Alec Bailey"
__license__ = "GPL-3.0"
__version__ = "1.0.0"
__maintainer__ = "Alec Bailey"
__email__ = "alecj.bailey@gmail.com"
__status__ = "Development"

def __generate_custom_fields_tables():
    UserCustomFields.create_table('UserCustomFields', 'UserId')
    AssetCustomFields.create_table('AssetCustomFields', 'AssetId')


# One unit of work, executed by a thread. Creates a session and preforms a web
# request to the IncidentIQ API. Inserts the returned elements into the
# appropriate database table, and commits the changes.
def __sync_object(cls : IIQ_Datatype, index):
    session = Session()
    
    # Retrieve an entire API Page worth of objects
    page = cls.get_page(index)


    # Add each object to the session and commit it
    session.add_all(page)
    

    session.commit() #TODO: this is causing a reace condition on commit?? changed to threadsafe version?
    session.close()


def __execute_sync(IIQ_Type : IIQ_Datatype):
    # Pull all users down into database
    num_pages = IIQ_Type.get_num_pages()

    # Create a thread pool with config.THREADS number of threads. This calls __sync_object
    # for each page of the API we wish to request, from page 0 to num_pages. Each thread
    # is responsible for adding exactly one page of the API response (by default 1000 objects) 
    # to it's session and commiting the data to the database. Threads then exit, making room 
    # for another thread to fetch and operate on the next page if config.THREADS is less than 
    # num_pages.
    with concurrent.futures.ThreadPoolExecutor(max_workers = int(config.THREADS)) as executor:
        thread = {executor.submit(__sync_object, IIQ_Type, index): index for index in range(0, num_pages)}

    
if __name__ == '__main__':
    start_time = time.time() #TODO: remove
    __generate_custom_fields_tables()
    # Generate database schema from SqlAlchemy
    Base.metadata.create_all(engine)

    # Execute the Users sync
    #__execute_sync(User)

    #__execute_sync(Location)



    stop_time = time.time() #TODO: remove

    print("Execution took --- %s seconds ---" % (stop_time - start_time))

