# -*- coding: utf-8 -*-
"""
MOVIA - EKSPORTER SPILLETS SKAERMLOGIK  (aendrer INTET)
Skriver blueprint-logikken (EventGraph + funktioner) for skaermene ud som
tekst, saa Claude kan laese hvordan spillet fylder stoplisten, forsinkelsen osv.
  Tools > Execute Python Script > movia_eksporter_logik.py
Resultat: MoviaTools\\Logik.zip  (send den til Claude)
"""
import os
import zipfile
import unreal

MAPPE = os.path.dirname(os.path.abspath(__file__))
UD = os.path.join(MAPPE, "Logik")
ASSETS = [
    "/Game/Gameplay/Vehicles/Common/Displays/PassengerDisplays/UMG_PassengersDisplay",
    "/Game/Gameplay/Vehicles/Common/Displays/PassengerDisplays/UMG_NextBusStop",
    "UMG_TB_NAtron_Time_Header",
    "/Game/UI/Berlin/Menu/Atron/NewAtron/Menus/UMG_TB_NAtron_Main",
]


def log(t):
    unreal.log("[MOVIA LOGIK] " + t)


def _find(navn):
    if navn.startswith("/"):
        return navn
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    for a in reg.get_all_assets():
        if str(a.asset_name) == navn:
            return str(a.package_name)
    return None


def _exporter():
    for n in ("ObjectExporterT3D", "ExporterT3D"):
        k = getattr(unreal, n, None)
        if k:
            try:
                return k()
            except Exception:
                pass
    return None


def _eksporter_obj(obj, fil, exporter):
    task = unreal.AssetExportTask()
    task.set_editor_property("object", obj)
    task.set_editor_property("filename", fil)
    task.set_editor_property("automated", True)
    task.set_editor_property("prompt", False)
    task.set_editor_property("replace_identical", True)
    if exporter:
        task.set_editor_property("exporter", exporter)
    ok = unreal.Exporter.run_asset_export_task(task)
    return ok and os.path.exists(fil) and os.path.getsize(fil) > 0


def _grafer(bp):
    grafer = []
    try:
        g = unreal.BlueprintEditorLibrary.find_event_graph(bp)
        if g:
            grafer.append(g)
    except Exception as e:
        log("find_event_graph: %s" % e)
    # alle EdGraph-objekter der ligger i blueprintet
    try:
        sti = bp.get_path_name()
        for g in unreal.ObjectIterator(unreal.EdGraph):
            if g.get_path_name().startswith(sti + ":") and g not in grafer:
                grafer.append(g)
    except Exception as e:
        log("EdGraph-soegning: %s" % e)
    return grafer


def main():
    os.makedirs(UD, exist_ok=True)
    exporter = _exporter()
    log("Exporter: %s" % exporter)
    rapport = []
    for navn in ASSETS:
        sti = _find(navn)
        if not sti:
            rapport.append("IKKE FUNDET: " + navn)
            continue
        bp = unreal.EditorAssetLibrary.load_asset(sti)
        kort = sti.split("/")[-1]
        # 1) hele blueprintet
        fil = os.path.join(UD, kort + "__HELE.t3d")
        try:
            ok = _eksporter_obj(bp, fil, exporter)
            rapport.append("%s hele: %s" % (kort, "OK" if ok else "FEJL"))
        except Exception as e:
            rapport.append("%s hele: FEJL %s" % (kort, e))
        # 2) hver graf for sig
        for g in _grafer(bp):
            gnavn = g.get_name()
            fil = os.path.join(UD, "%s__%s.t3d" % (kort, gnavn))
            try:
                ok = _eksporter_obj(g, fil, exporter)
                rapport.append("%s graf %s: %s" % (kort, gnavn, "OK" if ok else "FEJL"))
            except Exception as e:
                rapport.append("%s graf %s: FEJL %s" % (kort, gnavn, e))
        # 3) variabler og funktioner (navne)
        try:
            klasse = unreal.EditorAssetLibrary.load_blueprint_class(sti)
            cdo = unreal.get_default_object(klasse)
            props = [p for p in dir(cdo) if not p.startswith("_")]
            with open(os.path.join(UD, kort + "__navne.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(props))
        except Exception as e:
            rapport.append("%s navne: FEJL %s" % (kort, e))
    with open(os.path.join(UD, "_rapport.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rapport))
    zipsti = os.path.join(MAPPE, "Logik.zip")
    with zipfile.ZipFile(zipsti, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in os.listdir(UD):
            z.write(os.path.join(UD, fn), fn)
    for r in rapport:
        log(r)
    log("FAERDIG - send filen  %s  til Claude" % zipsti)


main()
