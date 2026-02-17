# Upload resume to S3 and generate presigned download URLs
import logging
import uuid
from pathlib import Path
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


def _client():
    """Lazy S3 client so we don't require boto3/credentials when S3 is not used."""
    import boto3
    from botocore.config import Config

    kwargs = {"region_name": settings.AWS_REGION}
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    return boto3.client("s3", config=Config(signature_version="s3v4"), **kwargs)


def is_s3_configured() -> bool:
    """Return True if S3 bucket is set (credentials can come from env or IAM)."""
    return bool(settings.S3_BUCKET)


def upload_resume_to_s3(content: bytes, filename: str, content_type: Optional[str] = None) -> Optional[str]:
    """
    Upload resume file to S3. Returns the S3 object key on success, None on failure.
    Key format: resumes/{uuid}/{sanitized_filename}
    """
    if not is_s3_configured():
        return None
    safe_name = Path(filename).name if filename else "resume.pdf"
    if not safe_name or safe_name in (".", ".."):
        safe_name = "resume.pdf"
    key = f"resumes/{uuid.uuid4().hex}/{safe_name}"
    try:
        client = _client()
        extra = {}
        if content_type:
            extra["ContentType"] = content_type
        client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=content,
            **extra,
        )
        logger.info("Resume uploaded to S3: bucket=%s key=%s", settings.S3_BUCKET, key)
        return key
    except Exception as e:
        logger.exception("S3 upload failed: %s", e)
        return None


def get_presigned_download_url(s3_key: str, expires_in: int = 3600) -> Optional[str]:
    """
    Generate a presigned URL to download the resume. Returns None if S3 not configured or key missing.
    Default expiry 1 hour; use 86400 for 24 hours in emails.
    """
    if not is_s3_configured() or not s3_key:
        return None
    try:
        client = _client()
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": s3_key},
            ExpiresIn=expires_in,
        )
        return url
    except Exception as e:
        logger.exception("Presigned URL failed: %s", e)
        return None
