# -*- coding: utf-8 -*-
"""
MOVIA TOOLS - nemme funktioner til at aendre skaerme i The Bus Modding Editor.

Brug: Tools > Execute Python Script > vaelg  movia_aendringer.py
(den fil importerer denne og kalder funktionerne nedenfor).

Alle funktioner tager:
  skaerm  = et kort navn fra SKAERME herunder (fx "Passager") ELLER en fuld sti
  element = navnet paa elementet, som det staar i Hierarchy i editoren
"""
import unreal

# ---------------------------------------------------------------
# Korte navne -> skaermfiler. Tilfoej selv flere her.
# ---------------------------------------------------------------
SKAERME = {
    "Passager":     "/Game/Gameplay/Vehicles/Common/Displays/PassengerDisplays/UMG_PassengersDisplay",
    "StopRaekke":   "/Game/Gameplay/Vehicles/Common/Displays/PassengerDisplays/UMG_NextBusStop",
    "Main":         "/Game/UI/Berlin/Menu/Atron/NewAtron/Menus/UMG_TB_NAtron_Main",
    "Driving":      "/Game/UI/Berlin/Menu/Atron/NewAtron/Menus/UMG_TB_NAtron_Driving_",
    "Startup":      "/Game/UI/Berlin/Menu/Atron/NewAtron/Menus/UMG_TB_NAtron_Startup",
    "Header":       "UMG_TB_NAtron_Time_Header",   # kun navn - stien findes automatisk
    "Start":        "/Game/UI/Berlin/Menu/Atron/NewAtron/Menus/UMG_TB_NAtron_Start",           # forskaerm foer login
    "LogIn":        "/Game/UI/Berlin/Menu/Atron/NewAtron/Menus/UMG_TB_NAtron_LogIn",           # saelger + PIN
    "Tur":          "/Game/UI/Berlin/Menu/Atron/NewAtron/Menus/UMG_TB_NAtron_Tour_Selection",  # linje + tur
    "Numpad":       "/Game/UI/Berlin/Menu/Atron/NewAtron/Widgets/UMG_TB_NAtron_Numpad",
}

# Skrifttyper vi har importeret
SKRIFT = {
    "Regular":   "/Game/MoviaSkaerme/Inter-Regular_Font",
    "Medium":    "/Game/MoviaSkaerme/Inter-Medium_Font",
    "SemiBold":  "/Game/MoviaSkaerme/Inter-SemiBold_Font",
    "Bold":      "/Game/MoviaSkaerme/Inter-Bold_Font",
    "ExtraBold": "/Game/MoviaSkaerme/Inter-ExtraBold_Font",
}

_aendrede = {}   # sti -> blueprint, saa vi kan gemme til sidst
_assets_klar = False
ASSET_KILDE = r"C:\Users\tacci\Documents\The Bus\MoviaTools\Assets"


def sikr_assets(bp=None):
    """Kopierer Movias skrifttyper og billeder ind i den mod, der er aaben, hvis de mangler.
    Saa virker funktionerne ogsaa i en helt ny mod."""
    global _assets_klar
    if _assets_klar:
        return
    if unreal.EditorAssetLibrary.does_asset_exist(SKRIFT["Regular"]):
        _assets_klar = True
        return
    import os, shutil
    if bp is None:
        raise RuntimeError("sikr_assets kraever en skaerm")
    # Gem skaermen i den aabne mod, og find modens Content-mappe ud fra filens placering
    sti = bp.get_path_name().split(".")[0]
    unreal.EditorAssetLibrary.save_asset(sti, only_if_is_dirty=False)
    fil = unreal.SystemLibrary.get_system_path(bp).replace("\\", "/")
    relativ = sti[len("/Game/"):] + ".uasset"
    if not fil.endswith(relativ):
        raise RuntimeError("Kunne ikke finde modens mappe ud fra " + fil)
    content = fil[: -len(relativ)]
    maal = os.path.join(content, "MoviaSkaerme")
    os.makedirs(maal, exist_ok=True)
    antal = 0
    for navn in os.listdir(ASSET_KILDE):
        if navn.endswith(".uasset") and not os.path.exists(os.path.join(maal, navn)):
            shutil.copy2(os.path.join(ASSET_KILDE, navn), maal)
            antal += 1
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    reg.scan_paths_synchronous(["/Game/MoviaSkaerme"], True)
    _ok("Kopierede %d Movia-filer (skrifttyper/billeder) ind i modden: %s" % (antal, maal))
    _assets_klar = True


