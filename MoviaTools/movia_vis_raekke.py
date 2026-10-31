# -*- coding: utf-8 -*-
"""
Skriver hvordan en stoprække (UMG_NextBusStop) er bygget op til filen
raekke_opbygning.txt i MoviaTools. Ændrer INTET.
  Tools > Execute Python Script > movia_vis_raekke.py
"""
import os
import unreal

STI = "/Game/Gameplay/Vehicles/Common/Displays/PassengerDisplays/UMG_NextBusStop"
UD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raekke_opbygning.txt")


def _info(w):
    t = "%s (%s)" % (w.get_name(), w.get_class().get_name())
    try:
        t += " vis=%s" % w.get_editor_property("visibility")
    except Exception:
        pass
    try:
        slot = w.get_editor_property("slot")
        if slot:
            t += " | slot=%s" % slot.get_class().get_name()
            for p in ("padding", "size", "layout_data", "horizontal_alignment", "vertical_alignment"):
                try:
                    t += " %s=%s" % (p, slot.get_editor_property(p))
                except Exception:
                    pass
    except Exception:
        pass
    for p in ("height_override", "min_desired_height", "width_override"):
        try:
            t += " %s=%s" % (p, w.get_editor_property(p))
        except Exception:
            pass
    return t


def main():
    unreal.EditorAssetLibrary.load_asset(STI)
    kort = STI.split("/")[-1]
    praefiks = "%s.%s:WidgetTree." % (STI, kort)
    alle = [w for w in unreal.ObjectIterator(unreal.Widget)
            if w.get_path_name().startswith(praefiks) and "." not in w.get_path_name()[len(praefiks):]]
    boern = {}
    for w in alle:
        boern.setdefault(w.get_parent(), []).append(w)
    linjer = []

    def gaa(w, dybde):
        linjer.append("  " * dybde + _info(w))
        for b in boern.get(w, []):
            gaa(b, dybde + 1)

    for rod in boern.get(None, []):
        gaa(rod, 0)
    with open(UD, "w", encoding="utf-8") as f:
        f.write("\n".join(linjer) + "\n")
    unreal.log("[MOVIA] Skrev %d elementer til %s" % (len(linjer), UD))


main()
