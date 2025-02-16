from fastapi import WebSocket
from typing import Dict, Set
from app.database.database import SessionLocal
from app.models import models


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.event_participants: Dict[str, Set[str]] = {}
        print("Connection Manager initialized")  # Debug line

    async def connect(self, websocket: WebSocket, user_id: str, event_id: str):
        db = SessionLocal()  # Initialize database session

        try:
            user = db.query(models.User).filter(models.User.id == user_id).first()
            event = db.query(models.Event).filter(models.Event.id == event_id).first()

            if not user or not event:
                print(
                    f"User or event not found: user={user is not None}, event={event is not None}"
                )
                return False

            await websocket.accept()
            self.active_connections[user_id] = websocket

            if event_id not in self.event_participants:
                self.event_participants[event_id] = set()
            self.event_participants[event_id].add(user_id)

            participants = (
                db.query(models.EventParticipant, models.User)
                .join(models.User, models.EventParticipant.user_id == models.User.id)
                .filter(models.EventParticipant.event_id == event_id)
                .all()
            )

            participant_list = [
                {
                    "id": participant.User.id,
                    "name": participant.User.name,  # ✅ Get the correct name
                    "role": participant.EventParticipant.role,
                    "profile": participant.User.profile,  # ✅ Get the correct profile
                }
                for participant in participants
            ]

            await websocket.send_json(
                {
                    "type": "initial_state",
                    "data": {
                        "event": {"id": event.id, "name": event.name, "type": "event"},
                        "participants": participant_list,  # ✅ Send correct data here
                        "connections": [
                            {
                                "source": conn.user_id_1,
                                "target": conn.user_id_2,
                                "status": conn.status,
                            }
                            for conn in db.query(models.Connection)
                            .filter(models.Connection.event_id == event_id)
                            .all()
                        ],
                    },
                }
            )

            return True
        except Exception as e:
            print(f"Error in connect: {str(e)}")
            raise
        finally:
            db.close()

    async def disconnect(self, user_id: str, event_id: str):
        try:
            if user_id in self.active_connections:
                del self.active_connections[user_id]

            if event_id in self.event_participants:
                self.event_participants[event_id].remove(user_id)
                print(f"User {user_id} removed from {event_id}")  # Debug line

                # Notify others about disconnect
                await self.broadcast_to_event(
                    event_id, {"type": "node_left", "data": {"user_id": user_id}}
                )
        except Exception as e:
            print(f"Error in disconnect: {str(e)}")  # Debug line

    async def broadcast_to_event(self, event_id: str, message: dict):
        try:
            if event_id in self.event_participants:
                print(f"Broadcasting to event {event_id}: {message}")  # Debug line
                for user_id in self.event_participants[event_id]:
                    if user_id in self.active_connections:
                        await self.active_connections[user_id].send_json(message)
                        print(f"Message sent to user {user_id}")  # Debug line
        except Exception as e:
            print(f"Error in broadcast: {str(e)}")  # Debug line
