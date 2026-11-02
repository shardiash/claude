# -*- coding: utf-8 -*-
"""
MOVIA NY MOTOR - saetter en ny motor (WBP_MoviaMotor) ind med saa faa klik som muligt.

TRIN 1 (i Python-konsollen):
    exec(open(r"C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\movia_ny_motor.py", encoding="utf-8").read())
  - tilfoejer nye variabler
  - sletter den gamle motor-graf (paa et oejeblik - ingen Delete-tast)
  - kopierer den nyeste motor (_motor_vNN.t3d) til udklipsholderen
  - aabner motoren

TRIN 2 (i motor-vinduet):  tryk  +  ud for GRAPHS (oeverst til venstre)  ->  Enter  ->  klik i grafen  ->  Ctrl+V  ->  Confirm
          ->  File > Refresh All Nodes  (VIGTIGT - ellers faar motoren fejl)

TRIN 3 (i Python-konsollen):
    movia_faerdig()
  - kompilerer, gemmer og lukker motoren (og koerer layoutet hvis du skriver movia_faerdig(layout=True))
"""
import glob, os, re, sys, unreal
MAPPE = r"C:\Users\tacci\Documents\The Bus\MoviaTools"
STI = "/Game/MoviaSkaerme/WBP_MoviaMotor"
if MAPPE not in sys.path:
    sys.path.append(MAPPE)
BEL = unreal.BlueprintEditorLibrary
EAL = unreal.EditorAssetLibrary
AES = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)


def _nyeste_motor():
    filer = glob.glob(os.path.join(MAPPE, "_motor_v*.t3d"))
    nr = lambda f: int(re.search(r"_motor_v(\d+)\.t3d$", f).group(1)) if re.search(r"_motor_v(\d+)\.t3d$", f) else -1
    return max(filer, key=nr) if filer else None


def movia_start(t3d=None):
    t3d = t3d or _nyeste_motor()
    unreal.log("[MOVIA] Ny motor: %s" % t3d)
    # 1) variabler
    exec(open(os.path.join(MAPPE, "movia_byg_motor.py"), encoding="utf-8").read(), {"__name__": "movia_byg"})
    bp = EAL.load_asset(STI)
    # 2) slet den gamle graf (alle noder paa en gang)
    AES.close_all_editors_for_asset(bp)
    for navn in ("EventGraph", "NewEventGraph", "Motor"):
        gr = BEL.find_graph(bp, navn)
        if gr:
            BEL.remove_graph(bp, gr)
            unreal.log("[MOVIA] Slettede grafen " + navn)
    # 3) udklipsholder
    import movia_klip, importlib
    importlib.reload(movia_klip)
    movia_klip.kopier_fil(t3d)
    # 4) aabn motoren
    AES.open_editor_for_assets([bp])
    unreal.log("[MOVIA] KLAR: tryk + ved GRAPHS -> Enter -> klik i grafen -> Ctrl+V -> Confirm -> File > Refresh All Nodes. Skriv derefter movia_faerdig() i konsollen.")


def _log_fil():
    filer = glob.glob(os.path.join(unreal.Paths.project_log_dir(), "*.log"))
    return max(filer, key=os.path.getmtime) if filer else None


def _compiler_fejl(marker):
    """Laeser editorens log efter markeren og finder compiler-fejl for motoren."""
    f = _log_fil()
    if not f:
        return None
    tekst = open(f, encoding="utf-8", errors="replace").read()
    i = tekst.rfind(marker)
    if i < 0:
        return None
    return [l for l in tekst[i:].splitlines() if "WBP_MoviaMotor" in l and "[Compiler]" in l and "Error" in l]


def movia_faerdig(layout=False):
    import time
    bp = EAL.load_asset(STI)
    marker = "MOVIA_KOMPILER_%d" % int(time.time())
    unreal.log(marker)
    BEL.compile_blueprint(bp)
    unreal.log("MOVIA_KOMPILER_SLUT")
    time.sleep(1.0)
    fejl = _compiler_fejl(marker)
    if fejl is None:
        unreal.log_warning("[MOVIA] Kunne ikke laese loggen - tjek selv at Compile siger 'Good to go' foer du gemmer.")
        return
    # sikkerhed: motoren skal faktisk indeholde logikken (ellers er grafen tom)
    try:
        gc = unreal.load_object(None, STI + ".WBP_MoviaMotor_C")
        har = hasattr(unreal.get_default_object(gc), "movia_update")
    except Exception:
        har = False
    if not har:
        unreal.log_error("[MOVIA] Motoren er TOM (ingen MoviaUpdate) - den er IKKE gemt. Indsaet motoren med Ctrl+V foerst.")
        return
    if fejl:
        for l in fejl[:5]:
            unreal.log_error("[MOVIA] " + l.split("[Compiler]")[-1].strip())
        unreal.log_error("[MOVIA] Motoren har %d fejl og er IKKE gemt. Har du koert File > Refresh All Nodes?" % len(fejl))
        return
    EAL.save_asset(STI, only_if_is_dirty=False)
    AES.close_all_editors_for_asset(bp)
    unreal.log("[MOVIA] Ingen fejl - motoren er gemt og lukket.")
    if layout:
        exec(open(os.path.join(MAPPE, "movia_kommando.py"), encoding="utf-8").read(), {"__name__": "movia_kommando"})
    unreal.log("[MOVIA] FAERDIG. Byg nu modden: TML > Mod Creator > Build Mod > Build Client Only.")


import builtins
builtins.movia_faerdig = movia_faerdig
builtins.movia_start = movia_start
if not getattr(builtins, "MOVIA_KUN_DEF", False):
    movia_start()
builtins.MOVIA_KUN_DEF = False
