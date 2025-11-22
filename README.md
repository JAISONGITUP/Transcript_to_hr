# Transcript HR - AI Recruiting Assistant

An AI-powered system that processes HR interview conversations, extracts relevant candidate information, and stores it in a structured format. It automates recruitment workflow by turning raw audio into searchable candidate data.

## Tech Stack

### Backend
- Python 3.8+
- FastAPI
- OpenAI Whisper (local model)
- spaCy (NLP)
- SQLite

### Frontend
- React.js
- Vite
- TailwindCSS
- Axios

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 16+ and npm
- FFmpeg (required for Whisper audio processing)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Download spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

6. Create `.env` file (optional):
```bash
cp .env.example .env
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Start Backend Server

1. Activate virtual environment (if not already activated)
2. Navigate to backend directory
3. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Start Frontend Server

1. Navigate to frontend directory
2. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

1. **Upload Audio**: Go to the Upload page and select an interview audio file (MP3, WAV, M4A, etc.)
2. **Automatic Processing**: The system will:
   - Upload the file
   - Transcribe audio to text
   - Extract candidate information (name, college, degree, skills, etc.)
   - Save to database
3. **View Candidates**: Browse all candidates on the Candidates page
4. **Search**: Use the search bar to filter candidates
5. **View Details**: Click on any candidate to see full details and transcript

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload-audio` | Upload interview audio file |
| POST | `/api/transcribe` | Transcribe audio to text |
| POST | `/api/extract` | Extract candidate information from transcript |
| GET | `/api/candidates` | Get all candidates |
| GET | `/api/candidates/{id}` | Get candidate by ID |
| POST | `/api/candidates` | Create new candidate |
| DELETE | `/api/candidates/{id}` | Delete candidate |

## Extracted Information

The system extracts the following information from interview transcripts:

- Name
- Email
- Phone
- College/University
- Degree
- Graduation Year
- Experience
- Location
- Skills

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── api/                 # API routes
│   │   ├── models/              # Pydantic models
│   │   ├── schemas/             # Database schemas
│   │   ├── services/            # Business logic (transcription, extraction)
│   │   └── database/            # Database setup
│   ├── uploads/                 # Temporary audio storage
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Notes

- Audio files are stored temporarily in `backend/uploads/`
- The database file (`candidates.db`) is created automatically in the backend directory
- Whisper model is downloaded automatically on first use (base model)
- For better accuracy, you can use larger Whisper models (small, medium, large) by modifying `backend/app/services/transcription.py`

## Troubleshooting

### Whisper Installation Issues
If you encounter issues with Whisper, ensure FFmpeg is installed:
- Windows: Download from https://ffmpeg.org/download.html
- Mac: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

### spaCy Model Not Found
Run: `python -m spacy download en_core_web_sm`

### CORS Issues
If you encounter CORS errors, ensure the frontend URL is added to CORS origins in `backend/app/main.py`

## Future Enhancements

- PDF Resume export
- Multi-speaker diarization
- ATS integration
- Sentiment analysis
- Skill matching with job roles

## License

MIT License

