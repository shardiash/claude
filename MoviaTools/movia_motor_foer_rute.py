import re
# -*- coding: utf-8 -*-
"""
MOVIA MOTOR - bygger en skaerm i spillet ud fra et layout fra Movia Editor.

Koer i The Bus Modding:  Tools > Execute Python Script > movia_motor_koer.py

Saadan virker den:
  * Almindelig tekst, bokse og billeder fra editoren bliver lavet som nye lag.
  * DATAFELTER bliver koblet til de felter, spillet allerede opdaterer
    (fx Text_NextBusStop). Motoren flytter dem hen, hvor du placerede dem,
    og giver dem din skrift og farve - saa de opdaterer stadig i spillet.
  * Billeder fra din computer bliver automatisk importeret i modden.
  * Spillets gamle layout bliver skjult.
  Koerer du motoren igen, bliver de gamle lag fjernet og bygget forfra.
"""
import csv
import os
import unreal

import movia_tools
from movia_tools import SKAERME, SKRIFT, _farve

# ---------------------------------------------------------------
# Datafelt -> spillets eget felt, pr. skaerm.
# Kun felter vi ved findes. Flere kan tilfoejes, naar vi finder dem.
# ---------------------------------------------------------------
KOBLINGER = {
    "Passager": {
        "NaesteStop":  "Text_NextBusStop",
        "Linje":       "Text_Busline",
        "SidsteStop":  "Text_Destination",
        "Ur":          "Text_Time",
        "StopListe":   "Vertical_NextNextObjects",
        "@StopOenske": "Border_1",
    },
    # Bordcomputerens topbjaelke (bruges af ALLE bordcomputer-skaerme)
    "Header": {
        "Ur":               "TextTime",
        "Forsinkelse":      "TextTimeOffset",
        "Dato":             "TextDate",
        "LinjeDestination": "TopLeftText",
    },
    # Bordcomputer - holder stille
    "Main": {
        "Header":     "UMG_TB_NAtron_Time_Icons",
        "StopListe":  "Grid Panel Scroll List",
    },
    # Bordcomputer - koerer
    "Driving": {
        "Header":        "UMG_TB_NAtron_Time_Icons_C_Driving",
        "NaesteStop":    "TextStop1",
        "NaesteStopTid": "TextStopTime1",
        "Afstand":       "TextDistance_",
        "SidsteStop":    "TextDirectionStop",
        "ForrigeStop":   "TextStop0",
    },
}
# Andre spil-elementer kan altid bruges direkte med  "spil": "ElementNavn"  i layoutet.

LAG_MAPPE = "/Game/MoviaSkaerme/Lag"
PRAEFIKS = "M_"
import time as _time
KOERSEL = format(int(_time.time()) % 1679616, "x")   # skifter ved hver koersel
SIDSTE_NAVNE = {}   # "E010" -> det rigtige widgetnavn fra sidste byg        # alle lag motoren laver hedder M_...


def log(t):
    unreal.log("[MOVIA MOTOR] " + t)


def _widget(sti, navn):
    kort = sti.split("/")[-1]
    return unreal.find_object(None, "%s.%s:WidgetTree.%s" % (sti, kort, navn))


def _alle_widgets(sti):
    kort = sti.split("/")[-1]
    praefiks = "%s.%s:WidgetTree." % (sti, kort)
    for w in unreal.ObjectIterator(unreal.Widget):
        p = w.get_path_name()
        if p.startswith(praefiks) and "." not in p[len(praefiks):]:
            yield w


def _rod(sti):
    """Finder skaermens yderste Canvas Panel."""
    for w in _alle_widgets(sti):
        if isinstance(w, unreal.CanvasPanel) and w.get_parent() is None:
            return w
    raise RuntimeError("Fandt ikke skaermens Canvas Panel")


def _importer_billede(fil):
    """Importerer et billede fra computeren og returnerer stien i modden."""
    navn = "L_" + "".join(c if c.isalnum() else "_" for c in os.path.splitext(os.path.basename(fil))[0])
    asset = LAG_MAPPE + "/" + navn
    if unreal.EditorAssetLibrary.does_asset_exist(asset):
        return asset
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", fil)
    task.set_editor_property("destination_path", LAG_MAPPE)
    task.set_editor_property("destination_name", navn)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)
    task.set_editor_property("replace_existing", True)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    log("Importeret billede: " + asset)
    return asset


def _find_billede(navn):
    if not navn:
        return None
    if os.path.isfile(navn):
        return unreal.load_asset(_importer_billede(navn))
    for kandidat in ("/Game/MoviaSkaerme/" + navn, "/Game/MoviaSkaerme/T_" + navn, LAG_MAPPE + "/L_" + navn):
        if unreal.EditorAssetLibrary.does_asset_exist(kandidat):
            return unreal.load_asset(kandidat)
    log("ADVARSEL: fandt ikke billedet " + navn)
    return None


FLIPBOOK_MAT = "/Game/MoviaSkaerme/M_MoviaFlipbook"


