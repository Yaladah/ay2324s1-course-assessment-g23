from typing import cast
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import JSONResponse
import httpx
import json
from fastapi.middleware.cors import CORSMiddleware
from api_models.error import ServiceError
from api_models.users import UserLoginResponse, UserLogoutResponse
from utils.api_permissions import Method
import websockets
from utils.api_gateway_util import check_permission, map_path_microservice_url, connect_matching_service_websocket, attach_cookie, delete_cookie
from utils.addresses import MATCHING_SERVICE_HOST

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        # Receive message from client
        message = await websocket.receive_text()
        request =  json.loads(message)
        service = request["service"]

        # Send message to microservice
        if service == "matching-service":
            # await connect_matching_service_websocket(websocket, message)
            websocket_url = "ws://" + MATCHING_SERVICE_HOST + ":8003/ws/matching"
            async with websockets.connect(websocket_url) as matching_service_websocket:
                await matching_service_websocket.send(message)
                response = await matching_service_websocket.recv()
                await websocket.send_text(response)
                websocket.close()
        else:
            raise HTTPException(status_code=400, detail=f"Invalid service requested: {service}")

    except HTTPException as http_exc:
        await websocket.send_text(http_exc.detail)

async def route_request(method: Method, path: str, request: Request):
    # Determine the microservice URL based on the path
    service, microservice_url = map_path_microservice_url(path)

    if not service:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    cookies = request.cookies
    session_id = cookies.get('session_id')

    # await check_permission(session_id, path, method)

    data = await request.body()

    # Forward the request to the microservice
    async with httpx.AsyncClient() as client:
        if method == "GET":
            if service == "sessions":
                path += f"/{session_id}"
            response = await client.get(f"{microservice_url}{path}")
        elif method == "POST":
            response = await client.post(f"{microservice_url}{path}", data=data)
        elif method == "PUT":
            response = await client.put(f"{microservice_url}{path}", data=data)
        elif method == "DELETE":
             if service == "sessions":
                path += f"/{session_id}"
             response = await client.delete(f"{microservice_url}{path}")

        return response

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def handle_request(request: Request) -> JSONResponse:
    print(request.cookies)
    path = request.url.path
    method = cast(Method, request.method)
    response = await route_request(method, path, request)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

    res_json: dict = response.json()
    if ServiceError.is_service_error(res_json):
        service_error = ServiceError(**res_json)
        raise HTTPException(status_code=service_error.status_code, detail=service_error.message)
    if path == "/sessions" and method == "POST":
        res = UserLoginResponse(**res_json)
        return attach_cookie(res)
    if path == "/sessions" and method == "DELETE":
        res = UserLogoutResponse(**res_json)
        return delete_cookie(res)

    return JSONResponse(content=res_json)

