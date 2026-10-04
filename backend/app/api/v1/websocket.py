from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import ws_manager

router = APIRouter(tags=["Real-time Telemetry"])


@router.websocket("/ws/exams/{exam_id}/monitor")
async def websocket_exam_monitor(websocket: WebSocket, exam_id: int):
    await ws_manager.connect(exam_id, websocket)
    try:
        while True:
            # Keep connection alive, listen for ping or client heartbeat
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(exam_id, websocket)
    except Exception:
        ws_manager.disconnect(exam_id, websocket)