def _sikr_flipbook_materiale():
    """Laver (1 gang) materialet der afspiller en flipbook (video) i et billede-lag."""
    if unreal.EditorAssetLibrary.does_asset_exist(FLIPBOOK_MAT):
        return unreal.load_asset(FLIPBOOK_MAT)
    mel = unreal.MaterialEditingLibrary
    at = unreal.AssetToolsHelpers.get_asset_tools()
    m = at.create_asset("M_MoviaFlipbook", "/Game/MoviaSkaerme", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("material_domain", unreal.MaterialDomain.MD_UI)
    def E(cls, x, y):
        return mel.create_material_expression(m, cls, x, y)
    def par(navn, v, y):
        e = E(unreal.MaterialExpressionScalarParameter, -1400, y)
        e.set_editor_property("parameter_name", navn)
        e.set_editor_property("default_value", v)
        return e
    def op(cls, a, b, x, y, pa="A", pb="B"):
        e = E(cls, x, y)
        mel.connect_material_expressions(a, "", e, pa)
        if b is not None:
            mel.connect_material_expressions(b, "", e, pb)
        return e
    cols, rows, n, fps = par("Kolonner", 8, 0), par("Raekker", 8, 120), par("Billeder", 64, 240), par("FPS", 8, 360)
    tid = E(unreal.MaterialExpressionTime, -1400, 480)
    fr = op(unreal.MaterialExpressionFloor, op(unreal.MaterialExpressionMultiply, tid, fps, -1200, 400), None, -1050, 400, pa="")
    fr = op(unreal.MaterialExpressionFmod, fr, n, -900, 300)
    kol = op(unreal.MaterialExpressionFmod, fr, cols, -750, 200)
    rk = op(unreal.MaterialExpressionFloor, op(unreal.MaterialExpressionDivide, fr, cols, -750, 320), None, -600, 320, pa="")
    off = op(unreal.MaterialExpressionAppendVector, kol, rk, -450, 250)
    tc = E(unreal.MaterialExpressionTextureCoordinate, -450, 80)
    uv = op(unreal.MaterialExpressionAdd, tc, off, -300, 150)
    stoer = op(unreal.MaterialExpressionAppendVector, cols, rows, -450, 400)
    uv = op(unreal.MaterialExpressionDivide, uv, stoer, -150, 200)
    tex = E(unreal.MaterialExpressionTextureSampleParameter2D, 0, 150)
    tex.set_editor_property("parameter_name", "Atlas")
    tex.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    mel.connect_material_expressions(uv, "", tex, "UVs")
    mel.connect_material_property(tex, "RGB", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m)
    unreal.EditorAssetLibrary.save_asset(FLIPBOOK_MAT, only_if_is_dirty=False)
    log("Lavet flipbook-materiale " + FLIPBOOK_MAT)
    return m


def _flipbook_instans(png):
    """Video-flipbook (png + json fra movia_video.py) -> material-instans til et billede-lag."""
    import json as _json
    meta_fil = os.path.splitext(png)[0] + ".json"
    meta = _json.load(open(meta_fil, encoding="utf-8")) if os.path.isfile(meta_fil) else {}
    mat = _sikr_flipbook_materiale()
    tex_sti = _importer_billede(png)
    tex = unreal.load_asset(tex_sti)
    try:
        tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
        tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
        tex.set_editor_property("never_stream", True)
        unreal.EditorAssetLibrary.save_asset(tex_sti, only_if_is_dirty=False)
    except Exception as e:
        log("flipbook-tekstur indstillinger: %s" % e)
    navn = "MI_" + os.path.basename(tex_sti)
    sti = LAG_MAPPE + "/" + navn
    mel = unreal.MaterialEditingLibrary
    if unreal.EditorAssetLibrary.does_asset_exist(sti):
        mi = unreal.load_asset(sti)
    else:
        mi = unreal.AssetToolsHelpers.get_asset_tools().create_asset(navn, LAG_MAPPE, unreal.MaterialInstanceConstant,
                                                                     unreal.MaterialInstanceConstantFactoryNew())
    mi.set_editor_property("parent", mat)
    mel.set_material_instance_texture_parameter_value(mi, "Atlas", tex)
    for p, k, std in (("Kolonner", "kolonner", 8), ("Raekker", "raekker", 8), ("Billeder", "billeder", 64), ("FPS", "fps", 8)):
        mel.set_material_instance_scalar_parameter_value(mi, p, float(meta.get(k, std)))
    mel.update_material_instance(mi)
    unreal.EditorAssetLibrary.save_asset(sti, only_if_is_dirty=False)
    log("Video-reklame klar: %s (%s billeder, %s fps)" % (sti, meta.get("billeder", "?"), meta.get("fps", "?")))
    return mi


def _style_tekst(w, r):
    font = w.get_editor_property("font")
    vaegt = "Bold" if r["Fed"] == "True" else "Regular"
    font.set_editor_property("font_object", unreal.load_asset(SKRIFT[vaegt]))
    font.set_editor_property("typeface_font_name", "Default")
    if float(r["Stoerrelse"] or 0) > 0:
        font.set_editor_property("size", float(r["Stoerrelse"]))
    w.set_editor_property("font", font)
    w.set_editor_property("color_and_opacity", unreal.SlateColor(_farve(r["Farve"])))


def _placer(rod, w, r, auto_stoerrelse):
    if w.get_parent() == rod:
        slot = w.get_editor_property("slot")
    else:
        if w.get_parent() is not None:
            w.remove_from_parent()
        slot = rod.add_child_to_canvas(w)
    slot.set_position(unreal.Vector2D(float(r["X"]), float(r["Y"])))
    if auto_stoerrelse:
        slot.set_auto_size(True)
    else:
        slot.set_auto_size(False)   # vigtigt: et genbrugt lag kan have auto-stoerrelse slaaet til fra foer
        slot.set_size(unreal.Vector2D(float(r["W"]), float(r["H"])))
    slot.set_z_order(int(r["Z"]) + 10)
    if r["Skjult"] == "True":
        w.set_editor_property("visibility", unreal.SlateVisibility.COLLAPSED)
    return slot


def _ny(cls, tree, navn):
    """Laver et nyt widget-lag. Det markeres som 'ikke variabel', saa
    UE ikke klager over manglende GUID (gav editor-frys foer)."""
    w = unreal.new_object(cls, outer=tree, name=navn)
    for prop in ("is_variable", "bIsVariable"):
        try:
            w.set_editor_property(prop, False)
            break
        except Exception:
            pass
    return w


def _hent_eller_ny(cls, tree, sti, navn):
    """Genbruger laget fra sidste koersel, hvis det findes - ellers laves et nyt."""
    w = _widget(sti, navn)
    if w is not None and isinstance(w, cls):
        w.modify()
        return w
    return _ny(cls, tree, navn)


def _daemp_ensure():
    # Saa en evt. GUID-advarsel kun vises 1 gang i stedet for mange (det var den, der fik editoren til at fryse)
    try:
        unreal.SystemLibrary.execute_console_command(None, "core.EnsureAlwaysEnabled 0")
    except Exception:
        pass


def byg(skaerm, csv_fil, beholdes=None):
    global KOERSEL
    KOERSEL = format(int(_time.time() * 10) % 60466176, "x")   # nyt for hver koersel
    sti = movia_tools._sti(skaerm)
    bp = unreal.EditorAssetLibrary.load_asset(sti)
    movia_tools.sikr_assets(bp)
    rod = _rod(sti)
    tree = rod.get_outer()
    koblinger = KOBLINGER.get(skaerm, {})

    # 1. skjul gamle lag fra sidste koersel. De SLETTES IKKE - slettede lag
    #    efterlader 'spoegelses-ID'er', som faar Build Mod til at fejle.
    for w in list(_alle_widgets(sti)):
        if w.get_name().startswith(PRAEFIKS) and w.get_parent() is not None:
            w.modify()
            w.set_editor_property("visibility", unreal.SlateVisibility.COLLAPSED)

    with open(csv_fil, encoding="utf-8") as f:
        raekker = list(csv.DictReader(f))
    log("Bygger %s ud fra %d elementer" % (skaerm, len(raekker)))

    flyttet = set()
    # 2. flyt koblede datafelter og tilstande ud foerst (foer gammelt layout skjules)
    for r in raekker:
        if r.get("KunVed") == "True":
            continue  # lag der kun vises i en tilstand laves i trin 4
        if r.get("Spil"):
            noegle, spil_navn = r["Spil"], r["Spil"]
        else:
            noegle = r["Data"] if r["Type"] in ("Data", "Omraade") else ("@" + r["Tilstand"] if r["Tilstand"] else "")
            if not noegle:
                continue
            spil_navn = koblinger.get(noegle)
        if not spil_navn:
            if r["Type"] in ("Data", "Omraade"):
                log("ADVARSEL: datafeltet '%s' kan endnu ikke kobles paa %s - springes over" % (r["Data"], skaerm))
            continue
        w = _widget(sti, spil_navn)
        if w is None:
            log("ADVARSEL: fandt ikke spillets felt " + spil_navn)
            continue
        w.modify()
        if isinstance(w, unreal.TextBlock):
            _style_tekst(w, r)
            _placer(rod, w, r, auto_stoerrelse=True)
        else:
            if isinstance(w, unreal.Border) and r.get("Farve"):
                w.set_editor_property("brush_color", _farve(r["Farve"]))   # baggrund naar tilstanden er fra
            _placer(rod, w, r, auto_stoerrelse=False)
        r["_faerdig"] = True
        flyttet.add(spil_navn)
        log("Koblet %s -> %s" % (noegle, spil_navn))

    # 3. skjul alt det gamle direkte under roden (undtagen det vi har flyttet og 'behold')
    behold = set(beholdes or [])
    for w in list(_alle_widgets(sti)):
        if w.get_parent() == rod and not w.get_name().startswith(PRAEFIKS) \
                and w.get_name() not in flyttet and w.get_name() not in behold:
            w.modify()
            w.set_editor_property("visibility", unreal.SlateVisibility.COLLAPSED)
            log("Skjult gammelt element: " + w.get_name())

    # 4. lav nye lag for tekst, bokse og billeder
    for r in raekker:
        if r.get("_faerdig") or r["Type"] in ("Data", "Omraade") or r.get("Spil"):
            continue
        if r.get("KunVed") == "True":
            log("BEMAERK: %s skal kun vises ved '%s' - det kraever en blueprint-kobling, "
                "som ikke er lavet endnu, saa laget vises altid indtil videre." % (r["Name"], r["Tilstand"]))
        bogstav = {"Tekst": "T", "Billede": "I", "Gps": "G", "Knap": "K"}.get(r["Type"], "B")
        navn = PRAEFIKS + bogstav + r["Name"][1:]      # fx M_T010 - samme navn = altid samme slags lag
        if r["Type"] == "Knap":
            # usynlig trykknap: regel-motoren ser hvornaar den trykkes (se KnapPath i saet_regler)
            w = _hent_eller_ny(unreal.Button, tree, sti, navn)
            stil = w.get_editor_property("widget_style")
            for felt in ("normal", "hovered", "pressed", "disabled"):
                b = stil.get_editor_property(felt)
                try:
                    b.set_editor_property("draw_as", unreal.SlateBrushDrawType.NO_DRAW_TYPE)
                except Exception:
                    b.set_editor_property("tint_color", unreal.SlateColor(unreal.LinearColor(0, 0, 0, 0)))
                stil.set_editor_property(felt, b)
            w.set_editor_property("widget_style", stil)
            w.set_editor_property("background_color", unreal.LinearColor(0, 0, 0, 0))
            _placer(rod, w, r, auto_stoerrelse=False)
            SIDSTE_NAVNE[r["Name"]] = navn
            w.set_editor_property("visibility", unreal.SlateVisibility.VISIBLE)
            log("Knap lavet: %s" % navn)
            continue
        if r["Type"] == "Gps":
            klasse = unreal.load_object(None, NAVI_KLASSE)
            w = _widget(sti, navn)
            if w is None or w.get_class() != klasse:
                w = _ny(klasse, tree, navn)
            else:
                w.modify()
            _placer(rod, w, r, auto_stoerrelse=False)
        elif r["Type"] == "Tekst":
            w = _hent_eller_ny(unreal.TextBlock, tree, sti, navn)
            w.set_editor_property("text", unreal.Text(r["Tekst"]))
            _style_tekst(w, r)
            fast = bool(r.get("Juster") or r.get("Klip") == "True") and float(r["W"] or 0) > 0
            try:
                w.set_editor_property("justification", {"c": unreal.TextJustify.CENTER, "r": unreal.TextJustify.RIGHT}.get(r.get("Juster"), unreal.TextJustify.LEFT))
            except Exception as e:
                log("justification: %s" % e)
            if r.get("Klip") == "True":
                try:
                    w.set_editor_property("overflow_policy", unreal.TextOverflowPolicy.ELLIPSIS)
                except Exception as e:
                    log("overflow_policy: %s" % e)
                try:
                    w.set_editor_property("clipping", unreal.WidgetClipping.CLIP_TO_BOUNDS)
                except Exception:
                    pass
            if fast and not float(r["H"] or 0):
                r["H"] = round(float(r["Stoerrelse"] or 12) * 1.7)
            _placer(rod, w, r, auto_stoerrelse=not fast)
        elif r["Type"] == "Billede":
            w = _hent_eller_ny(unreal.Image, tree, sti, navn)
            tex = _flipbook_instans(r["Video"]) if r.get("Video") else _find_billede(r["Billede"])
            if tex:
                brush = w.get_editor_property("brush")
                brush.set_editor_property("resource_object", tex)
                w.set_editor_property("brush", brush)
            _placer(rod, w, r, auto_stoerrelse=False)
        else:  # Boks
            w = _hent_eller_ny(unreal.Border, tree, sti, navn)
            w.set_editor_property("brush_color", _farve(r["Farve"]))
            _placer(rod, w, r, auto_stoerrelse=False)
        SIDSTE_NAVNE[r["Name"]] = navn
        w.set_editor_property("visibility", unreal.SlateVisibility.SELF_HIT_TEST_INVISIBLE if r["Skjult"] != "True"
                              else unreal.SlateVisibility.COLLAPSED)
        # startgennemsigtighed (fx 0 for lag der toner frem med en regel - saa blinker de ikke, naar skaermen aabnes)
        try:
            w.set_editor_property("render_opacity", float(r["Opacity"]) if r.get("Opacity") not in (None, "") else 1.0)
        except Exception as e:
            log("render_opacity: %s" % e)
        log("Lag lavet: %s (%s)" % (navn, r["Type"]))

    # 5. gem
    _daemp_ensure()
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_asset(sti, only_if_is_dirty=False)
    log("FAERDIG. Tryk nu TML > Mod Creator > Build Mod.")


# ---------------------------------------------------------------
# JSON-layout (samme format som Movia Editor gemmer / en AI skriver)
# ---------------------------------------------------------------
# Skaermenes rigtige stoerrelse inde i Unreal. Layoutet (fx 1600x430 i editoren)
# skaleres op til den, saa tingene havner rigtigt.
RIGTIG_STOERRELSE = {
    "Passager": (3100, 1000),
}


def _layout_til_raekker(layout, skaerm=None):
    raekker = []
    rw, rh = RIGTIG_STOERRELSE.get(skaerm, (0, 0))
    lw, lh = float(layout.get("w") or 0), float(layout.get("h") or 0)
    sx = rw / lw if (rw and lw) else 1.0
    sy = rh / lh if (rh and lh) else 1.0
    if sx != 1.0 or sy != 1.0:
        log("Skalerer layout %dx%d -> %dx%d" % (lw, lh, rw, rh))
    for i, d in enumerate(layout.get("items", [])):
        typ = ("Gps" if d.get("type") == "gps" else
               "Knap" if d.get("type") == "knap" else
               "Data" if (d.get("data") and d.get("type") == "text") else
               "Omraade" if d.get("data") else
               "Tekst" if d.get("type") == "text" else
               "Billede" if (d.get("image") or d.get("video")) else "Boks")
        raekker.append({
            "Name": "E%03d" % i, "Type": typ, "Data": d.get("data", ""), "Tilstand": d.get("state", ""),
            "X": round((d.get("x") or 0) * sx), "Y": round((d.get("y") or 0) * sy),
            "W": round((d.get("w") or 0) * sx), "H": round((d.get("h") or 0) * sy),
            "Tekst": d.get("text", ""), "Stoerrelse": round((d.get("size") or 0) * sy * (0.75 if sy != 1.0 else 1.0)),  # UE-skrift er i punkter (1 pt = 4/3 px)
            "Farve": d.get("color", "#FFFFFF"), "FarveTil": d.get("color_on", ""),
            "Fed": "True" if d.get("bold") else "False", "Skjult": "True" if d.get("hidden") else "False",
            "Billede": d.get("image", ""), "Z": int(d.get("z", i)), "KunVed": "True" if d.get("kun_ved") else "False",
            "Spil": d.get("spil", ""),
            "Video": d.get("video", ""),
            "Juster": {"midt": "c", "center": "c", "hoejre": "r", "højre": "r", "right": "r"}.get(str(d.get("align", "")).lower(), ""),
            "Klip": "True" if d.get("klip") else "False",
            "Opacity": "" if d.get("opacity") is None else str(d.get("opacity")),
        })
    return raekker


def byg_layout(skaerm, layout):
    """Bygger skaermen direkte fra et layout-dict (JSON)."""
    import tempfile
    raekker = _layout_til_raekker(layout, skaerm)
    felter = ["Name", "Type", "Data", "Tilstand", "X", "Y", "W", "H", "Tekst", "Stoerrelse",
              "Farve", "FarveTil", "Fed", "Skjult", "Billede", "Z", "KunVed", "Spil", "Juster", "Klip", "Video", "Opacity"]
    tmp = os.path.join(tempfile.gettempdir(), "movia_layout_tmp.csv")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=felter)
        w.writeheader()
        for r in raekker:
            w.writerow(r)
    byg(skaerm, tmp, layout.get("behold"))
    saet_regler(skaerm, layout, layout.get("regler"), layout.get("sider"))


