from datetime import date

from sqlalchemy.sql.sqltypes import DateTime
from asset import Asset
from base import Session, engine, Base

# Generate database schema from SqlAlchemy
Base.metadata.create_all(engine)

# Create a session
session = Session()

# Create Assets for testing
first = Asset('6ef611b2-f669-43c7-ae9b-e35a67b9f84b', '0112027449', date(2021,6,15))
second = Asset('45d6cb7d-49f6-4902-8533-587e6aa409db', '0234', date(1997,6,25))

session.add(first)
session.add(second)

session.commit()
session.close()