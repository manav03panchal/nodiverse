from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from ..database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    role = Column(String)  # participant/mentor/organizer
    profile = Column(JSON)  # flexible data like github, linkedin, etc
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(String)  # active/ended
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EventParticipant(Base):
    __tablename__ = "event_participants"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    event_id = Column(String, ForeignKey("events.id"))
    role = Column(String)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())


class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True)
    user_id_1 = Column(String, ForeignKey("users.id"))
    user_id_2 = Column(String, ForeignKey("users.id"))
    event_id = Column(String, ForeignKey("events.id"))
    status = Column(String)  # pending/accepted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
