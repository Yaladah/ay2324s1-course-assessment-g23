import asyncio
from typing import Any, cast
from fastapi import Cookie, FastAPI, HTTPException, Request, WebSocket
import fastapi
from fastapi.responses import JSONResponse
from fastapi.websockets import WebSocketState
from websockets.protocol import State
import httpx
import json
from fastapi.middleware.cors import CORSMiddleware
from api_models.error import ServiceError
from api_models.users import UserLoginResponse
from utils.api_permissions import Method
import websockets.client
from utils.api_gateway_util import has_permission, map_path_microservice_url, connect_matching_service_websocket
from utils.addresses import MATCHING_SERVICE_HOST
import websockets.exceptions
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure logging to write to stdout
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


async def forward_communication(ws_a: WebSocket, ws_b: websockets.client.WebSocketClientProtocol):
    """Handles communication from frontend -> microservice."""
    while True:
        data = await ws_a.receive_text()
        await ws_b.send(data)


async def reverse_communication(ws_a: WebSocket, ws_b: websockets.client.WebSocketClientProtocol):
    """Handles communication from microservice -> frontend."""
    while True:
        data = await ws_b.recv()
        assert isinstance(data, str)
        await ws_a.send_text(data)


@app.websocket("/ws")
async def websocket_endpoint(ws_a: WebSocket):
    matching_api_url = f"ws://{MATCHING_SERVICE_HOST}:8003/ws/matching"
    await ws_a.accept()
    async with websockets.client.connect(matching_api_url) as ws_b_client:
        try:
            while True:
                fwd_task = asyncio.create_task(
                    forward_communication(ws_a, ws_b_client))
                rev_task = asyncio.create_task(
                    reverse_communication(ws_a, ws_b_client))
                await asyncio.gather(fwd_task, rev_task)

        # Ignore any "connection closed" errors. They're expected because any
        # of the websockets methods might fail when the websocket closes.
        except fastapi.websockets.WebSocketDisconnect:
            pass
        except websockets.exceptions.ConnectionClosedOK:
            pass

        finally:
            # If any websockets aren't closed, close them.
            # `ws_a` and `ws_b_client` are from different packages, so they use
            # different websocket-states.
            if ws_a.client_state != WebSocketState.DISCONNECTED:  # FastAPI's websocket.
                await ws_a.close()
            if ws_b_client.state != State.CLOSED:  # websockets's websocket
                await ws_b_client.close()


async def route_request(
    method: Method,
    path: str,
    service: str,
    microservice_url: str,
    session_id: str | None,
    data: Any
) -> httpx.Response:
    # Forward the request to the microservice
    async with httpx.AsyncClient() as client:
        match method:
            case "GET":
                if service == "sessions":
                    path += f"/{session_id}"
                return await client.get(f"{microservice_url}{path}")
            case "POST":
                return await client.post(f"{microservice_url}{path}", data=data)
            case "PUT":
                return await client.put(f"{microservice_url}{path}", data=data)
            case "DELETE":
                if service == "sessions":
                    path += f"/{session_id}"
                return await client.delete(f"{microservice_url}{path}")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def handle_request(request: Request, session_id: str | None = Cookie(None)) -> JSONResponse:
    path = request.url.path
    method = cast(Method, request.method)

    # Determine the microservice URL based on the path
    service, microservice_url = map_path_microservice_url(path)
    if service is None:
        return JSONResponse(status_code=404, content="Endpoint not found")

    if not await has_permission(session_id, path, method):
        return JSONResponse(status_code=401, content="Unauthorized access")

    data = await request.body()
    res = await route_request(method, path, service, microservice_url, session_id, data)

    if res.status_code != 200:
        return JSONResponse(status_code=res.status_code, content=res.content)

    res_json: dict = res.json()
    output = JSONResponse(content=res_json)
    if ServiceError.is_service_error(res_json):
        service_error = ServiceError(**res_json)
        raise HTTPException(
            status_code=service_error.status_code, detail=service_error.message)

    if path == "/sessions" and method == "POST":
        login_json = UserLoginResponse(**res_json)
        output.set_cookie(key='session_id', value=login_json.session_id)
    elif path == "/sessions" and method == "DELETE":
        output.delete_cookie('session_id')

    return output
