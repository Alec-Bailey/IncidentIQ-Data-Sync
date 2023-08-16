#!/usr/bin/env python
"""config.py: Retrieve configuration information

Config uses configparser to read information from the user configured
config.ini. Appropriately named variables are created for use elsewhere
in the programs implementation.
"""

from configparser import ConfigParser

cf = ConfigParser()
cf.read('config.ini')

# Local Database for backup
DB_CONNECTION_STRING = cf.get('Database', 'ConnectionString')
SCHEMA = cf.get(
    'Database', 'Schema') if len(cf.get(
        'Database',
        'Schema').strip()) > 0 else None    # Assign to none if schema is blank
STRING_LENGTH = int(cf.get('Database', 'StringLength'))
# Table Names
ASSETS_TABLE_NAME = cf.get('Tables', 'Assets')
ASSETS_CF_TABLE_NAME = cf.get('Tables', 'AssetsCustomFields')
USERS_TABLE_NAME = cf.get('Tables', 'Users')
USERS_CF_TABLE_NAME = cf.get('Tables', 'UsersCustomFields')
LOCATIONS_TABLE_NAME = cf.get('Tables', 'Locations')
TICKETS_TABLE_NAME = cf.get('Tables', 'Tickets')
TICKETS_CF_TABLE_NAME = cf.get('Tables', 'TicketsCustomFields')
ROOMS_TABLE_NAME = cf.get('Tables', 'Rooms')
TEAMS_TABLE_NAME = cf.get('Tables', 'Teams')
# Incident IQ Credentials
IIQ_INSTANCE = cf.get('IncidentIQ', 'Instance')
IIQ_TOKEN = cf.get('IncidentIQ', 'Token')
# General configuration
PAGE_SIZE = cf.get('General', 'PageSize')
THREADS = cf.get('General', 'Threads')
TIMEOUT = int(cf.get('General', 'Timeout'))
