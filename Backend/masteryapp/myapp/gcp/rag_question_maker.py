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
    def __init__(self, credentials_path: Optional[str] = None, debug: bool = False):
        """Initialize the RAG model"""
        self.debug = debug
        env_path = './.env'
        load_dotenv(dotenv_path=env_path)
        
        self.project_id = "genaigenesis-454500" # os.getenv("PROJECT_ID")
        self.location = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
        
        if self.debug:
            print(f"Initializing RAG model with project_id: {self.project_id}, location: {self.location}")
        vertexai.init(project=self.project_id, location=self.location)
        
        # Initialize GCS client
        self.storage_client = storage.Client.from_service_account_json(credentials_path)

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
                print(f"Setting up corpus with selected data: {data_list}")

            embedding_model_config = rag.EmbeddingModelConfig(
                publisher_model=f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/text-embedding-005"
            )
            
            # Create corpus
            corpus = rag.create_corpus(
                display_name="simple-rag-corpus",
                embedding_model_config=embedding_model_config
            )

            if self.debug:
                print(f"Corpus created with ID: {corpus.name}")
            
            # Create full GCS paths for selected files
            timestamp = int(time.time())
            file_path = f'temp_file_{timestamp}'
            path = f"gs://{bucket_name}/{file_path}"
            
            with open(file_path, 'w') as f:
                json.dump(data_list, f)
                
            if self.debug:
                with open(file_path, 'r') as f:
                    file_content = f.read()
                    print(f"Debug: File content of {file_path}:\n{file_content}")
                
            rag.upload_file(
                corpus_name=corpus.name,
                path=file_path,
            )
            
            try:
                os.remove(file_path)
                if self.debug:
                    print(f"Debug: Deleted temporary file: {file_path}")
            except Exception as e:
                if self.debug:
                    print(f"Warning: Could not delete temporary file {file_path}. Error: {e}")

            
            # List files to verify import
            files = rag.list_files(corpus.name)
            if self.debug:
                print(f"Imported files: {files}")
            
            return corpus.name

        except Exception as e:
            print(f"Error setting up corpus: {str(e)}")
            return None

    def setup_model(self, corpus_name: str) -> GenerativeModel:
        """Set up the model with RAG capability"""
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

        # Create model with RAG tool
        return GenerativeModel(
            model_name="gemini-2.0-flash-001",
            tools=[retrieval_tool]
        )

    def generate_response(self, query: str, model: GenerativeModel, quiz_length: int) -> str:
        """Generate a response using RAG"""
        try:
            # First, let's get the retrieved context to verify it's working
            # retrieval_response = model.generate_content(
            #     "What is the main topic of this document? Return only the topic in a single sentence."
            # )
            # if self.debug:
            #     print(f"\nRetrieved context: {retrieval_response.text}")

            prompt = f"""
            You have in your data a JSON file which contains a list of subjects. Go through each entry one by one and create
            one and exactly one question for each ({quiz_length} total questions expected). The questions must be in mutliple choice (4) format, with exactly one correct answer.
            You may see the same subject appear twice, or even the same exact object appear twice. If so, make another question for the same
            snippet/subject. The important part is that you make exactly one question per ENTRY.
            
            For each questions, reference the entry you made it in regards to, using that entry's identifier (id column).
            
            Schema of expected response:
            [{{
                "snippet_id": str,
                "question": str,
                "choices": list[str],
                "answer_index": int,
                }},
                {{
                "snippet_id": str,
                "question": str,
                "choices": list[str],
                "answer_index": int,
                }},
                etc.
            }}]"""
                        
            if self.debug:
                print(f"\nGenerating quiz...")
            response = model.generate_content(prompt)
            
            # Clean the response text by removing markdown code fences if present
            cleaned_response = response.text.strip()
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response.split('```')[1]
            if cleaned_response.startswith('json'):
                cleaned_response = cleaned_response[4:]
            cleaned_response = cleaned_response.strip()
            
            # Try to parse as JSON to validate
            try:
                json.loads(cleaned_response)
                return cleaned_response
            except json.JSONDecodeError:
                return f"Error: Response was not valid JSON: {cleaned_response}"
                
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            raise

    def list_corpora(self):
        """List all RAG corpora"""
        return rag.list_corpora()

    def list_files(self, corpus_name: str):
        """List files in a specific RAG corpus"""
        return rag.list_files(corpus_name)

    def delete_corpus(self, corpus_name: str):
        """Delete a specific RAG corpus"""
        try:
            rag.delete_corpus(corpus_name)
            if self.debug:
                print(f"Successfully deleted corpus: {corpus_name}")
        except Exception as e:
            print(f"Error deleting corpus {corpus_name}: {str(e)}")

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
    debug_mode = False
    rag = QuizMakerRAG(credentials_path='genaigenesis-454500-2b74084564ba.json', debug=debug_mode)

    bucket_name = "educatorgenai"
    print("\nFetching available files from GCS bucket...")
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
    corpus_id = rag.setup_corpus(bucket_name=bucket_name, data_list=mock_data)

    if corpus_id:
        if debug_mode:
            print("\nSetting up model with RAG capability...")
        model = rag.setup_model(corpus_id)
        
        print("\nGenerating quiz based on the corpus...")
        response = rag.generate_response("", model)
        print(f"\nQuiz: {response}")
    
    try:
        rag.delete_corpus(corpus_id)
    except Exception as e:
        print(f"Error deleting corpus: {str(e)}")

if __name__ == "__main__":
    main()


        
