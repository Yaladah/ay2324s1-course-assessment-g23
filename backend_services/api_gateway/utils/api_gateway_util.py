import httpx
from fastapi import HTTPException, WebSocket
from fastapi.responses import JSONResponse
from .addresses import API_PORT, USERS_SERVICE_HOST, QUESTIONS_SERVICE_HOST, SESSIONS_SERVICE_HOST, MATCHING_SERVICE_HOST
from .api_permissions import *
import websockets
import json

async def connect_matching_service_websocket(websocket: WebSocket, message):
    # websocket_url = "ws://{MATCHING_SERVICE_HOST}/{API_PORT}/ws/matching"
    websocket_url = "ws://localhost:8003/ws/matching"
    async with websockets.connect(websocket_url) as matching_service_websocket:
                await matching_service_websocket.send(message)
                response = await matching_service_websocket.receive_text()
                await websocket.send_text(response)
                websocket.close()

def _get_id_from_url(path):
    tokens = path.split("/")
    tokens = tokens[1:] # remove service name
    if len(tokens) < 1:
        return None
    return tokens[-1]

def map_path_microservice_url(path):
    service = None
    microservice_url = "http://"
    if path.startswith("/users"):
        service = "users"
        microservice_url += f"{USERS_SERVICE_HOST}:{API_PORT}"
    elif path.startswith("/questions"):
        service = "questions"
        microservice_url += f"{QUESTIONS_SERVICE_HOST}:{API_PORT}"
    elif path.startswith("/sessions"):
        service = "sessions"
        microservice_url += f"{SESSIONS_SERVICE_HOST}:{API_PORT}"

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
    print("Service path: ", service_path)
    permission_required = PERMISSIONS_TABLE[service_path][method]
    print("permission_required: ", permission_required)
    if permission_required == PUBLIC_PERMISSION:
        return
    print("Session id: ", session_id)
    if session_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    headers = { 'session_id': session_id }
    url = f"http://{SESSIONS_SERVICE_HOST}/{API_PORT}/sessions"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        session = response.json()
        if 'status_code' in session:
            raise HTTPException(status_code=session['status_code'], detail=session['message'])

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


def attach_cookie(response):
    session_id = response['session_id']
    message = response['message']
    response = JSONResponse(content=message)
    response.set_cookie(key='session_id', value=session_id)
    return response

def delete_cookie(response):
        message = response['message']
        response = JSONResponse(content=message)
        response.delete_cookie('session_id')
        return response