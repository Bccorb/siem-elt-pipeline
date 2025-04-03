from fastapi import FastAPI, UploadFile
import pandas as pd
import boto3
import duckdb
import os
from prometheus_client import Counter, generate_latest
from fastapi.responses import PlainTextResponse

app = FastAPI()

# MinIO Config
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "password")
BUCKET_NAME = "rawlogs"

# DuckDB Path
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "/app/data/warehouse.db")

# Metrics
log_ingested = Counter("log_ingested_total", "Total logs ingested")

# Connect to MinIO
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)


# Ensure MinIO bucket exists
def ensure_bucket():
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
    except:
        s3_client.create_bucket(Bucket=BUCKET_NAME)


ensure_bucket()


@app.post("/upload/")
async def upload_log(file: UploadFile):
    try:
        file_contents = await file.read()

        # Save raw log file to MinIO
        s3_client.upload_fileobj(file.file, BUCKET_NAME, file.filename)

        # Load file into Pandas for transformation
        df = pd.read_json(file_contents.decode("utf-8"))

        # Perform transformations (example: standardize column names)
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]

        # Store transformed data in DuckDB
        con = duckdb.connect(DUCKDB_PATH)
        con.execute("CREATE TABLE IF NOT EXISTS logs AS SELECT * FROM df")
        con.execute("INSERT INTO logs SELECT * FROM df")
        con.close()

        log_ingested.inc()

        return {"message": "File uploaded and processed successfully"}
    except Exception as e:
        print(e)
        return {"message: 'An errror occured"}


@app.get("/metrics/")
def metrics():
    return PlainTextResponse(generate_latest())
