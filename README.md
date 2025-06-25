# FastAPI S3 API

A lightweight API to upload, list, and download files using FastAPI and Amazon S3.

## Tech Stack
- FastAPI
- Amazon S3 (AWS)
- Boto3
- Docker

## Features
- Upload files to an S3 bucket
- List all files in the bucket
- Generate secure, time-limited download URLs

## Setup
1. Copy `.env.example` to `.env` and fill in your AWS credentials and bucket name.
2. Build and run the service:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`. 