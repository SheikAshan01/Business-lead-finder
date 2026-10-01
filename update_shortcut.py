import os
import subprocess
import tempfile

def update():
    desktops = [
        r"C:\Users\User\OneDrive\Desktop",
        r"C:\Users\User\Desktop",
    ]
    target_exe = r"D:\scrap_tool\dist\SRA-Lead-Finder-App.exe"
    icon_ico = r"D:\scrap_tool\assets\icon.ico"

    for d in desktops:
        if os.path.exists(d):
            lnk = os.path.join(d, "SRA Business Lead Finder.lnk")
            vbs = f'''Set sh = CreateObject("WScript.Shell")
Set sc = sh.CreateShortcut("{lnk}")
sc.TargetPath = "{target_exe}"
sc.WorkingDirectory = "D:\\scrap_tool"
sc.IconLocation = "{icon_ico}"
sc.Description = "SRA Business Lead Finder - Find. Verify. Connect."
sc.Save
'''
            tmp = os.path.join(tempfile.gettempdir(), f"icon_{os.getpid()}.vbs")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(vbs)
            subprocess.run(["cscript", "//nologo", tmp], check=True)
            if os.path.exists(tmp):
                os.remove(tmp)
            print(f"Updated shortcut at: {lnk}")

    # Tell Windows Shell to clear and refresh icon cache
    ps = '''
$code = @'
[System.Runtime.InteropServices.DllImport("Shell32.dll")]
public static extern int SHChangeNotify(int eventId, int flags, IntPtr item1, IntPtr item2);
'@
$type = Add-Type -MemberDefinition $code -Name ShellUtil -Namespace WinAPI -PassThru
$type::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)
'''
    subprocess.run(["powershell", "-Command", ps], capture_output=True)
    print("Notified Shell32 SHChangeNotify to refresh desktop icons!")

if __name__ == "__main__":
    update()
