from typing import Optional
from pydantic import BaseModel

class CreateUser(BaseModel):
    username: str
    password: str
    email: str

class GetUser(BaseModel):
    session_id: str

class UpdateUserInfo(BaseModel):
    user_id: str
    username: str
    password: str
    email: str
    role: str
    session_id: str

class DeleteUser(BaseModel):
    session_id: str

class UserLogin(BaseModel):
    username: str
    password: str