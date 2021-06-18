from configparser import ConfigParser

cf = ConfigParser()
cf.read('config.ini')

# Local Database for backup
DATABASE = cf.get('Database', 'Database')
DB_CONNECTION_STRING = cf.get('Database', 'ConnectionString')
SCHEMA = cf.get('Database', 'Schema')
# Incident IQ Credentials
IIQ_INSTANCE = cf.get('IncidentIQ', 'Instance')
IIQ_TOKEN = cf.get('IncidentIQ', 'Token')
# The number of elements to request in each call to the API, can be tuned down for low memory machines (slower)
# or up for servers which can handle the load (faster).
PAGE_SIZE = cf.get('General', 'PageSize')
THREADS = cf.get('General', 'Threads')
