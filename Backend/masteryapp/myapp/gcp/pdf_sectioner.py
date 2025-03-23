import os
import tempfile
import uuid
import io
import re
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
        self.credentials_path = credentials_path
        env_path = '../.env'
        load_dotenv(dotenv_path=env_path)
        
        self.project_id = "genaigenesis-454500" # os.getenv("PROJECT_ID")
        self.location = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
        
        if self.debug:
            print(f"Initializing PDF processor with project_id: {self.project_id}, location: {self.location}")
        
        # Initialize GCP services
        vertexai.init(project=self.project_id, location=self.location)
        
        # Initialize storage client
        try:
            if credentials_path and os.path.exists(credentials_path):
                if self.debug:
                    print(f"Using service account credentials from: {credentials_path}")
                self.storage_client = storage.Client.from_service_account_json(credentials_path)
            else:
                if self.debug:
                    print("Using Application Default Credentials")
                self.storage_client = storage.Client()
                
            if self.debug:
                print("Storage client initialized successfully")
        except Exception as e:
            print(f"Error initializing storage client: {str(e)}")
            self.storage_client = None
            raise
        
        # Initialize the generative model for subject extraction
        self.model = GenerativeModel(model_name="gemini-1.5-flash-001")

    def get_pdf_from_bucket(self, bucket_name: str, user_id: str, course_id: str, file_name: str) -> Optional[io.BytesIO]:
        """Get a PDF from GCS bucket as a BytesIO object without downloading to disk
        
        Args:
            bucket_name: The GCS bucket name
            user_id: User ID or folder name where files are organized
            course_id: Course ID or folder name where files are organized
            file_name: Name of the PDF file stored in GCS
            
        Returns:
            Optional[io.BytesIO]: BytesIO object containing the PDF data, or None if an error occurs
        """
        try:
            # Construct the full blob path
            blob_path = f"{user_id}/{course_id}/{file_name}"
            
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            
            # Download blob to memory
            pdf_bytes = io.BytesIO()
            blob.download_to_file(pdf_bytes)
            pdf_bytes.seek(0)  # Reset pointer to beginning of file
            
            if self.debug:
                print(f"Downloaded {blob_path} to memory")
                
            return pdf_bytes
        except Exception as e:
            print(f"Error getting PDF from bucket: {str(e)}")
            return None

    def save_json_to_bucket(self, bucket_name: str, user_id: str, course_id: str, file_name: str, data: Dict[str, Any]) -> bool:
        """Save JSON data to GCS bucket
        
        Args:
            bucket_name: The GCS bucket name
            user_id: User ID or folder name where files are organized
            course_id: Course ID or folder name where files are organized
            file_name: Name of the PDF file stored in GCS (will be used to create JSON filename)
            data: Dictionary containing the data to save as JSON
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a JSON file name based on PDF name
            json_file_name = file_name.rsplit('.', 1)[0] + '.json'
            json_blob_path = f"{user_id}/{course_id}/{json_file_name}"
            
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(json_blob_path)
            
            # Convert dict to JSON string and encode as bytes
            json_bytes = json.dumps(data, indent=2).encode('utf-8')
            
            # Upload to GCS
            blob.upload_from_string(json_bytes, content_type='application/json')
            
            if self.debug:
                print(f"Uploaded results to {bucket_name}/{json_blob_path}")
                
            return True
        except Exception as e:
            print(f"Error saving JSON to bucket: {str(e)}")
            return False

    def extract_text_from_pdf(self, pdf_bytes: io.BytesIO) -> str:
        """Extract text content from a PDF file using Gemini, handling malformed PDFs with missing EOF markers"""
        try:
            # First try to create a PDF reader with the provided bytes
            try:
                pdf_reader = PyPDF2.PdfReader(pdf_bytes)
            except Exception as pdf_error:
                if self.debug:
                    print(f"Error initializing PDF reader: {str(pdf_error)}. Attempting to repair.")
                
                # Try to repair the PDF by ensuring it has an EOF marker
                pdf_bytes.seek(0)
                pdf_content = pdf_bytes.read()
                
                # Check if the PDF is missing the EOF marker (%%EOF)
                if not pdf_content.rstrip().endswith(b'%%EOF'):
                    if self.debug:
                        print("Detected missing EOF marker, attempting to repair")
                    
                    # Add the EOF marker
                    repaired_content = pdf_content + b'\n%%EOF\n'
                    
                    # Create a new BytesIO object with the repaired content
                    repaired_pdf = io.BytesIO(repaired_content)
                    try:
                        pdf_reader = PyPDF2.PdfReader(repaired_pdf)
                        if self.debug:
                            print("Successfully repaired and loaded PDF")
                    except Exception as repair_error:
                        if self.debug:
                            print(f"Failed to repair PDF: {str(repair_error)}")
                        return ""  # Return empty string if we can't repair it
                else:
                    # If it's not an EOF issue, re-raise the exception
                    if self.debug:
                        print("PDF has an EOF marker but still can't be read properly")
                    return ""
            
            total_pages = len(pdf_reader.pages)
            
            if self.debug:
                print(f"Extracting text from {total_pages} pages")
            
            # Extract text from all pages at once
            raw_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    raw_text += page_text + "\n\n"
                except Exception as page_error:
                    if self.debug:
                        print(f"Error extracting text from page {page_num + 1}: {str(page_error)}")
                    # Continue with other pages even if one fails
                    continue
            
            if not raw_text.strip():
                if self.debug:
                    print("No text could be extracted from PDF")
                return ""
            
            if self.debug:
                print(f"Extracted {len(raw_text)} characters, processing with LLM")
            
            # Process the entire text with LLM at once
            prompt = """Clean and structure this raw text extracted from a PDF document.
            Fix any formatting issues while:
            1. Preserving paragraph structure and flow
            2. Maintaining complete sentences and context
            3. Removing artifacts and noise
            4. Ensuring proper spacing between sections
            5. Keeping the document's logical structure
            6. Remove stay new lines and whitespace
            
            Return only the cleaned text, with no additional commentary or formatting.
            
            Raw text:
            """ + raw_text
            
            try:
                response = self.model.generate_content(prompt)
                cleaned_text = response.text.strip()
                
                # Remove any markdown formatting if present
                if cleaned_text.startswith('```'):
                    cleaned_text = cleaned_text.split('```')[1]
                    if cleaned_text.startswith('text'):
                        cleaned_text = cleaned_text[4:]
                cleaned_text = cleaned_text.strip()
                
                if self.debug:
                    print(f"Processed {len(cleaned_text)} characters of text")
                
                return cleaned_text if cleaned_text else raw_text
                
            except Exception as e:
                if self.debug:
                    print(f"Error processing text with LLM: {str(e)}")
                # If LLM fails, return the raw text as fallback
                return raw_text.strip()
            
        except Exception as e:
            if self.debug:
                print(f"Error extracting text from PDF: {str(e)}")
            return ""

    def identify_key_subjects(self, text_content: str, existing_subjects: List[str] = None) -> List[Dict[str, Any]]:
        """Use Gemini to identify key subjects from the extracted text, optionally including existing subjects"""
        try:
            existing_subjects_text = ""
            if existing_subjects and len(existing_subjects) > 0:
                existing_subjects_text = f"""
                Additionally, make sure to include the following subjects if they are relevant to the document:
                {', '.join(existing_subjects)}
                """
            
            prompt = f"""
            Extract key subjects (ONLY THE MOST IMPORTANT ONES) from the following text content from a PDF document.
            Analyze the entire document to identify the most important topics and concepts.
            The subjects should be the main topics of the document. (theoretical, not practical)
            {existing_subjects_text}
            
            You should, very rarely, be adding more subjects than what is already provided, unless nothing else is relevant. 
            SUBJECTS MUST BE AT MOST 3 WORDS.
            Format your response as a JSON array, each having the following structure:
            {{
                "subject": "The subject name/term",
                "context": "Brief description or context about this subject based on the document"
            }}
            
            Return only the JSON array with no additional text or explanation.
            {text_content}
            """
            
            response = self.model.generate_content(prompt)
            
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]  # Remove ```json and ```
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]  # Remove ``` and ```
                
            response_text = response_text.strip()
            
            try:
                subjects_data = json.loads(response_text)
                print(subjects_data)
                
                # Ensure we have a list
                if isinstance(subjects_data, dict) and "subjects" in subjects_data:
                    subjects = subjects_data["subjects"]
                elif isinstance(subjects_data, list):
                    subjects = subjects_data
                else:
                    subjects = [subjects_data]  
                
                if self.debug:
                    print(f"Extracted {len(subjects)} key subjects")
                    
                return subjects
            except json.JSONDecodeError as e:
                print(f"Error parsing subjects JSON: {str(e)}")
                return []
                
        except Exception as e:
            print(f"Error identifying key subjects: {str(e)}")
            return []

    def partition_text_by_subjects(self, text_content: str, subjects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Partition the entire PDF text into sections relevant to each key subject"""
        try:
            if not subjects:
                return []
                
            # Extract subject names for processing
            subject_names = [subject["subject"] for subject in subjects if isinstance(subject, dict) and "subject" in subject]
            
            if not subject_names:
                return []
            
            if self.debug:
                print(f"Processing document ({len(text_content)} chars) for {len(subject_names)} subjects")
            
            all_results = []
            
            # Process each subject
            for subject in subject_names:
                try:
                    prompt = f"""Given the following text content, extract all sections that are relevant to the subject: "{subject}"

                    Requirements:
                    1. Extract COMPLETE PARAGRAPHS or substantial blocks of text that discuss the subject in depth.
                    2. Each text section should be comprehensive and self-contained, explaining a complete thought or concept.
                    3. DO NOT break up related sentences into tiny fragments - keep related concepts together in a single text section.
                    4. The text must contain full sentences and provide substantial information (at least 2-3 sentences when possible).
                    5. Maintain the original context and meaning of the content.
                    6. If no relevant text is found, return an empty array []
                    7. YOU CANNOT, MUST NOT include exercises, questions, or exam problems (so no random numbers).
                    8. Do not include any commentary, formatting markers, or explanations outside the JSON structure.
                    NO QUESTIONS NO QUESTIONS NO QUESTIONS NO EXERCISES NO EXERCISES NO EXERCISES

                    Return the text as a JSON array of objects, each having the following structure:
                    [
                        {{
                            "text": "A complete paragraph or substantive block of text about the subject that includes multiple related sentences..."
                        }},
                        {{
                            "text": "Another complete section about a different aspect of the subject with full context..."
                        }}
                    ]
                    
                    IMPORTANT: DO NOT fragment the text into tiny pieces. Keep related sentences together in cohesive sections.
                    It is MISSION CRITICAL that you return ONLY the JSON array with no additional text.
                    
                    Text content:
                    {text_content}
                    """
                    
                    # Generate content with appropriate parameters
                    response = self.model.generate_content(
                        prompt,
                        generation_config={
                            "temperature": 0.1,
                            "top_p": 0.8,
                            "top_k": 40,
                            "max_output_tokens": 8192
                        }
                    )
                    
                    response_text = response.text.strip()
                    
                    # Extract and clean JSON
                    def extract_json(text):
                        # Remove markdown code block formatting if present
                        if text.startswith('```json'):
                            text = text[7:]
                        elif text.startswith('```'):
                            text = text[3:]
                        
                        if text.endswith('```'):
                            text = text[:-3]
                            
                        text = text.strip()
                        
                        # Handle other types of markdown formatting
                        if text.startswith('`') and text.endswith('`'):
                            text = text[1:-1].strip()
                            
                        # Handle escaped quotes and control characters
                        text = text.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
                        
                        # Ensure we have a JSON array
                        if not text.startswith('['):
                            # Try to find a JSON array in the text
                            start_idx = text.find('[')
                            end_idx = text.rfind(']') + 1
                            if start_idx >= 0 and end_idx > start_idx:
                                text = text[start_idx:end_idx]
                        
                        # Additional cleaning for multi-line code blocks
                        lines = text.split('\n')
                        cleaned_lines = []
                        skip_line = False
                        
                        for line in lines:
                            # Skip lines that just contain markdown formatting
                            if line.strip() in ('```', '```json'):
                                skip_line = True
                                continue
                                
                            # Skip lines with just backticks
                            if line.strip() == '`':
                                skip_line = True
                                continue
                                
                            if not skip_line:
                                cleaned_lines.append(line)
                            skip_line = False
                            
                        text = '\n'.join(cleaned_lines)
                        
                        # Final check to ensure we have valid JSON syntax
                        if text and not (text.startswith('[') or text.startswith('{')):
                            # Try to extract any array using regex
                            import re
                            array_matches = re.findall(r'\[(.*?)\]', text, re.DOTALL)
                            if array_matches:
                                longest_match = max(array_matches, key=len)
                                text = f"[{longest_match}]"
                        
                        return text.strip()
                    
                    # Clean and extract the JSON
                    json_text = extract_json(response_text)
                    
                    
                    # Try to parse the JSON
                    try:
                        sections = json.loads(json_text)
                        
                        # Handle the parsed data
                        if isinstance(sections, list):
                            for item in sections:
                                if isinstance(item, dict) and "text" in item:
                                    all_results.append({
                                        "subject": subject,
                                        "text": item["text"]  # Keep as "text" as requested
                                    })
                        elif isinstance(sections, dict) and "text" in sections:
                            all_results.append({
                                "subject": subject,
                                "text": sections["text"]
                            })
                            
                        if self.debug:
                            sections_count = len([r for r in all_results if r.get("subject") == subject])
                            print(f"Found {sections_count} text sections for subject: {subject}")
                            
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON for subject {subject}: {e}")
                        
                        # Check if this might be a JSON string inside the text field
                        if "```json" in response_text:
                            try:
                                # Extract JSON content from markdown code block
                                start_idx = response_text.find("```json") + 7
                                end_idx = response_text.find("```", start_idx)
                                if start_idx > 6 and end_idx > start_idx:
                                    json_content = response_text[start_idx:end_idx].strip()
                                    nested_data = json.loads(json_content)
                                    
                                    if isinstance(nested_data, list):
                                        for item in nested_data:
                                            if isinstance(item, dict) and "text" in item:
                                                all_results.append({
                                                    "subject": subject,
                                                    "text": item["text"]
                                                })
                                                
                                        # If we found items, skip to debugging output
                                        if any(r.get("subject") == subject for r in all_results):
                                            if self.debug:
                                                sections_count = len([r for r in all_results if r.get("subject") == subject])
                                                print(f"Extracted {sections_count} text sections from nested JSON for subject: {subject}")
                                            continue
                            except Exception as nested_e:
                                print(f"Error extracting nested JSON: {nested_e}")
                        
                        # Try to extract any JSON-like content from the text
                        if '[' in response_text and ']' in response_text and not any(r.get("subject") == subject for r in all_results):
                            try:
                                # Extract text between first [ and last ]
                                start_idx = response_text.find('[')
                                end_idx = response_text.rfind(']') + 1
                                if start_idx >= 0 and end_idx > start_idx:
                                    json_text = response_text[start_idx:end_idx]
                                    try:
                                        # Try to parse the extracted JSON
                                        extracted_data = json.loads(json_text)
                                        if isinstance(extracted_data, list):
                                            for item in extracted_data:
                                                if isinstance(item, dict) and "text" in item:
                                                    all_results.append({
                                                        "subject": subject,
                                                        "text": item["text"]
                                                    })
                                    except json.JSONDecodeError:
                                        # If still can't parse, try further cleanup of the content
                                        cleaned_json = re.sub(r'\\n', '\n', json_text)
                                        cleaned_json = re.sub(r'\\(.)', r'\1', cleaned_json)
                                        
                                        try:
                                            cleaned_data = json.loads(cleaned_json)
                                            if isinstance(cleaned_data, list):
                                                for item in cleaned_data:
                                                    if isinstance(item, dict) and "text" in item:
                                                        all_results.append({
                                                            "subject": subject,
                                                            "text": item["text"]
                                                        })
                                        except json.JSONDecodeError:
                                            # If still can't parse, split by newlines and look for text patterns
                                            lines = response_text.split('\n')
                                            for line in lines:
                                                line = line.strip()
                                                if '"text"' in line or "'text'" in line:
                                                    # Extract text value
                                                    text_match = re.search(r'"text"\s*:\s*"([^"]+)"', line)
                                                    if text_match:
                                                        text_value = text_match.group(1)
                                                        all_results.append({
                                                            "subject": subject,
                                                            "text": text_value
                                                        })
                            except Exception as e:
                                print(f"Error extracting JSON content: {e}")
                        
                        # If nothing was added, use paragraphs as fallback
                        if not any(r.get("subject") == subject for r in all_results):
                            # For text that looks like it contains JSON but we couldn't parse it
                            if '```json' in response_text:
                                # Try extracting all quoted strings that might be text values
                                text_matches = re.findall(r'"text"\s*:\s*"([^"]+)"', response_text)
                                for match in text_matches:
                                    if match and len(match) > 10:  # Require some minimum length
                                        all_results.append({
                                            "subject": subject,
                                            "text": match
                                        })
                            
                            # If still nothing, fall back to paragraph splitting
                            if not any(r.get("subject") == subject for r in all_results):
                                paragraphs = [p.strip() for p in re.split(r'\n\s*\n', response_text) if p.strip() 
                                            and not p.startswith('{') and not p.startswith('[')]
                                
                                for paragraph in paragraphs:
                                    if len(paragraph) > 50:  # Only include substantial paragraphs
                                        all_results.append({
                                            "subject": subject,
                                            "text": paragraph
                                        })
                        
                except Exception as e:
                    print(f"Error processing subject {subject}: {str(e)}")
            
            return all_results
                
        except Exception as e:
            print(f"Error in text partitioning: {str(e)}")
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
        
        return True

    def process_pdf(self, bucket_name: str, user_id: str, course_id: str, file_name: str, existing_subjects: List[str] = None) -> Dict[str, Any]:
        """Process a PDF file from GCS, extract text, identify subjects, and update database
        
        Args:
            bucket_name: The GCS bucket name
            user_id: User ID or folder name where files are organized
            course_id: Course ID or folder name where files are organized
            file_name: Name of the PDF file stored in GCS
            existing_subjects: Optional list of subjects to explicitly look for in the document
            
        Returns:
            Dictionary with processing results
        """
        results = {
            "pdf_name": file_name,
            "success": False,
            "text_extracted": False,
            "subjects": [],
            "partitioned_text": [],  # List to store all text sections
            "new_subjects_added": 0,
            "error": None
        }
        
        try:
            pdf_bytes = self.get_pdf_from_bucket(bucket_name, user_id, course_id, file_name)
            if not pdf_bytes:
                results["error"] = f"Failed to get PDF from bucket: {bucket_name}/{user_id}/{course_id}/{file_name}"
                return results
                
            # Extract text from PDF
            text_content = self.extract_text_from_pdf(pdf_bytes)
            if not text_content:
                results["error"] = "Failed to extract text from PDF"
                return results
                
            results["text_extracted"] = True
            
            subjects = self.identify_key_subjects(text_content, existing_subjects)
            results["subjects"] = subjects
            
            # Get text sections for all subjects
            partitioned_text = self.partition_text_by_subjects(text_content, subjects)
            
            # The partitioned_text is already a list of dictionaries with "subject" and "text" keys
            results["partitioned_text"] = partitioned_text
            
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
            self.save_json_to_bucket(bucket_name, user_id, course_id, file_name, results)
            
            return results
            
        except Exception as e:
            results["error"] = str(e)
            
            # Try to save error results to GCS bucket too
            try:
                self.save_json_to_bucket(bucket_name, user_id, course_id, file_name, results)
            except:
                pass
                
            return results

