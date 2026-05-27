import sys
import os
import json
# Setup path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ai_engine.audio_inference.realtime_audio_engine import RealtimeAudioInferenceEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python audio_predict.py <path_to_audio_file>")
        sys.exit(1)
        
    audio_path = sys.argv[1]
    if not os.path.exists(audio_path):
        print(f"Error: Target audio file missing: {audio_path}")
        sys.exit(1)
        
    try:
        engine = RealtimeAudioInferenceEngine()
        result = engine.predict_audio_file(audio_path)
        print(json.dumps(result, indent=4))
        
    except Exception as e:
        print(f"Error running audio inference engine: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
