import os
from typing import Optional, List
from dotenv import load_dotenv
import vertexai
from vertexai.preview import rag
from vertexai.preview.rag import RagCorpus
from vertexai.preview.generative_models import GenerativeModel, Tool
from pathlib import Path
import json
import time
from google.cloud import storage
from google.auth import default
import uuid


class QuizMakerRAG:
    def __init__(self, credentials_path: Optional[str] = None, debug: bool = False):
        """Initialize the RAG model"""
        self.debug = debug
        env_path = './.env'
        load_dotenv(dotenv_path=env_path)
        
        self.project_id = "genaigenesis-454500" # os.getenv("PROJECT_ID")
        self.location = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
        
        if self.debug:
            print(f"Initializing RAG model with project_id: {self.project_id}, location: {self.location}")
        
        # Get default credentials
        try:
            self.credentials, project = default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
            if self.debug:
                print(f"Using default credentials with project: {project}")
        except Exception as e:
            if self.debug:
                print(f"Failed to get default credentials: {e}")
            # Fallback to service account if provided
            if credentials_path:
                if self.debug:
                    print(f"Falling back to service account credentials: {credentials_path}")
                self.credentials = None
                self.storage_client = storage.Client.from_service_account_json(credentials_path)
            else:
                raise Exception("No credentials available")
        
        # Initialize clients with default credentials if available
        if hasattr(self, 'credentials') and self.credentials:
            self.storage_client = storage.Client(credentials=self.credentials, project=self.project_id)
            vertexai.init(project=self.project_id, location=self.location, credentials=self.credentials)
        else:
            vertexai.init(project=self.project_id, location=self.location)

    def list_gcs_files(self, bucket_name: str, prefix: str = "") -> List[str]:
        """List all files in a GCS bucket with given prefix"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            files = [blob.name for blob in blobs if blob.name.endswith(('.pdf', '.txt', '.doc', '.docx'))]
            return files
        except Exception as e:
            print(f"Error listing GCS files: {str(e)}")
            return []

    def setup_corpus(self, bucket_name: str, data_list: List[dict]) -> Optional[str]:
        """Set up the RAG corpus from selected files in GCS bucket"""
        try:
            if self.debug:
                print(f"\nSetting up corpus with {len(data_list)} data entries:")
                for i, data in enumerate(data_list, 1):
                    print(f"\nEntry {i}:")
                    print(f"  ID: {data.get('id', 'N/A')}")
                    print(f"  Snippet: {data.get('snippet', 'N/A')[:100]}...")
                    print(f"  Counter: {data.get('comment_helper_counter', 'N/A')}")

            embedding_model_config = rag.EmbeddingModelConfig(
                publisher_model=f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/text-embedding-005"
            )
            
            if self.debug:
                print(f"\nCreating corpus with embedding model: {embedding_model_config.publisher_model}")
            
            # Create corpus
            corpus = rag.create_corpus(
                display_name="simple-rag-corpus",
                embedding_model_config=embedding_model_config
            )

            if self.debug:
                print(f"\nCorpus created successfully:")
                print(f"  Corpus ID: {corpus.name}")
                print(f"  Display Name: {corpus.display_name}")
            
            # Create full GCS paths for selected files
            timestamp = int(time.time())
            file_path = f'temp_file_{timestamp}.json'
            path = f"gs://{bucket_name}/{file_path}"
            
            if self.debug:
                print(f"\nPreparing temporary file:")
                print(f"  Local path: {file_path}")
                print(f"  GCS path: {path}")
            
            with open(file_path, 'w') as f:
                json.dump(data_list, f)
                
            if self.debug:
                print(f"\nTemporary file created. Size: {os.path.getsize(file_path)} bytes")
                print("First few entries in the file:")
                with open(file_path, 'r') as f:
                    file_content = json.load(f)
                    for i, entry in enumerate(file_content[:3], 1):
                        print(f"\nEntry {i}:")
                        print(f"  ID: {entry.get('id', 'N/A')}")
                        print(f"  Snippet: {entry.get('snippet', 'N/A')[:100]}...")
                
            if self.debug:
                print(f"\nUploading file to corpus: {corpus.name}")
            
            rag.upload_file(
                corpus_name=corpus.name,
                path=file_path,
            )
            
            try:
                os.remove(file_path)
                if self.debug:
                    print(f"\nTemporary file deleted: {file_path}")
            except Exception as e:
                if self.debug:
                    print(f"\nWarning: Could not delete temporary file {file_path}")
                    print(f"Error: {e}")

            # List files to verify import
            files = list(rag.list_files(corpus.name))  # Convert pager to list
            if self.debug:
                print(f"\nFiles in corpus:")
                for file in files:
                    print(f"  - {file}")
                print(f"\nTotal files in corpus: {len(files)}")
            
            return corpus.name

        except Exception as e:
            print(f"\nError setting up corpus: {str(e)}")
            return None

    def setup_model(self, corpus_name: str) -> GenerativeModel:
        """Set up the model with RAG capability"""
        if self.debug:
            print(f"\nSetting up model with corpus: {corpus_name}")
            print("Creating RAG retrieval tool with parameters:")
            print("  - Similarity top k: 10")
            print("  - Vector distance threshold: 0.8")

        # Create RAG retrieval tool with adjusted parameters
        retrieval_tool = Tool.from_retrieval(
            retrieval=rag.Retrieval(
                source=rag.VertexRagStore(
                    rag_corpora=[corpus_name],
                    similarity_top_k=10,  
                    vector_distance_threshold=0.8,  # Adjusted threshold
                ),
            )
        )

        if self.debug:
            print("\nCreating model with RAG tool")
            print("  Model name: gemini-2.0-flash-001")

        # Create model with RAG tool
        return GenerativeModel(
            model_name="gemini-2.0-flash-001",
            tools=[retrieval_tool]
        )

    def generate_response(self, query: str, model: GenerativeModel, quiz_length: int) -> str:
        """Generate a response using RAG"""
        try:
            if self.debug:
                print(f"\nGenerating quiz with length: {quiz_length}")
                print("Prompt template:")
                print("  - Creating one question per entry")
                print("  - Multiple choice format (4 options)")
                print("  - Including snippet_id reference")

            # First, verify we can access the corpus data
            if self.debug:
                print("\nVerifying corpus access...")
            
            test_response = model.generate_content("What are the main topics in the provided data? List them briefly.")
            if self.debug:
                print("\nTest response received:")
                print(test_response.text[:200] + "..." if len(test_response.text) > 200 else test_response.text)

            prompt = f"""
            Your task is to create multiple-choice questions based on this data.

            Requirements:
            1. Create exactly one question for each entry in the data ({quiz_length} total questions)
            2. Each question must be multiple choice with exactly 4 options
            3. Each question must have exactly one correct answer
            4. Reference the entry's ID in the snippet_id field
            5. Make questions challenging but fair
            6. Ensure all options are plausible
            7. Avoid obvious patterns in correct answer positions

            Example of the expected response format:
            [
                {{
                    "snippet_id": "123e4567-e89b-12d3-a456-426614174000",
                    "question": "How has technology impacted global interactions?",
                    "choices": [
                        "It has completely eliminated face-to-face communication",
                        "It has dramatically reshaped how we interact with the world",
                        "It has had no significant impact on communication",
                        "It has only affected business communications"
                    ],
                    "answer_index": 1
                }}
            ]

            Important:
            - Your response MUST be a valid JSON array
            - Create exactly one question per entry
            - Make questions test understanding, not just memorization
            - Ensure all options are reasonable
            - Vary the position of correct answers
            - Keep questions clear and concise
            - Use the exact snippet_id from the data
            """
                        
            if self.debug:
                print("\nGenerating questions from model...")
            
            response = model.generate_content(prompt)
            
            if self.debug:
                print("\nRaw response received from model")
            
            # Clean the response text by removing markdown code fences if present
            cleaned_response = response.text.strip()
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response.split('```')[1]
            if cleaned_response.startswith('json'):
                cleaned_response = cleaned_response[4:]
            cleaned_response = cleaned_response.strip()
            
            if self.debug:
                print("\nCleaned response:")
                print(cleaned_response[:200] + "..." if len(cleaned_response) > 200 else cleaned_response)
            
            # Try to parse as JSON to validate
            try:
                parsed_json = json.loads(cleaned_response)
                if self.debug:
                    print(f"\nResponse successfully validated as JSON")
                    print(f"Number of questions generated: {len(parsed_json)}")
                return cleaned_response
            except json.JSONDecodeError as e:
                if self.debug:
                    print(f"\nError: Response was not valid JSON")
                    print(f"JSON Error: {str(e)}")
                return f"Error: Response was not valid JSON: {cleaned_response}"
                
        except Exception as e:
            print(f"\nError generating response: {str(e)}")
            raise

    def list_corpora(self):
        """List all RAG corpora"""
        return rag.list_corpora()

    def list_files(self, corpus_name: str):
        """List files in a specific RAG corpus"""
        try:
            files = list(rag.list_files(corpus_name))  # Convert pager to list
            if self.debug:
                print(f"\nFiles in corpus {corpus_name}:")
                for file in files:
                    print(f"  - {file}")
                print(f"Total files: {len(files)}")
            return files
        except Exception as e:
            print(f"\nError listing files: {str(e)}")
            return []

    def delete_corpus(self, corpus_name: str):
        """Delete a specific RAG corpus"""
        try:
            if not corpus_name:
                if self.debug:
                    print("\nNo corpus name provided for deletion")
                return
                
            if self.debug:
                print(f"\nAttempting to delete corpus: {corpus_name}")
            
            rag.delete_corpus(corpus_name)
            if self.debug:
                print("Corpus deleted successfully")
        except Exception as e:
            print(f"\nError deleting corpus {corpus_name}: {str(e)}")

def select_files(files: List[str]) -> List[str]:
    """Let user select files from the list"""
    print("\nAvailable files:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    
    while True:
        try:
            selection = input("\nEnter the numbers of files to include (comma-separated) or 'all' for all files: ").strip()
            if selection.lower() == 'all':
                return files
            
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_files = [files[i] for i in indices]
            return selected_files
        except (ValueError, IndexError):
            print("Invalid selection. Please try again.")

def main():
    debug_mode = True  # Set debug mode to True
    
    # Try to use default credentials first
    try:
        rag = QuizMakerRAG(debug=debug_mode)
        print("\nUsing default credentials")
    except Exception as e:
        print(f"\nFalling back to service account: {e}")
        rag = QuizMakerRAG(credentials_path='genaigenesis-454500-2b74084564ba.json', debug=debug_mode)

    bucket_name = "educatorgenai"
    print("\nInitializing QuizMakerRAG with debug mode enabled")
    print(f"Project ID: {rag.project_id}")
    print(f"Location: {rag.location}")
    
    print("\nCreating mock data for testing...")
    mock_data = [
        {
            "id": str(uuid.uuid4()),
            "snippet": "The evolution of technology has dramatically reshaped how we interact with the world.",
            "comment_helper_counter": 1,
        },
        {
            "id": str(uuid.uuid4()),
            "snippet": "Artificial Intelligence is rapidly advancing, opening up new opportunities across various sectors.",
            "comment_helper_counter": 2,
        },
        {
            "id": str(uuid.uuid4()),
            "snippet": "Renewable energy solutions are becoming essential as the world shifts towards sustainability.",
            "comment_helper_counter": 3,
        },
        {
            "id": str(uuid.uuid4()),
            "snippet": "Space exploration is taking a leap forward with commercial ventures leading the charge.",
            "comment_helper_counter": 4,
        },
        {
            "id": str(uuid.uuid4()),
            "snippet": "The digital economy is transforming traditional business models across the globe.",
            "comment_helper_counter": 5,
        },
        {
            "id": str(uuid.uuid4()),
            "snippet": "Healthcare innovations, especially in biotechnology, are significantly improving patient care.",
            "comment_helper_counter": 6,
        },
        {
            "id": str(uuid.uuid4()),
            "snippet": "Data privacy remains a critical concern as more personal information is shared online.",
            "comment_helper_counter": 7,
        },
        {
            "id": str(uuid.uuid4()),
            "snippet": "Environmental conservation efforts are increasingly crucial to combat climate change.",
            "comment_helper_counter": 8,
        },
        {
            "id": str(uuid.uuid4()),
            "snippet": "Advancements in education technology are reshaping how students learn and teachers instruct.",
            "comment_helper_counter": 9,
        },
        {
            "id": str(uuid.uuid4()),
            "snippet": "Remote work and digital communication tools are defining the future of the workplace.",
            "comment_helper_counter": 10,
        }
    ]
    
    print(f"\nCreated {len(mock_data)} mock entries")
    corpus_id = rag.setup_corpus(bucket_name=bucket_name, data_list=mock_data)

    if corpus_id:
        print("\nSetting up model with RAG capability...")
        model = rag.setup_model(corpus_id)
        
        print("\nGenerating quiz based on the corpus...")
        response = rag.generate_response("", model, quiz_length=10)
        print(f"\nQuiz: {response}")
    
    try:
        print("\nCleaning up - deleting corpus...")
        rag.delete_corpus(corpus_id)
    except Exception as e:
        print(f"\nError during cleanup: {str(e)}")

if __name__ == "__main__":
    main()


        
