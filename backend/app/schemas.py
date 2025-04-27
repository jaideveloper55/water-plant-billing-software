from pydantic import BaseModel,EmailStr
from typing import Optional,List
from uuid import UUID
import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role:Optional[str] = "user"

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id:UUID
    is_active: bool
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode= True
        json_encoders={
             datetime.datetime: lambda dt: dt.isoformat(timespec='seconds').split('+')[0] if '+' in dt.isoformat(timespec='seconds') else dt.isoformat(timespec='seconds').split('-')[0]
        }


class DeleteResponse(BaseModel):
    detail: str

class UserListResponse(BaseModel):
    data: List[User]
    total: int
    limit: int
    page: int


class TokenRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token :str
    token_type: str
  

class PasswordResetRequest(BaseModel):
    email: EmailStr
    

class PasswordResetVerify(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

