import os
import tempfile
import uuid
import io
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from google.cloud import storage
from vertexai.preview import rag
from vertexai.preview.generative_models import GenerativeModel, Tool, Content
import vertexai
import json
import PyPDF2
import requests
from pathlib import Path
import base64

class PDFProcessor:
    def __init__(self, credentials_path: Optional[str] = None, debug: bool = False):
        """Initialize the PDF processor with GCP credentials"""
        self.debug = debug
        env_path = '../.env'
        load_dotenv(dotenv_path=env_path)
        
        self.project_id = os.getenv("PROJECT_ID")
        self.location = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
        
        if self.debug:
            print(f"Initializing PDF processor with project_id: {self.project_id}, location: {self.location}")
        
        # Initialize GCP services
        vertexai.init(project=self.project_id, location=self.location)
        self.storage_client = storage.Client.from_service_account_json(credentials_path)
        
        # Initialize the generative model for subject extraction
        self.model = GenerativeModel(model_name="gemini-1.5-pro-001")

    def get_pdf_from_bucket(self, bucket_name: str, blob_name: str) -> Optional[io.BytesIO]:
        """Get a PDF from GCS bucket as a BytesIO object without downloading to disk"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Download blob to memory
            pdf_bytes = io.BytesIO()
            blob.download_to_file(pdf_bytes)
            pdf_bytes.seek(0)  # Reset pointer to beginning of file
            
            if self.debug:
                print(f"Downloaded {blob_name} to memory")
                
            return pdf_bytes
        except Exception as e:
            print(f"Error getting PDF from bucket: {str(e)}")
            return None

    def save_json_to_bucket(self, bucket_name: str, blob_name: str, data: Dict[str, Any]) -> bool:
        """Save JSON data to GCS bucket"""
        try:
            # Create a JSON file name based on PDF name
            json_blob_name = blob_name.rsplit('.', 1)[0] + '.json'
            
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(json_blob_name)
            
            # Convert dict to JSON string and encode as bytes
            json_bytes = json.dumps(data, indent=2).encode('utf-8')
            
            # Upload to GCS
            blob.upload_from_string(json_bytes, content_type='application/json')
            
            if self.debug:
                print(f"Uploaded results to {bucket_name}/{json_blob_name}")
                
            return True
        except Exception as e:
            print(f"Error saving JSON to bucket: {str(e)}")
            return False

    def extract_text_from_pdf(self, pdf_bytes: io.BytesIO) -> str:
        """Extract text content from a PDF file using PyPDF2"""
        try:
            text_content = ""
            pdf_reader = PyPDF2.PdfReader(pdf_bytes)
            
            # Get total pages and process them all
            total_pages = len(pdf_reader.pages)
            
            if self.debug:
                print(f"Extracting text from {total_pages} pages")
            
            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n\n"
            
            if self.debug:
                print(f"Extracted {len(text_content)} characters from PDF")
                
            return text_content
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return ""

    def identify_key_subjects(self, text_content: str, num_subjects: int = 5) -> List[Dict[str, Any]]:
        """Use Gemini to identify exactly 5 key subjects from the extracted text"""
        try:
            prompt = f"""
            Extract exactly {num_subjects} key subjects from the following text content from a PDF document.
            Identify the most important topics, concepts, methodologies, findings, or entities.
            
            Format your response as a JSON array with exactly {num_subjects} subjects, each having the following structure:
            {{
                "subject": "The subject name/term",
                "importance_score": A number between 0 and 1 indicating importance (where 1 is most important),
                "context": "Brief description or context about this subject based on the document",
                "category": "The category this subject belongs to (e.g., 'methodology', 'finding', 'technology', 'organization', 'person', 'concept')"
            }}
            
            Return only the JSON array with no additional text or explanation.
            
            TEXT CONTENT:
            {text_content[:50000]}  # Use a larger portion of text to ensure good coverage
            """
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]  # Remove ```json and ```
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]  # Remove ``` and ```
                
            response_text = response_text.strip()
            
            try:
                subjects_data = json.loads(response_text)
                
                # Ensure we have a list
                if isinstance(subjects_data, dict) and "subjects" in subjects_data:
                    subjects = subjects_data["subjects"]
                elif isinstance(subjects_data, list):
                    subjects = subjects_data
                else:
                    subjects = [subjects_data]  # Convert to list if it's a single object
                
                # Ensure we have exactly the requested number of subjects
                subjects = subjects[:num_subjects]
                
                if self.debug:
                    print(f"Extracted {len(subjects)} key subjects")
                    
                return subjects
            except json.JSONDecodeError as e:
                print(f"Error parsing subjects JSON: {str(e)}")
                return []
                
        except Exception as e:
            print(f"Error identifying key subjects: {str(e)}")
            return []

    def subject_exists_in_database(self, subject: str) -> bool:
        """Check if a subject already exists in the database
        This is a placeholder function that should be replaced with actual database integration
        """
        # TODO: Implement actual database query to check if subject exists
        if self.debug:
            print(f"Checking if subject '{subject}' exists in database")
        
        # For demonstration, return False (simulating new subject)
        return False

    def add_subject_to_database(self, subject_data: Dict[str, Any]) -> bool:
        """Add a new subject to the database
        This is a placeholder function that should be replaced with actual database integration
        """
        # TODO: Implement actual database insertion
        if self.debug:
            print(f"Adding subject '{subject_data['subject']}' to database")
        
        # For demonstration, return True (simulating successful insertion)
        return True

    def process_pdf(self, bucket_name: str, pdf_blob_name: str) -> Dict[str, Any]:
        """Process a PDF file from GCS, extract text, identify subjects, and update database"""
        results = {
            "pdf_name": pdf_blob_name,
            "success": False,
            "text_extracted": False,
            "subjects": [],
            "new_subjects_added": 0,
            "error": None
        }
        
        try:
            # Get the PDF directly from GCS bucket without downloading to disk
            pdf_bytes = self.get_pdf_from_bucket(bucket_name, pdf_blob_name)
            if not pdf_bytes:
                results["error"] = "Failed to get PDF from bucket"
                return results
                
            # Extract text from PDF
            text_content = self.extract_text_from_pdf(pdf_bytes)
            if not text_content:
                results["error"] = "Failed to extract text from PDF"
                return results
                
            results["text_extracted"] = True
                
            # Identify exactly 5 key subjects from the text
            subjects = self.identify_key_subjects(text_content, num_subjects=5)
            results["subjects"] = subjects
            
            # Check each subject against database and add if new
            new_subjects = 0
            for subject_data in subjects:
                # Make sure subject_data has all required fields
                if not isinstance(subject_data, dict) or "subject" not in subject_data:
                    continue
                    
                subject_name = subject_data["subject"]
                if not self.subject_exists_in_database(subject_name):
                    if self.add_subject_to_database(subject_data):
                        new_subjects += 1
                        
            results["new_subjects_added"] = new_subjects
            results["success"] = True
            
            # Save results to GCS bucket
            self.save_json_to_bucket(bucket_name, pdf_blob_name, results)
            
            return results
            
        except Exception as e:
            results["error"] = str(e)
            
            # Try to save error results to GCS bucket too
            try:
                self.save_json_to_bucket(bucket_name, pdf_blob_name, results)
            except:
                pass
                
            return results

def main():
    """Main function to demonstrate PDF processing"""
    # Initialize processor
    credentials_path = 'genaigenesis-454500-2b74084564ba.json'
    processor = PDFProcessor(debug=True, credentials_path=credentials_path)
    
    # Example usage with a GCS bucket and PDF
    bucket_name = "educatorgenai"
    pdf_blob_name = "katzman-et-al-2024-deep-learning-for-pneumothorax-detection-on-chest-radiograph-a-diagnostic-test-accuracy-systematic.pdf"
    
    results = processor.process_pdf(bucket_name, pdf_blob_name)
    
    # Print a summary of the results
    print(f"\nSummary:")
    print(f"PDF: {results['pdf_name']}")
    print(f"Success: {results['success']}")
    print(f"Text Extracted: {results['text_extracted']}")
    print(f"Subjects found: {len(results['subjects'])}")
    print(f"New subjects added: {results['new_subjects_added']}")
    
    if results.get('error'):
        print(f"Error: {results['error']}")
    
    print("\nKey Subjects:")
    for i, subject in enumerate(results.get('subjects', []), 1):
        print(f"{i}. {subject.get('subject', 'Unknown')} ({subject.get('category', 'Unknown')}) - "
              f"Importance: {subject.get('importance_score', 0)}")
        print(f"   Context: {subject.get('context', 'No context')[:100]}...")
        
    # Print where results were saved
    json_blob_name = pdf_blob_name.rsplit('.', 1)[0] + '.json'
    print(f"\nResults saved to: gs://{bucket_name}/{json_blob_name}")

if __name__ == "__main__":
    main()

