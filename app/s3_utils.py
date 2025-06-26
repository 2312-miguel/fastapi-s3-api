import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from .config import settings
from .exceptions import (
    S3UploadError, S3ListError, S3PresignedUrlError, 
    ConfigurationError, handle_s3_error
)

def get_s3_client():
    """Create and return an S3 client with credentials from configuration."""
    if not settings.validate_aws_config():
        missing_fields = settings.get_missing_config_fields()
        raise ConfigurationError(f"Missing required configuration: {', '.join(missing_fields)}")
    
    try:
        return boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    except NoCredentialsError:
        raise ConfigurationError("AWS credentials not found. Please check your configuration.")

def validate_file_extension(filename: str) -> bool:
    """Validate if file extension is allowed."""
    if not filename:
        return False
    
    file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
    return file_extension in settings.ALLOWED_EXTENSIONS

def validate_file_size(file_size: int) -> bool:
    """Validate if file size is within limits."""
    return file_size <= settings.MAX_FILE_SIZE

def upload_file_to_s3(file_content: bytes, file_name: str) -> bool:
    """Upload a file to S3 bucket with improved error handling."""
    try:
        # Validate file extension
        if not validate_file_extension(file_name):
            raise S3UploadError(f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}")
        
        # Validate file size
        if not validate_file_size(len(file_content)):
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            raise S3UploadError(f"File too large. Maximum size: {max_size_mb}MB")
        
        s3_client = get_s3_client()
        
        s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=file_name,
            Body=file_content
        )
        return True
        
    except (S3UploadError, ConfigurationError):
        raise
    except ClientError as e:
        raise S3UploadError(f"Failed to upload file: {str(e)}")
    except Exception as e:
        raise S3UploadError(f"Unexpected error during upload: {str(e)}")

def list_files_in_s3():
    """List all files in the S3 bucket with improved error handling."""
    try:
        s3_client = get_s3_client()
        
        response = s3_client.list_objects_v2(Bucket=settings.AWS_S3_BUCKET)
        files = []
        
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    'name': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })
        
        return files
        
    except ConfigurationError:
        raise
    except ClientError as e:
        raise S3ListError(f"Failed to list files: {str(e)}")
    except Exception as e:
        raise S3ListError(f"Unexpected error while listing files: {str(e)}")

def generate_presigned_url(file_name: str, expiration: int = None) -> str:
    """Generate a presigned URL for file download with improved error handling."""
    try:
        if not file_name:
            raise S3PresignedUrlError("File name is required")
        
        s3_client = get_s3_client()
        expiration = expiration or settings.PRESIGNED_URL_EXPIRATION
        
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_S3_BUCKET, 'Key': file_name},
            ExpiresIn=expiration
        )
        return url
        
    except ConfigurationError:
        raise
    except ClientError as e:
        raise S3PresignedUrlError(f"Failed to generate presigned URL: {str(e)}")
    except Exception as e:
        raise S3PresignedUrlError(f"Unexpected error generating presigned URL: {str(e)}")

def file_exists_in_s3(file_name: str) -> bool:
    """Check if a file exists in S3 bucket."""
    try:
        s3_client = get_s3_client()
        s3_client.head_object(Bucket=settings.AWS_S3_BUCKET, Key=file_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise S3PresignedUrlError(f"Error checking file existence: {str(e)}")
    except Exception as e:
        raise S3PresignedUrlError(f"Unexpected error checking file existence: {str(e)}") 