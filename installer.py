"""SRA Business Lead Finder - Official Windows Setup Installer.

Provides a modern, spacious Windows Setup Wizard that installs the software,
embeds the custom app icon, and creates a desktop shortcut.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
SOURCE_EXE = BASE_DIR / "dist" / "SRA-Lead-Finder-App.exe"
SOURCE_ICON = BASE_DIR / "assets" / "icon.ico"
DEFAULT_INSTALL_DIR = Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\SRA Lead Finder"))


def create_windows_shortcut(target_exe: str, target_dir: str, icon_path: str, shortcut_path: str, description: str):
    vbs_code = f'''Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target_exe}"
oLink.WorkingDirectory = "{target_dir}"
oLink.IconLocation = "{icon_path}, 0"
oLink.Description = "{description}"
oLink.Save
'''
    vbs_path = os.path.join(tempfile.gettempdir(), f"shortcut_{os.getpid()}.vbs")
    try:
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_code)
        subprocess.run(["cscript", "//nologo", vbs_path], check=True, creationflags=0x08000000)
    finally:
        if os.path.exists(vbs_path):
            try:
                os.remove(vbs_path)
            except Exception:
                pass


class SetupInstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SRA Business Lead Finder Setup")
        
        # Generous, spacious dimensions requested by user
        window_width = 680
        window_height = 560
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(640, 520)
        self.configure(bg="#0b1220")

        # Set title bar icon
        if SOURCE_ICON.exists():
            try:
                self.iconbitmap(str(SOURCE_ICON))
            except Exception:
                pass

        # Center on screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.install_dir = tk.StringVar(value=str(DEFAULT_INSTALL_DIR))
        self.chk_desktop_shortcut = tk.BooleanVar(value=True)
        self.chk_start_menu = tk.BooleanVar(value=True)
        self.chk_launch_after = tk.BooleanVar(value=True)

        self.setup_ui()

    def setup_ui(self):
        # 1. TOP HEADER BANNER (Packed to TOP)
        header = tk.Frame(self, bg="#0f1d36", padx=28, pady=20)
        header.pack(side=tk.TOP, fill=tk.X)

        title_frame = tk.Frame(header, bg="#0f1d36")
        title_frame.pack(anchor="w")

        title = tk.Label(
            title_frame,
            text="SRA BUSINESS LEAD FINDER",
            font=("Segoe UI", 16, "bold"),
            fg="#38bdf8",
            bg="#0f1d36",
        )
        title.pack(side=tk.LEFT)

        tag = tk.Label(
            title_frame,
            text="v1.0",
            font=("Segoe UI", 8, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
            padx=6,
            pady=1,
        )
        tag.pack(side=tk.LEFT, padx=(8, 0))

        sub = tk.Label(
            header,
            text="Setup Wizard • Find. Verify. Connect. • Tamil Nadu Edition",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#0f1d36",
        )
        sub.pack(anchor="w", pady=(4, 0))

        # 2. BOTTOM ACTION BAR (Packed to BOTTOM FIRST to prevent being pushed off screen!)
        self.bottom_bar = tk.Frame(self, bg="#0f172a", padx=28, pady=16, highlightthickness=1, highlightbackground="#1e293b")
        self.bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)

        btn_cancel = tk.Button(
            self.bottom_bar,
            text="Cancel",
            font=("Segoe UI", 10),
            fg="#cbd5e1",
            bg="#334155",
            activebackground="#475569",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=7,
            cursor="hand2",
            command=self.destroy,
        )
        btn_cancel.pack(side=tk.RIGHT, padx=(10, 0))

        self.btn_install = tk.Button(
            self.bottom_bar,
            text="Install Now",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#2563eb",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief=tk.FLAT,
            padx=28,
            pady=7,
            cursor="hand2",
            command=self.run_install,
        )
        self.btn_install.pack(side=tk.RIGHT)

        # 3. MAIN SCROLLABLE/EXPANDING CONTENT AREA (Fills center)
        self.content_frame = tk.Frame(self, bg="#0b1220", padx=32, pady=24)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Welcome message
        welcome_lbl = tk.Label(
            self.content_frame,
            text="Welcome to the SRA Lead Finder Setup Wizard",
            font=("Segoe UI", 13, "bold"),
            fg="white",
            bg="#0b1220",
        )
        welcome_lbl.pack(anchor="w", pady=(0, 6))

        desc_lbl = tk.Label(
            self.content_frame,
            text="This wizard will install SRA Business Lead Finder on your computer,\nconfigure the desktop shortcut with the official app logo, and prepare\ninstant lead discovery services.",
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0b1220",
            justify="left",
        )
        desc_lbl.pack(anchor="w", pady=(0, 20))

        # Destination Folder Frame
        dest_lbl = tk.Label(
            self.content_frame,
            text="Destination Installation Folder:",
            font=("Segoe UI", 10, "bold"),
            fg="#94a3b8",
            bg="#0b1220",
        )
        dest_lbl.pack(anchor="w", pady=(0, 6))

        path_frame = tk.Frame(self.content_frame, bg="#0b1220")
        path_frame.pack(fill=tk.X, pady=(0, 20))

        entry_path = tk.Entry(
            path_frame,
            textvariable=self.install_dir,
            font=("Segoe UI", 10),
            bg="#1e293b",
            fg="white",
            insertbackground="white",
            relief=tk.FLAT,
        )
        entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=7, padx=(0, 10))

        btn_browse = tk.Button(
            path_frame,
            text="Browse...",
            font=("Segoe UI", 9, "bold"),
            fg="white",
            bg="#334155",
            activebackground="#475569",
            activeforeground="white",
            relief=tk.FLAT,
            padx=16,
            pady=4,
            cursor="hand2",
            command=self.browse_folder,
        )
        btn_browse.pack(side=tk.RIGHT)

        # Checkbox Options Frame
        opts_frame = tk.Frame(self.content_frame, bg="#0f172a", padx=16, pady=12, highlightthickness=1, highlightbackground="#1e293b")
        opts_frame.pack(fill=tk.X, pady=(0, 20))

        cb_desktop = tk.Checkbutton(
            opts_frame,
            text="Create Desktop Shortcut (with official SRA radar shield logo)",
            variable=self.chk_desktop_shortcut,
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#0f172a",
            activebackground="#0f172a",
            activeforeground="#38bdf8",
            selectcolor="#1e293b",
            cursor="hand2",
        )
        cb_desktop.pack(anchor="w", pady=3)

        cb_start = tk.Checkbutton(
            opts_frame,
            text="Create Start Menu Program shortcut",
            variable=self.chk_start_menu,
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0f172a",
            activebackground="#0f172a",
            activeforeground="#cbd5e1",
            selectcolor="#1e293b",
            cursor="hand2",
        )
        cb_start.pack(anchor="w", pady=3)

        cb_launch = tk.Checkbutton(
            opts_frame,
            text="Launch SRA Business Lead Finder immediately after installation",
            variable=self.chk_launch_after,
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0f172a",
            activebackground="#0f172a",
            activeforeground="#cbd5e1",
            selectcolor="#1e293b",
            cursor="hand2",
        )
        cb_launch.pack(anchor="w", pady=3)

        # Progress bar
        self.progress = ttk.Progressbar(self.content_frame, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(4, 6))

        self.status_lbl = tk.Label(
            self.content_frame,
            text="Ready to install. Click 'Install Now' below to begin.",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#0b1220",
        )
        self.status_lbl.pack(anchor="w")

    def browse_folder(self):
        chosen = filedialog.askdirectory(initialdir=self.install_dir.get())
        if chosen:
            self.install_dir.set(chosen)

    def run_install(self):
        self.btn_install.config(state=tk.DISABLED)
        target = Path(self.install_dir.get())

        self.status_lbl.config(text="Creating destination directory...", fg="#38bdf8")
        self.progress["value"] = 15
        self.update()

        try:
            target.mkdir(parents=True, exist_ok=True)

            # Copy icon
            self.status_lbl.config(text="Deploying application assets and logo icon...")
            self.progress["value"] = 35
            self.update()

            dest_icon = target / "icon.ico"
            if SOURCE_ICON.exists():
                shutil.copy2(SOURCE_ICON, dest_icon)

            # Copy executable
            self.status_lbl.config(text="Installing SRA Lead Finder executable...")
            self.progress["value"] = 60
            self.update()

            dest_exe = target / "SRA-Lead-Finder.exe"
            if SOURCE_EXE.exists():
                shutil.copy2(SOURCE_EXE, dest_exe)
            else:
                alt_exe = BASE_DIR / "SRA-Lead-Finder-App.exe"
                if alt_exe.exists():
                    shutil.copy2(alt_exe, dest_exe)

            # Create uninstaller script
            self.status_lbl.config(text="Configuring uninstaller...")
            self.progress["value"] = 75
            self.update()

            uninstaller_path = target / "uninstall.bat"
            with open(uninstaller_path, "w", encoding="utf-8") as f:
                f.write(f'''@echo off
echo Uninstalling SRA Business Lead Finder...
del /q "%USERPROFILE%\\Desktop\\SRA Business Lead Finder.lnk" 2>nul
del /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\SRA Business Lead Finder.lnk" 2>nul
rmdir /s /q "{target}"
echo Successfully removed SRA Business Lead Finder.
pause
''')

            # Create Shortcuts across all active Desktop directories (OneDrive + Local)
            self.status_lbl.config(text="Creating Desktop shortcut with custom app icon...")
            self.progress["value"] = 90
            self.update()

            desktop_dirs = [
                Path(os.path.expanduser("~")) / "OneDrive" / "Desktop",
                Path(os.path.expanduser("~")) / "Desktop",
            ]
            if self.chk_desktop_shortcut.get():
                for d in desktop_dirs:
                    if d.exists():
                        shortcut_file = d / "SRA Business Lead Finder.lnk"
                        create_windows_shortcut(
                            target_exe=str(dest_exe),
                            target_dir=str(BASE_DIR),
                            icon_path=str(dest_icon),
                            shortcut_path=str(shortcut_file),
                            description="SRA Business Lead Finder - Find. Verify. Connect.",
                        )

            # Start menu shortcuts
            if self.chk_start_menu.get():
                sm_dirs = [
                    Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")),
                    Path(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"),
                ]
                for sm in sm_dirs:
                    if sm.exists():
                        sm_file = sm / "SRA Business Lead Finder.lnk"
                        try:
                            create_windows_shortcut(
                                target_exe=str(dest_exe),
                                target_dir=str(BASE_DIR),
                                icon_path=str(dest_icon),
                                shortcut_path=str(sm_file),
                                description="SRA Business Lead Finder - Find. Verify. Connect.",
                            )
                        except Exception:
                            pass

            # Trigger Windows Shell icon refresh
            try:
                subprocess.run(
                    ["powershell", "-Command", "[System.Runtime.InteropServices.DllImport('Shell32.dll')] | Out-Null;"],
                    capture_output=True,
                    creationflags=0x08000000,
                )
            except Exception:
                pass

            self.progress["value"] = 100
            self.status_lbl.config(text="[+] Installation completed successfully!", fg="#4ade80")
            self.update()

            messagebox.showinfo(
                "Installation Complete",
                "SRA Business Lead Finder has been successfully installed!\n\n"
                "A shortcut with the official logo has been placed on your Desktop."
            )

            # Launch if requested
            if self.chk_launch_after.get() and dest_exe.exists():
                subprocess.Popen([str(dest_exe)], cwd=str(BASE_DIR))

            self.destroy()

        except Exception as err:
            self.status_lbl.config(text=f"Error: {err}", fg="#f87171")
            self.btn_install.config(state=tk.NORMAL)
            messagebox.showerror("Installation Error", f"Failed to complete installation:\n{err}")


def main():
    app = SetupInstallerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
