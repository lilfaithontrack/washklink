from sqlalchemy import Column, Integer, String, Text, Float, DateTime, SmallInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "tbl_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    ccode = Column(Text, nullable=False)
    mobile = Column(Text, nullable=False)
    refercode = Column(Integer, nullable=False)
    parentcode = Column(Integer, nullable=True)
    password = Column(Text, nullable=False)
    registartion_date = Column(DateTime, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    wallet = Column(Float, nullable=False, default=0)
    status_login = Column(SmallInteger, nullable=False)