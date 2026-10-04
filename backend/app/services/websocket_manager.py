import json
import logging
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # exam_id -> set of active WebSockets
        self.active_rooms: Dict[int, Set[WebSocket]] = {}

    async def connect(self, exam_id: int, websocket: WebSocket):
        await websocket.accept()
        if exam_id not in self.active_rooms:
            self.active_rooms[exam_id] = set()
        self.active_rooms[exam_id].add(websocket)
        logger.info(f"WebSocket client connected to exam {exam_id}. Total: {len(self.active_rooms[exam_id])}")

    def disconnect(self, exam_id: int, websocket: WebSocket):
        if exam_id in self.active_rooms:
            self.active_rooms[exam_id].discard(websocket)
            if not self.active_rooms[exam_id]:
                del self.active_rooms[exam_id]
        logger.info(f"WebSocket client disconnected from exam {exam_id}")

    async def broadcast_to_exam(self, exam_id: int, event_type: str, data: dict):
        if exam_id not in self.active_rooms:
            return

        payload = {
            "eventType": event_type,
            "data": data,
        }
        message_str = json.dumps(payload, default=str)
        dead_connections = set()

        for connection in self.active_rooms[exam_id]:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.warning(f"Failed to send to websocket: {e}")
                dead_connections.add(connection)

        for dead in dead_connections:
            self.disconnect(exam_id, dead)


ws_manager = ConnectionManager()
