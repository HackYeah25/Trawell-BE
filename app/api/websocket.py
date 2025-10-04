"""
WebSocket endpoints for streaming responses
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/{conversation_id}/stream")
async def websocket_stream(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint for streaming AI responses

    Args:
        websocket: WebSocket connection
        conversation_id: Conversation ID
    """
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            # TODO: Implement streaming response logic
            # For now, echo back
            await websocket.send_text(f"Echo: {data}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for conversation {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()
