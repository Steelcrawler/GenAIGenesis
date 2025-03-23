import os
import io
from google.cloud import speech
from google.oauth2 import service_account
import wave
from vertexai.generative_models import GenerativeModel
from typing import List, Dict, Any, Optional
import json
import vertexai

def speech_to_text(audio_file_path, language_code="en-US", sample_rate=None, 
                  encoding=None, enable_word_time_offsets=False, 
                  enable_automatic_punctuation=True, model="default", 
                  credentials_file=None):
    """
    Convert speech in an audio file to text using Google Cloud Speech-to-Text API
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        language_code (str): Language code (default: en-US)
        sample_rate (int): Audio sample rate in hertz (default: 16000)
        encoding (str): Audio encoding type (default: LINEAR16/WAV)
        enable_word_time_offsets (bool): Include word timestamps (default: False)
        enable_automatic_punctuation (bool): Add punctuation to result (default: True)
        model (str): Speech recognition model (default: "default")
                     Other options: "command_and_search", "phone_call", "video", etc.
        credentials_file (str, optional): Path to GCP credentials JSON file (default: None)
        
    Returns:
        dict: Contains 'transcript' (full text) and 'results' (detailed API response)
    """
    # Initialize client with explicit credentials if provided
    if credentials_file:
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        client = speech.SpeechClient(credentials=credentials)
    else:
        # Use environment variable or application default credentials
        client = speech.SpeechClient()
    
    # Read the audio file
    with io.open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()
    
    # Auto-detect format and sample rate if not specified
    if encoding is None or sample_rate is None:
        detected_encoding, detected_sample_rate = detect_audio_format(audio_file_path)
        encoding = encoding or detected_encoding
        sample_rate = sample_rate or detected_sample_rate
    
    # Configure the recognition request
    audio = speech.RecognitionAudio(content=content)
    
    # Create base config
    config_args = {
        'language_code': language_code,
        'enable_word_time_offsets': enable_word_time_offsets,
        'enable_automatic_punctuation': enable_automatic_punctuation,
        'model': model,
    }
    
    # Add encoding
    if encoding:
        config_args['encoding'] = getattr(speech.RecognitionConfig.AudioEncoding, encoding)
    
    # Add sample rate only if it's known
    if sample_rate:
        config_args['sample_rate_hertz'] = sample_rate
    else:
        print("Warning: Could not determine sample rate. Letting the API auto-detect.")
    
    config = speech.RecognitionConfig(**config_args)
    
    # Perform the speech recognition
    try:
        response = client.recognize(config=config, audio=audio)
        
        # Extract results
        full_transcript = ""
        for result in response.results:
            full_transcript += result.alternatives[0].transcript
        
        return {
            "transcript": full_transcript,
            "results": response.results
        }
    
    except Exception as e:
        print(f"Error transcribing speech: {e}")
        return {
            "transcript": "",
            "error": str(e)
        }

def speech_to_text_from_bytes(audio_content, language_code="en-US", sample_rate=16000, 
                             encoding='LINEAR16', enable_word_time_offsets=False, 
                             enable_automatic_punctuation=True, model="default", 
                             credentials_file=None):
    """
    Convert speech in audio bytes to text using Google Cloud Speech-to-Text API
    
    Args:
        audio_content (bytes): Audio content as bytes
        language_code (str): Language code (default: en-US)
        sample_rate (int): Audio sample rate in hertz (default: 16000)
        encoding (str): Audio encoding type (default: LINEAR16/WAV)
        enable_word_time_offsets (bool): Include word timestamps (default: False)
        enable_automatic_punctuation (bool): Add punctuation to result (default: True)
        model (str): Speech recognition model (default: "default")
                     Other options: "command_and_search", "phone_call", "video", etc.
        credentials_file (str, optional): Path to GCP credentials JSON file (default: None)
        
    Returns:
        dict: Contains 'transcript' (full text) and 'results' (detailed API response)
    """
    # Initialize client with explicit credentials if provided
    if credentials_file:
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        client = speech.SpeechClient(credentials=credentials)
    else:
        # Use environment variable or application default credentials
        client = speech.SpeechClient()
    
    # Configure the recognition request
    audio = speech.RecognitionAudio(content=audio_content)
    
    config = speech.RecognitionConfig(
        encoding=getattr(speech.RecognitionConfig.AudioEncoding, encoding),
        sample_rate_hertz=sample_rate,
        language_code=language_code,
        enable_word_time_offsets=enable_word_time_offsets,
        enable_automatic_punctuation=enable_automatic_punctuation,
        model=model,
    )
    
    # Perform the speech recognition
    try:
        response = client.recognize(config=config, audio=audio)
        
        # Extract results
        full_transcript = ""
        for result in response.results:
            full_transcript += result.alternatives[0].transcript
        
        return {
            "transcript": full_transcript,
            "results": response.results
        }
    
    except Exception as e:
        print(f"Error transcribing speech: {e}")
        return {
            "transcript": "",
            "error": str(e)
        }

