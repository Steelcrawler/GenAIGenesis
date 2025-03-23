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

class SimpleRAG:
    def __init__(self, credentials_path: Optional[str] = None, debug: bool = False):
        """Initialize the RAG model"""
        self.debug = debug
        env_path = '../.env'
        load_dotenv(dotenv_path=env_path)
        
        self.project_id = os.getenv("PROJECT_ID")
        self.location = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
        
        if self.debug:
            print(f"Initializing RAG model with project_id: {self.project_id}, location: {self.location}")
        vertexai.init(project=self.project_id, location=self.location)
        
        # Initialize GCS client
        self.storage_client = storage.Client()

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

    def setup_corpus(self, bucket_name: str, selected_files = None, custom_data = None) -> Optional[str]:
        """Set up the RAG corpus from selected files in GCS bucket"""
        try:
            if self.debug:
                print(f"Setting up corpus with selected files: {selected_files}")

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
            paths = [f"gs://{bucket_name}/{file}" for file in selected_files]
            if self.debug:
                print(f"Importing files from paths: {paths}")
            
            if selected_files:
                rag.import_files(
                    corpus.name,
                    paths,
                    max_embedding_requests_per_min=1000
                )
            elif custom_data:
                timestamp = int(time.time())
                file_path = 'temp_file_{timestamp}'
                with open(file_path, 'w') as f:
                    json.dump(custom_data, f)
                rag.upload_file(
                    corpus_name=corpus.name,
                    path=file_path,
                )
            else:
                raise Exception('One of selected_files or custom_data must not be None')
            
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

    def generate_response(self, query: str, model: GenerativeModel) -> str:
        """Generate a response using RAG"""
        try:
            # First, let's get the retrieved context to verify it's working
            # retrieval_response = model.generate_content(
            #     "What is the main topic of this document? Return only the topic in a single sentence."
            # )
            # if self.debug:
            #     print(f"\nRetrieved context: {retrieval_response.text}")

            prompt = f"""Generate 10 quiz questions based on the retrieved context.
            Return ONLY a JSON object with no other text, markdown, or formatting.

            Schema:
            {{
                "question": str,
                "answer": str,
                "source": {{
                    "content": str,
                    "relevance": float,
                    "document_name": str
                }}
            }}"""
                        
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
    rag = SimpleRAG(credentials_path='genaigenesis-454500-aaca4e6f468e.json', debug=debug_mode)

    bucket_name = "educatorgenai"
    print("\nFetching available files from GCS bucket...")
    available_files = rag.list_gcs_files(bucket_name)
    
    if not available_files:
        print("No files found in the bucket.")
        return
    
    selected_files = select_files(available_files)
    
    if not selected_files:
        print("No files selected.")
        return
    
    corpus_id = rag.setup_corpus(bucket_name, selected_files)

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


        
