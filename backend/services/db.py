import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import re

# Configure logging
logger = logging.getLogger(__name__)

# Database Path
DB_PATH = Path(__file__).parent.parent / "candidates.db"

# --- Models ---

class CandidateBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[int] = None
    experience: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[str] = None
    transcript: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class Candidate(CandidateBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Validation Utils ---

def validate_email(email: Optional[str]) -> bool:
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: Optional[str]) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    # Remove common separators
    digits = re.sub(r'[^\d+]', '', phone)
    return 10 <= len(digits) <= 15

def validate_year(year: Optional[int]) -> bool:
    """Validate graduation year is reasonable"""
    if year is None:
        return False
    return 1950 <= year <= 2030

def validate_name(name: Optional[str]) -> bool:
    """Validate name format"""
    if not name:
        return False
    # Name should be 2-50 characters, contain letters, may contain spaces, hyphens, apostrophes
    pattern = r'^[A-Za-z\s\-\']{2,50}$'
    return bool(re.match(pattern, name))

def sanitize_string(value: Optional[str], max_length: int = 500) -> Optional[str]:
    """Sanitize string input"""
    if not value:
        return None
    # Remove excessive whitespace
    value = ' '.join(value.split())
    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length]
    return value.strip()

def sanitize_skills(skills: Optional[str]) -> Optional[str]:
    """Sanitize skills string"""
    if not skills:
        return None
    # Remove duplicates, sort, and limit length
    skill_list = [s.strip() for s in skills.split(',') if s.strip()]
    unique_skills = sorted(set(skill_list))[:20]  # Limit to 20 skills
    return ', '.join(unique_skills)

def validate_candidate_data(data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate candidate data before saving
    
    Returns:
        (is_valid, error_message)
    """
    # Email validation
    if data.get('email') and not validate_email(data['email']):
        return False, "Invalid email format"
    
    # Phone validation
    if data.get('phone') and not validate_phone(data['phone']):
        return False, "Invalid phone number format"
    
    # Year validation
    if data.get('graduation_year') and not validate_year(data['graduation_year']):
        return False, "Invalid graduation year"
    
    # Name validation (if provided)
    if data.get('name') and not validate_name(data['name']):
        return False, "Invalid name format"
    
    return True, None

# --- Database Connection ---

@contextmanager
def get_db():
    """Get database connection with context manager for proper cleanup"""
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        conn.close()

def init_db():
    """Initialize database with tables and indexes"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT,
                college TEXT,
                degree TEXT,
                graduation_year INTEGER,
                experience TEXT,
                location TEXT,
                skills TEXT,
                transcript TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_email ON candidates(email)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_name ON candidates(name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON candidates(created_at DESC)
        """)
        
        conn.commit()
        logger.info(f"Database initialized at {DB_PATH}")

# --- CRUD Operations ---

def create_candidate(candidate_data: CandidateCreate) -> int:
    """Create a new candidate record with validation"""
    # Convert to dict for validation
    data_dict = candidate_data.dict()
    
    # Sanitize string fields
    data_dict['name'] = sanitize_string(data_dict.get('name'), max_length=100)
    data_dict['email'] = sanitize_string(data_dict.get('email'), max_length=100)
    data_dict['phone'] = sanitize_string(data_dict.get('phone'), max_length=20)
    data_dict['college'] = sanitize_string(data_dict.get('college'), max_length=200)
    data_dict['degree'] = sanitize_string(data_dict.get('degree'), max_length=100)
    data_dict['experience'] = sanitize_string(data_dict.get('experience'), max_length=50)
    data_dict['location'] = sanitize_string(data_dict.get('location'), max_length=100)
    data_dict['skills'] = sanitize_skills(data_dict.get('skills'))
    data_dict['transcript'] = sanitize_string(data_dict.get('transcript'), max_length=50000)
    
    # Validate data
    is_valid, error_msg = validate_candidate_data(data_dict)
    if not is_valid:
        logger.error(f"Validation failed: {error_msg}")
        raise ValueError(error_msg)
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO candidates (name, email, phone, college, degree, graduation_year, 
                                       experience, location, skills, transcript)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data_dict.get('name'),
                data_dict.get('email'),
                data_dict.get('phone'),
                data_dict.get('college'),
                data_dict.get('degree'),
                data_dict.get('graduation_year'),
                data_dict.get('experience'),
                data_dict.get('location'),
                data_dict.get('skills'),
                data_dict.get('transcript')
            ))
            
            candidate_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Candidate created with ID: {candidate_id}")
            return candidate_id
    except Exception as e:
        logger.error(f"Error creating candidate: {str(e)}")
        raise

def get_candidate(candidate_id: int) -> Optional[dict]:
    """Get a candidate by ID"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    except Exception as e:
        logger.error(f"Error fetching candidate {candidate_id}: {str(e)}")
        raise

def get_all_candidates() -> List[dict]:
    """Get all candidates with optimized query"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM candidates ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching candidates: {str(e)}")
        raise

def delete_candidate(candidate_id: int) -> bool:
    """Delete a candidate by ID"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
    except Exception as e:
        logger.error(f"Error deleting candidate {candidate_id}: {str(e)}")
        raise
