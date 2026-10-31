# -*- coding: utf-8 -*-
"""MOVIA TEMA - saetter spillets Atron-farvetema (bus-computerens Atron Colors Day/Night).
Gamle vaerdier gemmes i _tema_backup.txt (koer med GENDAN=True for at gaa tilbage)."""
import unreal, re, os
MAPPE = r"C:\Users\tacci\Documents\The Bus\MoviaTools"
UD = os.path.join(MAPPE, "_tema_ud.txt")
BACKUP = os.path.join(MAPPE, "_tema_backup.txt")
BP = "/Game/Gameplay/Vehicles/Common/BP_BoardComputer_TheBus_NAtron"
try: GENDAN
except NameError: GENDAN = False

# Movia-tema (sRGB hex)
TEMA = {
    "TextBright": "#FFFFFF",
    "TextDark": "#15181D",
    "BackgroundWhite": "#E9EDF2",
    "BackgroundBlack": "#0F1115",
    "BackgroundBlueBright": "#3D7BEA",
    "BackgroundBlueMid": "#2B313B",
    "BackgroundBlueDark": "#1B1F25",
    "BackgroundGreyBright2": "#C9D1DC",
    "BackgroundGreyBright1": "#8A93A3",
    "BackgroundGreyMid": "#4A5260",
    "ButtonScaleDefault": "#FFFFFF",
    "ButtonScaleColored": "#FFFFFF",
    "ButtonSelected": "#1E5FD6",
}
NAT_LYS = 0.75

def lin(h):
    h = h.lstrip("#")
    def c(v):
        v = int(v, 16) / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return "(R=%.6f,G=%.6f,B=%.6f,A=1.000000)" % (c(h[0:2]), c(h[2:4]), c(h[4:6]))

out = []
bp = unreal.load_asset(BP)
cls = unreal.load_object(None, BP + "." + BP.split("/")[-1] + "_C")
cdo = unreal.get_default_object(cls)

def felt(navn):
    for n in (navn, "atron_colors_" + navn.split()[-1].lower()):
        try: return n, cdo.get_editor_property(n)
        except Exception: pass
    return None, None

def ny_tekst(txt, nat):
    def erst(m):
        navn = m.group(1); kort = navn.split("_")[0]
        if kort == "GeneralBrightnessScale":
            return "%s=%s" % (navn, "%.6f" % (NAT_LYS if nat else 1.0))
        if kort in TEMA:
            return "%s=%s" % (navn, lin(TEMA[kort]))
        return m.group(0)
    return re.sub(r"(\w+?)=(\([^()]*\)|[-\d.]+)", erst, txt)

backup = {}
if os.path.exists(BACKUP):
    for l in open(BACKUP, encoding="utf-8"):
        if "\t" in l:
            k, v = l.rstrip("\n").split("\t", 1); backup[k] = v
nye_backup = dict(backup)
for nat, pn in ((False, "Atron Colors Day"), (True, "Atron Colors Night")):
    navn, s = felt(pn)
    if s is None:
        out.append("FANDT IKKE " + pn); continue
    txt = s.export_text()
    out.append("%s (%s) FOER: %s" % (pn, navn, txt))
    nye_backup.setdefault(pn, txt)
    ny = backup.get(pn, txt) if GENDAN else ny_tekst(txt, nat)
    s.import_text(ny)
    cdo.set_editor_property(navn, s)
    out.append("%s EFTER: %s" % (pn, cdo.get_editor_property(navn).export_text()))
with open(BACKUP, "w", encoding="utf-8") as f:
    for k, v in nye_backup.items(): f.write("%s\t%s\n" % (k, v))
cdo.modify()
unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
out.append("GEMT")
open(UD, "w", encoding="utf-8").write("\n".join(out))
unreal.log("[MOVIA TEMA] faerdig - se _tema_ud.txt")
