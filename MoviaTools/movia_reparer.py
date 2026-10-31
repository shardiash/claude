# -*- coding: utf-8 -*-
"""
MOVIA REPARER - koer EN gang, hvis Build Mod fejler med:
  "Variable [M_E0xx_9eb26] was deleted but still has a GUID ..."
Den genskaber de slettede lag som usynlige pladsholdere, saa Unreals
'spoegelses-ID'er' passer igen, og Build Mod virker.
  Tools > Execute Python Script > movia_reparer.py
"""
import unreal

STI = "/Game/Gameplay/Vehicles/Common/Displays/PassengerDisplays/UMG_PassengersDisplay"
# navn -> slags (fra fejlen i build-loggen 24/10 kl. 02:12)
SPOEGELSER = {}
for i in (0,):
    SPOEGELSER["M_E%03d_9eb26" % i] = unreal.Image
for i in (1, 2, 3, 7, 8, 9, 12, 18):
    SPOEGELSER["M_E%03d_9eb26" % i] = unreal.Border
for i in (4, 5, 10, 13, 15, 19, 20, 21, 22):
    SPOEGELSER["M_E%03d_9eb26" % i] = unreal.TextBlock


def reparer():
    bp = unreal.EditorAssetLibrary.load_asset(STI)
    kort = STI.split("/")[-1]
    rod = None
    for w in unreal.ObjectIterator(unreal.CanvasPanel):
        p = w.get_path_name()
        if p.startswith("%s.%s:WidgetTree." % (STI, kort)) and w.get_parent() is None:
            rod = w
            break
    if rod is None:
        unreal.log_error("[MOVIA REPARER] Fandt ikke skaermens Canvas Panel")
        return
    tree = rod.get_outer()
    lavet = 0
    for navn, cls in SPOEGELSER.items():
        w = unreal.find_object(None, "%s.%s:WidgetTree.%s" % (STI, kort, navn))
        if w is not None and w.get_parent() is not None:
            continue                       # findes allerede paa skaermen
        if w is None:
            w = unreal.new_object(cls, outer=tree, name=navn)
        rod.add_child_to_canvas(w)
        w.set_editor_property("visibility", unreal.SlateVisibility.COLLAPSED)
        lavet += 1
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_asset(STI, only_if_is_dirty=False)
    unreal.log("[MOVIA REPARER] FAERDIG - %d pladsholdere sat ind. Proev Build Mod igen." % lavet)


reparer()
