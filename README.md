# Archived
This project has been archived, I no longer have access to IncidentIQ and cannot maintain the project further. In addition, IncidentIQ appears to have delivered tooling to handle the problems this tool intended to solve.

# Incident IQ Data Sync
Incident IQ Data Sync is a dynamic, database agnostic tool which syncs all of IncidentIQ's data into a local database. Designed to be performant, multithreaded, configurable and easily extended.

Contents
========

 * [Why?](#why)
 * [What databases are supported?](#supported-databases)
 * [Installation](#installation)
 * [Configuration](#configuration)
 * [Usage](#usage)
 * [What can I sync?](#what-can-i-sync)
 * [Contributing](#contributing)
 * [License](#license)

## Why?
---
Our district needed a tool that could:
+ Pull different types of Incident IQ data (Assets, Users, Locations, etc.) into a local database
+ Dynamically create and update tables for changing custom fields
+ Be configurable to run on changing infrastructure
+ Be easily maintainable and extensible
+ Support common SQL databases

## Supported Databases
---
Currently, support has been tested for:
 * [Microsoft SQL Server](https://www.microsoft.com/en-us/sql-server)
 * [Postgres](https://www.postgresql.org/)
 * [MySql](https://www.mysql.com/)
 * [Oracle](https://www.oracle.com/database/technologies/)
 * [MariaDB](https://mariadb.org/) 

Support *may* be possible for other database dialects [supported by SqlAlchemy](https://docs.sqlalchemy.org/en/14/dialects/). If you need support for an unsupported database create an issue, or see [Contributing](#contributing) and try it yourself!

## Installation
---

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the requirements.

```bash
pip install -r requirements.txt
```

*Note* Some libraries included in requirements.txt are database specific, and can be removed for your use case. Not all libraries for your specific database connection may be included in requirements.txt, check error messages and use pip to install libraries as needed. [The SqlAlchemy documentation](https://docs.sqlalchemy.org/en/14/core/engines.html) for setting up your connection string specifies the library used for that specific connection.

Rename `config-sample.ini` to `config.ini`

Set up your database connection - see [Configuration](#configuration)

*Note* some databases may require additional libraries on your system. It is up to you
to configure your system correctly.

#### *Note for Postgres users*

You may need to install libraries specific to Postgres, on Debian Based systems
`sudo apt-get install libpq-dev python-dev`


## Configuration
---
### Configuring your database connection string
To figure out how to write a connection string for your database see the [offical SqlAlchemy guide]( https://docs.sqlalchemy.org/en/14/core/engines.html).

**Basic Connection String**

`dialect+driver://username:password@host:port/database`

**Advanced Connection String**

The example in `config-sample.ini` is a connection string for an Microsoft Sql Server database using Windows authentication: 

`mssql+pyodbc://myDatabase.something.local/Inventory?driver=SQL+Server+Native+Client+11.0`

Every database and network is different, **please refer to the [official documentation.](https://docs.sqlalchemy.org/en/14/core/engines.html)**

Your configured database connection string should look like this:
```
[Database]
ConnectionString: 'postgresql://azurediamond:hunter2@localhost/mydatabase'
```
---

### Configuring the IncidentIQ API
**Instance**

Your IncidentIQ instance is just the unique host URL your district uses to access IncidentIQ. Usually, this is of the format `domain.incidentiq.com`.

*For example* Chicago Public Schools might have the host URL `cps.incidentiq.com`

**Token**

You must also create a bearer token within IncidentIQ. This is an authentication string which allows the program to make API requests out to your instance. Bearer tokens are assigned to a user in IncidentIQ, you can either create a user specifically for API access, or chose an administrator.

Navigate to ``Administration -> Developer Tools`` in the IncidentIQ webapp. Then chose a user from the drop down, and click `CREATE API TOKEN`.

![create token](images/create%20token.png "Create a bearer token")

A new API token will appear, copy this and add it to your config file under `Token`

![generated token](images/generated%20token.png "Generated bearer token")

Your configured IncidentIQ fields should look like this:

```
[IncidentIQ]
Instance: cps.incidentiq.com
Token: fewig23823g98h(*Hg203g92gjaglakjewjg8ag9w38gfhy9g3pg8y29ghig101--t--_)(EF9uw890euf9HFslkhjglajg4h29q8ytogjlawjl23j28u290gu2903gjlzsojgagya9pw38gyu29830ogjijgapwe49g8yu2pu8gjawoigja8w3hg982ugpoajgoiaesjg982h39ga2h9
```

### Optional Parameters
The following are optional parameters, explained more in-depth.


**Schema** for Databases such as Microsoft SQL Server that do not treat Schema as a Database itself, Schema can be specified. A schema will *not* be created if it does not already exist.
Additionally, if you are using a database like MySQL that does use schema and database interchangeably, leave this blank and specifcy your database in the connection string.
In all other cases, if left blank, the default schema will be used.
Defaults to blank.

**StringLength**
sets the longest allowable string or string-like type (varchar or similar). Tables will be created with types of this length. Any strings longer which exist in a field will be truncated. Defaults to 512.

**[Tables]** set the name of any given table as it will be created in your database. Defaults to the given name.

**PageSize**
is the number of elements to request in each call to the API.
This can be tuned down for low memory machines (slower)
or up for servers which can handle the load (faster). Currently this
defaults to the IIQ maximum, 1000, a reasonable size on most machines.
***Do not set higher than 1000*** or unexpected results will occur. *As of July 2021 the request to retrieve Users cannot handle more than 1000 elements per page. Due to a lack of documentation, we do not know whether or not this is by design or if it will change in the future.*

**Threads**
specifies the maximum number of worker threads at a time.
Smaller will use less memory & peak CPU usage at a given time.
However, lowering this very negatively impacts performance
as the majority of execution time is spent waiting on the
IIQ API to return data. Allowing all threads to request data
at once is much faster. *Be aware that rate limits are not well defined for the IncidentIQ API, so turning this up to infinity may result in intermittent errors*.
Your database may also have a connection limit that is worth
considering, as each thread makes its own database connection.
If you are seeing the error "The specified network name is no longer available" this probably means there are too many threads running for the DB. Defaults to 30.

**Timeout**
sets the time in seconds each request to the IncidentIQ API is allowed
to wait before an error is thrown. Setting this higher may be nescessary
on slow machines, or slow network connections. Defaults to 100.


## Usage
---
Simply execute main.py
```bash
python3 main.py
```

The sync may take a few minutes to complete, depending on the size of your inventory. This is mostly due to the time the API takes to respond to large requests.
A slow connection to your database will also cause slower script execution.

## What can I sync?
---

1. By default these are synced
  * `Users`
  * `User Custom Fields`
  * `Assets`
  * `Asset Custom Fields`
  * `Locations`

2. *Planned options will be available by configuration in `config.ini`*
  * `Tickets`
  * `Ticket Custom Fields`
  * `Fines`
  * `Rooms`


## Contributing
---
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Run all contributions through [YAPF](https://github.com/google/yapf/) using the included style-config.ini 

```yapf --style style-config.ini -i [filename].py```

## License
---
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
