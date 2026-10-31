# -*- coding: utf-8 -*-
"""
Koer denne i The Bus Modding:  Tools > Execute Python Script > movia_motor_koer.py
Ret SKAERM og LAYOUT herunder, hvis du vil bygge en anden skaerm.
"""
import sys, importlib
MAPPE = r"C:\Users\tacci\Documents\The Bus\MoviaTools"
sys.path.append(MAPPE)
import movia_tools, movia_motor
importlib.reload(movia_tools); importlib.reload(movia_motor)

SKAERM = "Passager"
LAYOUT = MAPPE + r"\Eksport\MoviaLayout_Passager.csv"

movia_motor.byg(SKAERM, LAYOUT)