# ---------------------------------------------------------------
# REGLER / UDTRYK  (oversaettes af movia_regler.py til tabeller, som
# regel-motoren WBP_MoviaMotor koerer inde i spillet)
# ---------------------------------------------------------------
import movia_regler

REGEL_WIDGET = "/Game/MoviaSkaerme/WBP_MoviaMotor"
NAVI_KLASSE = "/Game/UI/HUD/UMG_NaviMap.UMG_NaviMap_C"   # spillets eget GPS-kort
REGEL_NAVN = "MoviaMotor"
# Spildata motoren selv henter. Minutter1-3 = minutter til de naeste stop (passagerskaerm)
SPILDATA = {"Tid": ("tid", ""), "Klokken": ("klokken", ""), "KlokkeSek": ("klokkesek", ""),
            "GpsX": ("gpsx", ""), "GpsY": ("gpsy", ""),
            # v34 skilt (maerker paa bussen - virker paa alle skaerme, ogsaa passagerskaermen)
            "SkiltAaben": ("bustag", "MoviaSkilt", 0), "SkiltAktiv": ("bustag", "SKA", 0), "IkkeIRute": ("bustag", "SKI", 0),
            "SkiltLinje": ("tagtekst", "SKL:", 0), "SkiltDestination": ("tagtekst", "SKD:", 0),
            "DbgBC": ("skiltdbg", "", 1), "DbgBCData": ("skiltdbg", "", 2), "DbgBL": ("skiltdbg", "", 4)}
