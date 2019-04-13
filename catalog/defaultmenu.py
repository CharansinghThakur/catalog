from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Guitars, User

engine = create_engine('sqlite:///guitardb.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(
    id=1, name='Charan Singh', email='chandrapalsaicharansingh@gmail.com',
    picture='https://lh6.googleusercontent.com/-vlmLp3JE3_E/'
    'AAAAAAAAAAI/AAAAAAAABIU/KrHZbHAHZsE/photo.jpg')
session.add(User1)
session.commit()

guitar1 = Guitars(
    user_id=1, guitar_name="Yamaha FS300", guitar_type="Acoustic", price=10000)

session.add(guitar1)
session.commit()

guitar2 = Guitars(
    user_id=1, guitar_name="Yamaha F100", guitar_type="Acoustic", price=12000)

session.add(guitar2)
session.commit()


print "added items!"
