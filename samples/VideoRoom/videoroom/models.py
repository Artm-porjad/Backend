from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String, Integer, Boolean
from sqlalchemy import ForeignKey, func

Base = declarative_base()


class User(Base):
    """ User account
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    display_name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    salt = Column(String, nullable=False)
    password = Column(String, nullable=False)
    expired_at = Column(DateTime)


class RegToken(Base):
    """ Registration confirm token
    """
    __tablename__ = 'reg_token'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, index=True, nullable=False)
    token = Column(String)
    confirmed_at = Column(DateTime)


class Session(Base):
    """ Video session
    """
    __tablename__ = 'session'
    id = Column(String, primary_key=True)
    room_num = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    display_name = Column(String)
    allow_anonymous = Column(Boolean, default=True)
