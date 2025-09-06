from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AccessFileBase(BaseModel):
    group_id: int
    path: str
    login: Optional[str]
    password: Optional[str]


class AccessFileCreate(AccessFileBase):
    pass


class AccessFileOut(AccessFileBase):
    id: int
    last_updated: datetime
    locked_until: Optional[datetime]

    class Config:
        from_attributes = True