KUN_PASSAGER = {"Minutter1": ("minutter", "", 1), "Minutter2": ("minutter", "", 2), "Minutter3": ("minutter", "", 3),
                "Forventet1": ("forventet", "", 1), "Forventet2": ("forventet", "", 2), "Forventet3": ("forventet", "", 3),
                "Afstand": ("afstand", "", 1), "VedStop": ("vedstop", "", 0)}
for _r in (1, 2, 3):
    for _m in range(1, 6):
        KUN_PASSAGER["Linje%d_%d" % (_r, _m)] = ("stoplinje", "", _r * 10 + _m)
for _r in range(1, 9):
    KUN_PASSAGER["AfgLinje%d" % _r] = ("afgang", "", _r * 10 + 1)
    KUN_PASSAGER["AfgTil%d" % _r] = ("afgang", "", _r * 10 + 2)
    KUN_PASSAGER["AfgMin%d" % _r] = ("afgang", "", _r * 10 + 3)
SENERE = ("Hastighed", "Doere", "Blinklys", "Passagerer", "StopOenske")


NATRON_SKAERME = ("Main", "Driving", "Header", "Startup", "Start", "LogIn", "Tur")
NATRON_DATA = {"Forsinkelse": ("forsinkelse", ""), "SidsteStopTid": ("sidstetid", ""), "LinjeNr": ("linje", ""),
               "NaesteTid": ("naestetid", ""), "SidsteTidSek": ("sidstetidsek", ""), "SidsteStopNavn": ("sidstenavn", ""),
               "NaesteStopNavn": ("naestenavn", ""), "NaesteAfgang": ("naesteafgang", ""),
               "HolderVedStop": ("vedstop", ""), "AktuelAfgang": ("aktuelafgang", ""), "AfgangTekst": ("afgangtekst", ""),
               "LoginOK": ("loginok", "", 0), "Bekraeftet": ("bustag", "MoviaOK", 0), "AntalStop": ("rute", "", 1),
               "TurNr": ("rute", "", 2), "Alder": ("alder", "", 0),
               "ListeAaben": ("bustag", "MoviaListe", 0), "BilletAaben": ("bustag", "MoviaBillet", 0),
               "NatAaben": ("bustag", "MoviaNat", 0), "LogudAaben": ("bustag", "MoviaLogud", 0),
               "PauseSek": ("pause", "", 1), "ErFoersteStop": ("pause", "", 2), "PauseHoldtMin": ("pause", "", 3),
               "VagtMin": ("pause", "", 4), "StopNr": ("pause", "", 5),
               "LoginTid": ("tagtal", "ML_", 0), "SolgteBilletter": ("tagtal", "MB_", 0), "Kvitteringer": ("tagtal", "MK_", 0)}
