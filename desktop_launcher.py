"""SRA Business Lead Finder - Standalone Windows Desktop Application Launcher.

Provides a native Windows desktop GUI with one-click startup, service health monitoring,
instant app launching in desktop mode, and clean process lifecycle management.
"""

import os
import signal
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


def get_project_root() -> Path:
    candidates = [
        Path(r"D:\scrap_tool"),
        Path(sys.executable).resolve().parent.parent,
        Path(sys.executable).resolve().parent,
        Path(__file__).resolve().parent,
    ]
    for c in candidates:
        if (c / "backend").exists() and (c / "frontend").exists():
            return c
    return Path(r"D:\scrap_tool")


PROJECT_ROOT = get_project_root()
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def get_python_exe() -> Path:
    candidates = [
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",
        Path(r"D:\scrap_tool\.venv\Scripts\python.exe"),
        Path(r"C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return Path(sys.executable)


VENV_PYTHON = get_python_exe()
CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

backend_proc = None
frontend_proc = None


def is_service_ready(url: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SRA-Desktop-Launcher"})
        with urllib.request.urlopen(req, timeout=1.5) as r:
            return r.status in (200, 304, 307, 401)
    except Exception:
        return False


def start_services():
    global backend_proc, frontend_proc

    # 1. Start Backend if not already running on port 8000
    if not is_service_ready("http://localhost:8000/health"):
        try:
            backend_cmd = [
                str(VENV_PYTHON),
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ]
            backend_proc = subprocess.Popen(
                backend_cmd,
                cwd=str(BACKEND_DIR),
                creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            print(f"Error starting backend: {e}")

    # 2. Start Frontend if not already running on port 3000
    if not is_service_ready("http://localhost:3000"):
        try:
            npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
            frontend_proc = subprocess.Popen(
                [npm_cmd, "run", "dev"],
                cwd=str(FRONTEND_DIR),
                creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            print(f"Error starting frontend: {e}")


def launch_browser(path=""):
    target_url = f"http://localhost:3000{path}"

    # If frontend not ready yet, inform user
    if not is_service_ready("http://localhost:3000"):
        messagebox.showinfo(
            "Engines Booting",
            "SRA services are currently starting up.\nPlease wait 3-5 seconds and click again!"
        )
        return

    # Try launching in Chrome or Edge standalone app mode for a native window feel
    browsers = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]

    for b in browsers:
        if os.path.exists(b):
            try:
                subprocess.Popen([b, f"--app={target_url}"], creationflags=CREATE_NO_WINDOW)
                return
            except Exception:
                pass

    # Fallback to default browser
    webbrowser.open(target_url)


def stop_services():
    global backend_proc, frontend_proc
    if backend_proc:
        try:
            backend_proc.terminate()
            backend_proc.wait(timeout=2)
        except Exception:
            try:
                backend_proc.kill()
            except Exception:
                pass
    if frontend_proc:
        try:
            frontend_proc.terminate()
            frontend_proc.wait(timeout=2)
        except Exception:
            try:
                frontend_proc.kill()
            except Exception:
                pass


class DesktopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SRA Business Lead Finder - Desktop")
        self.geometry("480x540")
        self.resizable(False, False)
        self.configure(bg="#0b1220")

        self.has_auto_launched = False

        # Set title bar icon
        icon_path = PROJECT_ROOT / "assets" / "icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        # Window styling
        self.setup_ui()

        # Start services in background
        self.after(200, self.initial_boot)

    def setup_ui(self):
        # Header banner
        header_frame = tk.Frame(self, bg="#0f1d36", padx=20, pady=20)
        header_frame.pack(fill=tk.X)

        title_lbl = tk.Label(
            header_frame,
            text="SRA LEAD FINDER",
            font=("Segoe UI", 16, "bold"),
            fg="#38bdf8",
            bg="#0f1d36",
        )
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(
            header_frame,
            text="Find. Verify. Connect. • Desktop Edition",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#0f1d36",
        )
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Body container
        body_frame = tk.Frame(self, bg="#0b1220", padx=24, pady=20)
        body_frame.pack(fill=tk.BOTH, expand=True)

        # Status indicator box
        self.status_box = tk.Label(
            body_frame,
            text="[*] Initializing Local Engines...",
            font=("Segoe UI", 10, "italic"),
            fg="#38bdf8",
            bg="#0f172a",
            padx=12,
            pady=12,
            relief=tk.FLAT,
        )
        self.status_box.pack(fill=tk.X, pady=(0, 20))

        # Launch Main Web App Button
        self.btn_open = tk.Button(
            body_frame,
            text="Open Lead Finder (Desktop Window)",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#2563eb",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief=tk.FLAT,
            padx=16,
            pady=12,
            cursor="hand2",
            command=lambda: launch_browser("/"),
        )
        self.btn_open.pack(fill=tk.X, pady=6)

        # Pipeline Button
        self.btn_pipeline = tk.Button(
            body_frame,
            text="CRM Sales Pipeline (Kanban)",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#4f46e5",
            activebackground="#4338ca",
            activeforeground="white",
            relief=tk.FLAT,
            padx=16,
            pady=10,
            cursor="hand2",
            command=lambda: launch_browser("/pipeline"),
        )
        self.btn_pipeline.pack(fill=tk.X, pady=6)

        # Scraper Button
        self.btn_scraper = tk.Button(
            body_frame,
            text="New Business Discovery Job",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#0891b2",
            activebackground="#0e7490",
            activeforeground="white",
            relief=tk.FLAT,
            padx=16,
            pady=10,
            cursor="hand2",
            command=lambda: launch_browser("/scraper"),
        )
        self.btn_scraper.pack(fill=tk.X, pady=6)

        # Leads Button
        self.btn_leads = tk.Button(
            body_frame,
            text="All Discovered Leads & WhatsApp",
            font=("Segoe UI", 10),
            fg="#e2e8f0",
            bg="#1e293b",
            activebackground="#334155",
            activeforeground="white",
            relief=tk.FLAT,
            padx=16,
            pady=9,
            cursor="hand2",
            command=lambda: launch_browser("/leads"),
        )
        self.btn_leads.pack(fill=tk.X, pady=6)

        # Footer exit
        footer_frame = tk.Frame(self, bg="#0b1220", padx=24, pady=12)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        exit_btn = tk.Button(
            footer_frame,
            text="Stop & Exit SRA Lead Finder",
            font=("Segoe UI", 9),
            fg="#f87171",
            bg="#1e293b",
            activebackground="#ef4444",
            activeforeground="white",
            relief=tk.FLAT,
            pady=6,
            cursor="hand2",
            command=self.on_closing,
        )
        exit_btn.pack(fill=tk.X)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def initial_boot(self):
        self.status_box.config(text="[*] Starting FastAPI Backend & Next.js Engine...")
        self.update()
        start_services()

        # Poll until ready
        self.poll_readiness(0)

    def poll_readiness(self, attempts: int):
        backend_ok = is_service_ready("http://localhost:8000/health")
        frontend_ok = is_service_ready("http://localhost:3000")

        if backend_ok and frontend_ok:
            self.status_box.config(
                text="[+] SRA Services Active & Ready (Port 3000 & 8000)",
                fg="#4ade80",
            )
            # ONLY auto-launch window AFTER services are confirmed ready!
            if not self.has_auto_launched:
                self.has_auto_launched = True
                launch_browser("/")
        elif attempts < 45:
            dots = "." * ((attempts % 4) + 1)
            msg = f"[*] Connecting to engines{dots}"
            if not backend_ok and not frontend_ok:
                msg = f"[*] Booting Backend & Frontend{dots}"
            elif not frontend_ok:
                msg = f"[*] Next.js compiling frontend{dots}"
            elif not backend_ok:
                msg = f"[*] FastAPI backend starting{dots}"

            self.status_box.config(text=msg, fg="#38bdf8")
            self.after(1000, lambda: self.poll_readiness(attempts + 1))
        else:
            self.status_box.config(
                text="[!] Engine start delayed. Click Open when ready.",
                fg="#facc15",
            )

    def on_closing(self):
        self.status_box.config(text="[*] Closing application...", fg="#f87171")
        self.update()
        stop_services()
        self.destroy()


def main():
    app = DesktopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
