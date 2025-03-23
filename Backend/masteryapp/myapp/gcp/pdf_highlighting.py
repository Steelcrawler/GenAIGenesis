import os
import io
import json
import logging
import random
import tempfile
from typing import Dict, Any, List, Tuple, Optional
from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden
import fitz  # PyMuPDF

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_storage_client(credentials_path: Optional[str] = None):
    """Get a storage client using ADC or service account credentials"""
    try:
        if credentials_path and os.path.exists(credentials_path):
            logger.info(f"Using service account credentials from: {credentials_path}")
            return storage.Client.from_service_account_json(credentials_path)
        else:
            logger.info("Using Application Default Credentials")
            return storage.Client()
    except Exception as e:
        logger.error(f"Error creating storage client: {str(e)}")
        raise

def get_predefined_colors() -> List[Tuple[float, float, float]]:
    """Return a list of predefined pastel colors for consistent subject highlighting"""
    return [
        (1.0, 0.8, 0.8),  # Light Pink
        (0.8, 1.0, 0.8),  # Light Green
        (0.8, 0.8, 1.0),  # Light Blue
        (1.0, 1.0, 0.8),  # Light Yellow
        (1.0, 0.8, 1.0),  # Light Purple
        (0.8, 1.0, 1.0),  # Light Cyan
        (0.9, 0.9, 0.7),  # Light Tan
        (0.9, 0.7, 0.9),  # Light Lavender
        (0.7, 0.9, 0.9),  # Light Aqua
        (1.0, 0.9, 0.7),  # Light Orange
    ]

def download_file_from_gcs(storage_client, bucket_name: str, blob_name: str) -> io.BytesIO:
    """Download a file from GCS bucket as a BytesIO object"""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        file_bytes = io.BytesIO()
        blob.download_to_file(file_bytes)
        file_bytes.seek(0)  # Reset pointer to beginning of file
        
        logger.info(f"Downloaded {blob_name} from bucket {bucket_name}")
        return file_bytes
    except Exception as e:
        logger.error(f"Error downloading file from GCS: {str(e)}")
        raise

def upload_file_to_gcs(storage_client, bucket_name: str, blob_name: str, data: io.BytesIO) -> bool:
    """Upload a file to GCS bucket"""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        data.seek(0)  # Reset pointer to beginning of file
        blob.upload_from_file(data, content_type='application/pdf')
        
        logger.info(f"Uploaded file to gs://{bucket_name}/{blob_name}")
        return True
    except Exception as e:
        logger.error(f"Error uploading file to GCS: {str(e)}")
        return False

def get_json_data_from_gcs(storage_client, bucket_name: str, json_blob_name: str) -> Dict[str, Any]:
    """Get JSON data from GCS bucket"""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(json_blob_name)
        
        json_data = json.loads(blob.download_as_text())
        logger.info(f"Downloaded and parsed JSON from {bucket_name}/{json_blob_name}")
        return json_data
    except Exception as e:
        logger.error(f"Error getting JSON from GCS: {str(e)}")
        raise

