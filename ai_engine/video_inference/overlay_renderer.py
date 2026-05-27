import cv2
import os
from typing import List, Tuple, Dict, Any
from ai_engine.video_processing.video_loader import VideoLoader
from ai_engine.utils.logger import setup_logger

logger = setup_logger("overlay_renderer")

class ForensicVideoRenderer:
    """
    Renders forensic annotations (bounding boxes, classification tags, 
    confidence overlays) onto source video frames and compiles the final MP4.
    """
    def __init__(self, output_dir: str = "outputs/videos"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"ForensicVideoRenderer initialized. Output directory: {output_dir}")

    def render_annotated_video(self, source_path: str, output_name: str, frame_predictions: List[Dict[str, Any]]) -> str:
        """
        Ingests the original video, overlays frame-level predictions, and saves the output file.
        """
        output_filepath = os.path.join(self.output_dir, output_name)
        
        try:
            loader = VideoLoader(source_path)
            cap = loader.get_capture()
            
            fps = loader.metadata.get("fps", 30.0)
            width = loader.metadata.get("width", 1280)
            height = loader.metadata.get("height", 720)
            
            # Setup VideoWriter (using MP4V codec for high system compatibility)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_filepath, fourcc, fps, (width, height))
            
            logger.info(f"Beginning rendering loop for annotated video: {output_filepath}")
            
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # 1. Pull classification overlay values for this frame index
                pred_label = "PROCESSING..."
                pred_conf = ""
                box_color = (255, 0, 0) # Blue default
                
                if frame_idx < len(frame_predictions):
                    pred = frame_predictions[frame_idx]
                    pred_label = pred.get("prediction", "REAL")
                    pred_conf = f"{pred.get('confidence', 0.0):.2f}%"
                    
                    if pred_label == "FAKE":
                        box_color = (0, 0, 255) # Red for FAKE
                    else:
                        box_color = (0, 255, 0) # Green for REAL

                # 2. Draw HUD graphics overlay (Forensic dashboard banner)
                cv2.rectangle(frame, (10, 10), (350, 80), (0, 0, 0), -1) # Black banner background
                
                cv2.putText(
                    frame, 
                    f"FORENSIC ANALYTICS: {pred_label}", 
                    (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, 
                    box_color, 
                    2
                )
                cv2.putText(
                    frame, 
                    f"CONFIDENCE: {pred_conf}", 
                    (20, 65), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.5, 
                    (255, 255, 255), 
                    1
                )
                
                # Write annotated frame
                out.write(frame)
                frame_idx += 1

            cap.release()
            out.release()
            loader.close()
            
            logger.info(f"[SUCCESS] Compiled annotated video at: {output_filepath}")
            return output_filepath
            
        except Exception as e:
            logger.error(f"Failed to compile overlay annotated video: {e}")
            raise
