# tools.py

import os
import subprocess


def open_app(app_name):
    """
    Opens an application using the system shell.
    Example: open_app("notepad")
    """
    try:
        subprocess.Popen(app_name, shell=True)
        return f"Opened {app_name}"
    except Exception as e:
        return f"Failed to open {app_name}: {e}"


def read_file(file_path):
    """
    Reads a text file safely on Windows.
    Tries UTF-8, UTF-16, then falls back to a safe read.
    """
    if not os.path.exists(file_path):
        return "File not found."

    # 1️⃣ Try UTF-8
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        pass

    # 2️⃣ Try UTF-16 (Windows default for echo)
    try:
        with open(file_path, "r", encoding="utf-16") as f:
            return f.read()
    except UnicodeDecodeError:
        pass

    # 3️⃣ LAST RESORT: read without crashing
    try:
        with open(file_path, "r", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"Failed to read file: {e}"
