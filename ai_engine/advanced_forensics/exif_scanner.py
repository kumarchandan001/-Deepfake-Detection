import os
from PIL import Image
from PIL.ExifTags import TAGS
from typing import Dict, Any, Tuple
from ai_engine.utils.logger import setup_logger

logger = setup_logger("exif_scanner")

class EXIFForensicScanner:
    """
    Scans image files for digital metadata tampering, camera specifications, 
    and commercial editing software signatures (GIMP, Photoshop, Canva, etc.).
    """
    # Suspicious editing tool string tags to flag
    EDITING_SIGNATURES = [
        "adobe", "photoshop", "lightroom", "gimp", "canva", 
        "pixelmator", "snapseed", "picsart", "corel", "affinity"
    ]

    @staticmethod
    def scan_image_metadata(image_path: str) -> Dict[str, Any]:
        """
        Parses EXIF tags and analyzes creation history signatures.
        
        Returns:
            Forensic analysis dictionary containing parsed tags and risk verdicts.
        """
        logger.info(f"Initiating EXIF forensic scan on asset: {image_path}")
        
        report = {
            "success": False,
            "has_exif": False,
            "camera_make": None,
            "camera_model": None,
            "editing_software": None,
            "is_manipulated_metadata": False,
            "extracted_tags": {},
            "risk_verdict": "LOW_RISK"
        }

        if not os.path.exists(image_path):
            logger.error(f"Image asset missing during metadata scanner execution: {image_path}")
            return report

        try:
            with Image.open(image_path) as img:
                report["success"] = True
                
                # Check for basic format tags
                report["extracted_tags"]["format"] = img.format
                report["extracted_tags"]["dimensions"] = f"{img.width}x{img.height}"
                
                # Extract EXIF metadata dictionary
                exif_data = img.getexif()
                if not exif_data:
                    # Clean/stripped metadata is common in social media or compiled deepfakes
                    logger.warning("No EXIF metadata found. Standard stripped signature.")
                    report["risk_verdict"] = "SUSPICIOUS_STRIPPED"
                    return report

                report["has_exif"] = True
                parsed_exif = {}
                
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, f"Tag_{tag_id}")
                    # Ensure values are JSON-serializable strings
                    if isinstance(value, bytes):
                        try:
                            value = value.decode("utf-8", errors="replace")
                        except Exception:
                            value = str(value)
                    parsed_exif[tag_name] = str(value)

                report["extracted_tags"].update(parsed_exif)

                # Analyze specific fields: Software, Camera details
                software = parsed_exif.get("Software", "").lower()
                make = parsed_exif.get("Make")
                model = parsed_exif.get("Model")

                if make:
                    report["camera_make"] = make
                if model:
                    report["camera_model"] = model

                # Scan for commercial graphic software footprints
                for sig in EXIFForensicScanner.EDITING_SIGNATURES:
                    if sig in software:
                        report["editing_software"] = parsed_exif.get("Software")
                        report["is_manipulated_metadata"] = True
                        report["risk_verdict"] = "HIGH_RISK_MANIPULATED"
                        logger.warning(f"Metadata tampering footprint detected: {parsed_exif.get('Software')}")
                        break

            return report

        except Exception as e:
            logger.error(f"Metadata scanner execution failure: {e}")
            report["error"] = str(e)
            return report
