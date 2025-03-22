import os
import json
import logging
from typing import Dict, Any, Optional
from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden
from pdf_sectioner import PDFProcessor


# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_pdf_file(local_pdf_path: str) -> bool:
    """Validate that a PDF file exists and has the correct extension"""
    if not os.path.isfile(local_pdf_path):
        logger.error(f"PDF file not found: {local_pdf_path}")
        return False
    
    if not local_pdf_path.lower().endswith('.pdf'):
        logger.error(f"File does not have PDF extension: {local_pdf_path}")
        return False
    
    return True


def validate_credentials(credentials_path: str) -> bool:
    """Validate that credentials file exists"""
    if not os.path.isfile(credentials_path):
        logger.error(f"Credentials file not found: {credentials_path}")
        return False
    
    return True


def check_bucket_exists(bucket_name: str, credentials_path: str) -> bool:
    """Check if the GCS bucket exists and is accessible"""
    try:
        storage_client = storage.Client.from_service_account_json(credentials_path)
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


def upload_pdf_to_gcs(local_pdf_path: str, bucket_name: str, user_id: str, file_name: str, credentials_path: str) -> bool:
    """Upload a PDF file to Google Cloud Storage
    When a user uploads a PDF, we need to upload it to GCS to their corresponding folder
    
    Returns:
        bool: Success or failure
    """
    try:
        # Validate parameters
        if not validate_pdf_file(local_pdf_path):
            return False
        
        if not user_id or not file_name:
            logger.error("User ID and file name must be provided")
            return False
        
        # Upload file
        storage_client = storage.Client.from_service_account_json(credentials_path)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f"{user_id}/{file_name}")
        
        blob.upload_from_filename(local_pdf_path)
        logger.info(f"PDF uploaded to gs://{bucket_name}/{user_id}/{file_name}")
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


def check_user_folder_exists(bucket_name: str, user_id: str, credentials_path: str) -> bool:
    """Check if a user folder exists in the GCS bucket"""
    try:
        if not user_id:
            logger.error("User ID must be provided")
            return False
            
        storage_client = storage.Client.from_service_account_json(credentials_path)
        bucket = storage_client.bucket(bucket_name)
        # Check if any blobs exist with the user_id prefix
        blobs = list(bucket.list_blobs(prefix=f"{user_id}/", max_results=1))
        return len(blobs) > 0
    
    except Exception as e:
        logger.error(f"Error checking if user folder exists: {str(e)}")
        return False


def create_user_folder_in_gcs(bucket_name: str, user_id: str, credentials_path: str) -> bool:
    """Create a folder in Google Cloud Storage for a user
    GCS doesn't have actual folders, so we create an empty placeholder object
    
    Returns:
        bool: Success or failure
    """
    try:
        if not user_id:
            logger.error("User ID must be provided")
            return False
            
        storage_client = storage.Client.from_service_account_json(credentials_path)
        bucket = storage_client.bucket(bucket_name)
        # Create an empty placeholder object to represent the folder
        blob = bucket.blob(f"{user_id}/")
        blob.upload_from_string('')
        logger.info(f"User folder created in gs://{bucket_name}/{user_id}/")
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


def process_pdf_to_json(bucket_name: str, user_id: str, file_name: str, credentials_path: str) -> Dict[str, Any]:
    """Process a PDF file to create a JSON file with extracted subjects and text
    
    Returns:
        Dict: Results of processing with status information
    """
    try:
        if not user_id or not file_name:
            error_msg = "User ID and file name must be provided"
            logger.error(error_msg)
            return {
                "pdf_name": f"{user_id}/{file_name}" if user_id and file_name else "",
                "success": False,
                "error": error_msg
            }
            
        processor = PDFProcessor(debug=True, credentials_path=credentials_path)
        # The full blob path includes the user_id
        blob_path = f"{user_id}/{file_name}"
        results = processor.process_pdf(bucket_name, blob_path)
        logger.info(f"JSON file created in gs://{bucket_name}/{user_id}/{file_name}.json")
        return results
    
    except Exception as e:
        error_msg = f"Error processing PDF: {str(e)}"
        logger.error(error_msg)
        return {
            "pdf_name": f"{user_id}/{file_name}",
            "success": False,
            "text_extracted": False,
            "subjects": [],
            "partitioned_text": [],
            "error": error_msg
        }


