import sys
import os
import json
from typing import Optional
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ai_engine.inference.inference_engine import DeepfakeInferenceEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python predict.py <path_to_image>")
        sys.exit(1)
        
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"Error: Target image file missing: {image_path}")
        sys.exit(1)
        
    try:
        engine = DeepfakeInferenceEngine()
        result = engine.predict_image(image_path)
        print(json.dumps(result, indent=4))
        
    except Exception as e:
        print(f"Error running inference engine: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