def main():
    """Main function to demonstrate PDF processing"""
    credentials_path = 'genaigenesis-454500-aaca4e6f468e.json'
    processor = PDFProcessor(debug=True, credentials_path=credentials_path)
    
    # Example usage with a GCS bucket and PDF using separate parameters
    bucket_name = "educatorgenai"
    user_id = "john"
    course_id = "cs101"
    file_name = "lec02_1_DecisionTrees_complete.pdf"
    
    # List of existing subjects we want to look for in the document
    existing_subjects = ["Decision Trees", "Classification Algorithms", "Information Gain"]
    
    # Process the PDF with our existing subjects
    print(f"\nProcessing PDF with {len(existing_subjects)} existing subjects: {', '.join(existing_subjects)}")
    results = processor.process_pdf(bucket_name, user_id, course_id, file_name, existing_subjects=existing_subjects)
    
    # Print a summary of the results
    print(f"\nSummary:")
    print(f"PDF: {user_id}/{course_id}/{results['pdf_name']}")
    print(f"Success: {results['success']}")
    print(f"Text Extracted: {results['text_extracted']}")
    print(f"Subjects found: {len(results['subjects'])}")
    print(f"Text sections found: {len(results['partitioned_text'])}")
    print(f"New subjects added: {results['new_subjects_added']}")
    
    if results.get('error'):
        print(f"Error: {results['error']}")
    
    print("\nKey Subjects with Partitioned Text:")
    for i, subject in enumerate(results.get('subjects', []), 1):
        subject_name = subject.get('subject', 'Unknown')
        # Find all text sections for this subject
        subject_sections = [
            section for section in results.get('partitioned_text', [])
            if section.get('subject') == subject_name
        ]
        
        was_existing = subject_name in existing_subjects
        status_mark = "✓" if was_existing else "+"
        
        print(f"\n{i}. {subject_name} {status_mark}")
        print(f"   Context: {subject.get('context', 'No context')[:100]}...")
        
        if subject_sections:
            print(f"   Found {len(subject_sections)} relevant text sections:")
            for j, section in enumerate(subject_sections, 1):
                text = section.get('text', '').strip()
                if text:
                    print(f"   Section {j}: {text[:150]}...")
        else:
            print("   No relevant text found for this subject")
        
    # Print where results were saved
    json_file_name = file_name.rsplit('.', 1)[0] + '.json'
    print(f"\nResults saved to: gs://{bucket_name}/{user_id}/{course_id}/{json_file_name}")
    print("\nLegend: ✓ = Subject from existing list, + = New subject found in document")

if __name__ == "__main__":
    main()