from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict


# User schemas
class UserBase(BaseModel):
    name: str
    email: str
    role: str
    profile: Dict


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Event schemas
class EventBase(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    status: str


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Event Participant schemas
class EventParticipantBase(BaseModel):
    event_id: str
    user_id: str
    role: str


class EventParticipantCreate(EventParticipantBase):
    pass


class EventParticipant(EventParticipantBase):
    id: int
    joined_at: datetime

    class Config:
        from_attributes = True


# Connection schemas
class ConnectionBase(BaseModel):
    user_id_1: str
    user_id_2: str
    event_id: str
    status: str


class ConnectionCreate(ConnectionBase):
    pass


class Connection(ConnectionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
