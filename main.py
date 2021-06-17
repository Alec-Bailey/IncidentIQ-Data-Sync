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
from sqlalchemy.sql.sqltypes import DateTime
from base import Session, engine, Base
import user
import config

__author__ = "Alec Bailey"
__license__ = "GPL-3.0"
__version__ = "1.0.0"
__maintainer__ = "Alec Bailey"
__email__ = "alecj.bailey@gmail.com"
__status__ = "Development"

# One unit of work, executed by a thread. Creates a session preforms a web
# request to the IncidentIQ API. Inserts the returned elements into the
# appropriate database table, and commits the changes.
def __sync_object(index): #TODO: pass object to make object independent
    session = Session()

    page = user.get_users_page(index)
    for u in page:
        session.add(u)
    session.commit()
    session.close()

if __name__ == '__main__':
    start_time = time.time() #TODO: remove
    # Generate database schema from SqlAlchemy
    Base.metadata.create_all(engine)
    # Create a session
    session = Session()

    # Pull all users down into database
    num_pages = user.get_num_pages()

    # Create a thread pool with config.THREADS number of threads. This calls __sync_object
    # for each page of the API we wish to request, from page 0 to num_pages. Each thread
    # is responsible for adding exactly one page of the API response (by default 1000 objects) 
    # to it's session and commiting the data to the database. Threads then exit, making room 
    # for another thread to fetch and operate on the next page if config.THREADS is less than 
    # num_pages.
    with concurrent.futures.ThreadPoolExecutor(max_workers = int(config.THREADS)) as executor:
        thread = {executor.submit(__sync_object, index): index for index in range(0, num_pages)}

    stop_time = time.time() #TODO: remove

    print("Execution took --- %s seconds ---" % (stop_time - start_time))

