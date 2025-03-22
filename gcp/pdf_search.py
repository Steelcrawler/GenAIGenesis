import os
from typing import Optional, List, Tuple
from dotenv import load_dotenv
from google.cloud import storage
import io
import json
from PyPDF2 import PdfReader
import RAGtesting
from difflib import SequenceMatcher

def similar(a: str, b: str, threshold: float = 0.6) -> bool:
    """Check if two strings are similar using SequenceMatcher"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() > threshold

class PDFSearcher:
    def __init__(self, credentials_path: Optional[str] = None, debug: bool = False):
        """Initialize the PDF searcher"""
        self.debug = debug
        env_path = '../.env'
        load_dotenv(dotenv_path=env_path)
        
        # Initialize GCS client with credentials
        if credentials_path:
            self.storage_client = storage.Client.from_service_account_json(credentials_path)
        else:
            self.storage_client = storage.Client()

    def get_pdf_text(self, bucket_name: str, file_path: str) -> Optional[List[str]]:
        """Get text content from a PDF file in GCS, returning a list of pages"""
        try:
            print(f"\nAttempting to get text from: gs://{bucket_name}/{file_path}")
            
            # Get bucket
            print("Getting bucket...")
            bucket = self.storage_client.bucket(bucket_name)
            
            # Get blob
            print("Getting blob...")
            blob = bucket.blob(file_path)
            
            # Check if blob exists
            print("Checking if blob exists...")
            if not blob.exists():
                print(f"Error: File does not exist at gs://{bucket_name}/{file_path}")
                return None
            
            # Download PDF as bytes
            print("Downloading PDF content...")
            pdf_bytes = blob.download_as_bytes()
            print(f"Successfully downloaded PDF. Size: {len(pdf_bytes)} bytes")
            
            # Process PDF with PyPDF2
            print("Processing PDF with PyPDF2...")
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            
            # Extract text from each page separately
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text.strip():  # Only add non-empty pages
                    pages.append(text)
            
            print(f"Successfully extracted text from {len(pages)} pages")
            return pages
            
        except Exception as e:
            error_msg = str(e)
            print(f"\nError getting PDF text: {error_msg}")
            if "billing account" in error_msg.lower():
                print("\nGCP Billing Account Issue:")
                print("1. Go to GCP Console > Billing")
                print("2. Enable billing for your project")
                print("3. Link a billing account to your project")
                print("4. Ensure your service account has the necessary permissions")
            return None

    def find_text_in_pdf(self, bucket_name: str, file_path: str, search_text: str) -> List[Tuple[int, str]]:
        """Find text in PDF and return list of (page_number, context) tuples"""
        try:
            # Get the PDF text as a list of pages
            pages = self.get_pdf_text(bucket_name, file_path)
            if not pages:
                return []
            
            results = []
            for page_num, page_text in enumerate(pages, 1):
                # Split page into sentences for better matching
                sentences = [s.strip() for s in page_text.split('.') if s.strip()]
                
                # Look for similar sentences
                for sentence in sentences:
                    if similar(sentence, search_text):
                        # Get context around the matching sentence
                        context_start = max(0, page_text.find(sentence) - 100)
                        context_end = min(len(page_text), page_text.find(sentence) + len(sentence) + 100)
                        context = page_text[context_start:context_end]
                        
                        results.append((page_num, context))
                        break  # Found a match in this page, move to next page
            
            return results
            
        except Exception as e:
            print(f"Error searching PDF: {str(e)}")
            return []

def process_quiz_response(response: dict, bucket_name: str, searcher: PDFSearcher) -> dict:
    """Process a quiz response and find its source in PDF. Returns a dictionary with question info and page numbers."""
    try:
        # Get the source information
        source = response.get('source', {})
        document_name = source.get('document_name')
        content = source.get('content')
        
        if not document_name or not content:
            print("No source information found in response")
            return {}
        
        print(f"\nQuestion: {response.get('question')}")
        print(f"Answer: {response.get('answer')}")
        print(f"\nSearching for source in document: {document_name}")
        print(f"Source content: {content[:100]}...")
        
        # Search in the PDF
        results = searcher.find_text_in_pdf(bucket_name, document_name, content)
        
        # Create result dictionary
        result_dict = {
            'question': response.get('question'),
            'answer': response.get('answer'),
            'document': document_name,
            'pages': []
        }
        
        if results:
            print("\nFound matches:")
            for page_num, context in results:
                print(f"\nPage {page_num}:")
                print(f"Context: {context}")
                result_dict['pages'].append(page_num)
        else:
            print("\nNo matches found in the PDF")
            
        return result_dict
            
    except Exception as e:
        print(f"Error processing quiz response: {str(e)}")
        return {}

def main():
    # Initialize with credentials
    bucket_name = "educatorgenai"
    credentials_path = 'genaigenesis-454500-2b74084564ba.json'
    
    # Set up RAG
    rag = RAGtesting.SimpleRAG(credentials_path=credentials_path, debug=True)
    selected_files = rag.list_gcs_files(bucket_name)
    
    if not selected_files:
        print("\nNo files found in the bucket. Please check if:")
        print("1. The bucket name is correct")
        print("2. The files are in the correct location")
        print("3. You have proper permissions to list files")
        return
        
    corpus_id = rag.setup_corpus(bucket_name, selected_files)
    if not corpus_id:
        print("\nFailed to create corpus. Please check your GCP setup.")
        return
        
    model = rag.setup_model(corpus_id)
    
    # Generate quiz
    print("\nGenerating quiz...")
    response = rag.generate_response("", model)
    print("\nGenerated Quiz:")
    print(response)
    
    # Parse the JSON response
    try:
        if isinstance(response, str):
            response = json.loads(response)
    except json.JSONDecodeError as e:
        print(f"\nError parsing JSON response: {str(e)}")
        return
    
    # Initialize PDF searcher
    searcher = PDFSearcher(credentials_path=credentials_path, debug=True)
    
    # Process each quiz question and find its source
    print("\nFinding sources in PDFs...")
    quiz_results = {}
    
    if isinstance(response, list):
        for i, resp in enumerate(response, 1):
            result = process_quiz_response(resp, bucket_name, searcher)
            if result:
                quiz_results[f"Question {i}"] = result
    else:
        result = process_quiz_response(response, bucket_name, searcher)
        if result:
            quiz_results["Question 1"] = result
    
    # Print the final results dictionary
    print("\nQuiz Results Summary:")
    print(json.dumps(quiz_results, indent=2))
    
    # Clean up
    try:
        rag.delete_corpus(corpus_id)
        print("\nCorpus deleted successfully")
    except Exception as e:
        print(f"\nWarning: Could not delete corpus: {str(e)}")
    
    return quiz_results

if __name__ == "__main__":
    main() 