# Deadlock Simulator (Assets folder)

This folder contains the assets and small Python GUI programs for the Deadlock Simulator project (splash screen, intro, and simulator). It's prepared to be tracked with git.

Files of interest:
- `splash.py`, `intro.py`, `Moko.py`, `Mokoi.py` - small tkinter/pygame GUI scripts
- PNG/JPG/MP3 assets used by the GUI

Quick start (Windows):
1. Create and activate a Python virtual environment:

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

2. Install dependencies:

   pip install -r requirements.txt

3. Run the splash screen (which launches the intro):

   python splash.py

Notes:
- `tkinter` is part of the Python standard library on most installations. If you get import errors for `tkinter`, install the OS package that provides it (for example, on Ubuntu: `sudo apt-get install python3-tk`).
- `pygame` and `Pillow` are listed in `requirements.txt`.