# ---------------------------------------------------------------
# Hjaelpere
# ---------------------------------------------------------------
_fundne_stier = {}


def _sti(skaerm):
    """Skaermnavn -> sti. Er det kun et filnavn (uden /), soeges der efter det i spillet."""
    sti = SKAERME.get(skaerm, skaerm)
    if sti.startswith("/"):
        return sti
    if sti in _fundne_stier:
        return _fundne_stier[sti]
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    for a in reg.get_assets_by_path("/Game", recursive=True):
        if str(a.asset_name) == sti:
            fundet = str(a.package_name)
            _fundne_stier[sti] = fundet
            _ok("Fandt %s: %s" % (sti, fundet))
            return fundet
    raise RuntimeError("Fandt ikke filen " + sti)


def _bp(skaerm):
    sti = _sti(skaerm)
    bp = unreal.EditorAssetLibrary.load_asset(sti)
    if bp is None:
        raise RuntimeError("Kan ikke finde skaermen: " + sti)
    _aendrede[sti] = bp
    sikr_assets(bp)
    return bp, sti


def _element(skaerm, element):
    bp, sti = _bp(skaerm)
    navn = sti.split("/")[-1]
    obj = unreal.find_object(None, "%s.%s:WidgetTree.%s" % (sti, navn, element))
    if obj is None:
        raise RuntimeError("Fandt ikke '%s' i %s. Brug vis_elementer('%s') for at se navnene."
                           % (element, skaerm, skaerm))
    obj.modify()
    return obj


def _farve(hexfarve):
    h = hexfarve.lstrip("#")
    if len(h) == 6:
        h += "FF"
    r, g, b, a = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4, 6)]
    # editoren gemmer farver lineaert; konverter fra sRGB saa farven matcher hex-koden
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return unreal.LinearColor(lin(r), lin(g), lin(b), a)


def _ok(tekst):
    unreal.log("[MOVIA] " + tekst)


# ---------------------------------------------------------------
# FUNKTIONER DU KAN BRUGE
# ---------------------------------------------------------------
def vis_elementer(skaerm):
    """Skriver alle elementer i en skaerm til Output Log."""
    sti = _sti(skaerm)
    _bp(skaerm)
    praefiks = "%s.%s:WidgetTree." % (sti, sti.split("/")[-1])
    fundet = []
    for w in unreal.ObjectIterator(unreal.Widget):
        p = w.get_path_name()
        if p.startswith(praefiks) and "." not in p[len(praefiks):]:
            fundet.append("%s  (%s)" % (p[len(praefiks):], w.get_class().get_name()))
    _ok("Elementer i %s:" % skaerm)
    for f in sorted(fundet):
        unreal.log("    " + f)
    return fundet


def tekst(skaerm, element, ny_tekst):
    """Aendrer teksten i et tekstfelt."""
    _element(skaerm, element).set_editor_property("text", unreal.Text(ny_tekst))
    _ok("%s/%s tekst = %s" % (skaerm, element, ny_tekst))


def tekstfarve(skaerm, element, hexfarve):
    """Farve paa tekst, fx '#333333'."""
    w = _element(skaerm, element)
    w.set_editor_property("color_and_opacity", unreal.SlateColor(_farve(hexfarve)))
    _ok("%s/%s tekstfarve = %s" % (skaerm, element, hexfarve))


def skrift(skaerm, element, vaegt="Regular", stoerrelse=None):
    """Skrifttype (Regular/Medium/SemiBold/Bold/ExtraBold) og stoerrelse."""
    w = _element(skaerm, element)
    font = w.get_editor_property("font")
    font.set_editor_property("font_object", unreal.load_asset(SKRIFT[vaegt]))
    font.set_editor_property("typeface_font_name", "Default")
    if stoerrelse:
        font.set_editor_property("size", float(stoerrelse))
    w.set_editor_property("font", font)
    _ok("%s/%s skrift = %s %s" % (skaerm, element, vaegt, stoerrelse or ""))


def farve(skaerm, element, hexfarve):
    """Farve paa et billede eller en boks (Image / Border)."""
    w = _element(skaerm, element)
    c = _farve(hexfarve)
    if isinstance(w, unreal.Border):
        w.set_editor_property("brush_color", c)
    elif isinstance(w, unreal.Image):
        w.set_editor_property("color_and_opacity", c)
    else:
        w.set_editor_property("color_and_opacity", c)
    _ok("%s/%s farve = %s" % (skaerm, element, hexfarve))


