from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)


class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)   # now integer FK-style
    todo = Column(String)