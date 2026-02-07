from sqlalchemy import column, Integer, String
from .database import Base

class User(Base):
    # __tablename__ is used to specify the name of the table in the database that corresponds to this model
    __tablename__="users"

    id=column(Integer,primary_key=True,index=True)
    name=column(String)
    email=column(String,unique=True,index=True)
    password=column(String)