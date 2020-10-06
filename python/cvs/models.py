from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String, Integer, Boolean
from sqlalchemy import func

Base = declarative_base()


class Session(Base):
    """ Video session
    """
    __tablename__ = 'session'
    id = Column(String, primary_key=True)
    room_num = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    display_name = Column(String)
    allow_anonymous = Column(Boolean, default=True)