def detect_audio_format(audio_file_path):
    """
    Detect audio format and sample rate
    
    Args:
        audio_file_path (str): Path to the audio file
    
    Returns:
        tuple: (encoding, sample_rate) with detected values
    """
    # Get file extension
    ext = os.path.splitext(audio_file_path)[1].lower()
    
    # Default values
    encoding = 'LINEAR16'  # WAV default
    sample_rate = None
    
    # Adjust based on common formats
    if ext == '.flac':
        encoding = 'FLAC'
    elif ext == '.mp3':
        encoding = 'MP3'
    elif ext == '.ogg':
        encoding = 'OGG_OPUS'
    
    # For WAV files, read the sample rate from the header
    if ext == '.wav':
        try:
            with wave.open(audio_file_path, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                print(f"Detected WAV sample rate: {sample_rate} Hz")
        except Exception as e:
            print(f"Warning: Could not read WAV header: {e}")
    
    return encoding, sample_rate

def get_command_from_transcript(transcript, language_code="en-US", sample_rate=16000, credentials_file=None):
    """
    Extract command from transcript using Google Cloud Speech-to-Text API
    
    Args:
        transcript (str): Transcript text to analyze
        language_code (str): Language code (default: en-US)
    
    Returns:
        str: Extracted command
    """
    # Initialize client with explicit credentials if provided
    if credentials_file:
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        client = speech.SpeechClient(credentials=credentials)
    else:
        client = speech.SpeechClient()
    
    text = speech_to_text_from_bytes(transcript, language_code, sample_rate, credentials_file=credentials_file)

    # Extract command from transcript with LLM
    command = extract_command_from_transcript(text)
    return command
    
def extract_command_from_transcript(transcript: str, course_names: List[str] = None, pdf_names: List[str] = None,
                    credentials_path: Optional[str] = None, project_id: str = "genaigenesis-454500", 
                    location: str = "us-central1") -> Dict[str, Any]:
    """
    Extract educational navigation commands from transcript text using Google's Gemini model
    
    Args:
        transcript (str): The transcript text to analyze
        course_names (List[str]): List of valid course names for matching
        pdf_names (List[str]): List of valid PDF names for matching
        credentials_path (str, optional): Path to GCP credentials JSON file
        project_id (str): Google Cloud project ID (default: "genaigenesis-454500")
        location (str): Google Cloud region (default: "us-central1")
    
    Returns:
        dict: Contains command details including action and parameters
    """
    try:
        # Set defaults if not provided
        if course_names is None:
            course_names = []
        if pdf_names is None:
            pdf_names = []
        
        # Initialize Vertex AI with project ID and location
        vertexai.init(project=project_id, location=location)
        
        # Set credentials if provided
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        # Initialize the Gemini model
        model = GenerativeModel(model_name="gemini-1.5-flash-002")
        
        # Format the course and PDF names for inclusion in the prompt
        course_names_str = ", ".join([f'"{name}"' for name in course_names])
        pdf_names_str = ", ".join([f'"{name}"' for name in pdf_names])
        
        # Create a prompt for command extraction focused on the specific actions
        # and including the JSON structure
        prompt = f"""
        Analyze the following speech transcript and classify it into EXACTLY one of these specific actions:
        - Next (go to next page)
        - Previous (go to previous page)
        - Submit (submit current work)
        - Quit (exit the application)
        - Reread (read the current content again)
        - Open [course] [pdf] (open a specific PDF in a course)

        IMPORTANT: The "Open" command REQUIRES BOTH a course name AND a PDF name to be specified.
        If EITHER the course OR the PDF name is missing, you MUST classify the action as "Unknown" instead of "Open".

        Available course names: {course_names_str}
        Available PDF names: {pdf_names_str}

        For the "Open" command, match to the closest course and PDF name from the provided lists.
        Match even if the user only says part of the course or PDF name.

        Return your response in this exact JSON structure:

        For "Next", "Previous", "Submit", "Quit", "Reread", or "Unknown" commands:
        {{
        "action": "Next", // Or "Previous", "Submit", "Quit", "Reread", "Unknown" as appropriate
        "course_name": null,
        "pdf_name": null
        }}

        For "Open" commands (which MUST have BOTH course AND PDF specified):
        {{
        "action": "Open",
        "course_name": "Introduction to AI", // Match to provided course name
        "pdf_name": "Lecture 1 - Introduction" // Match to provided PDF name
        }}

        Examples of "Unknown" actions:
        - "Open the Introduction to Computer Science course" (PDF name is missing)
        - "Open the Neural Networks Explained PDF" (Course name is missing)
        - "Show me the course syllabus" (Unclear command with missing information)

        Transcript:
        "{transcript}"

        Respond with ONLY the JSON object and no additional text.
        """
        
        # Generate content from the model
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up the response to extract the JSON
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]  # Remove ```json and ```
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]  # Remove ``` and ```
        
        response_text = response_text.strip()
        
        # Parse the JSON response
        command_data = json.loads(response_text)
        
        return command_data
    
    except Exception as e:
        print(f"Error extracting command from transcript: {str(e)}")
        return {
            "action": "Unknown",
            "course_name": None,
            "pdf_name": None,
            "error": str(e)
        }

