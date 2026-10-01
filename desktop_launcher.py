"""SRA Business Lead Finder - Standalone Commercial Desktop Application Launcher.

Provides a 100% native Windows desktop experience:
- Zero external Node.js/Next.js dependencies
- Single-port FastAPI server hosting both backend REST APIs and production static frontend
- Dedicated isolated native desktop window with official SRA branding
- Clean lifecycle management: auto-terminates backend when desktop window closes
"""

import io
import os
import sys
import time
import signal
import threading
import subprocess
import urllib.request
import traceback
from pathlib import Path

# Explicit imports for PyInstaller dependency analysis
import fastapi
import starlette
import pydantic
import pydantic_settings
import sqlalchemy
import uvicorn
import webview
import passlib
import jose
import httpx
import bs4
import lxml
import rapidfuzz
import openpyxl

# In PyInstaller windowed/noconsole mode, stdout and stderr are None, causing isatty() errors in logging
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()


LOG_FILE = Path(os.path.expandvars(r"%TEMP%\sra_desktop_launcher.log"))


def log(msg: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def get_project_root() -> Path:
    candidates = [
        Path(r"D:\scrap_tool"),
        Path(__file__).resolve().parent,
        Path(sys.executable).resolve().parent,
    ]
    if hasattr(sys, "_MEIPASS"):
        candidates.insert(0, Path(sys._MEIPASS))

    for c in candidates:
        if (c / "backend").exists():
            return c
    return Path(r"D:\scrap_tool")


PROJECT_ROOT = get_project_root()
BACKEND_DIR = PROJECT_ROOT / "backend"
ICON_PATH = PROJECT_ROOT / "assets" / "icon.ico"

# Add backend directory to sys.path
sys.path.insert(0, str(BACKEND_DIR))

log(f"Starting SRA Desktop Launcher. PROJECT_ROOT={PROJECT_ROOT}")

try:
    import uvicorn
    from app.main import app
    log("FastAPI app imported successfully.")
except Exception as e:
    log(f"Fatal error importing FastAPI app: {e}\n{traceback.format_exc()}")
    raise

import ctypes
from ctypes import wintypes
import webview

server_instance = None
mutex_handle = None


def acquire_single_instance_mutex() -> bool:
    """Ensure only one instance of SRA Lead Finder runs at any time."""
    global mutex_handle
    try:
        mutex_name = "Local\\SRA_Lead_Finder_Single_Instance_Mutex"
        mutex_handle = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
        last_error = ctypes.windll.kernel32.GetLastError()
        ERROR_ALREADY_EXISTS = 183
        if last_error == ERROR_ALREADY_EXISTS:
            log("Another instance of SRA Lead Finder is already running.")
            # Bring existing window to front
            hwnd = ctypes.windll.user32.FindWindowW(None, "SRA Business Lead Finder")
            if hwnd:
                SW_RESTORE = 9
                ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
                ctypes.windll.user32.SetForegroundWindow(hwnd)
            return False
        return True
    except Exception as e:
        log(f"Warning acquiring mutex: {e}")
        return True


def run_uvicorn_server():
    global server_instance
    try:
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=8000,
            log_config=None,
            log_level="warning",
            access_log=False,
            use_colors=False,
        )
        server_instance = uvicorn.Server(config)
        server_instance.run()
    except Exception as e:
        log(f"Uvicorn runtime error: {e}\n{traceback.format_exc()}")


def is_service_ready(url: str = "http://127.0.0.1:8000/health") -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SRA-Desktop-Native"})
        with urllib.request.urlopen(req, timeout=1.0) as r:
            return r.status in (200, 304)
    except Exception:
        return False


def start_server_thread():
    if not is_service_ready():
        log("Starting Uvicorn backend thread...")
        t = threading.Thread(target=run_uvicorn_server, daemon=True)
        t.start()

        # Wait up to 10 seconds for backend initialization
        start_time = time.time()
        while not is_service_ready() and (time.time() - start_time) < 10:
            time.sleep(0.1)

        if is_service_ready():
            log("Backend confirmed online at http://127.0.0.1:8000")
        else:
            log("Warning: Backend readiness check timed out.")
    else:
        log("Backend already active on http://127.0.0.1:8000")


def launch_native_window():
    # 1. Start backend server
    start_server_thread()

    app_url = "http://127.0.0.1:8000"
    profile_dir = Path(os.path.expandvars(r"%LOCALAPPDATA%\SRA Lead Finder\App_Data"))
    profile_dir.mkdir(parents=True, exist_ok=True)

    # 2. Launch true native application window via PyWebView (WebView2 engine)
    try:
        log("Launching native PyWebView window...")
        window = webview.create_window(
            title="SRA Business Lead Finder",
            url=app_url,
            width=1366,
            height=860,
            min_size=(1024, 700),
            confirm_close=False,
            text_select=True,
        )
        icon_arg = str(ICON_PATH) if ICON_PATH.exists() else None
        webview.start(
            icon=icon_arg,
            storage_path=str(profile_dir),
            debug=False,
        )
        log("Native desktop application window closed by user.")
        return
    except Exception as e:
        log(f"PyWebView error, trying browser fallback: {e}\n{traceback.format_exc()}")

    # 3. Fallback: Edge App Mode if PyWebView fails
    browsers = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for b in browsers:
        if os.path.exists(b):
            try:
                log(f"Launching fallback browser window via: {b}")
                cmd = [
                    b,
                    f"--user-data-dir={profile_dir}",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-background-mode",
                    "--disable-features=msStartupBoost",
                    f"--app={app_url}",
                    "--window-size=1360,860",
                ]
                proc = subprocess.Popen(cmd)
                proc.wait()
                log("Fallback browser window closed by user.")
                return
            except Exception as e:
                log(f"Failed fallback browser window ({b}): {e}")

    # 4. Ultimate Fallback: default web browser
    log("Ultimate fallback: opening in system default browser")
    import webbrowser
    webbrowser.open(app_url)
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass


def cleanup():
    global server_instance, mutex_handle
    log("Cleaning up and stopping backend...")
    if server_instance:
        server_instance.should_exit = True

    # Release SQLite database connection pools to prevent file locking in temp
    try:
        from app.db import engine
        engine.dispose()
    except Exception:
        pass

    if mutex_handle:
        try:
            ctypes.windll.kernel32.CloseHandle(mutex_handle)
        except Exception:
            pass

    time.sleep(0.3)


def main():
    if not acquire_single_instance_mutex():
        return

    try:
        launch_native_window()
    except Exception as e:
        log(f"Fatal error in main: {e}\n{traceback.format_exc()}")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
