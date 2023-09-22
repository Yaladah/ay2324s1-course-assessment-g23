import httpx
from fastapi import HTTPException, Request
from .addresses import HOST_URL, USERS_SERVICE_PORT
from .api_permissions import *

async def check_permission(request: Request, permission_required):
    def map_role_permission(role):
        if role == "user":
            return USER_PERMISSION
        elif role == "maintainer":
            return MAINTAINER_PERMISSION
        return -1

    if permission_required == PUBLIC_PERMISSION:
        return

    session_id = request.cookies.get('session_id')

    headers = { session_id: session_id }
    url = f"{HOST_URL}/{USERS_SERVICE_PORT}/sessions"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        permission_level = map_role_permission(response.json()["role"])

        if permission_level < permission_required:
            raise HTTPException(status_code=401, detail="Unauthorized access")