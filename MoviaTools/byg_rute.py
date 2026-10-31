# -*- coding: utf-8 -*-
"""Skift rute (Driving/Main): trin 1 vaelg tur (naer dig / soeg linje), trin 2 vaelg startstop,
pause-kort med nedtaelling til afgang. Laver ogsaa skaermen 'Tjeneste' (tjenestekoersel til foerste stop)
som en kopi af Driving. Brug: python3 byg_rute.py [kommando.json]"""
import copy, json, sys
KOM = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/MoviaTools/kommando.json"
IK = "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\"
d = json.load(open(KOM, encoding="utf-8"))
sk = {k["skaerm"]: k for k in d}


def px(v): return round(v * 0.75)
def box(n, x, y, w, h, c, **kw): it = {"type": "box", "name": n, "x": x, "y": y, "w": w, "h": h, "color": c}; it.update(kw); return it
def img(n, x, y, w, h, f, **kw): it = box(n, x, y, w, h, "#FFFFFF", image=IK + f); it.update(kw); return it
def txt(n, x, y, t, s, c="#FFFFFF", fed=False, w=None, h=None, align=None, klip=False, **kw):
    it = {"type": "text", "name": n, "x": x, "y": y, "text": t, "size": px(s), "bold": fed, "color": c}
    if w: it["w"] = w
    if h: it["h"] = h
    if align: it["align"] = align
    if klip: it["klip"] = True
    it.update(kw); return it
def midt(n, x, y, w, h, t, s, c="#FFFFFF", fed=False, **kw):
    lh = s * 1.21
    return txt(n, x, round(y + (h - lh) / 2), t, s, c, fed, w=w, h=round(lh) + 4, align="midt", **kw)
def knap(n, x, y, w, h, **kw): it = {"type": "knap", "name": n, "x": x, "y": y, "w": w, "h": h}; it.update(kw); return it


AAB = "SRAaben = 1"
T1 = AAB + " og RTrin < 2"
T2 = AAB + " og RTrin = 2"
BLAA, GROEN, MOERK, MOERK2, PANEL, GRAA = "#1E5FD6", "#5CBF2A", "#1B1F25", "#20252C", "#262B33", "#3A414D"


