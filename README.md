# Jarvis-2025

A desktop assistant project that uses Eel for the frontend and a Python backend with speech, hotword detection, and Hugging Face chat integration.

Quick start

### Step 1: Create Virtual Environment

```powershell
python -m venv .\envJarvis
& '.\envJarvis\Scripts\Activate.ps1'
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 2: Initialize Database

```powershell
python create_sample_db.py
```

### Step 3: Configure HuggingFace Cookies (Optional)

Export your HuggingFace cookies and save to `backend/cookie.json`

### Step 4: Run the Application

```powershell
python run.py
```

## Troubleshooting

**NumPy Compatibility Error:**
```
pip install 'numpy<2.0'
```

**PyAudio Issues:**
```
pipwin install pyaudio
```

**cv2.face Module Error:**
```
pip install opencv-contrib-python
```

## Notes

- `backend/cookie.json` is ignored (contains auth cookies)
- `envJarvis/` is ignored
- Database: `jarvis.db`

License: MIT
