from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.websockets.connection_manager import ConnectionManager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Nodiverse")
manager = ConnectionManager()
app.mount("/static", StaticFiles(directory="static"), name="static")
# CORS setup for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/{event_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, event_id: str, user_id: str):
    print(f"Incoming WebSocket connection for user {user_id} in event {event_id}")
    try:
        await manager.connect(websocket, user_id, event_id)
        print(f"User {user_id} connected successfully")

        while True:
            data = await websocket.receive_json()
            print(f"Received message from {user_id}: {data}")
            await manager.broadcast_to_event(
                event_id,
                {"type": data.get("type"), "data": data.get("data"), "sender": user_id},
            )
    except WebSocketDisconnect:
        print(f"User {user_id} disconnected")
        await manager.disconnect(user_id, event_id)
    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
        await manager.disconnect(user_id, event_id)


@app.get("/test")
async def test_page():
    return FileResponse("static/test_client.html")
