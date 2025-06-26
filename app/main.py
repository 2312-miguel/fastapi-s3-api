from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from .s3_utils import upload_file_to_s3, list_files_in_s3, generate_presigned_url, file_exists_in_s3
from .config import settings
from .exceptions import (
    S3UploadError, S3ListError, S3PresignedUrlError, 
    ConfigurationError, FileValidationError, handle_s3_error
)

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

@app.get("/")
def read_root():
    return {
        "message": "FastAPI S3 API is running!",
        "version": settings.API_VERSION,
        "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024),
        "allowed_extensions": settings.ALLOWED_EXTENSIONS
    }

@app.get("/health")
def health_check():
    """Health check endpoint with configuration validation."""
    try:
        if not settings.validate_aws_config():
            missing_fields = settings.get_missing_config_fields()
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "message": f"Missing configuration: {', '.join(missing_fields)}"
                }
            )
        
        # Test S3 connection
        list_files_in_s3()
        return {"status": "healthy", "message": "All systems operational"}
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": str(e)}
        )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to S3 bucket with improved error handling."""
    try:
        if not file.filename:
            raise FileValidationError("No file name provided")
        
        file_content = await file.read()
        
        # Validate file size before processing
        if len(file_content) > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            raise FileValidationError(f"File too large. Maximum size: {max_size_mb}MB")
        
        upload_file_to_s3(file_content, file.filename)
        
        return {
            "message": f"File {file.filename} uploaded successfully",
            "file_name": file.filename,
            "file_size": len(file_content)
        }
        
    except (FileValidationError, ConfigurationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except S3UploadError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/files")
def list_files():
    """List all files in the S3 bucket with improved error handling."""
    try:
        files = list_files_in_s3()
        return {
            "files": files,
            "total_files": len(files)
        }
        
    except ConfigurationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except S3ListError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/download/{file_name}")
def get_download_url(file_name: str):
    """Generate a presigned URL for file download with improved error handling."""
    try:
        if not file_name:
            raise HTTPException(status_code=400, detail="File name is required")
        
        # Check if file exists before generating URL
        if not file_exists_in_s3(file_name):
            raise HTTPException(status_code=404, detail=f"File '{file_name}' not found")
        
        url = generate_presigned_url(file_name)
        
        return {
            "download_url": url,
            "file_name": file_name,
            "expires_in_seconds": settings.PRESIGNED_URL_EXPIRATION
        }
        
    except ConfigurationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except S3PresignedUrlError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.exception_handler(S3UploadError)
async def s3_upload_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(ConfigurationError)
async def configuration_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    ) 