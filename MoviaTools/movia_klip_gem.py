# Gemmer udklipsholderens tekst i en fil:  gem(r"C:\...\fil.t3d")
import ctypes
from ctypes import wintypes
def gem(sti):
    u = ctypes.windll.user32; k = ctypes.windll.kernel32
    u.GetClipboardData.restype = wintypes.HANDLE
    k.GlobalLock.restype = ctypes.c_void_p
    k.GlobalLock.argtypes = [wintypes.HANDLE]
    k.GlobalUnlock.argtypes = [wintypes.HANDLE]
    if not u.OpenClipboard(None):
        raise RuntimeError("OpenClipboard fejlede")
    try:
        h = u.GetClipboardData(13)
        p = k.GlobalLock(h)
        txt = ctypes.wstring_at(p)
        k.GlobalUnlock(h)
    finally:
        u.CloseClipboard()
    open(sti, "w", encoding="utf-8").write(txt)
    return len(txt)