def get_command_from_bytes(audio_bytes, language_code="en-US", sample_rate=None, credentials_file=None,
                      course_names: List[str] = None, pdf_names: List[str] = None):
    """
    Extract command from audio bytes using Google Cloud Speech-to-Text API
    
    Args:
        audio_bytes (bytes): Audio content as bytes
        language_code (str): Language code (default: en-US)
        sample_rate (int, optional): Audio sample rate in hertz. If None, will be detected from audio.
        credentials_file (str, optional): Path to GCP credentials JSON file
        course_names (List[str], optional): List of valid course names for matching
        pdf_names (List[str], optional): List of valid PDF names for matching
    
    Returns:
        dict: Contains command details including action and parameters
    """
    try:
        # Try to detect sample rate from WAV header if sample_rate is None
        if sample_rate is None:
            import io
            import wave
            
            # Create a BytesIO object from audio bytes
            byte_io = io.BytesIO(audio_bytes)
            
            try:
                # Try to open as WAV file to extract sample rate
                with wave.open(byte_io, 'rb') as wav_file:
                    detected_sample_rate = wav_file.getframerate()
                    print(f"Detected WAV sample rate: {detected_sample_rate} Hz")
                    sample_rate = detected_sample_rate
            except Exception as e:
                print(f"Warning: Could not detect sample rate from audio bytes: {e}")
                # Use a common default if detection fails
                sample_rate = 16000
                print(f"Using default sample rate: {sample_rate} Hz")
                
            # Reset BytesIO position
            byte_io.seek(0)
        
        # Get transcript from audio
        transcript_result = speech_to_text_from_bytes(
            audio_content=audio_bytes, 
            language_code=language_code, 
            sample_rate=sample_rate,
            credentials_file=credentials_file
        )
        
        if "error" in transcript_result:
            print(f"Error in speech-to-text: {transcript_result['error']}")
            return {
                "action": "Unknown",
                "course_name": None,
                "pdf_name": None,
                "error": transcript_result["error"],
                "transcript": None
            }
        
        transcript = transcript_result["transcript"]
        
        if not transcript:
            print("No transcript detected in audio")
            return {
                "action": "Unknown",
                "course_name": None,
                "pdf_name": None,
                "error": "No speech detected",
                "transcript": None
            }
            
        print(f"Transcript: {transcript}")
        
        # Extract command from the transcript
        command = extract_command_from_transcript(
            transcript=transcript,
            course_names=course_names,
            pdf_names=pdf_names,
            credentials_path=credentials_file
        )
        
        # Add transcript to the result
        command["transcript"] = transcript
        
        return command
        
    except Exception as e:
        print(f"Error in get_command_from_bytes: {str(e)}")
        return {
            "action": "Unknown",
            "course_name": None,
            "pdf_name": None,
            "error": str(e),
            "transcript": None
        }

# Example usage
if __name__ == "__main__":
    import os
    
    # Initialize Google Cloud credentials if needed
    credentials_path = "genaigenesis-454500-2b74084564ba.json"
    project_id = "genaigenesis-454500"
    location = "us-central1"
    
    # Example course names
    course_names = [
        "Introduction to Computer Science",
        "Data Structures and Algorithms",
        "Machine Learning",
        "Artificial Intelligence",
        "Web Development"
    ]
    
    # Example PDF names
    pdf_names = [
        "Lecture 1 - Overview",
        "Lecture 2 - Basics",
        "Midterm Review",
        "Programming Assignment",
        "Neural Networks Explained",
        "Decision Trees",
        "Course Syllabus"
    ]
    
    print("Processing WAV files in current directory:")
    print("========================================\n")

    for file in os.listdir(os.getcwd()):
        if file.endswith(".wav"):
            print(f"Processing: {file}")
            
            try:
                with open(file, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                
                command = get_command_from_bytes(
                    audio_bytes=audio_bytes, 
                    language_code="en-US", 
                    sample_rate=None,
                    credentials_file=credentials_path,
                    course_names=course_names,
                    pdf_names=pdf_names
                )
                
                print(f"Command action: {command.get('action')}")
                
                if command.get('action') == "Open":
                    print(f"Course: {command.get('course_name')}")
                    print(f"PDF: {command.get('pdf_name')}")
                    
                if command.get('error'):
                    print(f"Error: {command.get('error')}")
                    
                print("-" * 50)
                    
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")
                print("-" * 50)