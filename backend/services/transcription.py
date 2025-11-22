import whisper
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Whisper model
# Using 'tiny' model for maximum speed as requested by user ("quick responce")
# 'base' is better accuracy but slower. 'tiny' is ~32x faster than 'large'.
_model = None

def load_model():
    """Lazy load Whisper model with error handling"""
    global _model
    if _model is None:
        try:
            logger.info("Loading Whisper model (tiny)...")
            _model = whisper.load_model("tiny")
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            raise Exception(f"Failed to load Whisper model: {str(e)}")
    return _model

def transcribe_audio(audio_path: str, language: Optional[str] = None) -> str:
    """
    Transcribe audio file to text using Whisper
    
    Args:
        audio_path: Path to audio file
        language: Optional language code (e.g., 'en', 'hi'). Auto-detect if None.
        
    Returns:
        Transcribed text
        
    Raises:
        FileNotFoundError: If audio file doesn't exist
        Exception: If transcription fails
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    if not os.path.isfile(audio_path):
        raise ValueError(f"Path is not a file: {audio_path}")
    
    # Check file size (prevent processing extremely large files)
    file_size = os.path.getsize(audio_path)
    max_size = 500 * 1024 * 1024  # 500 MB
    if file_size > max_size:
        raise ValueError(f"File too large: {file_size / (1024*1024):.2f} MB. Maximum: {max_size / (1024*1024)} MB")
    
    try:
        model = load_model()
        logger.info(f"Transcribing audio: {audio_path} ({file_size / (1024*1024):.2f} MB)")
        
        # Transcribe with optimized settings
        result = model.transcribe(
            audio_path,
            language=language,  # Auto-detect if None
            task="transcribe",
            fp16=False,  # Use fp32 for better compatibility
            verbose=False
        )
        
        transcript = result.get("text", "").strip()
        
        if not transcript:
            logger.warning("Transcription returned empty text")
            return ""
        
        logger.info(f"Transcription complete. Length: {len(transcript)} characters")
        return transcript
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise Exception(f"Transcription failed: {str(e)}")
