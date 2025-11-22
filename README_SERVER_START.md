# How to Start the Servers Correctly

## Problem
You were getting `ECONNRESET` errors because multiple backend servers were running simultaneously, and the frontend was connecting to the wrong one (without timeout configuration).

## Solution: Use the Startup Scripts

### Backend Server

**Option 1: Use the PowerShell Script (Recommended)**
```powershell
cd "C:\Users\JAISON ALEXANDER\Documents\Projects\transcripto-hr - Copy\backend"
.\start_backend.ps1
```

**Option 2: Manual Start**
```powershell
cd "C:\Users\JAISON ALEXANDER\Documents\Projects\transcripto-hr - Copy\backend"

# Kill any existing processes on port 8000
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess -Unique | 
    ForEach-Object { Stop-Process -Id $_ -Force }

# Wait a moment
Start-Sleep -Seconds 2

# Start backend with timeout
.\venv\Scripts\Activate.ps1
uvicorn app:app --reload --timeout-keep-alive 600
```

### Frontend Server

```powershell
cd "C:\Users\JAISON ALEXANDER\Documents\Projects\transcripto-hr - Copy\frontend"
npm run dev
```

## Verification

After starting both servers, verify they're running correctly:

1. **Check Backend**: Open http://localhost:8000 in your browser
   - You should see: `{"message":"Transcript HR API is running"}`

2. **Check Frontend**: Open http://localhost:5173
   - You should see the application UI

3. **Check Ports**:
   ```powershell
   netstat -ano | findstr :8000
   netstat -ano | findstr :5173
   ```
   - You should see ONLY ONE process for each port

## Testing the Fix

1. Upload a small audio file (< 1 minute)
2. Watch the backend terminal for logs:
   ```
   INFO: Transcribing audio: /path/to/file.mp3 (X.XX MB)
   INFO: Transcription complete. Length: XXXX characters
   INFO: Candidate saved with ID: X
   ```
3. The frontend should show "Processing..." and then redirect to the candidate detail page
4. **No more ECONNRESET errors!** ✅

## Troubleshooting

### If you still get ECONNRESET:

1. **Stop ALL servers** (Ctrl+C in all terminals)
2. **Kill all processes on port 8000**:
   ```powershell
   Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | 
       Select-Object -ExpandProperty OwningProcess -Unique | 
       ForEach-Object { Stop-Process -Id $_ -Force }
   ```
3. **Wait 5 seconds**
4. **Restart using the startup script**

### If port 8000 is still in use:

```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the specific PID (replace XXXXX with the actual PID)
taskkill /F /PID XXXXX
```

## Configuration Summary

The following timeouts have been configured:

- **Vite Proxy**: 600 seconds (10 minutes)
- **Axios Request**: 600 seconds (10 minutes)
- **Uvicorn Keep-Alive**: 600 seconds (10 minutes)

This should handle audio files up to ~30 minutes in length.
