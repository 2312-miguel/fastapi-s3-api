from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from .s3_utils import upload_file_to_s3, list_files_in_s3, generate_presigned_url

app = FastAPI(title="FastAPI S3 API", description="A lightweight file upload and download API")

@app.get("/")
def read_root():
    return {"message": "FastAPI S3 API is running!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to S3 bucket."""
    try:
        file_content = await file.read()
        success = upload_file_to_s3(file_content, file.filename)
        
        if success:
            return {"message": f"File {file.filename} uploaded successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to upload file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
def list_files():
    """List all files in the S3 bucket."""
    try:
        files = list_files_in_s3()
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_name}")
def get_download_url(file_name: str):
    """Generate a presigned URL for file download."""
    try:
        url = generate_presigned_url(file_name)
        if url:
            return {"download_url": url, "file_name": file_name}
        else:
            raise HTTPException(status_code=404, detail="File not found or error generating URL")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 