for _r in range(1, 7):   # billetterne i den valgte kategori paa Main (billetknap 8-13)
    NATRON_DATA["Billet%dNavn" % _r] = ("billet", "UMG_TB_NAtron_Ticket_Button_%d" % (_r + 7), 1)
    NATRON_DATA["Billet%dKort" % _r] = ("billet", "UMG_TB_NAtron_Ticket_Button_%d" % (_r + 7), 2)
    NATRON_DATA["Billet%dFindes" % _r] = ("billet", "UMG_TB_NAtron_Ticket_Button_%d" % (_r + 7), 3)
KATEGORI_KNAP = {1: "UMG_TB_NAtron_Ticket_Button", 2: "UMG_TB_NAtron_Ticket_Button_1", 3: "UMG_TB_NAtron_Ticket_Button_2"}
for _k, _n in KATEGORI_KNAP.items():   # spillets billetkategorier (billetknap 0-2)
    NATRON_DATA["Kat%dNavn" % _k] = ("billet", _n, 4)
    NATRON_DATA["Kat%dFindes" % _k] = ("billet", _n, 5)
for _r in range(1, 9):   # ruten fra start (ingen rulning): Rute1Navn, Rute1Tid, Rute1Findes, Rute1Afgang
    NATRON_DATA["Rute%dNavn" % _r] = ("stopliste", "", 100 + _r * 10 + 1)
    NATRON_DATA["Rute%dTid" % _r] = ("stopliste", "", 100 + _r * 10 + 2)
    NATRON_DATA["Rute%dFindes" % _r] = ("stopliste", "", 100 + _r * 10 + 3)
    NATRON_DATA["Rute%dAfgang" % _r] = ("stopliste", "", 100 + _r * 10 + 4)
