# Transcript HR - Complete File Documentation

This document provides a comprehensive explanation of every file in the Transcript HR project, organized by directory structure.

---

## 📁 Project Root

### `README.md`
**Purpose**: Main project documentation and quick start guide  
**Contents**: 
- Project overview and description
- Tech stack information
- Installation instructions
- Usage guide
- API endpoints summary
- Troubleshooting tips

### `SETUP.md`
**Purpose**: Detailed setup instructions  
**Contents**: 
- Step-by-step installation guide
- Environment setup
- Dependency installation
- Configuration instructions
- Troubleshooting for common issues

### `.gitignore`
**Purpose**: Git ignore configuration  
**Contents**: 
- Files and directories to exclude from version control
- Python cache files (`__pycache__/`, `*.pyc`)
- Node modules
- Virtual environments
- Database files
- Upload directories
- Environment files

---

## 📁 Backend Directory (`backend/`)

### `requirements.txt`
**Purpose**: Python dependency list  
**Contents**: 
- FastAPI - Web framework for building APIs
- Uvicorn - ASGI server for running FastAPI
- OpenAI Whisper - Audio transcription model
- spaCy - Natural Language Processing library
- PyTorch & TorchAudio - Required for Whisper
- Python-multipart - For file uploads
- Pydantic - Data validation

**Usage**: `pip install -r requirements.txt`

### `candidates.db`
**Purpose**: SQLite database file  
**Contents**: 
- Stores all candidate information
- Created automatically on first run
- Contains `candidates` table with all extracted data

**Schema**: See `backend/app/database/database.py` for table structure

### `install_whisper.bat` (Windows)
**Purpose**: Windows batch script for installing Whisper  
**Contents**: 
- Upgrades pip, setuptools, wheel
- Installs Whisper from GitHub
- Alternative installation method if pip install fails

### `install_whisper.sh` (Linux/Mac)
**Purpose**: Shell script for installing Whisper  
**Contents**: 
- Same as `.bat` but for Unix-based systems
- Upgrades pip, setuptools, wheel
- Installs Whisper from GitHub

### `uploads/` (Directory)
**Purpose**: Temporary storage for uploaded audio files  
**Contents**: 
- Audio files are stored here during processing
- Files should be cleaned up after processing
- Not committed to git (in `.gitignore`)

---

## 📁 Backend Application (`backend/app/`)

### `main.py`
**Purpose**: FastAPI application entry point  
**Key Functions**:
- Initializes FastAPI app
- Sets up CORS middleware for frontend communication
- Configures database on startup
- Includes all API routers
- Defines root endpoint

**Routes Registered**:
- `/api/upload-audio` - File upload
- `/api/transcribe` - Audio transcription
- `/api/extract` - Information extraction
- `/api/candidates` - Candidate CRUD operations
- `/api/process-audio` - Combined workflow endpoint

**Configuration**:
- CORS origins: `http://localhost:5173`, `http://localhost:3000`
- App title: "Transcript HR API"
- Version: "1.0.0"

### `__init__.py`
**Purpose**: Python package marker  
**Contents**: Makes `app` directory a Python package

---

## 📁 API Routes (`backend/app/api/`)

### `__init__.py`
**Purpose**: Package marker for API module

### `upload.py`
**Purpose**: Handles audio file uploads  
**Endpoints**:
- `POST /api/upload-audio` - Upload audio file

**Functions**:
- Validates file type (MP3, WAV, M4A, MP4, OGG, FLAC, WEBM)
- Saves file to `uploads/` directory
- Returns file path for further processing

**File Validation**:
- Checks file extension
- Validates file exists
- Returns error if invalid format

### `transcribe.py`
**Purpose**: Audio transcription endpoint  
**Endpoints**:
- `POST /api/transcribe` - Transcribe audio to text

**Functions**:
- Accepts file path or audio data
- Calls transcription service
- Returns transcript text

**Usage**: Called after file upload to convert audio to text

