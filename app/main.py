from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.websockets.connection_manager import ConnectionManager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .database.database import get_db
from .models import models
from .schemas import schemas
import uuid

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
    connected = await manager.connect(websocket, user_id, event_id)
    if not connected:
        await websocket.close(code=4004)
        return

    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast_to_event(
                event_id,
                {"type": data.get("type"), "data": data.get("data"), "sender": user_id},
            )
    except WebSocketDisconnect:
        await manager.disconnect(user_id, event_id)


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(
        id=str(uuid.uuid4()),
        name=user.name,
        email=user.email,
        role=user.role,
        profile=user.profile,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/events/", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    db_event = models.Event(
        id=str(uuid.uuid4()),
        name=event.name,
        start_date=event.start_date,
        end_date=event.end_date,
        status=event.status,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.get("/users/", response_model=list[schemas.User])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.get("/events/", response_model=list[schemas.Event])
def get_events(db: Session = Depends(get_db)):
    events = db.query(models.Event).all()
    return events


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user


@app.post("/events/{event_id}/participants", response_model=schemas.EventParticipant)
async def add_participant(
    event_id: str,
    participant: schemas.EventParticipantCreate,
    db: Session = Depends(get_db),
):
    db_participant = models.EventParticipant(**participant.dict())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)

    # Fetch the user details to send in the WebSocket broadcast
    user = db.query(models.User).filter(models.User.id == participant.user_id).first()

    if user:
        # Notify all WebSocket clients about the new participant
        await manager.broadcast_to_event(
            event_id,
            {
                "type": "new_user",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role,
                    "profile": user.profile,
                },
            },
        )

    return db_participant


@app.get("/test")
async def test_page():
    return FileResponse("static/test_client.html")