NATRON_DATA["FoersteNavn"] = ("stopliste", "", 211)      # rutens foerste stop (paavirkes ikke af rulning)
NATRON_DATA["FoersteAfgang"] = ("stopliste", "", 214)
for _r in range(1, 9):   # stoplisten: Stop1Navn, Stop1Tid (ankomst, sek), Stop1Findes (1/0), Stop1Afgang
    NATRON_DATA["Stop%dNavn" % _r] = ("stopliste", "", _r * 10 + 1)
    NATRON_DATA["Stop%dTid" % _r] = ("stopliste", "", _r * 10 + 2)
    NATRON_DATA["Stop%dFindes" % _r] = ("stopliste", "", _r * 10 + 3)
    NATRON_DATA["Stop%dAfgang" % _r] = ("stopliste", "", _r * 10 + 4)


KNAP_GRUPPER = {}   # gruppenavn -> nummer (saettes af saet_regler ud fra lag af typen "knap")


def _knap_mode(d):
    if d.get("tekstsaet") is not None: return 14
    if d.get("saetskilt"): return 13
    if d.get("nulstilskilt"): return 15
    if d.get("rutetekst"): return 16
    if d.get("skiftrute") is not None: return 17
    if d.get("tegn") is not None: return 2
    if d.get("slet"): return 3
    if d.get("ryd"): return 4
    if d.get("login"): return 6
    if d.get("tilfoejtag"): return 7
    if d.get("skiftertag"): return 8
    if d.get("print"): return 9
    if d.get("kategori"): return 10
    if d.get("kvittering"): return 11
    if d.get("logud"): return 12
    return 0 if d.get("skifter") else 1


def _knap_grupper(layout):
    g = {}
    for d in (layout or {}).get("items", []):
        if d.get("type") == "knap":
            for navn in (d.get("skifter"), d.get("trin"), d.get("felt"), d.get("login"), d.get("nulstil"), d.get("store"), d.get("taeller"), d.get("gruppe")):
                if navn and navn not in g:
                    g[navn] = len(g)
    return g


def _kilde_for(skaerm):
    def find(navn):
        if navn in SPILDATA:
            return SPILDATA[navn]
        if navn in KNAP_GRUPPER:
            return ("knap", "", KNAP_GRUPPER[navn])
        m = re.match(r"^(Tekst|Maske|Ren)(\d)$", navn)
        if m:
            return ("tekstfelt", "", KNAP_GRUPPER.get("Felt", 0) * 100 + int(m.group(2)) * 10 + {"Tekst": 0, "Maske": 1, "Ren": 2}[m.group(1)])
        if skaerm in NATRON_SKAERME and navn in NATRON_DATA:
            return NATRON_DATA[navn]
        k = KOBLINGER.get(skaerm, {}).get(navn)
        if k:
            return ("tekst", k)
        if navn in KUN_PASSAGER:
            if skaerm != "Passager":
                raise movia_regler.RegelFejl("'%s' virker kun paa passagerskaermen" % navn)
            return KUN_PASSAGER[navn]
        if navn in NATRON_DATA:
            raise movia_regler.RegelFejl("'%s' virker kun paa bordcomputer-skaermene (Main, Driving, Header)" % navn)
        if navn in SENERE:
            raise movia_regler.RegelFejl("'%s' er ikke koblet til regel-motoren endnu" % navn)
        return None
    return find


