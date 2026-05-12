from functools import lru_cache
from typing import BinaryIO

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from .config import settings


@lru_cache(maxsize=1)
def get_s3_client():
    client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        use_ssl=settings.s3_use_ssl,
        config=Config(signature_version="s3v4", s3={"addressing_style": settings.s3_addressing_style}),
    )
    ensure_bucket(client, settings.s3_bucket)
    return client


def ensure_bucket(client, bucket: str) -> None:
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code in {"404", "NoSuchBucket", "NotFound"}:
            client.create_bucket(Bucket=bucket)
        else:
            raise


def upload_fileobj(fileobj: BinaryIO, key: str, content_type: str | None) -> None:
    extra = {"ContentType": content_type} if content_type else None
    get_s3_client().upload_fileobj(fileobj, settings.s3_bucket, key, ExtraArgs=extra or {})


def get_object_stream(key: str):
    """Return a streaming body for the given object key."""
    resp = get_s3_client().get_object(Bucket=settings.s3_bucket, Key=key)
    return resp["Body"], resp.get("ContentType"), resp.get("ContentLength")