### `extract.py`
**Purpose**: Information extraction endpoint  
**Endpoints**:
- `POST /api/extract` - Extract candidate info from transcript

**Functions**:
- Accepts transcript text
- Calls extraction service
- Returns structured candidate data

**Returns**: Dictionary with name, email, phone, college, degree, etc.

### `candidates.py`
**Purpose**: Candidate CRUD operations  
**Endpoints**:
- `GET /api/candidates` - Get all candidates
- `GET /api/candidates/{id}` - Get candidate by ID
- `POST /api/candidates` - Create new candidate
- `DELETE /api/candidates/{id}` - Delete candidate

**Functions**:
- List all candidates with pagination support
- Retrieve single candidate details
- Create new candidate record
- Delete candidate record

**Database Operations**: Uses schemas/candidate.py for database access

### `workflow.py`
**Purpose**: Combined workflow endpoint  
**Endpoints**:
- `POST /api/process-audio` - Complete workflow in one call

**Functions**:
- Uploads audio file
- Transcribes audio to text
- Extracts candidate information
- Saves to database
- Returns complete result

**Benefits**: 
- Single API call instead of multiple
- Better user experience
- Atomic operation (all or nothing)

---

## 📁 Database (`backend/app/database/`)

### `__init__.py`
**Purpose**: Package marker

### `database.py`
**Purpose**: Database configuration and operations  
**Key Functions**:

**`get_db()`**:
- Returns database connection
- Uses context manager for proper cleanup
- Creates connection to SQLite database
- Sets timeout to 10 seconds

**`init_db()`**:
- Creates database tables if they don't exist
- Defines `candidates` table schema
- Creates indexes for performance
- Called on application startup

**Table Schema**:
```sql
candidates (
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
```

**Indexes**:
- `idx_email` on email
- `idx_name` on name
- `idx_created_at` on created_at

---

## 📁 Models (`backend/app/models/`)

### `__init__.py`
**Purpose**: Package marker

### `candidate.py`
**Purpose**: Pydantic models for data validation  
**Models Defined**:

**`Candidate`**:
- Full candidate model with all fields
- Used for API responses
- Includes ID and timestamps

**`CandidateCreate`**:
- Model for creating new candidates
- Used for POST requests
- Validates input data
- Optional fields for flexibility

**Fields**:
- `name`: Optional[str] - Candidate name
- `email`: Optional[str] - Email address
- `phone`: Optional[str] - Phone number
- `college`: Optional[str] - College/University
- `degree`: Optional[str] - Degree information
- `graduation_year`: Optional[int] - Year of graduation
- `experience`: Optional[str] - Work experience
- `location`: Optional[str] - Location
- `skills`: Optional[str] - Skills (comma-separated)
- `transcript`: Optional[str] - Full transcript

**Purpose**: Type safety and automatic validation for API requests/responses

---

## 📁 Schemas (`backend/app/schemas/`)

### `__init__.py`
**Purpose**: Package marker

### `candidate.py`
**Purpose**: Database operations for candidates  
**Key Functions**:

**`create_candidate(candidate_data: CandidateCreate) -> int`**:
- Creates new candidate record
- Validates and sanitizes input data
- Inserts into database
- Returns candidate ID
- Handles errors and rollback

**`get_candidate(candidate_id: int) -> Optional[dict]`**:
- Retrieves candidate by ID
- Returns dictionary or None
- Handles database errors

**`get_all_candidates() -> List[dict]`**:
- Retrieves all candidates
- Ordered by creation date (newest first)
- Returns list of dictionaries
- Optimized query with indexes

**`delete_candidate(candidate_id: int) -> bool`**:
- Deletes candidate by ID
- Returns True if deleted, False if not found
- Commits transaction

**Data Validation**:
- Uses `utils/validation.py` for sanitization
- Validates email format
- Validates phone format
- Truncates long strings
- Sanitizes skills list

---

## 📁 Services (`backend/app/services/`)

