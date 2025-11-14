"""Utilities for S3 uploads (presigned URLs for brief attachments)."""

from __future__ import annotations

import os
import re
import uuid
from functools import lru_cache

import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, NoCredentialsError


class StorageConfigError(RuntimeError):
    """Raised when storage settings are missing or invalid."""


def _bucket() -> str:
    bucket = os.getenv("CONTENTHUB_S3_BUCKET")
    if not bucket:
        raise StorageConfigError("CONTENTHUB_S3_BUCKET is not configured")
    return bucket


def _region() -> str:
    return os.getenv("CONTENTHUB_S3_REGION", "us-east-1")


def _expires_seconds() -> int:
    return int(os.getenv("CONTENTHUB_S3_TTL", "3600"))


def _safe_filename(name: str | None) -> str:
    fallback = "upload"
    if not name:
        return fallback
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")
    return cleaned or fallback


@lru_cache(maxsize=1)
def _s3_client() -> BaseClient:
    return boto3.client("s3", region_name=_region())


def build_presigned_upload(filename: str, content_type: str = "application/octet-stream") -> dict:
    """Return presigned POST metadata for uploading a brief attachment."""
    bucket = _bucket()
    key = f"briefs/{uuid.uuid4().hex}-{_safe_filename(filename)}"
    client = _s3_client()
    try:
        presigned = client.generate_presigned_post(
            Bucket=bucket,
            Key=key,
            Fields={"Content-Type": content_type},
            Conditions=[{"Content-Type": content_type}],
            ExpiresIn=_expires_seconds(),
        )
    except (BotoCoreError, NoCredentialsError) as exc:
        raise StorageConfigError(f"Unable to generate upload URL: {exc}") from exc

    region = _region()
    url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    return {
        "key": key,
        "url": url,
        "upload_url": presigned["url"],
        "fields": presigned["fields"],
        "content_type": content_type,
    }
