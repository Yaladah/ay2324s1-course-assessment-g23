from typing import Optional
from pydantic import BaseModel

class CreateUser(BaseModel):
    username: str
    password: str
    email: str

class UpdateUserInfo(BaseModel):
    user_id: str
    username: str
    password: str
    email: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class UpdateUserRole(BaseModel):
    role: str