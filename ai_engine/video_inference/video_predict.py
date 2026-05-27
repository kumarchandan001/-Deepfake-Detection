import sys
import os
import json
# Insert path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ai_engine.video_inference.video_inference_engine import DeepfakeVideoInferenceEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python video_predict.py <path_to_video>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    if not os.path.exists(video_path):
        print(f"Error: Target video file missing: {video_path}")
        sys.exit(1)
        
    try:
        # Initialize video evaluation engine
        engine = DeepfakeVideoInferenceEngine()
        result = engine.analyze_video(video_path)
        
        # Display output in formatted JSON
        print(json.dumps(result, indent=4))
        
    except Exception as e:
        print(f"Error running video inference engine: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
