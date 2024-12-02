from typing import Optional
from enum import Enum
from datetime import datetime


from pydantic import BaseModel


class TaskState(Enum):
    not_exsists = 'not_exsists'
    creating = 'creating'
    scheduled = 'scheduled'
    accepted = 'accepted'
    in_work = 'in_work'
    awaits_user_review = 'awaits_user_review'
    finished = 'finished'
    canceled = 'canceled'
    suspended = 'suspended'


class TaskInDB(BaseModel):
    id: int
    title: str
    description: str
    user_id: int
    state: TaskState
    created_at: datetime


class TaskCreate(BaseModel):
    title: str
    description: str
    state: TaskState


class TaskUpdate(BaseModel):
    title: str
    description: str
    state: TaskState


class TaskPrototype(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    state: TaskState
