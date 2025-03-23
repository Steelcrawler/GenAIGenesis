import os
import logging
from typing import Dict, Any, Optional
from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden
from .pdf_sectioner import PDFProcessor
from google.auth import default
from .pdf_highlighting import process_pdf_with_subjects
from .gc_utils import (
    get_storage_client,
    validate_credentials,
    check_bucket_exists,
    upload_pdf_to_gcs,
    check_user_folder_exists,
    create_user_folder_in_gcs,
    download_file_from_gcs,
    get_json_data_from_gcs
)

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def process_pdf_to_json(bucket_name: str, user_id: str, course_id: str, file_name: str, 
                       credentials_path: Optional[str] = None) -> Dict[str, Any]:
    """Process a PDF file to create a JSON file with extracted subjects and text
    
    Returns:
        Dict: Results of processing with status information
    """
    try:
        if not user_id or not file_name:
            error_msg = "User ID and file name must be provided"
            logger.error(error_msg)
            return {
                "pdf_name": f"{user_id}/{course_id}/{file_name}" if user_id and file_name else "",
                "success": False,
                "error": error_msg
            }
            
        processor = PDFProcessor(debug=True, credentials_path=credentials_path)
        # The full blob path includes the user_id
        blob_path = f"{user_id}/{course_id}/{file_name}"
        results = processor.process_pdf(bucket_name, blob_path)
        logger.info(f"JSON file created in gs://{bucket_name}/{user_id}/{course_id}/{file_name}.json")
        return results
    
    except Exception as e:
        error_msg = f"Error processing PDF: {str(e)}"
        logger.error(error_msg)
        return {
            "pdf_name": f"{user_id}/{course_id}/{file_name}",
            "success": False,
            "text_extracted": False,
            "subjects": [],
            "partitioned_text": [],
            "error": error_msg
        }


def upload_and_process_pdf(file_obj, bucket_name: str, user_id: str, course_id: str, file_name: str,
                        credentials_path: Optional[str] = None) -> Dict[str, Any]:
    """End-to-end pipeline to upload a Django file object to GCS and process it
    
    Args:
        file_obj: A file-like object from Django's request.FILES
        bucket_name: Name of the GCS bucket
        user_id: User ID or folder name to organize files
        file_name: Name to save the file as in GCS
        credentials_path: Optional path to service account file (uses ADC if None)
        
    Returns:
        Dictionary with processing results
    """
    # Validate all input parameters
    if not file_obj or not bucket_name or not user_id or not file_name:
        error_msg = "All parameters must be provided: file_obj, bucket_name, user_id, file_name"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }
    
    # Validate file extension
    if not file_name.lower().endswith('.pdf'):
        error_msg = f"Invalid file extension: {file_name}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }
    
    # Validate credentials
    if not validate_credentials(credentials_path):
        return {
            "success": False,
            "error": "Failed to validate credentials"
        }
    
    # Check bucket exists
    if not check_bucket_exists(bucket_name, credentials_path):
        return {
            "success": False,
            "error": f"Cannot access bucket: {bucket_name}"
        }
    
    # 1. Check if user folder exists, create if not
    user_folder_exists = check_user_folder_exists(bucket_name, user_id, course_id, credentials_path)
    if not user_folder_exists:
        logger.info(f"User folder does not exist, creating: {user_id}")
        folder_created = create_user_folder_in_gcs(bucket_name, user_id, course_id, credentials_path)
        if not folder_created:
            return {
                "success": False,
                "error": f"Failed to create user folder: {user_id}"
            }
    
    # 2. Upload the PDF to the user's folder
    upload_success = upload_pdf_to_gcs(file_obj, bucket_name, user_id, course_id, file_name, credentials_path)
    if not upload_success:
        return {
            "success": False,
            "error": f"Failed to upload PDF: {file_name}"
        }
    
    # 3. Process the PDF and create JSON
    results = process_pdf_to_json(bucket_name, user_id, course_id, file_name, credentials_path)
    
    # Ensure all required fields are present in the results
    if not results.get("pdf_name"):
        results["pdf_name"] = file_name
    
    if "success" not in results:
        results["success"] = False if results.get("error") else True
    
    return results

def upload_process_and_highlight_pdf(file_obj, bucket_name: str, user_id: str, course_id: str, file_name: str,
                                     credentials_path: Optional[str] = None) -> Dict[str, Any]:
    """End-to-end pipeline to upload a Django file object to GCS, process it, and highlight it

    Args:
        file_obj: A file-like object from Django's request.FILES
        bucket_name: Name of the GCS bucket
        user_id: User ID or folder name to organize files
        course_id: Course ID or folder name to organize files
        file_name: Name to save the file as in GCS
        credentials_path: Optional path to service account file (uses ADC if None)
        
    Returns:
        Dictionary with processing results
    """
    try:
        # 1. Upload the PDF to GCS
        upload_success = upload_pdf_to_gcs(file_obj, bucket_name, user_id, course_id, file_name, credentials_path)
        if not upload_success:
            return {
                "success": False,
                "error": f"Failed to upload PDF: {file_name}"
            }
        
        # 2. Process the PDF and create JSON
        results = process_pdf_to_json(bucket_name, user_id, course_id, file_name, credentials_path)
        
        pdf_path = f"{user_id}/{course_id}/{file_name}"
        # 3. Highlight the PDF
        results = process_pdf_with_subjects(pdf_path, credentials_path, bucket_name)
        if not results:
            return {
                "success": False,
                "error": f"Failed to highlight PDF: {file_name}"
            }       
        
        return {
            "success": True,
            "pdf_name": f"{user_id}/{course_id}/{file_name}",
            "highlighted_bytes": results['pdf_bytes'],
            "highlighted_pdf_url": f"gs://{bucket_name}/{user_id}/{course_id}/{file_name}_highlighted.pdf"
        }
    
    except Exception as e:  
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }

if __name__ == "__main__":
    # Configuration
    credentials_path = "genaigenesis-454500-2b74084564ba.json"  # Set to None to use Application Default Credentials
    bucket_name = "educatorgenai"
    
    # Local file for testing
    local_pdf_path = "/Users/adityarajeev/Downloads/Code/GenAIGenesis/lec02_2_DecisionTrees_complete.pdf"
    user_id = "john2"
    course_id = "cs101"
    file_name = os.path.basename(local_pdf_path)  # Get the file name from the path
    
    print(f"Testing with file: {local_pdf_path}")
    print(f"User ID: {user_id}")
    print(f"Course ID: {course_id}")
    print(f"File name: {file_name}")
    print(f"Using credentials: {'ADC' if credentials_path is None else credentials_path}")
    
    # Enable more detailed logging for debugging
    logging.getLogger().setLevel(logging.DEBUG)
    
    # Create a file object from a local file for testing
    try:
        with open(local_pdf_path, 'rb') as f:
            # Pass the file object (similar to request.FILES in Django)
            results = upload_process_and_highlight_pdf(
                file_obj=f,
                bucket_name=bucket_name, 
                user_id=user_id, 
                course_id=course_id,
                file_name=file_name,
                credentials_path=credentials_path  # Pass None to use ADC
            )
        
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
    
    except FileNotFoundError:
        print(f"Error: The file {local_pdf_path} was not found.")
        print("Please make sure the path is correct relative to the script's location.")
    except Exception as e:
        print(f"Error: {str(e)}")