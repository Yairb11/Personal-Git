import shutil
import sys
from PyQt6 import QtWidgets 
from MyWidgets.BashWindow import *
import getpass
import os
import winreg

CREATE_NO_WINDOW = 0x08000000

def is_valid_bash(bash_path):
    if not bash_path or not os.path.exists(bash_path):
        return False
    try:
        result = subprocess.run(
            [bash_path, "-c", "echo verify_working"], 
            capture_output=True, 
            text=True, 
            creationflags=CREATE_NO_WINDOW,
            timeout=3
        )
        return result.returncode == 0 and "verify_working" in result.stdout
    except Exception:
        return False

def find_bash_universally():
    path_from_which = shutil.which("bash")
    if is_valid_bash(path_from_which):
        return path_from_which
    
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\GitForWindows")
        install_path, _ = winreg.QueryValueEx(key, "InstallPath")
        registry_bash_path = os.path.join(install_path, "bin", "bash.exe")
        
        if is_valid_bash(registry_bash_path):
            return registry_bash_path
    except Exception:
        pass 
    
    search_roots = [
        os.environ.get("ProgramW6432"),
        os.environ.get("ProgramFiles(x86)"), 
        os.environ.get("LOCALAPPDATA")       
    ]
    for root_dir in search_roots:
        if not root_dir or not os.path.exists(root_dir):
            continue
            
        for dirpath, _, filenames in os.walk(root_dir):
            if "Microsoft" in dirpath or "NVIDIA" in dirpath:
                continue
                
            if "bash.exe" in filenames:
                potential_bash = os.path.join(dirpath, "bash.exe")
                if is_valid_bash(potential_bash):
                    return potential_bash
    return None

if __name__ == "__main__":
    bash_path = find_bash_universally()
    user_name = getpass.getuser()
    computer_name = os.environ.get('COMPUTERNAME')
    desktop_app = QtWidgets.QApplication(sys.argv)
    window = BashWindow(bash_path, user_name, computer_name)
 
    window.show()
    sys.exit(desktop_app.exec())
 