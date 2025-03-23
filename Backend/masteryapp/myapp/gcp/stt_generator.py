import os
import io
from google.cloud import speech
from google.oauth2 import service_account
import wave

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

# Example usage
if __name__ == "__main__":
    # Method 1: Using environment variable
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/credentials.json"
    
    # Example 1: Basic transcription of a WAV file
    result = speech_to_text(
        "test_output.wav",  # You could use the file generated by text_to_speech.py
        language_code="en-US",
         credentials_file="genaigenesis-454500-2b74084564ba.json"
    )
    print("Transcription:", result["transcript"])
