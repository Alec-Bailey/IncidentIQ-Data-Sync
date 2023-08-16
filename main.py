#!/usr/bin/env python
"""main.py: Runs a sync to pull IncidentIQ information into a user 
   configured database

This execution script implements a ThreadPoolExecutor to spawn a
configurable number of worker threads which make API calls to
the IncidentIQ API. Inventory data recieved from the IncidentIQ
API is inserted into the configured database via SqlAlchemy ORM mappings.    
"""

import time
import concurrent.futures
import pyodbc
from base import Session, engine, Base, IIQ_Datatype
from user import User
from location import Location
from asset import Asset
from ticket import Ticket
from room import Room
from team import Team
from custom_fields import UserCustomFields, AssetCustomFields, TicketCustomFields
import config

__author__ = "Alec Bailey"
__license__ = "GPL-3.0"
__version__ = "1.0.0"
__maintainer__ = "Alec Bailey"
__email__ = "alecj.bailey@gmail.com"
__status__ = "Development"


# Dynamically create ORM mapped classes and tables from the existing
# custom fields for individual types in IncidentIQ.
def __generate_custom_fields_tables():
    UserCustomFields.create_table(config.USERS_CF_TABLE_NAME, 'UserId')
    AssetCustomFields.create_table(config.ASSETS_CF_TABLE_NAME, 'AssetId')
    TicketCustomFields.create_table(config.TICKETS_CF_TABLE_NAME, 'TicketId')


# One unit of work, executed by a thread. Creates a session and preforms a web
# request to the IncidentIQ API. Inserts the returned elements into the
# appropriate database table, and commits the changes.
def __sync_object(cls: IIQ_Datatype, index):
    try:
        session = Session()
        # Retrieve an entire API Page worth of objects
        page = cls.get_page(index)
        # Add each object to the session and commit it
        session.add_all(page)
        session.commit()
        session.close()

    #TODO: kill parent on error
    except pyodbc.Error as e:
        print("A pyodbc occured in a thread ", e)
    except Exception as e:
        print("A non pyodbc error occured - refer to documenation", e)
        raise e


# Sync all of a specified type into the database
def __execute_sync(IIQ_Type: IIQ_Datatype):
    # Retrieve the number of pages the passed type has in IncidentIQ
    num_pages = IIQ_Type.get_num_pages()

    # Create a thread pool with config.THREADS number of threads. This calls __sync_object
    # for each page of the API we wish to request, from page 0 to num_pages. Each thread
    # is responsible for adding exactly one page of the API response (by default 1000 objects)
    # to it's session and commiting the data to the database. Threads then exit, making room
    # for another thread to fetch and operate on the next page for as many pages as are present
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=int(config.THREADS)) as executor:
        thread = {
            executor.submit(__sync_object, IIQ_Type, index): index
            for index in range(0, num_pages)
        }


if __name__ == '__main__':
    start_time = time.time()
    __generate_custom_fields_tables()
    # Drop all tables to pull fresh data
    Base.metadata.drop_all(bind=engine)
    # Generate database schema from SqlAlchemy
    Base.metadata.create_all(engine)

    # Execute the sync for all types
    __execute_sync(Team)
    __execute_sync(Ticket)
    __execute_sync(User)
    __execute_sync(Location)
    __execute_sync(Asset)
    __execute_sync(Room)

    # Useful for testing without threading issues
    #num_pages = Asset.get_num_pages()
    #for i in range(0, 1):
    #    __sync_object(Asset, i)

    stop_time = time.time()
    print("Execution took --- %s seconds ---" % (stop_time - start_time))
