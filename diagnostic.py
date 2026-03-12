#!/usr/bin/env python3
"""
Jarvis-2025 Quick Diagnostic
Run this to check if everything is configured correctly
"""

import sys
import os

print("=" * 70)
print("JARVIS-2025 QUICK DIAGNOSTIC".center(70))
print("=" * 70)
print()

issues = 0

# Test 1: Python Version
print("TEST 1: Python Version")
version = sys.version_info
print(f"  Version: {version.major}.{version.minor}.{version.micro}", end="")
if version.major >= 3 and version.minor >= 9:
    print(" ✅")
else:
    print(" ❌ (need 3.9+)")
    issues += 1
print()

# Test 2: Files
print("TEST 2: Required Files")
files = {
    "backend/feature.py": "Feature module",
    "backend/command.py": "Command module",
    "backend/config.py": "Config",
    "frontend/index.html": "Frontend",
    "requirements.txt": "Dependencies",
    "jarvis.db": "Database",
    "backend/cookie.json": "HuggingFace token"
}

for fpath, desc in files.items():
    status = "✅" if os.path.exists(fpath) else "❌"
    print(f"  {fpath:35} {status}")
    if not os.path.exists(fpath) and fpath != "jarvis.db":
        issues += 1
print()

# Test 3: Dependencies
print("TEST 3: Required Packages")
deps = {
    'cv2': 'OpenCV',
    'hugchat': 'HuggingChat',
    'pyaudio': 'PyAudio',
    'pywhatkit': 'PyWhatKit',
    'speech_recognition': 'SpeechRecognition',
    'eel': 'Eel',
    'pygame': 'Pygame',
    'numpy': 'NumPy'
}

for module, name in deps.items():
    try:
        __import__(module)
        print(f"  {name:20} ✅")
    except ImportError:
        print(f"  {name:20} ❌")
        issues += 1
print()

# Test 4: NumPy Version
print("TEST 4: NumPy Compatibility")
try:
    import numpy
    version = numpy.__version__
    major = int(version.split('.')[0])
    status = "✅" if major < 2 else "❌ (NumPy 2.x breaks OpenCV)"
    print(f"  NumPy {version}: {status}")
    if major >= 2:
        issues += 1
except ImportError:
    print("  NumPy: ❌ Not installed")
    issues += 1
print()

# Test 5: Microphone
print("TEST 5: Microphone")
try:
    import pyaudio
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    p.terminate()
    status = "✅" if device_count > 0 else "❌ (no devices found)"
    print(f"  Devices: {device_count} {status}")
    if device_count == 0:
        issues += 1
except Exception as e:
    print(f"  Error: {e} ❌")
    issues += 1
print()

# Test 6: Feature syntax
print("TEST 6: Feature Module Syntax")
try:
    import py_compile
    py_compile.compile("backend/feature.py", doraise=True)
    print("  Syntax: ✅")
except Exception as e:
    print(f"  Syntax: ❌ {e}")
    issues += 1
print()

# Summary
print("=" * 70)
if issues == 0:
    print("✅ ALL TESTS PASSED - Ready to run: python run.py".center(70))
else:
    print(f"❌ {issues} ISSUE(S) FOUND - See above for what to fix".center(70))
print("=" * 70)
