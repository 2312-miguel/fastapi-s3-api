from fastapi import HTTPException
from typing import Optional

class S3Error(Exception):
    """Base exception for S3-related errors."""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class S3UploadError(S3Error):
    """Exception raised when file upload to S3 fails."""
    pass

class S3DownloadError(S3Error):
    """Exception raised when file download from S3 fails."""
    pass

class S3ListError(S3Error):
    """Exception raised when listing files from S3 fails."""
    pass

class S3PresignedUrlError(S3Error):
    """Exception raised when generating presigned URL fails."""
    pass

class ConfigurationError(Exception):
    """Exception raised when configuration is invalid or missing."""
    pass

class FileValidationError(Exception):
    """Exception raised when file validation fails."""
    pass

def handle_s3_error(error: Exception, operation: str) -> HTTPException:
    """Convert S3 errors to appropriate HTTP exceptions."""
    error_message = str(error)
    
    if "NoSuchBucket" in error_message:
        return HTTPException(
            status_code=500,
            detail=f"S3 bucket not found. Please check your configuration."
        )
    elif "AccessDenied" in error_message:
        return HTTPException(
            status_code=403,
            detail=f"Access denied to S3. Please check your AWS credentials."
        )
    elif "NoSuchKey" in error_message:
        return HTTPException(
            status_code=404,
            detail=f"File not found in S3 bucket."
        )
    elif "InvalidAccessKeyId" in error_message:
        return HTTPException(
            status_code=500,
            detail=f"Invalid AWS access key. Please check your configuration."
        )
    elif "SignatureDoesNotMatch" in error_message:
        return HTTPException(
            status_code=500,
            detail=f"Invalid AWS secret key. Please check your configuration."
        )
    else:
        return HTTPException(
            status_code=500,
            detail=f"S3 {operation} failed: {error_message}"
        ) 