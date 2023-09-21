import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .utils import requestModels as rm
from .controllers import users_controller as uc, sessions_controller as sc

# create app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/users", status_code=200)
async def create_user(r: rm.CreateUser):
    user_id = str(uuid.uuid4())
    return uc.create_user(user_id, r.username, r.email, r.password)

@app.get("/users/{user_id}", status_code=200)
async def get_user(user_id: str, r: rm.GetUser):
    return uc.get_user(user_id, r.session_id)

@app.delete("/users/{user_id}", status_code=200)
async def delete_user(user_id: str, r: rm.DeleteUser):
    return uc.delete_user(user_id, r.session_id)

@app.put("/users", status_code=200)
async def update_user_info(r: rm.UpdateUserInfo):
    return uc.update_user_info(r.user_id, r.username, r.password, r.email, r.role, r.session_id)

# @app.put("/users/{user_id}", status_code=200)
# async def update_user_role(user_id: str, r: rm.UpdateUserRole):
#     return uc.update_user_role(user_id, r.role, r.session_id)

@app.post("/sessions",  status_code=200)
async def user_login(r: rm.UserLogin):
    return sc.user_login(r.username, r.password)

@app.get("/sessions/{session_id}",  status_code=200)
async def get_session(session_id: str):
    return sc.get_session(session_id)

@app.delete("/sessions/{session_id}",  status_code=200)
async def user_logout(session_id: str):
    return sc.user_logout(session_id)