import os
import subprocess
import tempfile
from pathlib import Path

def setup_all_shortcuts():
    target_exe = r"D:\scrap_tool\dist\SRA-Lead-Finder-App.exe"
    icon_path = r"D:\scrap_tool\assets\icon.ico"
    work_dir = r"D:\scrap_tool"

    # All possible desktop locations (User, OneDrive, Public)
    desktop_dirs = [
        Path(os.path.expanduser("~")) / "OneDrive" / "Desktop",
        Path(os.path.expanduser("~")) / "Desktop",
        Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "Desktop",
    ]

    # Start menu locations (System-wide and User-specific)
    start_menu_dirs = [
        Path(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"),
        Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")),
    ]

    all_targets = []
    for d in desktop_dirs:
        if d.exists():
            all_targets.append(d / "SRA Business Lead Finder.lnk")

    for sm in start_menu_dirs:
        if sm.exists():
            all_targets.append(sm / "SRA Business Lead Finder.lnk")

    print(f"Deploying shortcuts to {len(all_targets)} locations...")

    for lnk in all_targets:
        try:
            # Delete old blank file if present
            if lnk.exists():
                try:
                    os.remove(lnk)
                except Exception:
                    pass

            vbs = f'''Set sh = CreateObject("WScript.Shell")
Set sc = sh.CreateShortcut("{lnk}")
sc.TargetPath = "{target_exe}"
sc.WorkingDirectory = "{work_dir}"
sc.IconLocation = "{icon_path}, 0"
sc.Description = "SRA Business Lead Finder - Find. Verify. Connect."
sc.Save
'''
            tmp = os.path.join(tempfile.gettempdir(), f"sc_{os.getpid()}_{hash(str(lnk)) % 10000}.vbs")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(vbs)

            res = subprocess.run(["cscript", "//nologo", tmp], capture_output=True, text=True)
            if os.path.exists(tmp):
                os.remove(tmp)

            print(f"[+] Created shortcut at: {lnk} (Size: {lnk.stat().st_size} bytes)")
        except Exception as e:
            print(f"[-] Failed for {lnk}: {e}")

    # Also notify Windows Shell to refresh desktop icons
    try:
        ps_refresh = '''
$code = @'
[System.Runtime.InteropServices.DllImport("Shell32.dll")]
public static extern int SHChangeNotify(int eventId, int flags, IntPtr item1, IntPtr item2);
'@
$type = Add-Type -MemberDefinition $code -Name ShellUtil -Namespace WinAPI -PassThru
$type::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)
'''
        subprocess.run(["powershell", "-Command", ps_refresh], capture_output=True)
        print("[+] Triggered Windows Shell icon cache refresh!")
    except Exception as e:
        print(f"Icon refresh notice: {e}")

if __name__ == "__main__":
    setup_all_shortcuts()