def upload_and_process_pdf(local_pdf_path: str, bucket_name: str, user_id: str, credentials_path: str) -> Dict[str, Any]:
    """End-to-end pipeline to upload a local PDF to GCS and process it
    
    Args:
        local_pdf_path: Path to the local PDF file
        bucket_name: Name of the GCS bucket
        user_id: User ID or folder name to organize files
        credentials_path: Path to the GCS credentials JSON file
        
    Returns:
        Dictionary with processing results
    """
    # Validate all input parameters
    if not local_pdf_path or not bucket_name or not user_id or not credentials_path:
        error_msg = "All parameters must be provided: local_pdf_path, bucket_name, user_id, credentials_path"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }
    
    # Validate PDF file
    if not validate_pdf_file(local_pdf_path):
        return {
            "success": False,
            "error": f"Invalid PDF file: {local_pdf_path}"
        }
    
    # Validate credentials
    if not validate_credentials(credentials_path):
        return {
            "success": False,
            "error": f"Invalid credentials file: {credentials_path}"
        }
    
    # Check bucket exists
    if not check_bucket_exists(bucket_name, credentials_path):
        return {
            "success": False,
            "error": f"Cannot access bucket: {bucket_name}"
        }
    
    # Extract just the filename from the local path
    file_name = os.path.basename(local_pdf_path)
    
    # 1. Check if user folder exists, create if not
    user_folder_exists = check_user_folder_exists(bucket_name, user_id, credentials_path)
    if not user_folder_exists:
        logger.info(f"User folder does not exist, creating: {user_id}")
        folder_created = create_user_folder_in_gcs(bucket_name, user_id, credentials_path)
        if not folder_created:
            return {
                "success": False,
                "error": f"Failed to create user folder: {user_id}"
            }
    
    # 2. Upload the PDF to the user's folder
    upload_success = upload_pdf_to_gcs(local_pdf_path, bucket_name, user_id, file_name, credentials_path)
    if not upload_success:
        return {
            "success": False,
            "error": f"Failed to upload PDF: {local_pdf_path}"
        }
    
    # 3. Process the PDF and create JSON
    results = process_pdf_to_json(bucket_name, user_id, file_name, credentials_path)
    
    # Ensure all required fields are present in the results
    if not results.get("pdf_name"):
        results["pdf_name"] = f"{user_id}/{file_name}"
    
    if "success" not in results:
        results["success"] = False if results.get("error") else True
    
    return results


if __name__ == "__main__":
    # Configuration
    credentials_path = 'genaigenesis-454500-2b74084564ba.json'
    bucket_name = "educatorgenai"
    
    local_pdf_path = "../lec02_2_DecisionTrees_complete.pdf"
    user_id = "john2"
    
    # Enable more detailed logging for debugging
    logging.getLogger().setLevel(logging.DEBUG)
    
    results = upload_and_process_pdf(local_pdf_path, bucket_name, user_id, credentials_path)
    
    # Print a summary of the results
    print(f"\nSummary:")
    print(f"PDF: {results.get('pdf_name', 'Unknown')}")
    print(f"Success: {results.get('success', False)}")
    print(f"Text Extracted: {results.get('text_extracted', False)}")
    
    if results.get('subjects'):
        print(f"Subjects found: {len(results['subjects'])}")
    else:
        print("Subjects found: 0")
        
    if results.get('partitioned_text'):
        print(f"Text sections found: {len(results['partitioned_text'])}")
    else:
        print("Text sections found: 0")
    
    if results.get('error'):
        print(f"Error: {results['error']}")
    
    if results.get('pdf_name') and results.get('success'):
        print(f"\nResults saved to: gs://{bucket_name}/{results['pdf_name']}.json")