def rute_lag():
    S, R = [], []
    z = [1700]
    kz = [2300]
    def s_(it, cond=AAB, glid=True):
        if it["type"] != "knap":
            it["z"] = z[0]; z[0] += 1; it.setdefault("opacity", 0)
        else:
            it["z"] = kz[0]; kz[0] += 1
        S.append(it)
        r = {"hvis": cond, "saet": "vis", "element": it["name"]}
        if glid and it["type"] != "knap": r["glid"] = 0.2
        R.append(r); return it
    def tekst(el, til): R.append({"saet": "tekst", "element": el, "til": til})

    # ---------- header ----------
    s_(box("SR header", 0, 26, 1200, 72, "#0A0A0A"))
    s_(box("SR luk bund", 0, 26, 80, 72, BLAA))
    s_(img("SR luk ikon", 26, 48, 28, 28, "ikon_luk.png"))
    s_(txt("SR titel", 100, 44, "Skift rute", 30, fed=True))
    s_(txt("SR under 1", 268, 56, "Trin 1 af 2 · vælg tur", 16, "#C9D1DC"), T1)
    s_(txt("SR under 2", 268, 56, "Trin 2 af 2 · hvor vil du starte? (fx som ekstrabus midt på ruten)", 16, "#C9D1DC"), T2)
    s_(txt("SR ur", 880, 36, "07:30:22", 42, w=258, h=56, align="hoejre"))
    tekst("SR ur", "{KlokkeSek:hh:mm:ss}")
    s_(box("SR venstre", 80, 98, 520, 602, PANEL))
    s_(box("SR hoejre", 600, 98, 600, 602, "#15181D"))

    # ---------- trin 1: faner ----------
    for j, (navn, x) in enumerate((("NÆR DIG", 120), ("SØG LINJE", 344))):
        s_(box("SR fane %d" % j, x, 112, 216, 48, MOERK), T1)
        s_(midt("SR fane %d tekst" % j, x, 112, 216, 48, navn, 17, "#AEB6C2", True), T1)
        R.append({"hvis": "RFane = %d" % j, "saet": "farve", "element": "SR fane %d" % j, "til": BLAA, "ellers": MOERK})
        R.append({"hvis": "RFane = %d" % j, "saet": "tekstfarve", "element": "SR fane %d tekst" % j, "til": "#FFFFFF", "ellers": "#AEB6C2"})
    s_(knap("SR fane 0 tryk", 120, 112, 216, 48, rutesoeg=0, gruppe="RFane", vaerdi=0), T1)
    s_(knap("SR fane 1 tryk", 344, 112, 216, 48, trin="RFane", vaerdi=0, min=1, max=1), T1)
    s_(txt("SR status", 120, 176, "", 14, "#AEB6C2", w=440, h=20, klip=True), T1)
    tekst("SR status", "{SRStatus}")
    s_(txt("SR tom", 120, 300, "Tryk NÆR DIG eller søg en linje", 16, "#8A93A3", w=440, h=24, align="midt"), T1 + " og SRAntal = 0")

    # ---------- trin 1: liste ----------
    for i in range(6):
        r = i + 1
        y = 198 + i * 62
        c = T1 + " og SRFindes%d = 1" % r
        s_(box("SR r%d bund" % r, 120, y, 440, 56, MOERK if i % 2 == 0 else MOERK2), c)
        R.append({"hvis": "SRValgt%d = 1" % r, "saet": "farve", "element": "SR r%d bund" % r, "til": BLAA, "ellers": MOERK if i % 2 == 0 else MOERK2})
        s_(txt("SR r%d tid" % r, 136, y + 8, "", 24, fed=True, w=86, h=32), c); tekst("SR r%d tid" % r, "{SRTid%d}" % r)
        s_(txt("SR r%d linje" % r, 226, y + 8, "", 16, "#FFB000", True, w=240, h=22, klip=True), c); tekst("SR r%d linje" % r, "{SRLinje%d}" % r)
        R.append({"hvis": "SRValgt%d = 1" % r, "saet": "tekstfarve", "element": "SR r%d linje" % r, "til": "#FFFFFF", "ellers": "#FFB000"})
        s_(txt("SR r%d til" % r, 226, y + 30, "", 13, "#AEB6C2", w=240, h=20, klip=True), c); tekst("SR r%d til" % r, "{SRTil%d}" % r)
        s_(txt("SR r%d om" % r, 466, y + 18, "", 14, "#AEB6C2", w=80, h=20, align="hoejre"), c); tekst("SR r%d om" % r, "{SROm%d}" % r)
        s_(knap("SR r%d tryk" % r, 120, y, 440, 56, raekke=i, gruppe="RValg", rul="RRul"), c)
    s_(txt("SR antal", 120, 582, "", 13, "#8A93A3", w=300, h=20), T1 + " og SRAntal > 0")
    tekst("SR antal", "{SRAntal} afgange · rul med pilene")
    for j, (navn, v, x) in enumerate((("op", -1, 440), ("ned", 1, 504))):
        s_(box("SR rul %s bund" % navn, x, 570, 56, 40, GRAA), T1 + " og SRAntal > 6")
        s_(img("SR rul %s ikon" % navn, x + 18, 580, 20, 20, "pil_%s.png" % navn), T1 + " og SRAntal > 6")
        s_(knap("SR rul %s tryk" % navn, x, 570, 56, 40, trin="RRul", vaerdi=v, min=0, max=74), T1 + " og SRAntal > 6")
    s_(box("SR ok bund", 120, 618, 440, 64, GROEN), T1)
    s_(midt("SR ok tekst", 120, 618, 440, 64, "VÆLG TUR · VÆLG STARTSTOP →", 19, fed=True), T1)
    s_(knap("SR ok tryk", 120, 618, 440, 64, rutevaelg=True), T1)

    # ---------- trin 1 hoejre: naer dig ----------
    N0 = T1 + " og RFane = 0"
    s_(box("SR naer kort", 640, 130, 520, 300, MOERK2), N0)
    s_(box("SR naer kant", 640, 130, 4, 300, BLAA), N0)
    s_(txt("SR naer t1", 670, 156, "Ture nær dig", 26, fed=True), N0)
    s_(txt("SR naer t2", 670, 204, "Listen viser ture fra alle linjer, der kører", 16, "#C9D1DC"), N0)
    s_(txt("SR naer t3", 670, 230, "forbi det stoppested, der er tættest på bussen,", 16, "#C9D1DC"), N0)
    s_(txt("SR naer t4", 670, 256, "de næste 2 timer.", 16, "#C9D1DC"), N0)
    s_(box("SR opdater bund", 670, 330, 230, 64, BLAA), N0)
    s_(midt("SR opdater tekst", 670, 330, 230, 64, "OPDATER", 20, fed=True), N0)
    s_(knap("SR opdater tryk", 670, 330, 230, 64, rutesoeg=0, gruppe="RFane", vaerdi=0), N0)

    # ---------- trin 1 hoejre: soeg linje ----------
    N1 = T1 + " og RFane = 1"
    s_(txt("SR felt label", 640, 116, "LINJENUMMER", 14, "#AEB6C2"), N1)
    s_(box("SR felt ramme", 638, 138, 304, 64, BLAA), N1)
    s_(box("SR felt", 640, 140, 300, 60, "#E9EDF2"), N1)
    s_(box("SR felt kant", 640, 140, 6, 60, BLAA), N1)
    s_(txt("SR felt tekst", 660, 152, "", 26, "#15181D", True, w=270, h=36, klip=True), N1)
    tekst("SR felt tekst", "{Ren8}")
    s_(box("SR vis bund", 952, 140, 208, 60, GROEN), N1)
    s_(midt("SR vis tekst", 952, 140, 208, 60, "VIS AFGANGE", 18, fed=True), N1)
    s_(knap("SR vis tryk", 952, 140, 208, 60, rutesoeg=1, gruppe="RFane", vaerdi=1), N1)
    taster = [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"),
              ("RYD", "C"), ("0", "0"), ("⌫", "<")]
    for k, (lab, tegn) in enumerate(taster):
        x, y = 640 + (k % 3) * 176, 218 + (k // 3) * 88
        farve = GRAA if tegn in ("C", "<") else "#2B313B"
        s_(box("SR tast %d bund" % k, x, y, 168, 80, farve), N1)
        s_(box("SR tast %d kant" % k, x, y + 77, 168, 3, "#0F1115"), N1)
        if tegn == "<":
            s_(img("SR tast %d ikon" % k, x + 70, y + 30, 28, 20, "ikon_slet.png"), N1)
        else:
            s_(midt("SR tast %d tekst" % k, x, y, 168, 80, lab, 20 if tegn == "C" else 30), N1)
        s_(knap("SR tast %d tryk" % k, x, y, 168, 80, rutetegn=tegn), N1)
    s_(box("SR info", 640, 574, 520, 112, PANEL), T1)
    s_(box("SR info kant", 640, 574, 4, 112, "#FFB000"), T1)
    s_(txt("SR info 1", 660, 588, "Nær dig eller søg linje", 15, fed=True), T1)
    s_(txt("SR info 2", 660, 614, "Nær dig viser ture forbi det nærmeste stop.", 13, "#C9D1DC"), T1)
    s_(txt("SR info 3", 660, 634, "Søg linje: skriv fx 17 og se alle dagens afgange,", 13, "#C9D1DC"), T1)
    s_(txt("SR info 4", 660, 654, "uanset hvor du er på kortet.", 13, "#C9D1DC"), T1)

    # ---------- trin 2 ----------
    s_(box("SR tur kort", 120, 112, 440, 56, MOERK), T2)
    s_(box("SR tur kant", 120, 112, 4, 56, "#FFB000"), T2)
    s_(txt("SR tur titel", 136, 118, "", 18, fed=True, w=410, h=24, klip=True), T2); tekst("SR tur titel", "{SRTitel}")
    s_(txt("SR tur under", 136, 142, "", 13, "#AEB6C2", w=410, h=20, klip=True), T2); tekst("SR tur under", "{SRUnder}")
    s_(txt("SR stop label", 120, 182, "VÆLG STARTSTOP", 14, "#AEB6C2"), T2)
    for i in range(6):
        r = i + 1
        y = 204 + i * 58
        c = T2 + " og SRStop%dFindes = 1" % r
        alt = MOERK if i % 2 == 0 else MOERK2
        s_(box("SR s%d bund" % r, 120, y, 440, 52, alt), c)
        R.append({"hvis": "SRStop%dValgt = 1" % r, "saet": "farve", "element": "SR s%d bund" % r, "til": BLAA, "ellers": alt})
        s_(box("SR s%d prik" % r, 134, y + 20, 12, 12, "#FFB000"), c)
        R.append({"hvis": "SRStop%dValgt = 1" % r, "saet": "farve", "element": "SR s%d prik" % r, "til": "#FFFFFF", "ellers": "#FFB000"})
        s_(txt("SR s%d tid" % r, 160, y + 12, "", 20, fed=True, w=74, h=28), c); tekst("SR s%d tid" % r, "{SRStop%dTid}" % r)
        s_(txt("SR s%d navn" % r, 240, y + 13, "", 17, w=196, h=26, klip=True), c); tekst("SR s%d navn" % r, "{SRStop%dNavn}" % r)
        s_(txt("SR s%d maerke" % r, 436, y + 16, "", 13, "#8A93A3", w=110, h=20, align="hoejre"), c); tekst("SR s%d maerke" % r, "{SRStop%dMaerke}" % r)
        s_(knap("SR s%d tryk" % r, 120, y, 440, 52, raekke=i, gruppe="SValg", rul="SRul"), c)
    s_(txt("SR stop hint", 120, 566, "Stop før dit startstop springes over", 13, "#8A93A3"), T2)
    for j, (navn, v, x) in enumerate((("op", -1, 440), ("ned", 1, 504))):
        s_(box("SR srul %s bund" % navn, x, 556, 56, 40, GRAA), T2 + " og SRStopAntal > 6")
        s_(img("SR srul %s ikon" % navn, x + 18, 566, 20, 20, "pil_%s.png" % navn), T2 + " og SRStopAntal > 6")
        s_(knap("SR srul %s tryk" % navn, x, 556, 56, 40, trin="SRul", vaerdi=v, min=0, max=60), T2 + " og SRStopAntal > 6")
    s_(box("SR tilbage bund", 120, 618, 130, 64, GRAA), T2)
    s_(midt("SR tilbage tekst", 120, 618, 130, 64, "← TILBAGE", 16, fed=True), T2)
    s_(knap("SR tilbage tryk", 120, 618, 130, 64, trin="RTrin", vaerdi=0, min=1, max=1), T2)
    s_(box("SR start bund", 260, 618, 300, 64, GROEN), T2)
    s_(midt("SR start tekst", 260, 618, 300, 64, "", 20, fed=True), T2); tekst("SR start tekst", "START VED {SRStartTid}")
    s_(knap("SR start tryk", 260, 618, 300, 64, rutestart=True), T2)
    # hoejre: opsummering
    s_(box("SR opsum", 640, 130, 520, 300, MOERK2), T2)
    s_(box("SR opsum kant", 640, 130, 4, 300, GROEN), T2)
    s_(txt("SR opsum l1", 670, 150, "DIN NYE TUR", 14, "#AEB6C2"), T2)
    s_(txt("SR opsum titel", 670, 172, "", 26, fed=True, w=470, h=36, klip=True), T2); tekst("SR opsum titel", "{SRTitel}")
    s_(txt("SR opsum l2", 670, 236, "STARTSTOP", 14, "#AEB6C2"), T2)
    s_(txt("SR opsum stop", 670, 258, "", 24, fed=True, w=470, h=34, klip=True), T2); tekst("SR opsum stop", "{SRStartNavn}")
    s_(txt("SR opsum l3", 670, 318, "AFGANG", 14, "#AEB6C2"), T2)
    s_(txt("SR opsum tid", 670, 338, "", 40, "#5CBF2A", True, w=300, h=54), T2); tekst("SR opsum tid", "{SRStartTid}")
    s_(box("SR info2", 640, 574, 520, 112, PANEL), T2)
    s_(box("SR info2 kant", 640, 574, 4, 112, "#FFB000"), T2)
    s_(txt("SR info2 1", 660, 588, "Ekstrabus / backup", 15, fed=True), T2)
    s_(txt("SR info2 2", 660, 614, "Kør hen til det valgte stop. Pause-kortet tæller ned", 13, "#C9D1DC"), T2)
    s_(txt("SR info2 3", 660, 634, "til afgang derfra, og stoplisten starter ved stoppet.", 13, "#C9D1DC"), T2)

    # luk + klik-blokering
    s_(knap("SR blok", 80, 26, 1120, 674, trin="Blok", vaerdi=0, min=0, max=0), AAB)
    S[-1]["z"] = 1699
    s_(knap("SR luk tryk", 0, 26, 80, 72, skiftertag="MoviaRute"), AAB)
    return S, R


def pause_kort():
    """Trin 3: pause-kort med nedtaelling til afgang fra startstoppet (vises naar menuen er lukket)."""
    S, R = [], []
    P = "SRNed > 0 og SRAaben = 0"
    z = [380]
    def s_(it):
        it["z"] = z[0]; z[0] += 1; it.setdefault("opacity", 0)
        S.append(it); R.append({"hvis": P, "saet": "vis", "element": it["name"], "glid": 0.3}); return it
    s_(box("SR pause bund", 84, 102, 420, 190, BLAA))
    s_(txt("SR pause label", 100, 112, "PAUSE · NÆSTE TUR", 13, fed=True))
    s_(txt("SR pause tid", 100, 134, "", 46, fed=True, w=190, h=60)); R.append({"saet": "tekst", "element": "SR pause tid", "til": "{SRNed}"})
    s_(txt("SR pause til", 300, 154, "til afgang", 16))
    s_(box("SR pause streg", 100, 206, 388, 1, "#FFFFFF"))
    s_(txt("SR pause linje", 100, 216, "", 15, w=388, h=22, klip=True)); R.append({"saet": "tekst", "element": "SR pause linje", "til": "{SRTekst}"})
    s_(txt("SR pause fra", 100, 240, "", 15, "#DCE6FF", w=388, h=22, klip=True)); R.append({"saet": "tekst", "element": "SR pause fra", "til": "Fra {SRStopNavn}"})
    s_(txt("SR pause hint", 100, 264, "Kør til startstoppet før afgang", 13, "#DCE6FF", w=388, h=20))
    return S, R


PRE = ("SR ", "RuteTest")
def ryd(L):
    L["items"] = [i for i in L["items"] if not i["name"].startswith(PRE)]
    L["regler"] = [r for r in L.get("regler", []) if not str(r.get("element", "")).startswith(PRE)]

for navn in ("Driving", "Main"):
    L = sk[navn]["layout"]
    ryd(L)
    L["items"].append(img("SR ikon", 4, 542, 72, 84, "knap_rute3.png", z=205))
    L["items"].append(knap("SR tryk", 4, 542, 72, 84, skiftertag="MoviaRute", z=211))
    S, R = rute_lag()
    L["items"] += S; L["regler"] += R
    S, R = pause_kort()
    L["items"] += S; L["regler"] += R

# Tjeneste (spillets "Service Journey" - koersel hen til foerste stop): samme design som Driving
tj = {"skaerm": "Tjeneste", "layout": copy.deepcopy(sk["Driving"]["layout"])}
tj["layout"]["behold"] = []
d = [k for k in d if k["skaerm"] != "Tjeneste"]
idx = [i for i, k in enumerate(d) if k["skaerm"] == "Driving"][0]
d.insert(idx + 1, tj)

json.dump(d, open(KOM, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok", {k["skaerm"]: len(k.get("layout", {}).get("items", [])) for k in d})
