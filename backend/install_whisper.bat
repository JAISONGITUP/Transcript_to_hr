@echo off
REM Alternative installation script for Whisper on Windows if pip install fails

echo Installing Whisper dependencies...
python -m pip install --upgrade pip setuptools wheel

echo Installing PyTorch (CPU version)...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

echo Installing Whisper...
pip install git+https://github.com/openai/whisper.git

echo Installation complete!
pause