### `__init__.py`
**Purpose**: Package marker

### `transcription.py`
**Purpose**: Audio-to-text transcription using Whisper  
**Key Functions**:

**`transcribe_audio(audio_path: str) -> str`**:
- Loads Whisper model (base model)
- Transcribes audio file to text
- Returns transcript as string
- Handles errors gracefully

**Model Configuration**:
- Model: "base" (can be changed to "small", "medium", "large")
- Device: Auto-detects CPU/GPU
- Language: English (can be auto-detected)

**Performance**:
- Model loaded once and cached
- Supports various audio formats
- Handles long audio files

### `extraction.py`
**Purpose**: Extract candidate information from transcript using NLP  
**Key Functions**:

**`extract_candidate_info(transcript: str) -> Dict[str, Optional[str]]`**:
- Main extraction function
- Orchestrates all extraction methods
- Returns structured data dictionary

**Extraction Functions**:

1. **`extract_email(transcript: str)`**:
   - Uses regex pattern
   - Validates email format
   - Returns first valid email

2. **`extract_phone(transcript: str)`**:
   - Uses regex pattern
   - Validates phone format
   - Returns formatted phone number

3. **`extract_experience(transcript: str)`**:
   - Finds years of experience
   - Multiple pattern matching
   - Returns formatted string

4. **`extract_skills(transcript: str)`**:
   - Keyword-based extraction
   - Set-based lookup for speed
   - Returns comma-separated skills

5. **`extract_name(transcript: str, doc)`**:
   - Uses spaCy NER (Named Entity Recognition)
   - Validates name format
   - Filters common words

6. **`extract_location(transcript: str, doc)`**:
   - Prioritizes city names over regions
   - Uses regex for Indian cities
   - Filters programming languages
   - Uses spaCy GPE entities as fallback

7. **`extract_graduation_year(transcript: str, doc)`**:
   - Searches in graduation context first
   - Validates year range (1950-2030)
   - Returns most recent year

8. **`extract_college(transcript: str, doc)`**:
   - Uses spaCy ORG entities
   - Filters for educational institutions
   - Returns college/university name

9. **`extract_degree(transcript: str, doc)`**:
   - Most complex extraction
   - Handles "degree in [specialization]" format
   - Searches for M.Tech/B.Tech in context
   - Prioritizes longer/more specific specializations
   - Returns degree with specialization if found

**Optimization**:
- Regex-based extractions first (faster)
- NLP only for complex entities
- Processes only relevant sentences for long transcripts
- Pre-compiled regex patterns
- Set-based skill lookups

**Specializations List**:
- Computer Science Engineering
- Computer Science
- Information Technology
- Various engineering fields
- Business degrees
- Science degrees

---

## 📁 Utils (`backend/app/utils/`)

### `__init__.py`
**Purpose**: Package marker

### `validation.py`
**Purpose**: Data validation and sanitization utilities  
**Key Functions**:

**`validate_email(email: str) -> bool`**:
- Validates email format using regex
- Returns True if valid

**`validate_phone(phone: str) -> bool`**:
- Validates phone number format
- Checks length and format
- Returns True if valid

**`validate_year(year: int) -> bool`**:
- Validates year range (1950-2030)
- Returns True if in valid range

**`sanitize_string(value: Optional[str], max_length: int = None) -> Optional[str]`**:
- Removes excessive whitespace
- Truncates to max_length if provided
- Returns None if input is None/empty

**`sanitize_skills(skills: Optional[str]) -> Optional[str]`**:
- Parses comma-separated skills
- Removes duplicates
- Sorts alphabetically
- Returns comma-separated string

**`validate_candidate_data(data: dict) -> Tuple[bool, str]`**:
- Validates all candidate fields
- Checks email format if provided
- Checks phone format if provided
- Validates year if provided
- Returns (is_valid, error_message)

---

## 📁 Frontend Directory (`frontend/`)

