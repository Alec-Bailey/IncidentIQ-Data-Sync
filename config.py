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
SCHEMA = cf.get('Database', 'Schema')
STRING_LENGTH = int(cf.get('Database', 'StringLength'))
# Incident IQ Credentials
IIQ_INSTANCE = cf.get('IncidentIQ', 'Instance')
IIQ_TOKEN = cf.get('IncidentIQ', 'Token')
# General configuration
PAGE_SIZE = cf.get('General', 'PageSize')
THREADS = cf.get('General', 'Threads')
TIMEOUT = int(cf.get('General', 'Timeout'))
