# -*- coding: utf-8 -*-
"""
DINE AENDRINGER - ret i denne fil og koer den.
I editoren: Tools > Execute Python Script > vaelg denne fil.
Resultatet skrives i Output Log (linjer med [MOVIA]).

Linjer der starter med # bliver ikke koert. Fjern # for at bruge en linje.
"""
import sys, importlib
sys.path.append(r"C:\Users\tacci\Documents\The Bus\MoviaTools")
import movia_tools
importlib.reload(movia_tools)
from movia_tools import *

# ---------- SE HVAD DER FINDES ----------
# Skriver alle elementnavne til Output Log:
vis_elementer("Passager")
# vis_elementer("Main")

# ---------- PASSAGERSKAERM ----------
# billede("Passager", "Image_Reklame", "/Game/MoviaSkaerme/T_Reklame_Boennebaren")
# tekst("Passager", "TextBlock_216", "Next stop")
# tekstfarve("Passager", "Text_NextBusStop", "#1D1D1D")
# skrift("Passager", "Text_NextBusStop", "SemiBold", 57)

# ---------- BORDCOMPUTER (Main) ----------
# skjul("Main", "Grid Panel Scroll List")
# farve("Main", "Image_BG Default", "#FFFFFF")

# ---------- GEM (skal altid staa sidst) ----------
gem_alt()
