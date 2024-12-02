from enum import IntEnum
from typing import Optional


from pydantic import BaseModel


class UserInDB(BaseModel):
    telegram_id: int
    username: str
    login: str


class UserCreate(BaseModel):
    username: str
    login: str


class UserUpdate(BaseModel):
    username: str
    login: str


class UserPrototypeState(IntEnum):
    not_exsists = 1
    creating = 2
    created = 3


class UserPrototype(BaseModel):
    username: Optional[str] = None
    login: Optional[str] = None
    state: UserPrototypeState
