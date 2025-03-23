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
import uuid

class QuizMakerRAG:
    def __init__(self, service_account_path: Optional[str] = None, debug: bool = False):
        """Initialize the RAG model with ADC or service account credentials"""
        self.debug = debug
        self.service_account_path = service_account_path
        env_path = './.env'
        load_dotenv(dotenv_path=env_path)
        
        self.project_id = "genaigenesis-454500"
        self.location = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
        
        if self.debug:
            print(f"\nInitializing RAG model with:")
            print(f"  Project ID: {self.project_id}")
            print(f"  Location: {self.location}")
            print(f"  Credentials: {'ADC' if not service_account_path else service_account_path}")
        
        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        
        # Initialize storage client
        try:
            if service_account_path and os.path.exists(service_account_path):
                if self.debug:
                    print(f"  Using service account for storage client")
                self.storage_client = storage.Client.from_service_account_json(service_account_path)
            else:
                if self.debug:
                    print(f"  Using Application Default Credentials for storage client")
                self.storage_client = storage.Client()
                
            if self.debug:
                print("  Storage client initialized successfully")
        except Exception as e:
            print(f"Error initializing storage client: {str(e)}")
            raise

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

            # Define the embedding model configuration
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
            
            # Step 1: Create and save the temp JSON file locally
            timestamp = int(time.time())
            file_name = f'temp_file_{timestamp}.json'
            local_path = file_name
            
            if self.debug:
                print(f"\nPreparing temporary file:")
                print(f"  Local path: {local_path}")
            
            with open(local_path, 'w') as f:
                json.dump(data_list, f, default=str)
                
            if self.debug:
                print(f"\nTemporary file created. Size: {os.path.getsize(local_path)} bytes")
            
            # Step 2: Upload the file to GCS
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(file_name)
            blob.upload_from_filename(local_path)
            
            gcs_uri = f"gs://{bucket_name}/{file_name}"
            
            if self.debug:
                print(f"\nUploaded file to GCS: {gcs_uri}")
            
            # Step 3: Import from GCS to RAG corpus - matching the working example
            if self.debug:
                print(f"\nImporting file from GCS to corpus...")
            
            rag.import_files(
                corpus_name=corpus.name,
                paths=[gcs_uri],
                max_embedding_requests_per_min=1000
            )
            
            # Clean up local file
            try:
                os.remove(local_path)
                if self.debug:
                    print(f"\nTemporary file deleted: {local_path}")
            except Exception as e:
                if self.debug:
                    print(f"\nWarning: Could not delete temporary file {local_path}")
                    print(f"Error: {e}")

            # List files to verify import
            files = list(rag.list_files(corpus.name))
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

        # Create RAG retrieval tool
        retrieval_tool = Tool.from_retrieval(
            retrieval=rag.Retrieval(
                source=rag.VertexRagStore(
                    rag_corpora=[corpus_name],
                    similarity_top_k=10,
                    vector_distance_threshold=0.8,
                ),
            )
        )

        # Create model with RAG tool
        return GenerativeModel(
            model_name="gemini-2.0-flash-001",
            tools=[retrieval_tool]
        )

    def generate_response(self, query: str, model: GenerativeModel, quiz_length: int, options_per_question: int) -> str:
        """Generate a response using RAG"""
        try:
            if self.debug:
                print(f"\nGenerating quiz with length: {quiz_length}")
            
            # Test response to verify corpus access
            if self.debug:
                print("\nVerifying corpus access...")
                test_response = model.generate_content("What are the main topics in the provided data?")
                print(f"Test response: {test_response.text[:100]}...")

            prompt = f"""
            Your task is to create multiple-choice questions based on this data.

            Requirements:
            1. Create exactly one question for each entry in the data ({quiz_length} total questions)
            2. Each question must be multiple choice with exactly ${options_per_question} options
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
            
            # Clean the response text
            cleaned_response = response.text.strip()
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response.split('```')[1]
                if cleaned_response.startswith('json'):
                    cleaned_response = cleaned_response[4:]
            cleaned_response = cleaned_response.strip()
            
            # Validate JSON
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

def main():
    debug_mode = True
    service_account = 'genaigenesis-454500-2b74084564ba.json'  # Fallback service account
    
    try:
        # Initialize RAG with simplified approach
        rag = QuizMakerRAG(
            service_account_path=service_account,
            debug=debug_mode
        )
    except Exception as e:
        print(f"Failed to initialize RAG: {e}")
        return

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
        response = rag.generate_response("", model, quiz_length=len(mock_data))
        print(f"\nQuiz: {response}")
    
    try:
        print("\nCleaning up - deleting corpus...")
        rag.delete_corpus(corpus_id)
    except Exception as e:
        print(f"\nError during cleanup: {str(e)}")

if __name__ == "__main__":
    main()