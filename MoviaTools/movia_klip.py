# -*- coding: utf-8 -*-
"""Kopierer en tekstfil til udklipsholderen (bruges af Claude til at indsaette blueprint-noder)."""
import ctypes, ctypes.wintypes as w, sys

def kopier(tekst):
    k32, u32 = ctypes.windll.kernel32, ctypes.windll.user32
    k32.GlobalAlloc.restype = w.HGLOBAL
    k32.GlobalAlloc.argtypes = [w.UINT, ctypes.c_size_t]
    k32.GlobalLock.restype = w.LPVOID
    k32.GlobalLock.argtypes = [w.HGLOBAL]
    k32.GlobalUnlock.argtypes = [w.HGLOBAL]
    u32.SetClipboardData.argtypes = [w.UINT, w.HANDLE]
    data = tekst.encode("utf-16-le") + b"\x00\x00"
    h = k32.GlobalAlloc(0x0042, len(data))
    p = k32.GlobalLock(h)
    ctypes.memmove(p, data, len(data))
    k32.GlobalUnlock(h)
    u32.OpenClipboard(None)
    u32.EmptyClipboard()
    u32.SetClipboardData(13, h)
    u32.CloseClipboard()

def kopier_fil(sti):
    kopier(open(sti, encoding="utf-8").read())
    print("[MOVIA] Kopieret til udklipsholder:", sti)

def gem_klip(sti):
    """Gemmer udklipsholderens tekst i en fil."""
    k32, u32 = ctypes.windll.kernel32, ctypes.windll.user32
    u32.GetClipboardData.restype = w.HANDLE
    k32.GlobalLock.restype = w.LPVOID
    k32.GlobalLock.argtypes = [w.HGLOBAL]
    k32.GlobalUnlock.argtypes = [w.HGLOBAL]
    u32.OpenClipboard(None)
    h = u32.GetClipboardData(13)
    p = k32.GlobalLock(h)
    t = ctypes.wstring_at(p)
    k32.GlobalUnlock(h)
    u32.CloseClipboard()
    open(sti, "w", encoding="utf-8").write(t)
    print("[MOVIA] Klip gemt:", sti, len(t))

def gem_klip_senere(sti, sek=8.0):
    import unreal, time
    slut = time.time() + sek
    st = {}
    def tik(dt):
        if time.time() >= slut:
            unreal.unregister_slate_post_tick_callback(st["h"])
            gem_klip(sti)
            unreal.log("[MOVIA] Klip gemt (forsinket): " + sti)
    st["h"] = unreal.register_slate_post_tick_callback(tik)
    print("[MOVIA] Gemmer klip om %.0f sek" % sek)
