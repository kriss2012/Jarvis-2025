# Jarvis-2025

A desktop assistant project that uses Eel for the frontend and a Python backend with speech, hotword detection, and Hugging Face chat integration.

Quick start

1. Create and activate a virtualenv (recommended):

```powershell
python -m venv .\envJarvis
& '.\envJarvis\Scripts\Activate.ps1'
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

2. (Optional) Export your Hugging Face cookies JSON and save to `backend/cookie.json` (private):

- Export cookies for huggingface.co as a JSON array and place the file at `backend/cookie.json`.

3. Run the app:

```powershell
python .\run.py
```

Notes
- `backend/cookie.json` is ignored in `.gitignore` because it contains auth cookies. Keep it private.
- `envJarvis/` is ignored.

License: MIT
