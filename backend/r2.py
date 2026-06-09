import os
import boto3
from botocore.config import Config

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT = os.getenv("R2_ENDPOINT", f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com")

def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )

def upload_file(file_obj, key: str, content_type: str = "application/octet-stream") -> str:
    client = get_r2_client()
    client.upload_fileobj(
        file_obj,
        R2_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": content_type},
    )
    return key

def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    client = get_r2_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": R2_BUCKET_NAME, "Key": key},
        ExpiresIn=expires_in,
    )

def delete_file(key: str) -> None:
    client = get_r2_client()
    client.delete_object(Bucket=R2_BUCKET_NAME, Key=key)
