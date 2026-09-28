import os
import uuid
import datetime
from werkzeug.utils import secure_filename
from google.cloud import storage

# Configurations
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "pika-wil")
GCS_FOLDER_PREFIX = os.getenv("GCS_FOLDER_PREFIX", "ksr-biology").strip("/")
CREDS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcp_creds.json")

_gcs_client = None

def get_storage_client():
    global _gcs_client
    if _gcs_client is None:
        if os.path.exists(CREDS_FILE):
            _gcs_client = storage.Client.from_service_account_json(CREDS_FILE)
        else:
            _gcs_client = storage.Client()
    return _gcs_client

def get_bucket():
    client = get_storage_client()
    return client.bucket(GCS_BUCKET_NAME)

def format_file_size(size_bytes):
    if not size_bytes:
        return "0 KB"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"

def upload_file_to_gcs(file_storage, folder="materials"):
    """
    Uploads a Werkzeug FileStorage object to GCS.
    Returns a dict with: blob_name, original_filename, file_size_str, file_type
    """
    original_filename = secure_filename(file_storage.filename) or "material.pdf"
    ext = os.path.splitext(original_filename)[1].lower().replace(".", "").upper() or "PDF"
    
    # Generate unique blob name under the designated folder prefix
    unique_id = uuid.uuid4().hex[:8]
    sanitized_name = f"{unique_id}_{original_filename}"
    blob_name = f"{GCS_FOLDER_PREFIX}/{folder}/{sanitized_name}"
    
    bucket = get_bucket()
    blob = bucket.blob(blob_name)
    
    # Read file data to get content-type and size
    file_storage.seek(0, os.SEEK_END)
    file_size = file_storage.tell()
    file_storage.seek(0)
    
    content_type = file_storage.content_type or "application/octet-stream"
    if ext == "PDF":
        content_type = "application/pdf"
    elif ext in ["JPG", "JPEG"]:
        content_type = "image/jpeg"
    elif ext == "PNG":
        content_type = "image/png"
        
    blob.upload_from_file(file_storage, content_type=content_type)
    
    return {
        "blob_name": blob_name,
        "original_filename": original_filename,
        "file_size": format_file_size(file_size),
        "file_type": ext,
        "content_type": content_type
    }

def generate_signed_url(blob_name, disposition="inline", download_name=None, minutes=60):
    """
    Generates a secure GCS v4 signed URL for inline preview or attachment download.
    """
    try:
        bucket = get_bucket()
        blob = bucket.blob(blob_name)
        
        response_disposition = disposition
        if download_name and disposition == "attachment":
            safe_download_name = secure_filename(download_name)
            response_disposition = f'attachment; filename="{safe_download_name}"'
        elif download_name and disposition == "inline":
            safe_download_name = secure_filename(download_name)
            response_disposition = f'inline; filename="{safe_download_name}"'

        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=minutes),
            method="GET",
            response_disposition=response_disposition
        )
        return url
    except Exception as e:
        print(f"Error generating signed URL for {blob_name}: {e}")
        return None

def delete_file_from_gcs(blob_name):
    """
    Deletes a blob from GCS.
    """
    try:
        bucket = get_bucket()
        blob = bucket.blob(blob_name)
        if blob.exists():
            blob.delete()
            return True
        return False
    except Exception as e:
        print(f"Error deleting blob {blob_name}: {e}")
        return False
