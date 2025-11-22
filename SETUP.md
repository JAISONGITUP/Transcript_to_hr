## Prerequisites Check

Before starting, ensure you have:
- Python 3.8+ installed
- Node.js 16+ and npm installed
- FFmpeg installed (required for Whisper)

### Check FFmpeg Installation
```bash
ffmpeg -version
```

If not installed:
- **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg` or `sudo yum install ffmpeg`

## Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create and activate virtual environment**
```bash
# Windows
py -3.11 -m venv venv
venv\Scripts\activate
```
3. **Upgrade pip and build tools first** (recommended)
```bash
python -m pip install --upgrade pip setuptools wheel
```
4. **Install dependencies**
```bash
pip install -r requirements.txt
```
5. **Install spaCy model**
```bash
python -m spacy download en_core_web_sm
```
 if encounter erroe 
 'wget https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl'

6. **Start the server**
```bash
uvicorn app:app --reload --port 8000
```

✅ Backend should now be running at http://localhost:8000

## Frontend Setup

1. **Open a new terminal and navigate to frontend**
```bash
cd frontend
```
2. **Install dependencies**
```bash
npm install
```
3. **Start development server**
```bash
npm run dev
```
✅ Frontend should now be running at http://localhost:5173

## Testing the Application
Open http://localhost:5173 in your browser

