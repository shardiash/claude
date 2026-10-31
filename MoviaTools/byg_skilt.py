# -*- coding: utf-8 -*-
"""Skilt-menu (Driving/Main) + 'Ikke i rute' paa passagerskaermen. Brug: python3 byg_skilt.py [kommando.json]"""
import json, sys
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


AAB = "SkiltAaben = 1"
def skilt_lag():
    S, R = [], []
    z = [1000]
    def s_(it, cond=AAB, glid=True):
        if it["type"] != "knap":
            it["z"] = z[0]; z[0] += 1; it.setdefault("opacity", 0)
        S.append(it)
        r = {"hvis": cond, "saet": "vis", "element": it["name"]}
        if glid and it["type"] != "knap": r["glid"] = 0.2
        R.append(r); return it
    # header
    s_(box("Skilt header", 0, 26, 1200, 72, "#0A0A0A"))
    s_(box("Skilt luk bund", 0, 26, 80, 72, "#1E5FD6"))
    s_(img("Skilt luk ikon", 26, 48, 28, 28, "ikon_luk.png"))
    s_(txt("Skilt titel", 100, 44, "Skilt", 30, fed=True))
    s_(txt("Skilt undertitel", 190, 56, "Linje og destination på bussens skilt", 16, "#C9D1DC"))
    s_(txt("Skilt ur", 880, 36, "07:30:22", 42, w=258, h=56, align="hoejre"))
    # venstre panel
    s_(box("Skilt venstre", 80, 98, 520, 602, "#262B33"))
    s_(txt("Skilt forh label", 120, 112, "FORHÅNDSVISNING", 13, "#AEB6C2"))
    s_(box("Skilt forh ramme", 118, 132, 444, 74, "#3A414D"))
    s_(box("Skilt forh", 120, 134, 440, 70, "#050505"))
    s_(txt("Skilt forh linje", 136, 146, "", 32, "#FFB000", True, w=90, h=44, klip=True))
    s_(txt("Skilt forh dest", 232, 150, "", 26, "#FFB000", True, w=318, h=40, klip=True))
    R += [{"saet": "tekst", "element": "Skilt forh linje", "til": "{Ren0}"},
          {"saet": "tekst", "element": "Skilt forh dest", "til": "{Ren1}"}]
    # felter
    for nr, (lab, y, w) in enumerate((("LINJENUMMER", 244, 300), ("DESTINATION", 336, 440))):
        s_(txt("Skilt felt %d label" % nr, 120, y - 22, lab, 14, "#AEB6C2"))
        s_(box("Skilt felt %d ramme" % nr, 118, y - 2, w + 4, 56, "#1E5FD6"), AAB + " og Felt = %d" % nr, glid=False)
        s_(box("Skilt felt %d" % nr, 120, y, w, 52, "#E9EDF2"))
        s_(box("Skilt felt %d kant" % nr, 120, y, 6, 52, "#8A93A3"))
        s_(txt("Skilt felt %d tekst" % nr, 138, y + 12, "", 22, "#15181D", w=w - 30, h=30, klip=True))
        R += [{"hvis": "Felt = %d" % nr, "saet": "farve", "element": "Skilt felt %d kant" % nr, "til": "#1E5FD6", "ellers": "#8A93A3"},
              {"saet": "tekst", "element": "Skilt felt %d tekst" % nr, "til": "{Tekst%d}" % nr}]
        s_(knap("Skilt felt %d tryk" % nr, 120, y, w, 52, trin="Felt", vaerdi=nr, min=nr, max=nr, z=1580 + nr))
    s_(box("Skilt fjern bund", 430, 244, 130, 52, "#3A414D"))
    s_(midt("Skilt fjern tekst", 430, 244, 130, 52, "FJERN NR.", 16, fed=True))
    s_(knap("Skilt fjern tryk", 430, 244, 130, 52, tekstsaet="", vaerdi=0, z=1583))
    # hurtigvalg
    s_(txt("Skilt hurtig label", 120, 408, "HURTIGVALG", 14, "#AEB6C2"))
    s_(box("Skilt rute bund", 120, 430, 440, 52, "#1E5FD6"))
    s_(txt("Skilt rute titel", 136, 434, "MIN RUTE", 12, "#C9D8F5", True))
    s_(txt("Skilt rute linje", 136, 450, "", 19, fed=True, w=64, h=28, klip=True))
    s_(txt("Skilt rute tekst", 204, 450, "", 19, fed=True, w=342, h=28, klip=True))
    R.append({"saet": "tekst", "element": "Skilt rute linje", "til": "{LinjeNr}"})
    R.append({"saet": "tekst", "element": "Skilt rute tekst", "til": "{SidsteStopNavn}"})
    s_(knap("Skilt rute tryk", 120, 430, 440, 52, rutetekst=True, z=1589))
    for k, (navn, tekst) in enumerate((("ikke", "Ikke i rute"), ("ekstra", "Ekstrabus"), ("skole", "Skolebus"), ("proeve", "Prøvekørsel"))):
        x, y = 120 + (k % 2) * 224, 490 + (k // 2) * 54
        s_(box("Skilt hv %s bund" % navn, x, y, 216, 46, "#1B1F25"))
        s_(box("Skilt hv %s kant" % navn, x, y, 4, 46, "#FFB000"))
        s_(midt("Skilt hv %s tekst" % navn, x, y, 216, 46, tekst, 17, fed=True))
        s_(knap("Skilt hv %s tryk" % navn, x, y, 216, 46, tekstsaet=tekst, vaerdi=1, z=1590 + k))
    # status (i forhaandsvisningens label-linje)
    s_(txt("Skilt status ruten", 360, 112, "Viser ruten", 13, "#AEB6C2", w=200, h=18, align="hoejre"), AAB + " og SkiltAktiv = 0")
    s_(txt("Skilt status eget", 360, 112, "Eget skilt sat", 13, "#FFB000", True, w=200, h=18, align="hoejre"), AAB + " og SkiltAktiv = 1")
    s_(box("Skilt saet bund", 120, 604, 300, 72, "#5CBF2A"))
    s_(midt("Skilt saet tekst", 120, 604, 300, 72, "SÆT SKILT", 24, fed=True))
    s_(knap("Skilt saet tryk", 120, 604, 300, 72, saetskilt=True, z=1600))
    s_(box("Skilt nulstil bund", 430, 604, 130, 72, "#3A414D"))
    s_(midt("Skilt nulstil tekst", 430, 604, 130, 72, "RUTEN", 18, fed=True))
    s_(knap("Skilt nulstil tryk", 430, 604, 130, 72, nulstilskilt=True, z=1601))
    # hoejre: tastatur
    s_(box("Skilt tastatur", 600, 98, 600, 602, "#15181D"))
    TEGN = dict(felt="Felt", store="Store")
    def tast(navn, x, y, w, label, farve="#2B313B", kant="#0F1115", storr=22, ikon=None, **kw):
        s_(box(navn + " bund", x, y, w, 62, farve)); s_(box(navn + " kant", x, y + 59, w, 3, kant))
        if ikon: s_(img(navn + " ikon", x + ikon[3], y + (62 - ikon[2]) // 2, ikon[1], ikon[2], ikon[0]))
        if label: s_(midt(navn + " tekst", x, y, w, 62, label, storr))
        s_(knap(navn + " tryk", x, y, w, 62, z=1610, **kw))
    for ri, r in enumerate(["1234567890", "QWERTYUIOP", "ASDFGHJKLÆ", "ZXCVBNMØÅ"]):
        for ci, c in enumerate(r):
            tast("Skilt tast %s" % c, 616 + ci * 57, 124 + ri * 68, 52, c, tegn=c.lower(), **TEGN)
    tast("Skilt tast slet", 616 + 9 * 57, 124 + 3 * 68, 52, "", farve="#3A414D", ikon=("ikon_slet.png", 28, 20, 12), slet=True, felt="Felt")
    for navn, x, w, c in (("punktum", 616, 52, "."), ("bindestreg", 673, 52, "-"), ("skraa", 730, 52, "/"), ("plus", 787, 52, "+")):
        tast("Skilt tast %s" % navn, x, 396, w, c, farve="#3A414D", tegn=c, **TEGN)
    tast("Skilt tast ryd", 844, 396, 166, "RYD", farve="#3A414D", storr=18, ryd=True, felt="Felt")
    tast("Skilt tast mellemrum", 1015, 396, 166, "MELLEMRUM", storr=16, tegn=" ", **TEGN)
    s_(box("Skilt tast store bund", 616, 476, 166, 62, "#3A414D")); s_(box("Skilt tast store kant", 616, 535, 166, 3, "#0F1115"))
    s_(img("Skilt tast store ikon", 650, 497, 20, 20, "ikon_store.png")); s_(txt("Skilt tast store tekst", 678, 493, "STORE", 18))
    s_(knap("Skilt tast store tryk", 616, 476, 166, 62, skifter="Store", z=1610))
    R.append({"hvis": "Store = 1", "saet": "farve", "element": "Skilt tast store bund", "til": "#1E5FD6", "ellers": "#3A414D"})
    tast("Skilt tast naeste", 1015, 476, 166, "NÆSTE FELT", farve="#1E5FD6", kant="#123A85", storr=18, skifter="Felt")
    s_(txt("Skilt tastatur hint", 616, 566, "Tryk på et felt for at skrive i det", 13, "#8A93A3"))
    # luk + klik-blokering
    s_(knap("Skilt blok", 80, 26, 1120, 674, trin="Blok", vaerdi=0, min=0, max=0, z=999))
    s_(knap("Skilt luk tryk", 0, 26, 80, 72, skiftertag="MoviaSkilt", z=1620))
    R.append({"saet": "tekst", "element": "Skilt ur", "til": "{KlokkeSek:hh:mm:ss}"})
    return S, R


PRE = ("Skilt ",)
def ryd(L):
    L["items"] = [i for i in L["items"] if not i["name"].startswith(PRE)]
    L["regler"] = [r for r in L.get("regler", []) if not str(r.get("element", "")).startswith(PRE)]

for navn in ("Driving", "Main", "Start", "LogIn", "Tur"):
    L = sk[navn]["layout"]
    ryd(L)
    if navn in ("Driving", "Main"):
        L["items"].append(img("Skilt ikon", 4, 454, 72, 84, "knap_skilt3.png", z=205))
        L["items"].append(knap("Skilt tryk", 4, 454, 72, 84, skiftertag="MoviaSkilt", z=211))
        S, R = skilt_lag()
        L["items"] += S; L["regler"] += R

# passagerskaerm: "Ikke i rute"
P = sk["Passager"]["layout"]
P["items"] = [i for i in P["items"] if not i["name"].startswith("IkkeIRute")]
P["regler"] = [r for r in P["regler"] if not str(r.get("element", "")).startswith("IkkeIRute")]
IKR = "IkkeIRute = 1"
P["items"] += [
    {"type": "box", "name": "IkkeIRute top", "x": 990, "y": 0, "w": 610, "h": 92, "color": "#FFFFFF", "z": 5000, "opacity": 0},
    {"type": "text", "name": "IkkeIRute tekst", "x": 1000, "y": 16, "text": "Ikke i rute", "size": 33, "bold": True, "color": "#1D1D1D", "z": 5001, "opacity": 0},
    {"type": "box", "name": "IkkeIRute bund", "x": 982, "y": 94, "w": 618, "h": 336, "color": "#FFFFFF", "z": 5002, "opacity": 0}]
P["regler"] += [{"hvis": IKR, "saet": "vis", "element": n, "glid": 0.3} for n in ("IkkeIRute top", "IkkeIRute tekst", "IkkeIRute bund")]
# eget skilt -> linjenummer paa passagerskaermen
P["regler"] = [r for r in P["regler"] if r.get("_skilt") is None]
P["regler"] += [{"hvis": "SkiltAktiv = 1", "saet": "tekst", "element": "Linje", "til": "{SkiltLinje}", "_skilt": 1},
                # ikke i rute: blaa STOP-boks uden tekst, Linje og Zone tomme, uret bliver
                {"hvis": IKR, "saet": "tekst", "element": "Linje", "til": "", "_skilt": 1},
                {"hvis": IKR, "saet": "tekst", "element": "Zone", "til": "Zone:", "ellers": "Zone: 2", "_skilt": 1},
                {"hvis": IKR, "saet": "tekst", "element": "Stop it tekst", "til": "", "_skilt": 1}]

json.dump(d, open(KOM, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok", {n: len(sk[n]["layout"]["items"]) for n in ("Driving", "Main", "Passager")})
