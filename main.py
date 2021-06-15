from asset import Asset
from user import User
from sqlalchemy.sql.sqltypes import DateTime
import config



if __name__ == '__main__':
    
    print('Creating IIQ Tables...')
    # Generate database schema from SqlAlchemy
    Base.metadata.create_all(engine)

    print('Complete\nInitializing a database session...')
    # Create a session
    session = Session()

    