### `package.json`
**Purpose**: Node.js dependencies and scripts  
**Contents**:
- Dependencies: React, Vite, TailwindCSS, Axios, React Router
- Scripts: dev, build, preview
- Project metadata

### `vite.config.js`
**Purpose**: Vite build configuration  
**Contents**:
- React plugin configuration
- Development server settings
- Proxy configuration for API calls

### `tailwind.config.js`
**Purpose**: TailwindCSS configuration  
**Contents**:
- Content paths for CSS scanning
- Theme customization
- Plugin configuration

### `postcss.config.js`
**Purpose**: PostCSS configuration  
**Contents**:
- TailwindCSS plugin
- Autoprefixer configuration

### `index.html`
**Purpose**: HTML entry point  
**Contents**:
- Root div for React app
- Meta tags
- Title

---

## 📁 Frontend Source (`frontend/src/`)

### `main.jsx`
**Purpose**: React application entry point  
**Contents**:
- Renders App component
- Sets up React Router
- Imports global CSS

### `App.jsx`
**Purpose**: Main React application component  
**Key Functions**:
- Sets up routing
- Defines all routes
- Wraps app in Router

**Routes**:
- `/` - Dashboard
- `/upload` - Upload Audio page
- `/record` - Live Recording page
- `/candidates` - Candidate List
- `/candidates/:id` - Candidate Detail

**Components Used**:
- Navbar - Navigation bar
- Dashboard - Home page
- UploadAudio - File upload
- LiveRecording - Live recording
- CandidateList - List all candidates
- CandidateDetail - Single candidate view

### `index.css`
**Purpose**: Global CSS styles  
**Contents**:
- TailwindCSS directives
- Custom utility classes
- Minimal gradient styles
- Hover effects
- Animations

**Custom Classes**:
- `.hover-lift` - Hover lift effect
- `.gradient-subtle` - Subtle gradient background
- `.gradient-border` - Gradient border

---

## 📁 Frontend Components (`frontend/src/components/`)

### `Navbar.jsx`
**Purpose**: Navigation bar component  
**Features**:
- Responsive navigation
- Active route highlighting
- Links to all main pages
- Professional styling

**Links**:
- Dashboard
- Upload Audio
- Live Record
- Candidates

### `Dashboard.jsx`
**Purpose**: Home page / Dashboard  
**Features**:
- Displays total candidate count
- Quick action cards
- Recent candidates list
- Statistics overview

**Data Fetched**:
- Total candidates count
- Recent 5 candidates

**Quick Actions**:
- Upload Interview (link to upload page)
- Live Recording (link to record page)
- View All (link to candidates page)

### `UploadAudio.jsx`
**Purpose**: Audio file upload component  
**Features**:
- File input with drag-and-drop styling
- File validation
- Upload progress
- Processing status
- Displays transcript after processing
- Shows extracted information
- Auto-navigates to candidate detail after success

**State Management**:
- File selection
- Upload status
- Processing status
- Transcript display
- Extracted data display
- Error/success messages

**API Calls**:
- POST `/api/process-audio` - Combined workflow

### `LiveRecording.jsx`
**Purpose**: Live audio recording component  
**Features**:
- Browser MediaRecorder API integration
- Recording timer
- Visual recording indicator
- Start/Stop recording buttons
- Process recording button
- Reset/Record again functionality
- Displays transcript and extracted data

**State Management**:
- Recording status
- Recording time
- Audio blob
- Processing status
- Transcript
- Extracted data

**Functionality**:
- Requests microphone permission
- Records audio as WebM format
- Converts to blob for upload
- Processes recording through API

### `CandidateList.jsx`
**Purpose**: List all candidates component  
**Features**:
- Searchable candidate list
- Table view with all candidate info
- Delete functionality
- Link to candidate details
- Empty state handling
- Professional table design

**Search Functionality**:
- Searches by name, college, skills, degree, location
- Real-time filtering
- Case-insensitive