def highlight_pdf_with_subjects(storage_client, bucket_name: str, pdf_blob_name: str, 
                               json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Add subject indicators to PDF pages where subjects are detected"""
    results = {
        "pdf_name": pdf_blob_name,
        "success": False,
        "marked_subjects": [],
        "marked_pdf_url": "",
        "pdf_bytes": None,
        "error": None
    }
    
    try:
        # Get partitioned text from JSON data
        partitioned_text = json_data.get("partitioned_text", [])
        if not partitioned_text:
            results["error"] = "No partitioned text found in JSON data"
            return results
        
        # Get subjects from the JSON data
        subjects = [subject.get("subject") for subject in json_data.get("subjects", [])]
        
        # Download the PDF file
        pdf_bytes = download_file_from_gcs(storage_client, bucket_name, pdf_blob_name)
        
        # Open the PDF with PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Get predefined colors
        colors = get_predefined_colors()
        
        # Create a mapping of subjects to colors
        subject_colors = {}
        for i, subject in enumerate(subjects):
            subject_colors[subject] = colors[i % len(colors)]
        
        # Track subjects found on each page
        page_subjects = {}
        
        # Group partitioned text by subject
        text_by_subject = {}
        for item in partitioned_text:
            subject = item.get("subject")
            text = item.get("text")
            
            if subject and text:
                if subject not in text_by_subject:
                    text_by_subject[subject] = []
                text_by_subject[subject].append(text)
        
        # Process each subject
        for subject in subjects:
            if subject not in subject_colors:
                continue
                
            color = subject_colors[subject]
            
            # Search for text matches in PDF
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text().lower()
                
                # If subject has associated text, search for that
                if subject in text_by_subject:
                    for text in text_by_subject[subject]:
                        # Clean the text
                        clean_text = text.replace('\n', ' ').strip()
                        if len(clean_text) < 10:
                            continue
                        
                        # Split into sentences
                        sentences = [s.strip() for s in clean_text.split('.') if s.strip()]
                        
                        # For each sentence, try to find a match
                        for sentence in sentences:
                            sentence = sentence.replace('\n', ' ').strip()
                            if len(sentence) < 10:
                                continue
                            
                            # Get key words from the sentence
                            words = [w for w in sentence.split() if len(w) > 4 and w.isalpha()]
                            if not words:
                                continue
                            
                            # Look for sentences containing our key words
                            page_sentences = [s.strip() for s in page_text.split('.') if s.strip()]
                            
                            for page_sentence in page_sentences:
                                # Check if this sentence contains enough of our key words
                                matching_words = sum(1 for word in words if word.lower() in page_sentence.lower())
                                
                                # If we have enough matching words (at least 2 or 50% of key words)
                                if matching_words >= max(2, len(words) // 2):
                                    if page_num not in page_subjects:
                                        page_subjects[page_num] = set()
                                    page_subjects[page_num].add(subject)
                                    logger.info(f"Found text matching subject '{subject}' on page {page_num+1}")
                                    break
                            
                            # If we found a match, move to next subject
                            if page_num in page_subjects and subject in page_subjects[page_num]:
                                break
        
        # Add subject indicators to each page
        for page_num, subjects in page_subjects.items():
            page = doc[page_num]
            
            # Get page dimensions
            page_width = page.rect.width
            page_height = page.rect.height
            
            # Calculate position for circles in top right corner
            circle_radius = 6  # Smaller circles
            circle_spacing = 25  # Spacing between items
            circle_x = page_width - 15  # Circles 15px from right edge
            y_offset = 20  # Start 20px from top
            
            # Draw circles for each subject
            for subject in subjects:
                color = subject_colors[subject]
                
                circle_y = y_offset
                
                # Draw filled circle
                page.draw_circle((circle_x, circle_y), circle_radius, color=color, fill=color)
                
                # Add text to the left of circle
                text_x = circle_x - circle_radius - 8  # 8px gap between circle and text
                text = subject[:40]  # Limit length to avoid overflow
                
                # Insert text with right alignment
                text_width = fitz.get_text_length(text, fontsize=8)  # Get width of text
                page.insert_text(
                    point=(text_x - text_width, circle_y + 3),  # Position text vertically centered with circle
                    text=text,
                    fontsize=8,
                    color=(0, 0, 0)  # Black text
                )
                
                # Move down for next pair
                y_offset += circle_spacing
        
        # Save the modified PDF
        output_pdf = io.BytesIO()
        doc.save(output_pdf)
        doc.close()
        
        # Upload modified PDF back to GCS
        marked_pdf_name = pdf_blob_name.rsplit('.', 1)[0] + '_subject_marked.pdf'
        upload_success = upload_file_to_gcs(storage_client, bucket_name, marked_pdf_name, output_pdf)
        
        if not upload_success:
            results["error"] = "Failed to upload marked PDF"
            return results
        
        # Reset buffer position for future reading
        output_pdf.seek(0)
        
        # Update results
        results["success"] = True
        results["marked_pdf_url"] = f"gs://{bucket_name}/{marked_pdf_name}"
        results["marked_subjects"] = list(set().union(*page_subjects.values())) if page_subjects else []
        results["pdf_bytes"] = output_pdf  # Add PDF bytes to results
        
        return results
        
    except Exception as e:
        results["error"] = f"Error marking PDF: {str(e)}"
        return results

def process_pdf_with_subjects(pdf_path: str, json_path: str, credentials_path: Optional[str] = None, bucket_name: str = "educatorgenai") -> Dict[str, Any]:
    """
    Process a PDF file with subjects from a JSON file and return the highlighted PDF.
    
    Args:
        pdf_path: Path to the PDF file in GCS (e.g. "folder/file.pdf")
        json_path: Path to the JSON file in GCS (e.g. "folder/file.json")
        credentials_path: Optional path to GCP credentials file. If None, uses ADC.
        bucket_name: Name of the GCS bucket
        
    Returns:
        Dictionary containing:
        - success: bool indicating if process completed successfully
        - marked_pdf_url: URL of the marked PDF in GCS
        - marked_subjects: List of subjects that were marked
        - pdf_bytes: BytesIO object containing the marked PDF data
        - error: Error message if any
    """
    results = {
        "success": False,
        "marked_pdf_url": "",
        "marked_subjects": [],
        "pdf_bytes": None,
        "error": None
    }
    
    try:
        # Initialize storage client
        storage_client = get_storage_client(credentials_path)
        
        # Get JSON data
        logger.info(f"Retrieving JSON data from GCS: {json_path}")
        json_data = get_json_data_from_gcs(storage_client, bucket_name, json_path)
        
        # Process the PDF
        logger.info(f"Processing PDF with subjects from JSON: {pdf_path}")
        results = highlight_pdf_with_subjects(storage_client, bucket_name, pdf_path, json_data)
        
        return results
        
    except Exception as e:
        results["error"] = f"Pipeline error: {str(e)}"
        return results

if __name__ == "__main__":
    # Example usage
    pdf_path = "john2/lec02_2_DecisionTrees_complete.pdf"
    json_path = "john2/lec02_2_DecisionTrees_complete.json"
    
    # Use Application Default Credentials by default
    credentials_path = None
    
    # Log authentication method
    if credentials_path:
        logger.info(f"Using service account credentials: {credentials_path}")
    else:
        logger.info("Using Application Default Credentials")
    
    results = process_pdf_with_subjects(pdf_path, json_path, credentials_path)
    
    # Print results
    print("\nProcessing Results:")
    print(f"Success: {results['success']}")
    
    if results.get('marked_subjects'):
        print(f"Marked subjects: {', '.join(results['marked_subjects'])}")
    
    if results.get('marked_pdf_url'):
        print(f"Marked PDF saved to: {results['marked_pdf_url']}")
        
    if results.get('pdf_bytes'):
        print(f"PDF bytes available for local usage")
    
    if results.get('error'):
        print(f"Error: {results['error']}")