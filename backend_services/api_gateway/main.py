from fastapi import FastAPI, HTTPException, Request, WebSocket
import httpx
import json
import websockets

from .utils.api_permissions import PERMISSIONS_TABLE
from .utils.addresses import HOST_URL, USERS_SERVICE_PORT, QUESTIONS_SERVICE_PORT, SESSIONS_SERVICE_PORT, MATCHING_SERVICE_PORT
from .utils.api_gateway_util import check_permission

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        # Receive message from client
        message = await websocket.receive_text()

        request =  json.loads(message)
        service = request["service"]

        websocket_url = f"{HOST_URL}"
        # Send message to microservice
        if service == "matching-service":
            websocket_url += f"/{MATCHING_SERVICE_PORT}"
            async with websockets.connect(websocket_url) as matching_service_websocket:
                await matching_service_websocket.send(json.dumps(request))
                response = await matching_service_websocket.recv()
                await websocket.send_text(response)
                websocket.close()
        else:
            raise HTTPException(status_code=400, detail=f"Invalid service requested: {service}")

    except HTTPException as http_exc:
        await websocket.send_text(http_exc.detail)

async def route_request(method: str, path: str, request: Request):
    # Determine the microservice URL based on the path
    service = None
    if path.startswith("/users"):
        service = "users"
        microservice_url = f"{HOST_URL}:{USERS_SERVICE_PORT}"
    elif path.startswith("/questions"):
        service = "questions"
        microservice_url = f"{HOST_URL}:{QUESTIONS_SERVICE_PORT}"
    elif path.startswith("/sessions"):
        service = "sessions"
        microservice_url = f"{HOST_URL}:{SESSIONS_SERVICE_PORT}"
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