from fastapi import WebSocket
from typing import List, Set
from ai_engine.utils.logger import setup_logger

logger = setup_logger("websocket_manager")

class ConnectionManager:
    """
    Manages active WebSocket connections, broadcasting messages, 
    and handling disconnects in real-time streaming networks.
    """
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accepts inbound connection, keeping the socket active.
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection established. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Safely removes connection on socket close event.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Active remaining: {len(self.active_connections)}")

    async def send_json_message(self, message: dict, websocket: WebSocket) -> None:
        """
        Sends private JSON message to specific connection.
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to transmit socket payload: {e}. Removing connection.")
            self.disconnect(websocket)

    async def broadcast_json_message(self, message: dict) -> None:
        """
        Broadcasts public JSON message to all active WebSocket listeners.
        """
        logger.debug(f"Broadcasting payload to {len(self.active_connections)} sockets.")
        
        # Make a copy to prevent modification errors during loops
        sockets = list(self.active_connections)
        for websocket in sockets:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to broadcast to socket: {e}. Removing connection.")
                self.disconnect(websocket)
