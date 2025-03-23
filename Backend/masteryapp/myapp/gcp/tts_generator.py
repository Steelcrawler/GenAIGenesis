import os
from google.cloud import texttospeech
from google.oauth2 import service_account
import io

def text_to_speech(text, output_filename="output.wav", voice_name="en-US-Standard-C", 
                  language_code="en-US", speaking_rate=1.0, pitch=0.0, credentials_file=None):
    """
    Convert text to speech using Google Cloud TTS API and save as WAV file
    
    Args:
        text (str): The text to convert to speech
        output_filename (str): The output filename (default: output.wav)
        voice_name (str): The voice to use (default: en-US-Standard-C)
        language_code (str): The language code (default: en-US)
        speaking_rate (float): Speaking rate from 0.25 to 4.0 (default: 1.0)
        pitch (float): Pitch from -20.0 to 20.0 (default: 0.0)
        credentials_file (str, optional): Path to GCP credentials JSON file (default: None)
        
    Returns:
        str: Path to the output audio file
    """
    # Initialize the client with explicit credentials if provided
    if credentials_file:
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        client = texttospeech.TextToSpeechClient(credentials=credentials)
    else:
        # Use environment variable or application default credentials
        client = texttospeech.TextToSpeechClient()
    
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
    )
    
    # Select the type of audio file (WAV)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=speaking_rate,
        pitch=pitch
    )
    
    # Perform the text-to-speech request
    try:
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # Save the audio content to a WAV file
        with open(output_filename, "wb") as out_file:
            out_file.write(response.audio_content)
            print(f"Audio content written to {output_filename}")
            
        return output_filename
    
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

def text_to_speech_bytes(text, voice_name="en-US-Standard-C", 
                        language_code="en-US", speaking_rate=1.0, pitch=0.0, credentials_file=None):
    """
    Convert text to speech using Google Cloud TTS API and return audio bytes
    
    Args:
        text (str): The text to convert to speech
        voice_name (str): The voice to use (default: en-US-Standard-C)
        language_code (str): The language code (default: en-US)
        speaking_rate (float): Speaking rate from 0.25 to 4.0 (default: 1.0)
        pitch (float): Pitch from -20.0 to 20.0 (default: 0.0)
        credentials_file (str, optional): Path to GCP credentials JSON file (default: None)
        
    Returns:
        bytes: The audio content as bytes
    """
    # Initialize the client with explicit credentials if provided
    if credentials_file:
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        client = texttospeech.TextToSpeechClient(credentials=credentials)
    else:
        # Use environment variable or application default credentials
        client = texttospeech.TextToSpeechClient()
    
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
    )
    
    # Select the type of audio file (WAV)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=speaking_rate,
        pitch=pitch
    )
    
    # Perform the text-to-speech request
    try:
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response.audio_content
    
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Method 1: Using environment variable (recommended approach)
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/credentials.json"
    
    # Example 1: Save to file using default credentials
    text_to_speech(
        "Hello, this is a test of Google Cloud Platform's text to speech API.",
        output_filename="test_output.wav",
        voice_name="en-US-Neural2-F",  # Using a neural voice
        speaking_rate=1.0,
        credentials_file="genaigenesis-454500-2b74084564ba.json"
    )
    
    # Example 2: Get audio bytes using default credentials
    audio_bytes = text_to_speech_bytes(
        "This is another example that returns the audio as bytes.",
        voice_name="en-US-Neural2-F", 
        credentials_file="genaigenesis-454500-2b74084564ba.json"
    )
    
    
    # You could save the bytes to a file
    if audio_bytes:
        with open("example_bytes.wav", "wb") as f:
            f.write(audio_bytes)