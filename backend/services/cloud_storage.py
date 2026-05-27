import os
import shutil
from typing import Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("cloud_storage")

class CloudStorageAdapter:
    """
    Manages secure uploads, temporary presigned URLs, and chunked video ingestion.
    Supports AWS S3 buckets and falls back cleanly to the local /uploads directory 
    when cloud environment variables are missing.
    """
    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or os.getenv("AWS_S3_BUCKET", "antigravity-forensics-media")
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.s3_client = None

        # Try to initialize boto3 client
        if self.aws_access_key and self.aws_secret_key:
            try:
                import boto3
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key
                )
                logger.info(f"AWS S3 Client successfully initialized for bucket: {self.bucket_name}")
            except ImportError:
                logger.warning("AWS SDK 'boto3' not available. Falling back to local offline storage.")
            except Exception as e:
                logger.error(f"S3 Connection configuration failed: {e}. Falling back to offline mode.")
        else:
            logger.info("AWS credentials not injected. Operating in localized offline-filesystem storage mode.")

    def upload_file(self, local_file_path: str, destination_filename: str) -> str:
        """
        Uploads a media file to active storage layer (AWS S3 or Local /uploads).
        
        Returns:
            URL/path representing the saved resource profile location.
        """
        if self.s3_client:
            try:
                logger.info(f"Initiating AWS S3 binary upload of: {local_file_path}")
                self.s3_client.upload_file(
                    local_file_path, 
                    self.bucket_name, 
                    destination_filename,
                    ExtraArgs={"ACL": "private"} # Enforce private authorization scopes
                )
                cloud_url = f"https://{self.bucket_name}.s3.amazonaws.com/{destination_filename}"
                logger.info(f"S3 upload finished successfully. URL: {cloud_url}")
                return cloud_url
            except Exception as e:
                logger.error(f"AWS S3 transaction failed: {e}. Falling back to copying locally.")

        # Fallback Local Filesystem Operations
        local_dest_dir = "uploads/cloud_fallback"
        os.makedirs(local_dest_dir, exist_ok=True)
        local_dest_path = os.path.join(local_dest_dir, destination_filename)
        
        try:
            shutil.copy2(local_file_path, local_dest_path)
            logger.info(f"Saved asset to local fallback file cache: {local_dest_path}")
            return f"/static/cloud_fallback/{destination_filename}"
        except Exception as err:
            logger.error(f"Local storage fallback copy failed: {err}")
            raise err

    def get_presigned_url(self, filename: str, expires_in_seconds: int = 3600) -> str:
        """
        Generates a secure temporary signed URL for protected media access.
        """
        if self.s3_client:
            try:
                url = self.s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": filename},
                    ExpiresIn=expires_in_seconds
                )
                return url
            except Exception as e:
                logger.error(f"Failed to generate AWS S3 presigned URL: {e}")

        # Fallback local URL referencing standard static mount points
        return f"/static/cloud_fallback/{filename}"
