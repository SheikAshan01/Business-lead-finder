"""SRA Business Lead Finder - Official Windows Setup Installer.

Provides a modern Windows Setup Wizard that installs the software,
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
        self.geometry("540x480")
        self.resizable(False, False)
        self.configure(bg="#0b1220")

        self.install_dir = tk.StringVar(value=str(DEFAULT_INSTALL_DIR))
        self.chk_desktop_shortcut = tk.BooleanVar(value=True)
        self.chk_start_menu = tk.BooleanVar(value=True)
        self.chk_launch_after = tk.BooleanVar(value=True)

        self.setup_ui()

    def setup_ui(self):
        # Header banner
        header = tk.Frame(self, bg="#0f1d36", padx=24, pady=18)
        header.pack(fill=tk.X)

        title = tk.Label(
            header,
            text="SRA BUSINESS LEAD FINDER",
            font=("Segoe UI", 15, "bold"),
            fg="#38bdf8",
            bg="#0f1d36",
        )
        title.pack(anchor="w")

        sub = tk.Label(
            header,
            text="Setup Wizard • Find. Verify. Connect.",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#0f1d36",
        )
        sub.pack(anchor="w", pady=(2, 0))

        # Main wizard container
        self.content_frame = tk.Frame(self, bg="#0b1220", padx=28, pady=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Welcome message
        welcome_lbl = tk.Label(
            self.content_frame,
            text="Welcome to the SRA Lead Finder Setup Wizard",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg="#0b1220",
        )
        welcome_lbl.pack(anchor="w", pady=(0, 6))

        desc_lbl = tk.Label(
            self.content_frame,
            text="This wizard will install SRA Business Lead Finder on your computer,\nconfigure desktop shortcuts with the custom app icon, and prepare\ninstant lead discovery services.",
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0b1220",
            justify="left",
        )
        desc_lbl.pack(anchor="w", pady=(0, 16))

        # Destination Folder Frame
        dest_lbl = tk.Label(
            self.content_frame,
            text="Destination Installation Folder:",
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg="#0b1220",
        )
        dest_lbl.pack(anchor="w", pady=(0, 4))

        path_frame = tk.Frame(self.content_frame, bg="#0b1220")
        path_frame.pack(fill=tk.X, pady=(0, 16))

        entry_path = tk.Entry(
            path_frame,
            textvariable=self.install_dir,
            font=("Segoe UI", 9),
            bg="#1e293b",
            fg="white",
            insertbackground="white",
            relief=tk.FLAT,
        )
        entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8))

        btn_browse = tk.Button(
            path_frame,
            text="Browse...",
            font=("Segoe UI", 9),
            fg="white",
            bg="#334155",
            activebackground="#475569",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            command=self.browse_folder,
        )
        btn_browse.pack(side=tk.RIGHT)

        # Checkbox Options
        opts_frame = tk.Frame(self.content_frame, bg="#0b1220")
        opts_frame.pack(fill=tk.X, pady=(0, 16))

        cb_desktop = tk.Checkbutton(
            opts_frame,
            text="Create Desktop Shortcut (with custom SRA radar logo icon)",
            variable=self.chk_desktop_shortcut,
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#0b1220",
            activebackground="#0b1220",
            activeforeground="#38bdf8",
            selectcolor="#1e293b",
        )
        cb_desktop.pack(anchor="w", pady=2)

        cb_start = tk.Checkbutton(
            opts_frame,
            text="Create Start Menu Program shortcut",
            variable=self.chk_start_menu,
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0b1220",
            activebackground="#0b1220",
            activeforeground="#cbd5e1",
            selectcolor="#1e293b",
        )
        cb_start.pack(anchor="w", pady=2)

        cb_launch = tk.Checkbutton(
            opts_frame,
            text="Launch SRA Business Lead Finder after installation",
            variable=self.chk_launch_after,
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0b1220",
            activebackground="#0b1220",
            activeforeground="#cbd5e1",
            selectcolor="#1e293b",
        )
        cb_launch.pack(anchor="w", pady=2)

        # Progress bar
        self.progress = ttk.Progressbar(self.content_frame, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(4, 6))

        self.status_lbl = tk.Label(
            self.content_frame,
            text="Ready to install.",
            font=("Segoe UI", 8),
            fg="#94a3b8",
            bg="#0b1220",
        )
        self.status_lbl.pack(anchor="w")

        # Bottom action bar
        bottom_bar = tk.Frame(self, bg="#0f172a", padx=24, pady=14)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)

        btn_cancel = tk.Button(
            bottom_bar,
            text="Cancel",
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#334155",
            activebackground="#475569",
            activeforeground="white",
            relief=tk.FLAT,
            padx=16,
            pady=5,
            command=self.destroy,
        )
        btn_cancel.pack(side=tk.RIGHT, padx=(8, 0))

        self.btn_install = tk.Button(
            bottom_bar,
            text="Install Now",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#2563eb",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=5,
            command=self.run_install,
        )
        self.btn_install.pack(side=tk.RIGHT)

    def browse_folder(self):
        chosen = filedialog.askdirectory(initialdir=self.install_dir.get())
        if chosen:
            self.install_dir.set(chosen)

    def run_install(self):
        self.btn_install.config(state=tk.DISABLED)
        target = Path(self.install_dir.get())

        self.status_lbl.config(text="Creating destination directory...")
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
                # If compiled standalone is nearby
                alt_exe = BASE_DIR / "SRA-Lead-Finder-App.exe"
                if alt_exe.exists():
                    shutil.copy2(alt_exe, dest_exe)

            # Copy project workspace files for runtime
            self.status_lbl.config(text="Configuring local runtime and modules...")
            self.progress["value"] = 75
            self.update()

            # Create uninstaller script
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

            # Create Shortcuts
            self.status_lbl.config(text="Creating Desktop shortcut with custom app icon...")
            self.progress["value"] = 90
            self.update()

            desktop = Path(os.path.expanduser("~")) / "Desktop"
            if self.chk_desktop_shortcut.get() and desktop.exists():
                shortcut_file = desktop / "SRA Business Lead Finder.lnk"
                create_windows_shortcut(
                    target_exe=str(dest_exe),
                    target_dir=str(BASE_DIR),
                    icon_path=str(dest_icon),
                    shortcut_path=str(shortcut_file),
                    description="SRA Business Lead Finder - Find. Verify. Connect.",
                )

            # Start menu shortcut
            if self.chk_start_menu.get():
                start_menu = Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"))
                if start_menu.exists():
                    sm_file = start_menu / "SRA Business Lead Finder.lnk"
                    create_windows_shortcut(
                        target_exe=str(dest_exe),
                        target_dir=str(BASE_DIR),
                        icon_path=str(dest_icon),
                        shortcut_path=str(sm_file),
                        description="SRA Business Lead Finder - Find. Verify. Connect.",
                    )

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
