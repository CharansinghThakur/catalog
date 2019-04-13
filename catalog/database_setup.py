from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Guitars(Base):
    __tablename__ = 'guitars'
    user_id = Column(Integer, ForeignKey('user.id'))
    guitar_name = Column(String(30), nullable=False)
    guitar_type = Column(String(30), nullable=False)
    price = Column(Integer, nullable=False)
    guitar_id = Column(Integer, primary_key=True)

    @property
    def serialize(self):
        return {

            'guitarName': self.guitar_name,
            'guitarPrice': self.price,
            'guitarId': self.guitar_id,
            }
    


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250))
    picture = Column(String(250))

engine = create_engine('sqlite:///guitardb.db')

Base.metadata.create_all(engine)
