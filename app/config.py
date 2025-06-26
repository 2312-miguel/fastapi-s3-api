import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "")
    
    # API Configuration
    API_TITLE: str = "FastAPI S3 API"
    API_DESCRIPTION: str = "A lightweight file upload and download API"
    API_VERSION: str = "1.0.0"
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
    ALLOWED_EXTENSIONS: list = os.getenv("ALLOWED_EXTENSIONS", "txt,pdf,jpg,jpeg,png,gif").split(",")
    
    # Presigned URL Configuration
    PRESIGNED_URL_EXPIRATION: int = int(os.getenv("PRESIGNED_URL_EXPIRATION", "3600"))  # 1 hour default
    
    @classmethod
    def validate_aws_config(cls) -> bool:
        """Validate that all required AWS configuration is present."""
        required_fields = [
            cls.AWS_ACCESS_KEY_ID,
            cls.AWS_SECRET_ACCESS_KEY,
            cls.AWS_S3_BUCKET
        ]
        return all(field for field in required_fields)
    
    @classmethod
    def get_missing_config_fields(cls) -> list:
        """Get list of missing configuration fields."""
        missing = []
        if not cls.AWS_ACCESS_KEY_ID:
            missing.append("AWS_ACCESS_KEY_ID")
        if not cls.AWS_SECRET_ACCESS_KEY:
            missing.append("AWS_SECRET_ACCESS_KEY")
        if not cls.AWS_S3_BUCKET:
            missing.append("AWS_S3_BUCKET")
        return missing

# Global settings instance
settings = Settings() 