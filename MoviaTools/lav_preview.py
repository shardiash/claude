"""Laver Movia_preview.html: interaktiv browser-preview af kommando.json (ingen Unreal nødvendig).
Brug: python3 lav_preview.py [kommando.json] [ud.html]"""
import base64, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
kfil = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, "kommando.json")
ud = sys.argv[2] if len(sys.argv) > 2 else os.path.join(H, "Movia_preview.html")
k = json.load(open(kfil, encoding="utf-8"))
k = [e for e in k if e.get("skaerm") != "Tjeneste" and e.get("layout")]
txt = json.dumps(k, ensure_ascii=False)
txt = re.sub(r"[A-Za-z0-9._%+-]+@movia\.dk", "chauffoer@eksempel.dk", txt)  # ingen rigtig mail i preview
def b64(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
brugt = set(re.findall(r"([\w\-]+\.png)", txt))
ik = {f: b64(os.path.join(H, "Ikoner", f)) for f in os.listdir(os.path.join(H, "Ikoner")) if f in brugt}
for navn in re.findall(r'"image": "(T_[\w]+)"', txt):          # Unreal-tekstur -> lokal png hvis den findes
    f = navn[2:].lower() + ".png"
    if os.path.exists(os.path.join(H, f)): brugt.add(f)
bil = {f: b64(os.path.join(H, f)) for f in brugt if f not in ik and os.path.exists(os.path.join(H, f)) and not f.startswith("_")}
tpl = open(os.path.join(H, "preview_tpl.html"), encoding="utf-8").read()
html = tpl.replace("__DATA__", txt.replace("</", "<\\/")).replace("__ICONS__", json.dumps(ik)).replace("__BILLEDER__", json.dumps(bil))
open(ud, "w", encoding="utf-8").write(html)
print(ud, round(len(html)/1024), "KB;", len(ik), "ikoner,", len(bil), "billeder; skærme:", [e["skaerm"] for e in k])
