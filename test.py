from datetime import date

from sqlalchemy.sql.sqltypes import DateTime
from asset import Asset
from base import Session, engine, Base

import user

# Generate database schema from SqlAlchemy
Base.metadata.create_all(engine)

# Create a session
session = Session()

# Create Assets for testing
users = user.get_users_page(0)

for u in users:
    session.add(u)


session.commit()
session.close()