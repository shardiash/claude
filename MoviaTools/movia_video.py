# -*- coding: utf-8 -*-
"""
MOVIA - laver videoer om til "flipbooks" (alle billeder samlet i et stort billede),
saa de kan afspilles som reklamer paa skaermene i The Bus.

Brug:  laeg .mp4/.mov/.webm/.gif i mappen  MoviaTools\\Reklamer  og dobbeltklik  video_til_flipbook.bat
Kraever:  pip install opencv-python pillow

For hver video laves:
   Reklamer\\<navn>_flipbook.png   (billedet)
   Reklamer\\<navn>_flipbook.json  (kolonner, raekker, fps)
Saa kan videoen bruges i kommando.json med  "video": "...\\Reklamer\\<navn>_flipbook.png"
"""
import json
import os
import sys

MAPPE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Reklamer")
MAX_BILLEDER = 64        # flere billeder = laengere video, men stoerre fil
FPS = 8                  # billeder pr. sekund i flipbooken
BREDDE = 480             # bredde af hvert billede i pixels
MAX_ATLAS = 4096         # Unreal-graense for et billede


def lav_flipbook(sti):
    import cv2
    from PIL import Image
    cap = cv2.VideoCapture(sti)
    if not cap.isOpened():
        print("  kunne ikke aabne", sti)
        return
    kilde_fps = cap.get(cv2.CAP_PROP_FPS) or 25
    antal = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    trin = max(1.0, kilde_fps / FPS)
    billeder, i, naeste = [], 0, 0.0
    while len(billeder) < MAX_BILLEDER:
        ok, frame = cap.read()
        if not ok:
            break
        if i >= naeste:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            billeder.append(Image.fromarray(frame))
            naeste += trin
        i += 1
    cap.release()
    if not billeder:
        print("  ingen billeder i", sti)
        return
    w0, h0 = billeder[0].size
    bw = BREDDE
    bh = max(1, round(h0 * bw / w0))
    kol = min(len(billeder), MAX_ATLAS // bw)
    rk = -(-len(billeder) // kol)
    while rk * bh > MAX_ATLAS:          # for hoej - gør billederne mindre
        bw = int(bw * 0.85)
        bh = max(1, round(h0 * bw / w0))
        kol = min(len(billeder), MAX_ATLAS // bw)
        rk = -(-len(billeder) // kol)
    atlas = Image.new("RGB", (kol * bw, rk * bh), (0, 0, 0))
    for n, b in enumerate(billeder):
        atlas.paste(b.resize((bw, bh), Image.LANCZOS), ((n % kol) * bw, (n // kol) * bh))
    navn = os.path.splitext(os.path.basename(sti))[0]
    ud = os.path.join(MAPPE, navn + "_flipbook.png")
    atlas.save(ud)
    meta = {"kolonner": kol, "raekker": rk, "billeder": len(billeder), "fps": FPS,
            "bredde": bw, "hoejde": bh, "sekunder": round(len(billeder) / FPS, 1)}
    json.dump(meta, open(os.path.join(MAPPE, navn + "_flipbook.json"), "w"), indent=1)
    print("  OK: %s  (%d billeder, %.1f sek, %dx%d)" % (os.path.basename(ud), len(billeder), meta["sekunder"], atlas.width, atlas.height))


def main():
    try:
        import cv2  # noqa
        import PIL  # noqa
    except ImportError:
        print("Mangler pakker. Koer:  pip install opencv-python pillow")
        input("Tryk Enter...")
        return
    os.makedirs(MAPPE, exist_ok=True)
    filer = [f for f in sorted(os.listdir(MAPPE)) if f.lower().endswith((".mp4", ".mov", ".webm", ".gif", ".avi", ".mkv"))]
    if not filer:
        print("Ingen videoer i", MAPPE)
    for f in filer:
        print("Laver flipbook af", f)
        lav_flipbook(os.path.join(MAPPE, f))
    if "--stille" not in sys.argv:
        input("Faerdig. Tryk Enter...")


if __name__ == "__main__":
    main()
