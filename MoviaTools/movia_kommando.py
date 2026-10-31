# -*- coding: utf-8 -*-
"""
MOVIA KOMMANDO - koerer en kommandofil (JSON), fx skrevet af en AI.

I The Bus Modding:  Tools > Execute Python Script > movia_kommando.py
Den koerer filen  kommando.json  i samme mappe.
Se AI_GUIDE.md for formatet.
"""
import json, os, sys, importlib
MAPPE = r"C:\Users\tacci\Documents\The Bus\MoviaTools"
sys.path.append(MAPPE)
import unreal
import movia_tools, movia_regler, movia_motor
importlib.reload(movia_tools); importlib.reload(movia_regler); importlib.reload(movia_motor)

FIL = os.path.join(MAPPE, "kommando.json")
FUNKTIONER = {
    "tekst": movia_tools.tekst, "tekstfarve": movia_tools.tekstfarve, "skrift": movia_tools.skrift,
    "farve": movia_tools.farve, "billede": movia_tools.billede, "skjul": movia_tools.skjul,
    "vis": movia_tools.vis, "gennemsigtighed": movia_tools.gennemsigtighed,
    "vis_elementer": movia_tools.vis_elementer, "hoejde": movia_tools.hoejde, "klip": movia_tools.klip, "juster": movia_tools.juster, "egenskab": movia_tools.egenskab,
}


def koer(fil=FIL):
    with open(fil, encoding="utf-8") as f:
        data = json.load(f)
    kommandoer = data if isinstance(data, list) else [data]
    for k in kommandoer:
        if isinstance(k, dict) and "items" in k and "layout" not in k:
            k = {"skaerm": k.get("ue", "Passager"), "layout": k}
        if isinstance(k, dict):
            koer_en(k, fil)
    unreal.log("[MOVIA KOMMANDO] ALT FAERDIGT (%d skaerm(e)). Tryk TML > Mod Creator > Build Mod." % len(kommandoer))


def koer_en(k, fil):
    skaerm = k.get("skaerm", "Passager")
    unreal.log("[MOVIA KOMMANDO] Koerer %s paa %s" % (os.path.basename(fil), skaerm))

    if k.get("layout"):
        movia_motor.byg_layout(skaerm, k["layout"])

    if k.get("regler") or k.get("sider"):     # regler kan ogsaa staa uden for layoutet
        try:
            movia_motor.saet_regler(skaerm, k.get("layout"), k.get("regler"), k.get("sider"))
        except Exception as e:
            unreal.log_error("[MOVIA KOMMANDO] Reglerne fejlede: %s" % e)

    for nr, a in enumerate(k.get("aendringer", []), 1):
        try:
            fn = FUNKTIONER[a["funktion"]]
            args = [a.get("skaerm", skaerm)]
            if a["funktion"] != "vis_elementer":
                args.append(a["element"])
            if "vaerdi" in a:
                args.append(a["vaerdi"])
            if a["funktion"] == "skrift":
                args = [a.get("skaerm", skaerm), a["element"], a.get("vaegt", "Regular"), a.get("stoerrelse")]
            fn(*args)
        except Exception as e:
            unreal.log_error("[MOVIA KOMMANDO] Aendring %d fejlede (%s): %s" % (nr, a, e))
    if k.get("aendringer"):
        movia_tools.gem_alt()
    unreal.log("[MOVIA KOMMANDO] Faerdig med " + skaerm)


koer()