def _maal_for(skaerm, layout):
    navne = {}
    for i, d in enumerate((layout or {}).get("items", [])):
        if not d.get("name"):
            continue
        if d.get("spil"):
            navne[d["name"]] = d["spil"]
        elif d.get("data") or d.get("state"):
            noegle = d.get("data") or ("@" + d["state"])
            navne[d["name"]] = KOBLINGER.get(skaerm, {}).get(noegle, noegle)
        else:
            bogstav = "G" if d.get("type") == "gps" else "K" if d.get("type") == "knap" else "T" if d.get("type") == "text" else ("I" if (d.get("image") or d.get("video")) else "B")
            navne[d["name"]] = PRAEFIKS + bogstav + "%03d" % i
    return lambda el: navne.get(el, el)


def _billed_holdere(skaerm, billeder):
    """Skjulte billed-lag, saa billederne kommer med i modden og
    regel-motoren kan kopiere dem over i andre lag."""
    if not billeder:
        return {}
    sti = movia_tools._sti(skaerm)
    rod = _rod(sti)
    tree = rod.get_outer()
    holdere = {}
    for navn in sorted(billeder):
        tex = _find_billede(navn)
        if not tex:
            log("ADVARSEL: fandt ikke billedet " + navn)
            continue
        wnavn = PRAEFIKS + "BILLEDE_" + "".join(c if c.isalnum() else "_" for c in navn)
        w = _hent_eller_ny(unreal.Image, tree, sti, wnavn)
        brush = w.get_editor_property("brush")
        brush.set_editor_property("resource_object", tex)
        w.set_editor_property("brush", brush)
        _placer(rod, w, {"X": 0, "Y": 0, "W": 1, "H": 1, "Z": -50, "Skjult": "True"}, auto_stoerrelse=False)
        holdere[navn] = wnavn
    return holdere


NAVNE_OPSLAG = {"til": False}


def _indeks_sti(sti, rod, navn):
    """Widgetnavn -> sti af barne-numre fra rod, fx '3/0/2' (det kan motoren finde i spillet)."""
    w = _widget(sti, navn) if navn else None
    if w is None:
        if navn:
            unreal.log_error("[MOVIA REGLER] fandt ikke elementet '%s' paa skaermen" % navn)
        return "999"
    dele, cur = [], w
    while True:
        p = cur.get_parent()
        if p is None:
            return "999"
        dele.insert(0, str(p.get_child_index(cur)))
        if p == rod:
            # "@Navn|sti": motoren finder elementet paa navn i spillet, og bruger kun stien hvis navnet ikke findes
            if NAVNE_OPSLAG.get("til"):
                return "@%s|%s" % (w.get_name(), "/".join(dele))
            return "/".join(dele)
        cur = p


