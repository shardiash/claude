# -*- coding: utf-8 -*-
"""
MOVIA - opretter regel-motoren WBP_MoviaMotor (widget-blueprint) med alle
dens variabler. Selve logikken saettes ind bagefter (Claude indsaetter den).
  Tools > Execute Python Script > movia_byg_motor.py
"""
import unreal
import traceback

STI = "/Game/MoviaSkaerme/WBP_MoviaMotor"
NY = globals().get("MOVIA_NY_MOTOR", False)   # True = slet og byg forfra
UD = r"C:\Users\tacci\Documents\The Bus\MoviaTools\_motor_ud.txt"
BEL = unreal.BlueprintEditorLibrary

# navn, type, array?, instance editable?
VARIABLER = [
    # program (skrives af movia_motor.py)
    ("VarType", "int", True, True), ("VarPath", "string", True, True), ("VarIdx", "int", True, True),
    ("CVar", "int", True, True), ("CKind", "int", True, True), ("CLo", "real", True, True),
    ("CHi", "real", True, True), ("CStr", "string", True, True), ("CNeg", "bool", True, True),
    ("CA", "real", True, True), ("CB", "real", True, True), ("CM", "real", True, True),
    ("CNew", "bool", True, True),
    ("RStart", "int", True, True), ("RCount", "int", True, True), ("RAction", "int", True, True),
    ("RTarget", "string", True, True), ("RHasEllers", "bool", True, True),
    ("RColTil", "color", True, True), ("RColEllers", "color", True, True),
    ("RNumTil", "real", True, True), ("RNumEllers", "real", True, True),
    ("RTxtTil", "string", True, True), ("RSuffix", "string", True, True), ("RTxtEllers", "string", True, True),
    ("RSlotVar", "int", True, True), ("RSlotA", "real", True, True), ("RSlotB", "real", True, True),
    ("RSlotM", "real", True, True), ("RSlotFmt", "int", True, True), ("RGlid", "real", True, True),
    ("Interval", "real", False, True),
    # arbejdsvariabler
    ("Host", "userwidget", False, False), ("tW", "widget", False, False), ("tW2", "widget", False, False),
    ("tPath", "string", False, False), ("tStr", "string", False, False), ("tNum", "real", False, False),
    ("tParts", "string", True, False), ("tAcc", "real", False, False), ("tOK", "bool", False, False),
    ("tAny", "bool", False, False), ("tCond", "bool", False, False), ("tV", "real", False, False),
    ("tRes", "string", False, False), ("tR", "int", False, False), ("tJ", "int", False, False),
    ("tVar", "int", False, False), ("tT", "int", False, False), ("tNeg", "bool", False, False),
    ("LastTime", "real", False, False), ("DT", "real", False, False),
    ("fA", "real", False, False), ("fB", "real", False, False), ("fM", "real", False, False),
    ("fFmt", "int", False, False), ("tCol", "color", False, False),
]


def _type(navn, arr):
    if navn == "color":
        t = BEL.get_struct_type(unreal.LinearColor.static_struct())
    elif navn == "userwidget":
        t = BEL.get_object_reference_type(unreal.UserWidget.static_class())
    elif navn == "widget":
        t = BEL.get_object_reference_type(unreal.Widget.static_class())
    else:
        t = None
        for kandidat in ({"real": ["real", "double", "float"]}.get(navn, [navn])):
            try:
                t = BEL.get_basic_type_by_name(kandidat)
                if t:
                    break
            except Exception:
                pass
    if arr:
        t = BEL.get_array_type(t)
    return t


def main():
    log = []
    try:
        if NY and unreal.EditorAssetLibrary.does_asset_exist(STI):
            gammel = unreal.EditorAssetLibrary.load_asset(STI)
            unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(gammel)
            unreal.EditorAssetLibrary.delete_asset(STI)
            log.append("Slettede gammel motor")
        bp = unreal.EditorAssetLibrary.load_asset(STI) if unreal.EditorAssetLibrary.does_asset_exist(STI) else None
        if bp is None:
            fabrik = unreal.WidgetBlueprintFactory()
            fabrik.set_editor_property("parent_class", unreal.UserWidget)
            at = unreal.AssetToolsHelpers.get_asset_tools()
            bp = at.create_asset("WBP_MoviaMotor", "/Game/MoviaSkaerme", unreal.WidgetBlueprint, fabrik)
            log.append("Oprettet " + STI)
        for navn, typ, arr, inst in VARIABLER:
            try:
                ok = BEL.add_member_variable(bp, navn, _type(typ, arr))
                if inst:
                    BEL.set_blueprint_variable_instance_editable(bp, navn, True)
                log.append("%s: %s" % (navn, ok))
            except Exception as e:
                log.append("%s: FEJL %s" % (navn, e))
        try:
            BEL.remove_unused_nodes(bp)      # fjerner de graa 'spoegelses'-events
        except Exception as e:
            log.append("remove_unused_nodes: %s" % e)
        BEL.compile_blueprint(bp)
        unreal.EditorAssetLibrary.save_asset(STI, only_if_is_dirty=False)
        unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([bp])
        log.append("FAERDIG")
    except Exception:
        log.append(traceback.format_exc())
    open(UD, "w", encoding="utf-8").write("\n".join(log))
    unreal.log("[MOVIA] " + log[-1][:200])


main()
