import httpx
from fastapi import HTTPException
from .addresses import HOST_URL, USERS_SERVICE_PORT, QUESTIONS_SERVICE_PORT, SESSIONS_SERVICE_PORT, MATCHING_SERVICE_PORT
from .api_permissions import *

def _get_id_from_url(path):
    tokens = path.split("/")
    tokens = tokens[1:] # remove service name
    if len(tokens) < 1:
        return None
    return tokens[-1]

def map_path_microservice_url(path):
    service = None
    microservice_url = None
    if path.startswith("/users"):
        service = "users"
        microservice_url = f"{HOST_URL}:{USERS_SERVICE_PORT}"
    elif path.startswith("/questions"):
        service = "questions"
        microservice_url = f"{HOST_URL}:{QUESTIONS_SERVICE_PORT}"
    elif path.startswith("/sessions"):
        service = "sessions"
        microservice_url = f"{HOST_URL}:{SESSIONS_SERVICE_PORT}"

    return service, microservice_url

def _map_role_permission(role):
        if role == PUBLIC_PERMISSION:
            return "public"
        elif role == "user":
            return USER_PERMISSION
        elif role == "maintainer":
            return MAINTAINER_PERMISSION
        return -1

def _get_service_path(path):
    tokens = path.split("/")
    return tokens[1]

async def check_permission(session_id, path, method):
    service_path = _get_service_path(path)
    permission_required = PERMISSIONS_TABLE[service_path][method]

    if permission_required == PUBLIC_PERMISSION:
        return

    if session_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    headers = { 'session_id': session_id }
    url = f"{HOST_URL}/{SESSIONS_SERVICE_PORT}/sessions"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        session = response.json()
        _check_access_to_supplied_id(session, path, service_path)

        permission_level = _map_role_permission(session['role'])

        if permission_level < permission_required:
            raise HTTPException(status_code=401, detail="Unauthorized access")


def _check_access_to_supplied_id(session, path, service):
    if session['role'] == "maintainer":
        return

    # Normal users will pass these checks to call `users_all``. There are no supplied ids => vacuously true.
    # But their permissions will be checked by permissions table
    if service == "users":
        supplied_id = _get_id_from_url(path)
        session_user_id = session['user_id']
        if supplied_id != session_user_id:
            raise HTTPException(status_code=401, detail="Unauthorized access")

    elif service == "sessions":
        supplied_id = _get_id_from_url(path)
        if supplied_id != session['session_id']:
            raise HTTPException(status_code=401, detail="Unauthorized access")