**Table Columns**:
- Name (with avatar)
- Email
- College
- Degree (badge)
- Experience (badge)
- Skills
- Actions (View, Delete)

### `CandidateDetail.jsx`
**Purpose**: Single candidate detail view  
**Features**:
- Full candidate information display
- Grid layout for fields
- Full transcript display
- Delete candidate button
- Back to list navigation
- Professional card design

**Information Displayed**:
- Name
- Email
- Phone
- Location
- College
- Degree
- Graduation Year
- Experience
- Skills (as badges)
- Full Transcript (scrollable)

**Actions**:
- Delete candidate (with confirmation)
- Back to candidates list

---

## 🔄 Data Flow

### Upload Workflow:
1. User uploads audio file → `UploadAudio.jsx`
2. File sent to → `POST /api/process-audio` (`workflow.py`)
3. File saved → `uploads/` directory
4. Audio transcribed → `transcription.py` (Whisper)
5. Transcript extracted → `extraction.py` (spaCy + Regex)
6. Data validated → `validation.py`
7. Saved to database → `schemas/candidate.py` → `database.py`
8. Response returned → Frontend displays result
9. User redirected → `CandidateDetail.jsx`

### Live Recording Workflow:
1. User starts recording → `LiveRecording.jsx`
2. Browser records audio → MediaRecorder API
3. User stops recording → Audio blob created
4. User processes → `POST /api/process-audio`
5. Same flow as upload workflow

### View Candidates:
1. User navigates → `CandidateList.jsx`
2. Fetches data → `GET /api/candidates`
3. Data retrieved → `candidates.py` → `schemas/candidate.py` → `database.py`
4. Displayed in table → User can search/filter
5. Click candidate → Navigate to `CandidateDetail.jsx`
6. Fetch details → `GET /api/candidates/{id}`
7. Display full information

---

## 🗄️ Database Schema

### `candidates` Table:
```sql
CREATE TABLE candidates (
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
```

**Indexes**:
- `idx_email` on `email`
- `idx_name` on `name`
- `idx_created_at` on `created_at`

---

## 🔧 Configuration Files

### Backend:
- `requirements.txt` - Python dependencies
- `install_whisper.bat/.sh` - Whisper installation scripts

### Frontend:
- `package.json` - Node.js dependencies
- `vite.config.js` - Build configuration
- `tailwind.config.js` - CSS framework config
- `postcss.config.js` - CSS processing config

---

## 📝 Key Design Patterns

1. **Separation of Concerns**:
   - API routes handle HTTP
   - Services handle business logic
   - Schemas handle database operations
   - Models handle data validation

2. **RESTful API**:
   - Standard HTTP methods
   - Resource-based URLs
   - JSON responses

3. **Component-Based Frontend**:
   - Reusable React components
   - Single responsibility
   - Props for data flow

4. **Error Handling**:
   - Try-catch blocks
   - Validation at multiple levels
   - User-friendly error messages

5. **Performance Optimization**:
   - Regex before NLP
   - Sentence filtering for long transcripts
   - Database indexes
   - Pre-compiled patterns

---

## 🚀 Deployment Considerations

### Backend:
- Set `UPLOAD_DIR` environment variable
- Configure CORS for production domain
- Use production ASGI server (Gunicorn + Uvicorn)
- Set up database backups
- Configure logging

### Frontend:
- Build for production: `npm run build`
- Serve static files from `dist/` directory
- Configure API proxy in production
- Set up environment variables for API URL

---

## 📚 Additional Notes

- **Audio Formats Supported**: MP3, WAV, M4A, MP4, OGG, FLAC, WEBM
- **Whisper Model**: Base model (can be upgraded)
- **NLP Model**: spaCy `en_core_web_sm`
- **Database**: SQLite (can be migrated to PostgreSQL)
- **File Storage**: Local filesystem (can be migrated to S3)

---

This documentation covers all files in the Transcript HR project. Each file has a specific purpose and works together to create a complete AI-powered recruitment assistant system.

