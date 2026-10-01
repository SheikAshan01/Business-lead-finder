"""SRA Business Lead Finder - Standalone Commercial Desktop Application Launcher.

Provides a 100% native Windows desktop experience:
- Zero dependency on external Node.js/Next.js dev servers
- In-process / daemon FastAPI server hosting both REST APIs and production Next.js frontend
- Native Edge WebView2 desktop application window (via pywebview) with official SRA glowing radar icon
- Seamless fallback to Windows Edge/Chrome standalone application window
- Clean lifecycle management and instant shutdown
"""

import os
import sys
import time
import signal
import threading
import subprocess
import urllib.request
from pathlib import Path


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

import uvicorn
from app.main import app

server_instance = None


def run_uvicorn_server():
    global server_instance
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="warning",
        access_log=False,
    )
    server_instance = uvicorn.Server(config)
    server_instance.run()


def is_service_ready(url: str = "http://127.0.0.1:8000/health") -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SRA-Desktop-Native"})
        with urllib.request.urlopen(req, timeout=1.0) as r:
            return r.status in (200, 304)
    except Exception:
        return False


def start_server_thread():
    if not is_service_ready():
        t = threading.Thread(target=run_uvicorn_server, daemon=True)
        t.start()

        # Wait up to 10 seconds for backend initialization
        start_time = time.time()
        while not is_service_ready() and (time.time() - start_time) < 10:
            time.sleep(0.1)


def launch_native_window():
    # 1. Start the single-port production server
    start_server_thread()

    # 2. Try native WebView2 Desktop Window (pywebview)
    try:
        import webview

        icon_file = str(ICON_PATH) if ICON_PATH.exists() else None

        window = webview.create_window(
            title="SRA Business Lead Finder - Commercial Edition",
            url="http://127.0.0.1:8000",
            width=1340,
            height=860,
            min_size=(1024, 700),
            background_color="#0b1220",
            text_select=True,
            zoomable=True,
        )
        webview.start(icon=icon_file)
        return
    except Exception as e:
        print(f"[-] pywebview native window failed: {e}")

    # 3. Fallback: Launch standalone app mode via Edge or Chrome
    app_url = "http://127.0.0.1:8000"
    browsers = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]

    for b in browsers:
        if os.path.exists(b):
            try:
                proc = subprocess.Popen([b, f"--app={app_url}"])
                proc.wait()
                return
            except Exception:
                pass

    # 4. Final fallback: system default browser
    import webbrowser
    webbrowser.open(app_url)


def cleanup():
    global server_instance
    if server_instance:
        server_instance.should_exit = True


def main():
    try:
        launch_native_window()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
