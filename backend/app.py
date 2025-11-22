from fastapi import FastAPI, HTTPException, UploadFile, File, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path
import os
import uuid
import logging
from typing import List

# Import services
from services.db import (
    init_db, create_candidate, get_candidate, get_all_candidates, delete_candidate,
    CandidateCreate, Candidate
)
from services.transcription import transcribe_audio
from services.nlp import extract_candidate_info

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".ogg", ".flac", ".webm"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)

app = FastAPI(title="Transcript HR API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---

@app.get("/")
async def root():
    return {"message": "Transcript HR API is running"}

# Upload Route
@app.post("/api/upload-audio", tags=["upload"])
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload interview audio file
    """
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Save file
    file_path = UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        file_size = os.path.getsize(file_path)
        
        return JSONResponse({
            "message": "File uploaded successfully",
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "file_type": file_ext
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

# Transcribe Route
@app.post("/api/transcribe", tags=["transcribe"])
async def transcribe_endpoint(file_path: str):
    """
    Transcribe audio file to text using Whisper
    """
    path_obj = Path(file_path)
    
    if not path_obj.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        transcript = transcribe_audio(str(path_obj))
        
        return {
            "success": True,
            "transcript": transcript,
            "file_path": str(path_obj)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

# Extract Route
@app.post("/api/extract", tags=["extract"])
async def extract_endpoint(transcript: str):
    """
    Extract candidate information from transcript
    """
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript is required")
    
    try:
        extracted_data = extract_candidate_info(transcript)
        
        return {
            "success": True,
            "data": extracted_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")

# Candidates Routes
@app.post("/api/candidates", tags=["candidates"])
async def create_candidate_endpoint(candidate: CandidateCreate):
    """Create a new candidate record"""
    try:
        candidate_id = create_candidate(candidate)
        return {
            "success": True,
            "id": candidate_id,
            "message": "Candidate created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating candidate: {str(e)}")

@app.get("/api/candidates", tags=["candidates"])
async def list_candidates():
    """Get all candidates"""
    try:
        candidates = get_all_candidates()
        return {
            "success": True,
            "count": len(candidates),
            "candidates": candidates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching candidates: {str(e)}")

@app.get("/api/candidates/{candidate_id}", tags=["candidates"])
async def get_candidate_endpoint(candidate_id: int):
    """Get a single candidate by ID"""
    candidate = get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {
        "success": True,
        "candidate": candidate
    }

@app.delete("/api/candidates/{candidate_id}", tags=["candidates"])
async def delete_candidate_endpoint(candidate_id: int):
    """Delete a candidate by ID"""
    deleted = delete_candidate(candidate_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {
        "success": True,
        "message": "Candidate deleted successfully"
    }

# Workflow Route
@app.post("/api/process-audio", tags=["workflow"])
async def process_audio(file: UploadFile = File(...)):
    """
    Complete workflow: Upload audio, transcribe, extract info, and save to database
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {file_size / (1024*1024):.2f} MB. Maximum: {MAX_FILE_SIZE / (1024*1024)} MB"
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    
    # Generate unique filename to avoid conflicts
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        # Step 1: Save uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        logger.info(f"File saved: {file_path} ({file_size / (1024*1024):.2f} MB)")
        
        # Step 2: Transcribe
        try:
            transcript = transcribe_audio(str(file_path))
            if not transcript or len(transcript.strip()) < 10:
                raise HTTPException(
                    status_code=400,
                    detail="Transcription failed or returned insufficient text"
                )
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
        
        # Step 3: Extract information
        try:
            extracted_data = extract_candidate_info(transcript)
        except Exception as e:
            logger.error(f"Extraction error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Information extraction failed: {str(e)}")
        
        # Step 4: Save to database
        try:
            candidate_data = CandidateCreate(
                name=extracted_data.get("name"),
                email=extracted_data.get("email"),
                phone=extracted_data.get("phone"),
                college=extracted_data.get("college"),
                degree=extracted_data.get("degree"),
                graduation_year=extracted_data.get("graduation_year"),
                experience=extracted_data.get("experience"),
                location=extracted_data.get("location"),
                skills=extracted_data.get("skills"),
                transcript=transcript
            )
            
            candidate_id = create_candidate(candidate_data)
            logger.info(f"Candidate saved with ID: {candidate_id}")
        except ValueError as e:
            # Validation error
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save candidate: {str(e)}")
        
        # Clean up uploaded file
        try:
            if file_path.exists():
                os.remove(file_path)
                logger.info(f"Temporary file deleted: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete temporary file: {str(e)}")
        
        return JSONResponse({
            "success": True,
            "message": "Audio processed and candidate saved successfully",
            "candidate_id": candidate_id,
            "transcript": transcript,
            "extracted_data": extracted_data
        })
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        # Clean up on error
        if file_path and file_path.exists():
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
