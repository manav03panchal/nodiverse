# app/websockets/connection_manager.py
from fastapi import WebSocket
from typing import Dict, Set
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.event_participants: Dict[str, Set[str]] = {}
        print("Connection Manager initialized")  # Debug line

    async def connect(self, websocket: WebSocket, user_id: str, event_id: str):
        try:
            await websocket.accept()
            print(f"Accepted connection for user {user_id}")  # Debug line

            self.active_connections[user_id] = websocket

            if event_id not in self.event_participants:
                self.event_participants[event_id] = set()
            self.event_participants[event_id].add(user_id)

            print(
                f"Current participants in {event_id}: {self.event_participants[event_id]}"
            )  # Debug line

            # Notify others
            await self.broadcast_to_event(
                event_id, {"type": "node_joined", "data": {"user_id": user_id}}
            )
        except Exception as e:
            print(f"Error in connect: {str(e)}")  # Debug line
            raise

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
