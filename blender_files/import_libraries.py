import sys
import subprocess
import os
import platform
import bpy


def python_exec():
    print(sys.prefix)
    return os.path.join(sys.prefix, 'bin', 'python.exe')

def installModule(packageName):

    try:
        subprocess.call([python_exe, "import ", packageName])
    except:
        python_exe = python_exec()
       # upgrade pip
        subprocess.call([python_exe, "-m", "ensurepip"])
        subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
       # install required packages
        subprocess.call([python_exe, "-m", "pip", "install", packageName])
        
installModule("pandas")

import pandas as pd