def saet_regler(skaerm, layout, regler, sider=None):
    sider = sider or (layout or {}).get("sider")
    if not regler and not sider:
        return
    billeder = {str(r.get(k)) for r in (regler or []) if r.get("saet") == "billede"
                for k in ("til", "ellers") if r.get(k)}
    holdere = _billed_holdere(skaerm, billeder)
    KNAP_GRUPPER.clear()
    KNAP_GRUPPER.update(_knap_grupper(layout))
    prog = movia_regler.kompiler(regler, _kilde_for(skaerm), _maal_for(skaerm, layout),
                                 lambda n: holdere.get(n, n), sider,
                                 log=lambda t: unreal.log_error("[MOVIA REGLER] " + t))
    for l in prog["log"]:
        log("  regel: " + l)
    sti = movia_tools._sti(skaerm)
    rod = _rod(sti)
    tree = rod.get_outer()

    if not unreal.EditorAssetLibrary.does_asset_exist(REGEL_WIDGET):
        log("BEMAERK: regel-motoren (WBP_MoviaMotor) findes ikke i denne mod - reglerne er ikke sat ind.")
        return

    # saet motoren ind paa skaermens rod
    w = _widget(sti, REGEL_NAVN)
    if w is None or w.get_parent() != rod:
        klasse = unreal.EditorAssetLibrary.load_blueprint_class(REGEL_WIDGET)
        w = _hent_eller_ny(klasse, tree, sti, REGEL_NAVN) if w is None else w
        _placer(rod, w, {"X": 0, "Y": 0, "W": 1, "H": 1, "Z": 9999, "Skjult": "False"}, auto_stoerrelse=False)
        log("Regel-motoren sat ind paa " + skaerm)
    w.modify()

    NAVNE_OPSLAG["til"] = False   # navne-opslag slaaet fra (virkede ikke i spillet) - stier som foer
    P = lambda navn: _indeks_sti(sti, rod, navn)
    V, C, Rr = prog["vars"], prog["conds"], prog["rules"]
    vals = {
        "VarType": [v[0] for v in V], "VarPath": [P(v[1]) if v[0] in (0, 1, 30) else (v[1] if v[0] in (27, 32, 33) else "") for v in V],
        "VarIdx": [int(v[2]) for v in V],
        "CVar": [c["var"] for c in C], "CKind": [c["kind"] for c in C], "CLo": [float(c["lo"]) for c in C],
        "CHi": [float(c["hi"]) for c in C], "CStr": [c["str"] for c in C], "CNeg": [bool(c["neg"]) for c in C],
        "CA": [float(c["a"]) for c in C], "CB": [float(c["b"]) for c in C], "CM": [float(c["m"]) for c in C],
        "CNew": [bool(c["new"]) for c in C],
        "RStart": [r["start"] for r in Rr], "RCount": [r["count"] for r in Rr], "RAction": [r["action"] for r in Rr],
        "RTarget": [P(r["target"]) for r in Rr], "RHasEllers": [r["has_ellers"] for r in Rr],
        "RColTil": [_farve(r["col_til"]) for r in Rr], "RColEllers": [_farve(r["col_ellers"]) for r in Rr],
        "RNumTil": [float(r["num_til"]) for r in Rr], "RNumEllers": [float(r["num_ellers"]) for r in Rr],
        "RTxtTil": [P(r["txt_til"]) if r["action"] == 6 else r["txt_til"] for r in Rr],
        "RSuffix": [r["suffix"] for r in Rr],
        "RTxtEllers": [P(r["txt_ellers"]) if r["action"] == 6 else r["txt_ellers"] for r in Rr],
        "RSlotVar": [int(r["slot"][0]) for r in Rr], "RSlotA": [float(r["slot"][1]) for r in Rr],
        "RSlotB": [float(r["slot"][2]) for r in Rr], "RSlotM": [float(r["slot"][3]) for r in Rr],
        "RSlotFmt": [int(r["slot"][4]) for r in Rr], "RGlid": [float(r["glid"]) for r in Rr],
    }
    items = (layout or {}).get("items", [])
    gps = [(i, d) for i, d in enumerate(items) if d.get("type") == "gps"]
    ring = [(i, d) for i, d in enumerate(items) if d.get("ring")]
    vals["AfgBrug"] = any(v[0] in (16, 17) for v in V)   # v2: henter fra koereplanen (OperatingPlan), ingen komponent
    if any(d.get("video") for d in (layout or {}).get("items", [])):
        vals["Interval"] = 0.08      # hurtigere opdatering saa videoer koerer flydende
    knapper = [(i, d) for i, d in enumerate(items) if d.get("type") == "knap"]
    vals.update({
        "KnapPath": [P(PRAEFIKS + "K%03d" % i) for i, d in knapper],
        "KnapGruppe": [KNAP_GRUPPER.get(d.get("skifter") or d.get("trin") or d.get("felt") or d.get("login") or d.get("taeller") or d.get("gruppe"), 0) for i, d in knapper],
        "KnapMode": [_knap_mode(d) for i, d in knapper],
        "KnapVaerdi": [float(d.get("vaerdi", 1)) for i, d in knapper],
        "KnapMin": [float(KNAP_GRUPPER.get(d.get("nulstil"), -1)) if _knap_mode(d) in (2, 3, 4) else float(d.get("min", -999)) for i, d in knapper],
        "KnapMax": [float(KNAP_GRUPPER.get(d.get("store"), -1)) if _knap_mode(d) in (2, 3, 4) else float(d.get("max", 999)) for i, d in knapper],
        "KnapTegn": [P(d["print"]) if d.get("print") else P(d["kategori"]) if d.get("kategori") else str(d["skiftrute"] if d.get("skiftrute") is not None else d["tekstsaet"] if d.get("tekstsaet") is not None else d.get("tegn", d.get("tilfoejtag", d.get("skiftertag", "")))) for i, d in knapper],
        "HuskGruppe": KNAP_GRUPPER.get("Husk", -1), "FeltGruppe": KNAP_GRUPPER.get("Felt", -1),
        "RulGruppe": KNAP_GRUPPER.get("Rul", -1),
    })
    if knapper:
        log("Knapper: %s  grupper: %s" % ([d.get("name") for i, d in knapper], KNAP_GRUPPER))
    vals["NaviPath"] = ""
    vals["RingPath"] = ""
    if gps:
        i, d = gps[0]
        vals.update({"NaviPath": P(PRAEFIKS + "G%03d" % i), "NaviX": float(d.get("x", 0)), "NaviY": float(d.get("y", 0)),
                     "NaviW": float(d.get("w", 0)), "NaviH": float(d.get("h", 0)),
                     "NaviPitch": float(d.get("pitch", -35)), "NaviDist": float(d.get("afstand", 4000)),
                     "NaviAngle": float(d.get("vinkel", 35)), "Interval": float(d.get("interval", 0.05)),
                     "NaviZoom": float(d.get("zoom", 0.4)),
                     "NaviVej": _farve(d.get("vej", "#8E9CC4")), "NaviVejStor": _farve(d.get("storvej", "#C3CCE6"))})
        bg = _find_billede(d.get("baggrund", "")) if d.get("baggrund") else None
        vals["NaviBg"] = bg
        log("GPS-kort: %s (pitch %s)" % (vals["NaviPath"], vals["NaviPitch"]))
        if ring:
            j, rd = ring[0]
            bogstav = "I" if rd.get("image") else "B"
            vals.update({"RingPath": P(PRAEFIKS + bogstav + "%03d" % j), "RingW": float(rd.get("w", 0)), "RingH": float(rd.get("h", 0))})
            log("3D-ring om naeste stop: " + vals["RingPath"])
    for navn, v in vals.items():
        try:
            w.set_editor_property(navn, v)
        except Exception as e:
            unreal.log_error("[MOVIA REGLER] kunne ikke saette %s: %s" % (navn, e))
    try:
        mappe = os.path.dirname(os.path.abspath(__file__))
        import json
        with open(os.path.join(mappe, "program_%s.txt" % skaerm), "w", encoding="utf-8") as f:
            json.dump({k: (v if k not in ("RColTil", "RColEllers") else [str(x) for x in v]) for k, v in vals.items()},
                      f, ensure_ascii=False, indent=1, default=str)
    except Exception:
        pass
    bp = unreal.EditorAssetLibrary.load_asset(sti)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_asset(sti, only_if_is_dirty=False)
    log("Regel-motoren paa %s har nu %d regel(er), %d betingelse(r), %d datafelt(er)" % (skaerm, len(Rr), len(C), len(V)))
