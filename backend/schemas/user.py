from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    tg_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    bonus_balance: int = 0
    xp: int = 0
    level_id: int = 1
    experience_id: Optional[int] = None
    platform_id: Optional[int] = None
    traffic_source_id: Optional[int] = None
    referrer_id: Optional[int] = None

class UserCreate(BaseModel):
    tg_id: int
    username: str | None = None
    full_name: str | None = None
    traffic_source_id: int | None = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    bonus_balance: Optional[int] = None
    xp: Optional[int] = None
    level_id: Optional[int] = None
    experience_id: Optional[int] = None
    platform_id: Optional[int] = None
    traffic_source_id: Optional[int] = None
    referrer_id: Optional[int] = None


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class ReferralBase(BaseModel):
    referrer_id: int
    referred_id: int
    activated: bool = False
    reward_given: bool = False


class ReferralCreate(ReferralBase):
    pass


class ReferralOut(ReferralBase):
    id: int

    class Config:
        from_attributes = True

class ProfileOut(BaseModel):
    user_id: int
    tg_id: int
    username: Optional[str]
    full_name: Optional[str]

    tariff_code: Optional[str]
    tariff_name: Optional[str]
    active_until: Optional[datetime]

    access_group: Optional[str]       
    access_file_path: Optional[str]  
    level_name: Optional[str] = None
    xp: int = 0
    bonus_balance: int = 0

    class Config:
        from_attributes = True