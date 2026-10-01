"""SRA Business Lead Finder - Standalone Commercial Desktop Application Launcher.

Provides a 100% native Windows desktop experience:
- Zero external Node.js/Next.js dependencies
- Single-port FastAPI server hosting both backend REST APIs and production static frontend
- Dedicated isolated native desktop window with official SRA branding
- Clean lifecycle management: auto-terminates backend when desktop window closes
"""

import os
import sys
import time
import signal
import threading
import subprocess
import urllib.request
import traceback
from pathlib import Path


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

server_instance = None


def run_uvicorn_server():
    global server_instance
    try:
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="warning",
            access_log=False,
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


def launch_native_window():
    # 1. Start backend server
    start_server_thread()

    app_url = "http://127.0.0.1:8000"
    profile_dir = Path(os.path.expandvars(r"%LOCALAPPDATA%\SRA Lead Finder\App_Data"))
    profile_dir.mkdir(parents=True, exist_ok=True)

    # 2. Try launching dedicated isolated application window via Edge or Chrome
    browsers = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]

    for b in browsers:
        if os.path.exists(b):
            try:
                log(f"Launching desktop application window via: {b}")
                cmd = [
                    b,
                    f"--user-data-dir={profile_dir}",
                    f"--app={app_url}",
                    "--window-size=1360,860",
                ]
                proc = subprocess.Popen(cmd)
                proc.wait()
                log("Desktop application window closed by user.")
                return
            except Exception as e:
                log(f"Failed launching browser window ({b}): {e}")

    # 3. Fallback: default browser
    log("Fallback: opening in default browser")
    import webbrowser
    webbrowser.open(app_url)
    # Keep server running until user terminates or exits
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass


def cleanup():
    global server_instance
    log("Cleaning up and stopping backend...")
    if server_instance:
        server_instance.should_exit = True


def main():
    try:
        launch_native_window()
    except Exception as e:
        log(f"Fatal error in main: {e}\n{traceback.format_exc()}")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
