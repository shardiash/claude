# -*- coding: utf-8 -*-
"""
MOVIA EDITOR - starter.
Virker baade ved dobbeltklik og fra Unreal (Tools > Execute Python Script).
Selve editoren ligger i movia_editor_app.py.
"""
import os
import subprocess
import sys

MAPPE = os.path.dirname(os.path.abspath(__file__))

try:
    import unreal  # findes kun inde i Unreal
    INDE_I_UNREAL = True
except ImportError:
    INDE_I_UNREAL = False

if INDE_I_UNREAL:
    # Unreals Python har ikke PyQt6 - aabn editoren i sit eget vindue
    subprocess.Popen(['cmd', '/c', 'start', '', os.path.join(MAPPE, 'start_editor.bat')], cwd=MAPPE)
    unreal.log("[MOVIA] Movia Editor aabnes i sit eget vindue ...")
else:
    sys.path.insert(0, MAPPE)
    import runpy
    runpy.run_path(os.path.join(MAPPE, 'movia_editor_app.py'), run_name='__main__')