def billede(skaerm, element, billed_sti):
    """Skifter billedet i et Image, fx '/Game/MoviaSkaerme/T_Reklame_Aeblefest'."""
    w = _element(skaerm, element)
    brush = w.get_editor_property("brush")
    brush.set_editor_property("resource_object", unreal.load_asset(billed_sti))
    w.set_editor_property("brush", brush)
    _ok("%s/%s billede = %s" % (skaerm, element, billed_sti))


def skjul(skaerm, element):
    """Skjuler et element helt."""
    _element(skaerm, element).set_editor_property("visibility", unreal.SlateVisibility.COLLAPSED)
    _ok("%s/%s skjult" % (skaerm, element))


def hoejde(skaerm, element, vaerdi):
    """Saetter hoejden paa en Spacer (luft) eller SizeBox (fast hoejde)."""
    w = _element(skaerm, element)
    v = float(vaerdi)
    if isinstance(w, unreal.Spacer):
        gl = w.get_editor_property("size")
        w.set_editor_property("size", unreal.Vector2D(gl.x, v))
    elif isinstance(w, unreal.SizeBox):
        w.set_editor_property("override_height_override", True)
        w.set_editor_property("height_override", v)
    else:
        raise RuntimeError("hoejde virker kun paa Spacer og SizeBox")
    _ok("%s/%s hoejde = %s" % (skaerm, element, v))


def klip(skaerm, element):
    """Klipper alt der stikker udenfor elementet (fx en ekstra tom tekstlinje)."""
    w = _element(skaerm, element)
    w.set_editor_property("clipping", unreal.WidgetClipping.CLIP_TO_BOUNDS)
    _ok("%s/%s klipper nu indholdet" % (skaerm, element))


def juster(skaerm, element, vaerdi):
    """Lodret placering i sin kasse: top, midt eller bund."""
    w = _element(skaerm, element)
    slot = w.get_editor_property("slot")
    v = {"top": unreal.VerticalAlignment.V_ALIGN_TOP, "midt": unreal.VerticalAlignment.V_ALIGN_CENTER,
         "bund": unreal.VerticalAlignment.V_ALIGN_BOTTOM, "fyld": unreal.VerticalAlignment.V_ALIGN_FILL}[str(vaerdi).lower()]
    slot.set_editor_property("vertical_alignment", v)
    _ok("%s/%s justeret %s" % (skaerm, element, vaerdi))


def egenskab(skaerm, element, vaerdi):
    """Avanceret: saet en vilkaarlig egenskab. vaerdi = {"navn": ..., "vaerdi": ...}
    Enum skrives som tekst, fx "WidgetClipping.CLIP_TO_BOUNDS"."""
    w = _element(skaerm, element)
    navn, v = vaerdi["navn"], vaerdi["vaerdi"]
    if isinstance(v, str) and "." in v and v.split(".")[0] in dir(unreal):
        enum, medlem = v.split(".", 1)
        v = getattr(getattr(unreal, enum), medlem)
    w.set_editor_property(navn, v)
    _ok("%s/%s %s = %s" % (skaerm, element, navn, v))


def vis(skaerm, element):
    """Viser et skjult element igen."""
    _element(skaerm, element).set_editor_property("visibility", unreal.SlateVisibility.SELF_HIT_TEST_INVISIBLE)
    _ok("%s/%s vist" % (skaerm, element))


def gennemsigtighed(skaerm, element, vaerdi):
    """0 = usynlig, 1 = helt synlig."""
    _element(skaerm, element).set_editor_property("render_opacity", float(vaerdi))
    _ok("%s/%s gennemsigtighed = %s" % (skaerm, element, vaerdi))


def gem_alt():
    """Kompilerer og gemmer alle skaerme, der er aendret. Kald til sidst."""
    for sti, bp in _aendrede.items():
        try:
            unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        except Exception as e:
            unreal.log_warning("[MOVIA] Kunne ikke kompilere %s: %s" % (sti, e))
        unreal.EditorAssetLibrary.save_asset(sti, only_if_is_dirty=False)
        _ok("Gemt: " + sti)
    _aendrede.clear()
    _ok("FAERDIG. Tryk nu TML > Mod Creator > Build Mod.")
