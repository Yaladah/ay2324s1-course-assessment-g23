from fastapi import FastAPI, HTTPException, Request, WebSocket
import httpx

from .utils.api_permissions import PERMISSIONS_TABLE, PUBLIC_PERMISSION, USER_PERMISSION, MAINTAINER_PERMISSION
from .utils.addresses import HOST_URL, USERS_API_PORT, QUESTIONS_API_PORT, SESSIONS_API_PORT
from .utils.api_gateway_util import check_permission

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Receive message from client
        message = await websocket.receive_text()

        # Process message from client
        # ...

        # Send message to microservice
        # ...

        # Receive response from microservice
        response = "Response from microservice"

        # Send response back to client
        await websocket.send_text(response)

async def route_request(method: str, path: str, request: Request):
    # Determine the microservice URL based on the path
    service = None
    if path.startswith("/users"):
        service = "users"
        microservice_url = f"{HOST_URL}:{USERS_API_PORT}"
    elif path.startswith("/questions"):
        service = "questions"
        microservice_url = f"{HOST_URL}:{QUESTIONS_API_PORT}"
    elif path.startswith("/sessions"):
        service = "sessions"
        microservice_url = f"{HOST_URL}:{USERS_API_PORT}"
    else:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    permission_required = PERMISSIONS_TABLE[service][method]
    check_permission(request, permission_required)

    # Forward the request to the microservice
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(f"{microservice_url}{path}")
        elif method == "POST":
            response = await client.post(f"{microservice_url}{path}", data=await request.body())
        elif method == "PUT":
            response = await client.post(f"{microservice_url}{path}", data=await request.body())
        elif method == "DELETE":
             response = await client.delete(f"{microservice_url}{path}", data=await request.body())

        response.raise_for_status()
        return response.text

@app.route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def handle_request(path: str, request: Request):
    method = request.method
    return await route_request(method, path, request)