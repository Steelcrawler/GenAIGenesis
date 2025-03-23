import os
import io
import json
import logging
from typing import Dict, Any, Optional
from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_storage_client(credentials_path: Optional[str] = None):
    """Get a storage client using ADC or service account credentials
    
    Args:
        credentials_path: Optional path to service account file (fallback)
        
    Returns:
        Google Cloud Storage client
    """
    try:
        # Try Application Default Credentials first
        if credentials_path is None:
            logger.info("Using Application Default Credentials")
            return storage.Client()
            
        # Fall back to service account file if provided
        elif os.path.isfile(credentials_path):
            logger.info(f"Using service account credentials from: {credentials_path}")
            return storage.Client.from_service_account_json(credentials_path)
        else:
            logger.warning(f"Credentials file not found: {credentials_path}, falling back to ADC")
            return storage.Client()
            
    except Exception as e:
        logger.error(f"Error creating storage client: {str(e)}")
        raise


def validate_credentials(credentials_path: Optional[str] = None) -> bool:
    """Validate that credentials are available (either ADC or file)"""
    try:
        if credentials_path is not None and not os.path.isfile(credentials_path):
            logger.warning(f"Credentials file not found: {credentials_path}, will try ADC")
        
        # Test creating a client
        client = get_storage_client(credentials_path)
        return True
    except Exception as e:
        logger.error(f"Failed to initialize credentials: {str(e)}")
        return False


def check_bucket_exists(bucket_name: str, credentials_path: Optional[str] = None) -> bool:
    """Check if the GCS bucket exists and is accessible"""
    try:
        storage_client = get_storage_client(credentials_path)
        bucket = storage_client.get_bucket(bucket_name)
        return True
    except NotFound:
        logger.error(f"Bucket not found: {bucket_name}")
        return False
    except Forbidden:
        logger.error(f"No permission to access bucket: {bucket_name}")
        return False
    except Exception as e:
        logger.error(f"Error checking bucket: {str(e)}")
        return False


def upload_pdf_to_gcs(file_obj, bucket_name: str, user_id: str, course_id: str, file_name: str, 
                     credentials_path: Optional[str] = None) -> bool:
    """Upload a PDF file to Google Cloud Storage
    When a user uploads a PDF, we need to upload it to GCS to their corresponding folder
    
    Args:
        file_obj: A file-like object (e.g., from Django's request.FILES)
        bucket_name: Name of the GCS bucket
        user_id: User ID or folder name to organize files
        course_id: Course ID or folder name to organize files
        file_name: Name of the file to be stored in GCS
        credentials_path: Optional path to service account file (uses ADC if None)
    
    Returns:
        bool: Success or failure
    """
    try:
        # Validate parameters
        if not file_obj:
            logger.error("File object is required")
            return False
        
        if not user_id or not file_name:
            logger.error("User ID and file name must be provided")
            return False
        
        # Validate file extension
        if not file_name.lower().endswith('.pdf'):
            logger.error(f"File does not have PDF extension: {file_name}")
            return False
        
        # Upload file
        storage_client = get_storage_client(credentials_path)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f"{user_id}/{course_id}/{file_name}")
        
        # Upload from file object
        blob.upload_from_file(file_obj)
        logger.info(f"PDF uploaded to gs://{bucket_name}/{user_id}/{course_id}/{file_name}")
        return True
    
    except NotFound:
        logger.error(f"Bucket not found: {bucket_name}")
        return False
    except Forbidden:
        logger.error(f"No permission to access bucket: {bucket_name}")
        return False
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}")
        return False
    
def get_pdf_bytes_from_gcs(bucket_name: str, user_id: str, course_id: str, file_name: str, credentials_path: Optional[str] = None) -> bytes:
    """Get PDF bytes from GCS bucket
    
    Args:
        bucket_name: Name of the GCS bucket
        user_id: User ID or folder name where files are organized
        course_id: Course ID or folder name where files are organized
        file_name: Name of the file stored in GCS
        credentials_path: Optional path to service account file (uses ADC if None)
        
    Returns:
        bytes: The file content as bytes
    """
    try:
        storage_client = get_storage_client(credentials_path)
        bucket = storage_client.bucket(bucket_name)
        base_file_name = file_name.split('.')[0]  # Get everything before the first period
        
        # Attempt to get the highlighted PDF first
        highlighted_blob = bucket.blob(f"{user_id}/{course_id}/{base_file_name}_highlighted.pdf")
        if highlighted_blob.exists():
            return highlighted_blob.download_as_bytes()
        
        # If highlighted PDF does not exist, get the regular PDF
        regular_blob = bucket.blob(f"{user_id}/{course_id}/{file_name}")
        return regular_blob.download_as_bytes()
    except Exception as e:
        logger.error(f"Error getting PDF bytes from GCS: {str(e)}")
        raise


