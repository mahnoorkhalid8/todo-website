from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Handle EmailStr import gracefully in case email-validator is not available
try:
    from pydantic import EmailStr
except ImportError:
    # Fallback to regular string if email-validator is not installed
    from pydantic import Field
    EmailStr = str


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None


class UserInDB(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserResponse] = None


class TokenData(BaseModel):
    user_id: str
    email: str

# from pydantic import BaseModel, EmailStr
# from typing import Optional
# from datetime import datetime


# class UserBase(BaseModel):
#     email: EmailStr
#     name: str  # Made name required


# class UserCreate(UserBase):
#     password: str


# class UserUpdate(BaseModel):
#     name: Optional[str] = None


# class UserInDB(UserBase):
#     id: str
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True


# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str


# class UserResponse(BaseModel):
#     id: str
#     email: str
#     name: Optional[str] = None

#     class Config:
#         from_attributes = True


# class Token(BaseModel):
#     access_token: str
#     token_type: str
#     user: Optional[UserResponse] = None


# class TokenData(BaseModel):
#     user_id: str
#     email: str