from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import cv2
import numpy as np
import json
import time
from backend.websocket.websocket_manager import ConnectionManager
from ai_engine.realtime.stream_processor import RealtimeStreamProcessor
from ai_engine.utils.logger import setup_logger

logger = setup_logger("realtime_routes")
router = APIRouter(prefix="/api/v1/forensics/realtime", tags=["Realtime WebSocket Streamer"])

# Singleton connection manager instance
manager = ConnectionManager()

# Preloaded processor instance (decoupled for route dependencies)
def get_stream_processor() -> RealtimeStreamProcessor:
    return RealtimeStreamProcessor()

@router.websocket("/stream")
async def websocket_realtime_stream(
    websocket: WebSocket,
    processor: RealtimeStreamProcessor = Depends(get_stream_processor)
) -> None:
    """
    Asynchronously streams live webcam frames (binary payloads) from client,
    executes real-time predictions, and streams json scores back.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # 1. Ingest binary frame payload
            data = await websocket.receive_bytes()
            start_time = time.time()
            
            # 2. Decode raw byte stream into image matrix
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                await manager.send_json_message(
                    {"success": False, "error": "Invalid frame payload bytes."}, 
                    websocket
                )
                continue
                
            # 3. Process frame and run model inference
            annotated_frame, metadata = processor.process_frame(frame)
            
            # 4. Optional: Encode annotated frame to bytes for browser canvas display
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                logger.error("Failed to encode annotated output frame.")
                continue
                
            # 5. Format and stream results back
            processing_time = time.time() - start_time
            await manager.send_json_message({
                "success": True,
                "prediction": metadata["prediction"],
                "confidence": metadata["confidence"],
                "raw_score": metadata["raw_score"],
                "face_detected": metadata["face_detected"],
                "processing_time": round(processing_time, 4)
            }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client closed realtime WebSocket channel.")
    except Exception as e:
        logger.error(f"WebSocket execution runtime failure: {e}")
        manager.disconnect(websocket)
