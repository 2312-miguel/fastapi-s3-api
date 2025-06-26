import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def get_s3_client():
    """Create and return an S3 client with credentials from environment variables."""
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

def get_bucket_name():
    """Get the S3 bucket name from environment variables."""
    return os.getenv('AWS_S3_BUCKET')

def upload_file_to_s3(file_content, file_name):
    """Upload a file to S3 bucket."""
    try:
        s3_client = get_s3_client()
        bucket_name = get_bucket_name()
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=file_content
        )
        return True
    except ClientError as e:
        print(f"Error uploading file: {e}")
        return False

def list_files_in_s3():
    """List all files in the S3 bucket."""
    try:
        s3_client = get_s3_client()
        bucket_name = get_bucket_name()
        
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        files = []
        
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    'name': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })
        
        return files
    except ClientError as e:
        print(f"Error listing files: {e}")
        return []

def generate_presigned_url(file_name, expiration=3600):
    """Generate a presigned URL for file download."""
    try:
        s3_client = get_s3_client()
        bucket_name = get_bucket_name()
        
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None 