import sys
import os
import csv
import time
from tqdm import tqdm
from typing import Optional
# Setup path mapping
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ai_engine.inference.inference_engine import DeepfakeInferenceEngine
from ai_engine.utils.logger import setup_logger

logger = setup_logger("batch_predict")

def run_batch_inference(input_dir: str, output_csv: str) -> None:
    """
    Scans a folder recursively for images, runs model evaluations,
    and writes results to a summary ledger.
    """
    if not os.path.exists(input_dir):
        logger.error(f"Target input folder does not exist: {input_dir}")
        sys.exit(1)
        
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    logger.info("Initializing DeepfakeInferenceEngine for batch evaluation...")
    engine = DeepfakeInferenceEngine()
    
    # catalog files
    image_paths = []
    for root, _, files in os.walk(input_dir):
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                image_paths.append(os.path.join(root, f))
                
    logger.info(f"Located {len(image_paths)} valid images to analyze.")
    
    # Ingress CSV creation
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["filename", "prediction", "confidence", "raw_score", "processing_time"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for path in tqdm(image_paths, desc="Batch Analysis Progress"):
            try:
                res = engine.predict_image(path)
                if res.get("success", False):
                    writer.writerow({
                        "filename": os.path.relpath(path, input_dir),
                        "prediction": res["prediction"],
                        "confidence": res["confidence"],
                        "raw_score": res["raw_score"],
                        "processing_time": res["processing_time"]
                    })
                else:
                    logger.warning(f"Failed to analyze file: {path}. Error: {res.get('error')}")
            except Exception as e:
                logger.error(f"An unexpected error occurred processing {path}: {e}")

    logger.info(f"[SUCCESS] Batch analysis completed. Forensic records compiled at: {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python batch_predict.py <input_directory> <output_csv_path>")
        sys.exit(1)
        
    run_batch_inference(sys.argv[1], sys.argv[2])