def check_user_folder_exists(bucket_name: str, user_id: str, course_id: str, 
                            credentials_path: Optional[str] = None) -> bool:
    """Check if a user folder exists in the GCS bucket"""
    try:
        if not user_id:
            logger.error("User ID must be provided")
            return False
            
        storage_client = get_storage_client(credentials_path)
        bucket = storage_client.bucket(bucket_name)
        # Check if any blobs exist with the user_id prefix
        blobs = list(bucket.list_blobs(prefix=f"{user_id}/{course_id}/", max_results=1))
        return len(blobs) > 0
    
    except Exception as e:
        logger.error(f"Error checking if user folder exists: {str(e)}")
        return False


def create_user_folder_in_gcs(bucket_name: str, user_id: str, course_id: str, 
                             credentials_path: Optional[str] = None) -> bool:
    """Create a folder in Google Cloud Storage for a user
    GCS doesn't have actual folders, so we create an empty placeholder object
    
    Returns:
        bool: Success or failure
    """
    try:
        if not user_id:
            logger.error("User ID must be provided")
            return False
            
        storage_client = get_storage_client(credentials_path)
        bucket = storage_client.bucket(bucket_name)
        # Create an empty placeholder object to represent the folder
        blob = bucket.blob(f"{user_id}/{course_id}/")
        blob.upload_from_string('')
        logger.info(f"User folder created in gs://{bucket_name}/{user_id}/{course_id}/")
        return True
    
    except NotFound:
        logger.error(f"Bucket not found: {bucket_name}")
        return False
    except Forbidden:
        logger.error(f"No permission to access bucket: {bucket_name}")
        return False
    except Exception as e:
        logger.error(f"Error creating user folder: {str(e)}")
        return False


def download_file_from_gcs(bucket_name: str, user_id: str, course_id: str, file_name: str, credentials_path: Optional[str] = None) -> io.BytesIO:
    """Download a file from GCS bucket as a BytesIO object
    
    Args:
        bucket_name: Name of the GCS bucket
        user_id: User ID or folder name where files are organized
        course_id: Course ID or folder name where files are organized
        file_name: Name of the file to download from GCS
        credentials_path: Optional path to service account file (uses ADC if None)
        
    Returns:
        io.BytesIO: File contents as a BytesIO object
    """
    try:
        storage_client = get_storage_client(credentials_path)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f"{user_id}/{course_id}/{file_name}")
        
        file_bytes = io.BytesIO()
        blob.download_to_file(file_bytes)
        file_bytes.seek(0)  # Reset pointer to beginning of file
        
        logger.info(f"Downloaded {file_name} from bucket {bucket_name}")
        return file_bytes
    except Exception as e:
        logger.error(f"Error downloading file from GCS: {str(e)}")
        raise


def get_json_data_from_gcs(bucket_name: str, user_id: str, course_id: str, file_name: str, credentials_path: Optional[str] = None) -> Dict[str, Any]:
    """Get JSON data from GCS bucket
    
    Args:
        bucket_name: Name of the GCS bucket
        user_id: User ID or folder name where files are organized
        course_id: Course ID or folder name where files are organized
        file_name: Name of the file to get JSON data from
        credentials_path: Optional path to service account file (uses ADC if None)
        
    Returns:
        Dict[str, Any]: Parsed JSON data
    """
    try:
        storage_client = get_storage_client(credentials_path)
        bucket = storage_client.bucket(bucket_name)
        file_blob_name = f"{user_id}/{course_id}/{file_name}"
        json_blob_name = file_blob_name.rsplit('.', 1)[0] + '.json'
        blob = bucket.blob(json_blob_name)
        
        json_data = json.loads(blob.download_as_text())
        logger.info(f"Downloaded and parsed JSON from {bucket_name}/{json_blob_name}")
        return json_data
    except Exception as e:
        logger.error(f"Error getting JSON from GCS: {str(e)}")
        raise