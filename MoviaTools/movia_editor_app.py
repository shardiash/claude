# -*- coding: utf-8 -*-
"""
MOVIA EDITOR - lille visuel editor til skaermene i The Bus.

Start:  dobbeltklik  start_editor.bat   (eller:  python movia_editor.py)
Kraever: pip install PyQt6

- Traek elementer rundt med musen
- Dobbeltklik paa en tekst for at skrive i den
- Panelet til hoejre: tekst, stoerrelse, farve, UE-elementnavn, skjul
- "Eksporter script" laver linjer til movia_aendringer.py ud fra de
  elementer, der har et UE-elementnavn (tekst, farver og skjul).
  Placeringen (traek) er kun preview - den kommer ikke med i scriptet.
"""
import json
import os
import sys

from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QObject
from PyQt6.QtGui import (QAction, QBrush, QColor, QFont, QImage, QPainter, QPen,
                         QKeySequence, QPixmap)
from PyQt6.QtWidgets import (QApplication, QCheckBox, QListWidget, QColorDialog, QComboBox,
                             QFileDialog, QFormLayout, QGraphicsItem,
                             QGraphicsPixmapItem, QGraphicsRectItem,
                             QGraphicsScene, QGraphicsTextItem, QGraphicsView,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton, QSpinBox, QToolBar,
                             QVBoxLayout, QWidget)

MAPPE = os.path.dirname(os.path.abspath(__file__))
KOMMANDO = os.path.join(MAPPE, "kommando.json")
FONT = "Inter"

# ------------------------------------------------------------------
# Datafelter: hentes fra spillet af motoren (MoviaMotor) i modden.
# Teksten her er kun eksempel i preview.
# ------------------------------------------------------------------
DATAFELTER = {
    # tekst-datafelter (spillet skriver teksten)
    "NaesteStop":  "Hellbrookstraße",
    "SidsteStop":  "S+U Alexanderplatz",
    "Linje":       "7",
    "Ur":          "16:48",
    "Forsinkelse": "-0:01:35",
    "Dato":        "24. Okt. 2026",
    "LinjeDestination": "498 - S OSTBAHNHOF",
    "NaesteStopTid": "20:14",
    "Afstand":     "34m",
    "ForrigeStop": "S+U Alexanderplatz/Memhardstr.",
}
# hvilke datafelter der virker paa hvilken skaerm (som i AI_GUIDE.md)
PR_SKAERM = {
    "Passager": ["NaesteStop", "SidsteStop", "Linje", "Ur", "StopListe"],
    "Header":   ["Ur", "Forsinkelse", "Dato", "LinjeDestination"],
    "Main":     ["Header", "StopListe"],
    "Driving":  ["Header", "NaesteStop", "NaesteStopTid", "Afstand", "SidsteStop", "ForrigeStop"],
}
# omraade-datafelter (bokse som spillet fylder, fx hele stoplisten)
DATAOMRAADER = {"": "(ingen)", "StopListe": "Spillets stopliste", "Header": "Bordcomputerens topbjælke"}
# Bokse kan skifte farve efter tilstand:
TILSTANDE = {
    "": "Ingen (fast farve)",
    "StopOenske": "STOP trykket",
}

# ------------------------------------------------------------------
# Standard-layouts (samme som vores design)
# ------------------------------------------------------------------
SKAERME = {
    "Passager": {
        "w": 1600, "h": 430, "bg": "#FFFFFF", "ue": "Passager",
        "items": [
            {"type": "box", "x": 0, "y": 0, "w": 790, "h": 430, "color": "#FFD36E", "name": "Reklame", "ue": "", "image": "T_Reklame_Aeblefest"},
            {"type": "box", "x": 790, "y": 0, "w": 810, "h": 92, "color": "#F3F4F5", "name": "Topfelt", "ue": "Image_0"},
            {"type": "text", "x": 806, "y": 22, "text": "Næste stop", "size": 18, "color": "#333333", "bold": False, "name": "Næste stop", "ue": "TextBlock_98"},
            {"type": "text", "x": 806, "y": 46, "text": "Next stop", "size": 18, "color": "#8A8F94", "bold": False, "name": "Next stop", "ue": "TextBlock_216"},
            {"type": "text", "x": 942, "y": 18, "text": "", "data": "NaesteStop", "size": 40, "color": "#1D1D1D", "bold": True, "name": "Næste stops navn", "ue": "Text_NextBusStop"},
            {"type": "box", "x": 790, "y": 92, "w": 152, "h": 338, "color": "#F3F4F5", "name": "Venstre kolonne", "ue": ""},
            {"type": "box", "x": 790, "y": 93, "w": 152, "h": 136, "color": "#111111", "color_on": "#E2231A", "state": "StopOenske", "name": "STOP-felt", "ue": ""},
            {"type": "text", "x": 815, "y": 136, "text": "STOP", "size": 36, "color": "#FFFFFF", "bold": True, "name": "STOP-tekst", "ue": "TextBlock_0"},
            {"type": "text", "x": 806, "y": 250, "text": "Linje:", "size": 20, "color": "#333333", "bold": False, "name": "Linje-label", "ue": ""},
            {"type": "text", "x": 870, "y": 250, "text": "", "data": "Linje", "size": 20, "color": "#8A8F94", "bold": False, "name": "Linje", "ue": ""},
            {"type": "text", "x": 806, "y": 285, "text": "Zone: 2", "size": 20, "color": "#333333", "bold": False, "name": "Zone", "ue": ""},
            {"type": "text", "x": 806, "y": 320, "text": "", "data": "Ur", "size": 20, "color": "#333333", "bold": False, "name": "Tid", "ue": ""},
            {"type": "box", "x": 960, "y": 100, "w": 620, "h": 320, "color": "#FFFFFF", "data": "StopListe", "name": "Stopliste", "ue": ""},
        ],
    },
    "Main": {"w": 1200, "h": 764, "bg": "#233257", "items": [{"type": "box", "name": "Kort", "x": 0, "y": 0, "w": 1200, "h": 764, "color": "#FFFFFF", "image": "T_Movia_Kort"}, {"type": "box", "name": "Topbjælke", "x": 0, "y": 0, "w": 1200, "h": 100, "color": "#0A0A0A", "data": "Header"}, {"type": "box", "name": "Stopliste", "x": 20, "y": 120, "w": 460, "h": 540, "color": "#DE3B26", "data": "StopListe"}], "ue": "Main"},
    "Driving": {"w": 1200, "h": 764, "bg": "#233257", "items": [{"type": "box", "name": "Kort", "x": 0, "y": 0, "w": 1200, "h": 764, "color": "#FFFFFF", "image": "T_Movia_Kort"}, {"type": "box", "name": "Topbjælke", "x": 0, "y": 0, "w": 1200, "h": 100, "color": "#0A0A0A", "data": "Header"}], "ue": "Driving"},
    "Header": {"w": 900, "h": 100, "bg": "#0A0A0A", "items": [{"type": "box", "name": "Baggrund", "x": 0, "y": 0, "w": 900, "h": 100, "color": "#0A0A0A"}, {"type": "text", "name": "Linje og destination", "x": 20, "y": 30, "data": "LinjeDestination", "size": 30, "color": "#FFFFFF", "bold": True}, {"type": "text", "name": "Ur", "x": 660, "y": 8, "data": "Ur", "size": 44, "color": "#FFFFFF"}, {"type": "text", "name": "Forsinkelse", "x": 700, "y": 62, "data": "Forsinkelse", "size": 24, "color": "#FFFFFF"}], "ue": "Header"},
    "Chauffør (skitse)": {
        "w": 1200, "h": 764, "bg": "#233257", "ue": "Main",
        "items": [
            {"type": "box", "x": 0, "y": 0, "w": 1200, "h": 100, "color": "#0A0A0A", "name": "Header", "ue": ""},
            {"type": "box", "x": 20, "y": 14, "w": 90, "h": 72, "color": "#45A6DC", "name": "Linjeboks", "ue": ""},
            {"type": "text", "x": 32, "y": 22, "text": "", "data": "Linje", "size": 34, "color": "#FFFFFF", "bold": True, "name": "Linje", "ue": ""},
            {"type": "text", "x": 130, "y": 26, "text": "", "data": "SidsteStop", "size": 34, "color": "#FFFFFF", "bold": True, "name": "Destination", "ue": ""},
            {"type": "text", "x": 900, "y": 14, "text": "", "data": "UrSekunder", "size": 50, "color": "#FFFFFF", "bold": False, "name": "Ur", "ue": ""},
            {"type": "box", "x": 20, "y": 120, "w": 460, "h": 220, "color": "#DE3B26", "color_on": "#3FA535", "state": "TilTiden", "name": "Næste stop-boks", "ue": ""},
            {"type": "text", "x": 36, "y": 132, "text": "Næste stop:", "size": 16, "color": "#FFFFFF", "bold": False, "name": "Label næste", "ue": ""},
            {"type": "text", "x": 36, "y": 170, "text": "", "data": "NaesteStop", "size": 40, "color": "#FFFFFF", "bold": True, "name": "Næste stop", "ue": ""},
            {"type": "text", "x": 300, "y": 132, "text": "Planlagt ankomst:", "size": 16, "color": "#FFFFFF", "bold": False, "name": "Label ankomst", "ue": ""},
            {"type": "text", "x": 320, "y": 230, "text": "", "data": "Forsinkelse", "size": 36, "color": "#FFFFFF", "bold": False, "name": "Forsinkelse", "ue": ""},
            {"type": "box", "x": 20, "y": 350, "w": 460, "h": 120, "color": "#DE3B26", "color_on": "#3FA535", "state": "TilTiden", "name": "Sidste stop-boks", "ue": ""},
            {"type": "text", "x": 36, "y": 360, "text": "Sidste stop:", "size": 16, "color": "#FFFFFF", "bold": False, "name": "Label sidste", "ue": ""},
            {"type": "text", "x": 36, "y": 395, "text": "", "data": "SidsteStop", "size": 30, "color": "#FFFFFF", "bold": True, "name": "Sidste stop", "ue": ""},
        ],
    },
}


# ------------------------------------------------------------------
# Elementer paa laerredet
# ------------------------------------------------------------------
class Signaler(QObject):
    valgt = pyqtSignal(object)


SIG = None


class TekstElement(QGraphicsTextItem):
    def __init__(self, data):
        super().__init__(data.get("text", ""))
        self.data_ = data
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setPos(data["x"], data["y"])
        self.opdater()

    def opdater(self):
        d = self.data_
        f = QFont(FONT, -1)
        f.setPixelSize(int(d.get("size", 20)))
        f.setBold(bool(d.get("bold")))
        self.setFont(f)
        self.setDefaultTextColor(QColor(d.get("color", "#000000")))
        vis = ("{%s} " % d["data"] + DATAFELTER.get(d["data"], "")) if d.get("data") and SIG and getattr(SIG, "vis_navne", False) else \
              (DATAFELTER.get(d["data"], d.get("text", "")) if d.get("data") else d.get("text", ""))
        if self.toPlainText() != vis:
            self.setPlainText(vis)
        if d.get("data"):
            self.setToolTip("Datafelt: " + d["data"])
        self.setOpacity(0.25 if d.get("hidden") else 1.0)

    def mouseDoubleClickEvent(self, e):
        if self.data_.get("data"):
            return  # datafelter skrives af spillet
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(e)

    def focusOutEvent(self, e):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        if not self.data_.get("data"):
            self.data_["text"] = self.toPlainText()
        SIG.valgt.emit(self)
        super().focusOutEvent(e)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.data_["x"], self.data_["y"] = round(self.pos().x()), round(self.pos().y())
        return super().itemChange(change, value)


class BoksElement(QGraphicsRectItem):
    def __init__(self, data):
        super().__init__(0, 0, data["w"], data["h"])
        self.data_ = data
        self.pix = None
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setPos(data["x"], data["y"])
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.opdater()

    def opdater(self):
        d = self.data_
        self.setRect(0, 0, d["w"], d["h"])
        farve = d.get("color_on") if (d.get("state") and SIG and getattr(SIG, "tilstand_til", False) and d.get("color_on")) else d.get("color", "#888888")
        self.setBrush(QBrush(QColor(farve)))
        self.setOpacity(0.25 if d.get("hidden") else 1.0)
        self.pix = None
        img = d.get("image")
        if img:
            for p in (img, os.path.join(MAPPE, img), os.path.join(MAPPE, img + ".png"),
                      os.path.join(MAPPE, "..", "MoviaImport", img + ".png"), os.path.join(MAPPE, "..", "MoviaImport", img)):
                if os.path.exists(p):
                    self.pix = QPixmap(p)
                    break
        self.update()

    def paint(self, painter, option, widget=None):
        if self.data_.get("kun_ved") and not getattr(SIG, "tilstand_til", False):
            painter.setPen(QPen(QColor("#888888"), 1, Qt.PenStyle.DotLine))
            painter.drawRect(self.rect())
        elif self.pix and not self.pix.isNull():
            painter.drawPixmap(self.rect().toRect(), self.pix)
        else:
            super().paint(painter, option, widget)
        if self.data_.get("data"):
            painter.setPen(QColor("#2F7FE0"))
            f = QFont(FONT); f.setPixelSize(18); painter.setFont(f)
            painter.drawText(self.rect().adjusted(10, 10, -10, -10), 0, "⟳ " + DATAOMRAADER.get(self.data_["data"], self.data_["data"]))
        if self.isSelected():
            painter.setPen(QPen(QColor("#2F7FE0"), 2, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.rect())

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.data_["x"], self.data_["y"] = round(self.pos().x()), round(self.pos().y())
        return super().itemChange(change, value)


# ------------------------------------------------------------------
# Hovedvindue
# ------------------------------------------------------------------
class Editor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movia Editor")
        self.resize(1500, 800)
        self.layout_ = None
        self.valgt = None

        self.scene = QGraphicsScene()
        self.scene.selectionChanged.connect(self.valg_aendret)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setBackgroundBrush(QColor("#2B2B2B"))

        # Panel
        panel = QWidget()
        form = QFormLayout(panel)
        self.f_navn = QLineEdit()
        self.f_ue = QLineEdit()
        self.f_ue.setPlaceholderText("fx Text_NextBusStop")
        self.f_tekst = QLineEdit()
        self.f_str = QSpinBox(); self.f_str.setRange(6, 300)
        self.f_bred = QSpinBox(); self.f_bred.setRange(1, 4000)
        self.f_hoej = QSpinBox(); self.f_hoej.setRange(1, 4000)
        self.f_fed = QCheckBox("Fed")
        self.f_skjul = QCheckBox("Skjul i spillet")
        self.f_farve = QPushButton("Vælg farve")
        self.f_billede = QPushButton("Vælg billede…")
        self.f_data = QComboBox(); self.f_data.addItem("(fast tekst)", "")
        for k in DATAFELTER: self.f_data.addItem(k, k)
        self.f_state = QComboBox()
        for k, v in TILSTANDE.items(): self.f_state.addItem(v, k)
        self.f_farve2 = QPushButton("Vælg farve")
        self.f_omraade = QComboBox()
        for k, v in DATAOMRAADER.items(): self.f_omraade.addItem(v, k)
        self.f_kunved = QCheckBox("Vis kun når tilstanden er til")
        self.f_spil = QLineEdit(); self.f_spil.setPlaceholderText("spillets elementnavn")
        self.lagliste = QListWidget()
        self.lagliste.currentRowChanged.connect(self.lag_valgt)
        form.addRow(QLabel("<b>Valgt element</b>"))
        form.addRow("Navn", self.f_navn)
        form.addRow("UE-element", self.f_ue)
        form.addRow("Tekst", self.f_tekst)
        form.addRow("Datafelt", self.f_data)
        form.addRow("Størrelse", self.f_str)
        form.addRow("Bredde", self.f_bred)
        form.addRow("Højde", self.f_hoej)
        form.addRow("", self.f_fed)
        form.addRow("Farve", self.f_farve)
        form.addRow("Billede", self.f_billede)
        form.addRow("Skifter ved", self.f_state)
        form.addRow("Farve når til", self.f_farve2)
        form.addRow("Dataområde", self.f_omraade)
        form.addRow("", self.f_kunved)
        form.addRow("Spil-element", self.f_spil)
        form.addRow(QLabel("<b>Lag</b> (øverst = forrest)"))
        form.addRow(self.lagliste)
        form.addRow("", self.f_skjul)
        hjælp = QLabel("Træk for at flytte.\nDobbeltklik på tekst for at skrive.\n"
                       "Delete sletter valgt element.\n\nUE-element = navnet i Hierarchy\n"
                       "i The Bus Modding. Kun elementer\nmed UE-navn kommer med i scriptet.")
        hjælp.setStyleSheet("color:#888")
        form.addRow(hjælp)
        panel.setFixedWidth(300)

        for w, s in ((self.f_navn, "name"), (self.f_ue, "ue"), (self.f_tekst, "text")):
            w.editingFinished.connect(lambda w=w, s=s: self.saet(s, w.text()))
        self.f_str.valueChanged.connect(lambda v: self.saet("size", v))
        self.f_bred.valueChanged.connect(lambda v: self.saet("w", v))
        self.f_hoej.valueChanged.connect(lambda v: self.saet("h", v))
        self.f_fed.toggled.connect(lambda v: self.saet("bold", v))
        self.f_skjul.toggled.connect(lambda v: self.saet("hidden", v))
        self.f_farve.clicked.connect(self.vaelg_farve)
        self.f_farve2.clicked.connect(self.vaelg_farve2)
        self.f_data.currentIndexChanged.connect(lambda i: self.saet("data", self.f_data.itemData(i)))
        self.f_omraade.currentIndexChanged.connect(lambda i: self.saet("data", self.f_omraade.itemData(i)))
        self.f_kunved.toggled.connect(lambda v: self.saet("kun_ved", v))
        self.f_spil.editingFinished.connect(lambda: self.saet("spil", self.f_spil.text().strip()))
        self.f_state.currentIndexChanged.connect(lambda i: self.saet("state", self.f_state.itemData(i)))
        self.f_billede.clicked.connect(self.vaelg_billede)

        midt = QWidget()
        lay = QHBoxLayout(midt)
        lay.addWidget(self.view, 1)
        lay.addWidget(panel)
        self.setCentralWidget(midt)

        # Vaerktoejslinje
        tb = QToolBar(); self.addToolBar(tb)
        self.vaelger = QComboBox(); self.vaelger.addItems(list(SKAERME.keys()))
        self.vaelger.currentTextChanged.connect(self._vis_skaerm)
        tb.addWidget(QLabel(" Skærm: ")); tb.addWidget(self.vaelger)
        tb.addSeparator()
        for navn, fn in (("📂 Åbn kommando.json", self.aabn_kommando), ("💾 Gem som kommando.json", self.gem_kommando), (None, None),
                         ("+ Tekst", self.tilfoej_tekst), ("+ Boks", self.tilfoej_boks), ("+ Datafelt", self.tilfoej_datafelt), ("+ Billede", self.tilfoej_billede),
                         ("Slet", self.slet), ("Fremad", lambda: self.lag(1)), ("Bagud", lambda: self.lag(-1)),
                         (None, None),
                         ("Åbn…", self.aabn), ("Gem…", self.gem), ("Eksporter PNG…", self.eksporter_png),
                         ("Eksporter script…", self.eksporter_script), (None, None),
                         ("Eksporter til spillet…", self.eksporter_spil), ("Vis datanavne", self.skift_navne),
                         ("Test tilstand", self.skift_tilstand), (None, None), ("⚙ Regler…", self.rediger_regler)):
            if navn is None:
                tb.addSeparator(); continue
            a = QAction(navn, self); a.triggered.connect(fn); tb.addAction(a)
        slet = QAction(self); slet.setShortcut(QKeySequence.StandardKey.Delete)
        slet.triggered.connect(self.slet); self.addAction(slet)

        self.indlaes(json.loads(json.dumps(SKAERME["Passager"])))
        if os.path.exists(KOMMANDO):
            self.aabn_kommando(stille=True)

    # ---------- laerred ----------
    def indlaes(self, layout):
        self.layout_ = layout
        self.scene.clear()
        bg = self.scene.addRect(0, 0, layout["w"], layout["h"], QPen(Qt.PenStyle.NoPen), QBrush(QColor(layout["bg"])))
        bg.setZValue(-1000)
        for i, d in enumerate(layout["items"]):
            self._tilfoej_item(d, i)
        self.scene.setSceneRect(QRectF(-20, -20, layout["w"] + 40, layout["h"] + 40))
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.vis_valgt(None)

    def _tilfoej_item(self, d, z):
        it = TekstElement(d) if d["type"] == "text" else BoksElement(d)
        it.setZValue(float(d.get("z", z)))
        self.scene.addItem(it)
        self.opdater_lag()
        return it

    def _items(self):
        return [i for i in self.scene.items() if isinstance(i, (TekstElement, BoksElement))]

    def opdater_lag(self):
        if not hasattr(self, "lagliste") or not self.layout_:
            return
        self.lagliste.blockSignals(True)
        self.lagliste.clear()
        for d in reversed(self.layout_["items"]):
            ikon = "🗺 " if d.get("type") == "gps" else "🖼 " if d.get("image") else ("⟳ " if d.get("data") else ("T " if d["type"] == "text" else "▭ "))
            ekstra = "  [kun ved %s]" % d["state"] if d.get("kun_ved") else ""
            self.lagliste.addItem(ikon + d.get("name", "") + ekstra)
        self.lagliste.blockSignals(False)

    def lag_valgt(self, raekke):
        if raekke < 0:
            return
        d = list(reversed(self.layout_["items"]))[raekke]
        for it in self._items():
            if it.data_ is d:
                self.scene.clearSelection(); it.setSelected(True)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self.layout_:
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def valg_aendret(self):
        try:
            sel = self.scene.selectedItems()
        except RuntimeError:
            return
        self.vis_valgt(sel[0] if sel else None)

    def vis_valgt(self, it):
        self.valgt = it
        d = it.data_ if it else {}
        er_tekst = isinstance(it, TekstElement)
        for w in (self.f_navn, self.f_ue, self.f_tekst, self.f_str, self.f_bred, self.f_hoej,
                  self.f_fed, self.f_skjul, self.f_farve, self.f_billede, self.f_data, self.f_state, self.f_farve2, self.f_omraade, self.f_kunved):
            w.blockSignals(True)
        self.f_navn.setText(d.get("name", ""))
        self.f_ue.setText(d.get("ue", ""))
        self.f_tekst.setText(d.get("text", ""))
        self.f_str.setValue(int(d.get("size", 20)))
        self.f_bred.setValue(int(d.get("w", 100)))
        self.f_hoej.setValue(int(d.get("h", 100)))
        self.f_fed.setChecked(bool(d.get("bold")))
        self.f_skjul.setChecked(bool(d.get("hidden")))
        self.f_farve.setStyleSheet("background:%s" % d.get("color", "#444") if it else "")
        self.f_farve2.setStyleSheet("background:%s" % d.get("color_on", "#444") if it else "")
        self.f_data.setCurrentIndex(max(0, self.f_data.findData(d.get("data", ""))))
        self.f_state.setCurrentIndex(max(0, self.f_state.findData(d.get("state", ""))))
        self.f_omraade.setCurrentIndex(max(0, self.f_omraade.findData(d.get("data", ""))))
        self.f_kunved.setChecked(bool(d.get("kun_ved")))
        self.f_spil.setText(d.get("spil", ""))
        self.f_spil.setEnabled(it is not None)
        for w in (self.f_navn, self.f_ue, self.f_skjul, self.f_farve):
            w.setEnabled(it is not None)
        for w in (self.f_tekst, self.f_str, self.f_fed, self.f_data):
            w.setEnabled(er_tekst)
        self.f_tekst.setEnabled(er_tekst and not d.get("data"))
        for w in (self.f_bred, self.f_hoej, self.f_billede, self.f_state, self.f_farve2, self.f_omraade, self.f_kunved):
            w.setEnabled(it is not None and not er_tekst)
        for w in (self.f_navn, self.f_ue, self.f_tekst, self.f_str, self.f_bred, self.f_hoej,
                  self.f_fed, self.f_skjul, self.f_farve, self.f_billede, self.f_data, self.f_state, self.f_farve2, self.f_omraade, self.f_kunved):
            w.blockSignals(False)

    def saet(self, noegle, vaerdi):
        if not self.valgt:
            return
        self.valgt.data_[noegle] = vaerdi
        self.valgt.opdater()
        if noegle == "data":
            self.vis_valgt(self.valgt)
        self.opdater_lag()

    def vaelg_farve(self):
        if not self.valgt:
            return
        c = QColorDialog.getColor(QColor(self.valgt.data_.get("color", "#000000")), self)
        if c.isValid():
            self.saet("color", c.name().upper())
            self.f_farve.setStyleSheet("background:%s" % c.name())

    def vaelg_farve2(self):
        if not self.valgt:
            return
        c = QColorDialog.getColor(QColor(self.valgt.data_.get("color_on", "#E2231A")), self)
        if c.isValid():
            self.saet("color_on", c.name().upper())
            self.f_farve2.setStyleSheet("background:%s" % c.name())

    def vaelg_billede(self):
        if not self.valgt:
            return
        p, _ = QFileDialog.getOpenFileName(self, "Vælg billede", MAPPE, "Billeder (*.png *.jpg)")
        if p:
            self.saet("image", p)

    def tilfoej_tekst(self):
        d = {"type": "text", "x": 100, "y": 100, "text": "Ny tekst", "size": 30, "color": "#1D1D1D",
             "bold": False, "name": "Tekst %d" % (len(self.layout_["items"]) + 1), "ue": ""}
        self.layout_["items"].append(d)
        it = self._tilfoej_item(d, len(self.layout_["items"]))
        self.scene.clearSelection(); it.setSelected(True)

    def tilfoej_datafelt(self):
        d = {"type": "text", "x": 100, "y": 100, "text": "", "data": "NaesteStop", "size": 30,
             "color": "#1D1D1D", "bold": False, "name": "Datafelt %d" % (len(self.layout_["items"]) + 1), "ue": ""}
        self.layout_["items"].append(d)
        it = self._tilfoej_item(d, len(self.layout_["items"]))
        self.scene.clearSelection(); it.setSelected(True)

    def tilfoej_billede(self):
        p, _ = QFileDialog.getOpenFileName(self, "Vælg billede", MAPPE, "Billeder (*.png *.jpg)")
        if not p:
            return
        pix = QPixmap(p)
        w, h = pix.width() or 200, pix.height() or 200
        skala = min(1.0, 400.0 / max(w, h))
        d = {"type": "box", "x": 100, "y": 100, "w": int(w * skala), "h": int(h * skala),
             "color": "#FFFFFF", "image": p, "name": os.path.splitext(os.path.basename(p))[0], "ue": ""}
        # Er en boks med tilstand valgt (fx STOP-feltet)? Saa bliver billedet et nyt lag
        # oven paa den, som kun vises i den tilstand.
        mor = self.valgt.data_ if isinstance(self.valgt, BoksElement) else None
        if mor and mor.get("state"):
            d.update(x=mor["x"], y=mor["y"], w=mor["w"], h=mor["h"], state=mor["state"], kun_ved=True,
                     name="%s (%s)" % (d["name"], TILSTANDE.get(mor["state"], mor["state"])))
            i = self.layout_["items"].index(mor) + 1
        else:
            i = len(self.layout_["items"])
        self.layout_["items"].insert(i, d)
        self.indlaes(self.layout_)
        for it in self._items():
            if it.data_ is d:
                it.setSelected(True)

    def skift_navne(self):
        SIG.vis_navne = not getattr(SIG, "vis_navne", False)
        self.indlaes(self.layout_)

    def skift_tilstand(self):
        SIG.tilstand_til = not getattr(SIG, "tilstand_til", False)
        self.indlaes(self.layout_)

    def tilfoej_boks(self):
        d = {"type": "box", "x": 100, "y": 100, "w": 200, "h": 120, "color": "#3FA535",
             "name": "Boks %d" % (len(self.layout_["items"]) + 1), "ue": ""}
        self.layout_["items"].append(d)
        it = self._tilfoej_item(d, len(self.layout_["items"]))
        self.scene.clearSelection(); it.setSelected(True)

    def slet(self):
        if self.valgt and not (isinstance(self.valgt, TekstElement) and
                               self.valgt.textInteractionFlags() & Qt.TextInteractionFlag.TextEditorInteraction):
            self.layout_["items"].remove(self.valgt.data_)
            self.scene.removeItem(self.valgt)
            self.vis_valgt(None)
            self.opdater_lag()

    def lag(self, retning):
        if not self.valgt:
            return
        items = self.layout_["items"]
        i = items.index(self.valgt.data_)
        j = max(0, min(len(items) - 1, i + retning))
        items[i], items[j] = items[j], items[i]
        self.indlaes(self.layout_)

    # ---------- filer ----------
    def aabn_kommando(self, stille=False):
        """Viser kommando.json (fx lavet af Gemini) som preview. Kan indeholde flere skaerme."""
        if not os.path.exists(KOMMANDO):
            if not stille:
                QMessageBox.information(self, "Ingen kommando.json", "Der ligger ingen kommando.json i\n" + MAPPE)
            return
        try:
            with open(KOMMANDO, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Fejl i kommando.json", "Filen kunne ikke læses (er det gyldig JSON?):\n%s" % e)
            return
        kommandoer = data if isinstance(data, list) else [data]
        self.kommandoer = []
        for k in kommandoer:
            if not isinstance(k, dict):
                continue
            if "items" in k and "layout" not in k:          # bare et layout
                k = {"skaerm": k.get("ue", "Passager"), "layout": k}
            self.kommandoer.append(k)
        # fjern gamle kommando-punkter i listen og tilfoej et pr. skaerm
        self.vaelger.blockSignals(True)
        for i in reversed(range(self.vaelger.count())):
            if self.vaelger.itemText(i).startswith("kommando: "):
                self.vaelger.removeItem(i)
        foerste = None
        for i, k in enumerate(self.kommandoer):
            if not k.get("layout"):
                continue
            L = k["layout"]
            L["ue"] = k.get("skaerm", L.get("ue", "Passager"))
            L.setdefault("w", 1600); L.setdefault("h", 430); L.setdefault("bg", "#FFFFFF")
            L.setdefault("items", [])
            navn = "kommando: %s" % L["ue"]
            self.vaelger.addItem(navn, i)
            if foerste is None:
                foerste = navn
        self.vaelger.blockSignals(False)
        aendringer = sum(len(k.get("aendringer", [])) for k in self.kommandoer)
        if foerste is None:
            if not stille:
                QMessageBox.information(self, "Kun ændringer",
                    "kommando.json har ingen 'layout' – kun %d små ændringer, som ikke kan vises som preview." % aendringer)
            return
        self.vaelger.setCurrentText(foerste)
        advarsler = []
        for k in self.kommandoer:
            if k.get("layout"):
                ue = k["layout"]["ue"]
                forkerte = sorted({d["data"] for d in k["layout"]["items"] if d.get("data") and d["data"] not in PR_SKAERM.get(ue, [])})
                if forkerte:
                    advarsler.append("%s: %s" % (ue, ", ".join(forkerte)))
        self.statusBar().showMessage("kommando.json indlæst: %d skærm(e), %d ændring(er). Vælg skærm øverst." %
                                     (len([k for k in self.kommandoer if k.get("layout")]), aendringer), 15000)
        if advarsler and not stille:
            QMessageBox.warning(self, "Advarsel", "Datafelter der ikke virker:\n" + "\n".join(advarsler))

    def _vis_skaerm(self, navn):
        if navn.startswith("kommando: "):
            k = self.kommandoer[self.vaelger.currentData()]
            self.indlaes(k["layout"])          # samme objekt -> rettelser gemmes i kommandoen
            self.setWindowTitle("Movia Editor – preview af kommando.json (%s)" % k["layout"]["ue"])
        else:
            self.indlaes(json.loads(json.dumps(SKAERME[navn])))
            self.setWindowTitle("Movia Editor")

    def rediger_regler(self):
        """Regler som 'hvis Forsinkelse > 60 -> farve StatusBoks rod'. Gemmes i layoutet."""
        from PyQt6.QtWidgets import QDialog, QPlainTextEdit, QDialogButtonBox, QVBoxLayout
        dlg = QDialog(self); dlg.setWindowTitle("Regler for denne skærm"); dlg.resize(620, 420)
        v = QVBoxLayout(dlg)
        v.addWidget(QLabel("Skriv regler som JSON-liste. 'element' = navnet på et element i editoren.\n"
                           "er: >  <  =  !=  indeholder     saet: farve  vis  skjul  tekst  tekstfarve"))
        eks = [{"hvis": "Forsinkelse", "er": ">", "vaerdi": 60, "saet": "farve",
                "element": "StatusBoks", "til": "#DE3B26", "ellers": "#3FA535"}]
        felt = QPlainTextEdit(json.dumps(self.layout_.get("regler") or eks, ensure_ascii=False, indent=2))
        v.addWidget(felt)
        knap = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        knap.accepted.connect(dlg.accept); knap.rejected.connect(dlg.reject); v.addWidget(knap)
        if dlg.exec():
            try:
                regler = json.loads(felt.toPlainText() or "[]")
                if isinstance(regler, dict):
                    regler = [regler]
                navne = {d.get("name") for d in self.layout_.get("items", [])}
                mangler = [r.get("element") for r in regler if r.get("element") not in navne]
                self.layout_["regler"] = regler
                msg = "%d regel(er) gemt i layoutet – husk 'Gem som kommando.json'" % len(regler)
                if mangler:
                    msg += "  (OBS: findes ikke i editoren: %s)" % ", ".join(map(str, mangler))
                self.statusBar().showMessage(msg, 12000)
            except Exception as e:
                QMessageBox.warning(self, "Fejl i reglerne", "Kunne ikke læse JSON:\n%s" % e)

    def gem_kommando(self):
        """Gemmer kommando.json. Er en kommando.json aaben, gemmes alle dens skaerme med dine rettelser."""
        if self.vaelger.currentText().startswith("kommando: ") and getattr(self, "kommandoer", None):
            data = self.kommandoer if len(self.kommandoer) > 1 else self.kommandoer[0]
        else:
            data = {"skaerm": self.layout_.get("ue", "Passager"), "layout": self.layout_}
        with open(KOMMANDO, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.statusBar().showMessage("Gemt som kommando.json – kør movia_kommando.py i The Bus Modding", 8000)

    def gem(self):
        p, _ = QFileDialog.getSaveFileName(self, "Gem layout", MAPPE, "Movia layout (*.json)")
        if p:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(self.layout_, f, ensure_ascii=False, indent=2)

    def aabn(self):
        p, _ = QFileDialog.getOpenFileName(self, "Åbn layout", MAPPE, "Movia layout (*.json)")
        if p:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            self.indlaes(data["layout"] if "layout" in data else data)

    def render_png(self, sti):
        L = self.layout_
        self.scene.clearSelection()
        img = QImage(L["w"], L["h"], QImage.Format.Format_ARGB32)
        img.fill(QColor(L["bg"]))
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.scene.render(p, QRectF(0, 0, L["w"], L["h"]), QRectF(0, 0, L["w"], L["h"]))
        p.end()
        img.save(sti)

    def eksporter_png(self):
        p, _ = QFileDialog.getSaveFileName(self, "Eksporter billede", MAPPE, "PNG (*.png)")
        if p:
            self.render_png(p)

    def lav_script(self):
        ue = self.layout_.get("ue", "Passager")
        linjer = []
        for d in self.layout_["items"]:
            n = d.get("ue", "").strip()
            if not n:
                continue
            if d.get("hidden"):
                linjer.append('skjul("%s", "%s")' % (ue, n)); continue
            if d["type"] == "text":
                linjer.append('tekst("%s", "%s", %s)' % (ue, n, json.dumps(d.get("text", ""), ensure_ascii=False)))
                linjer.append('tekstfarve("%s", "%s", "%s")' % (ue, n, d["color"]))
                linjer.append('skrift("%s", "%s", "%s", %d)' % (ue, n, "Bold" if d.get("bold") else "Regular", d["size"]))
            else:
                linjer.append('farve("%s", "%s", "%s")' % (ue, n, d["color"]))
        return linjer

    def eksporter_script(self):
        linjer = self.lav_script()
        if not linjer:
            QMessageBox.information(self, "Intet at eksportere",
                                    "Ingen elementer har et UE-element-navn.\nSkriv navnet fra Hierarchy i feltet 'UE-element'.")
            return
        p, _ = QFileDialog.getSaveFileName(self, "Gem script", os.path.join(MAPPE, "movia_aendringer.py"), "Python (*.py)")
        if not p:
            return
        hoved = ('# -*- coding: utf-8 -*-\n# Lavet af Movia Editor. Koer i The Bus Modding:\n'
                 '# Tools > Execute Python Script\nimport sys, importlib\n'
                 'sys.path.append(r"%s")\nimport movia_tools\nimportlib.reload(movia_tools)\n'
                 'from movia_tools import *\n\n' % MAPPE)
        with open(p, "w", encoding="utf-8") as f:
            f.write(hoved + "\n".join(linjer) + "\n\ngem_alt()\n")
        QMessageBox.information(self, "Script gemt", "Gemt:\n%s\n\nKør det i The Bus Modding via\nTools > Execute Python Script." % p)


KOLONNER = ["Type", "Data", "Tilstand", "X", "Y", "W", "H", "Tekst", "Stoerrelse",
            "Farve", "FarveTil", "Fed", "Skjult", "Billede", "Z", "KunVed"]


def layout_til_csv(layout):
    """Laver CSV til en DataTable (raekke-struct: S_MoviaElement) i modden."""
    import csv, io
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["Name"] + KOLONNER)
    for i, d in enumerate(layout["items"]):
        typ = "Data" if (d.get("data") and d["type"] == "text") else "Omraade" if d.get("data") else ("Tekst" if d["type"] == "text" else ("Billede" if d.get("image") else "Boks"))
        w.writerow([
            "E%03d" % i, typ, d.get("data", ""), d.get("state", ""),
            d["x"], d["y"], d.get("w", 0), d.get("h", 0),
            d.get("text", ""), d.get("size", 0),
            d.get("color", "#FFFFFF"), d.get("color_on", ""),
            "True" if d.get("bold") else "False", "True" if d.get("hidden") else "False",
            d.get("image", ""), i, "True" if d.get("kun_ved") else "False",
        ])
    return out.getvalue()


def _eksporter_spil(self):
    navn = self.vaelger.currentText()
    ue = self.layout_.get("ue", navn)
    tilladt = PR_SKAERM.get(ue, [])
    forkerte = sorted({d["data"] for d in self.layout_["items"] if d.get("data") and d["data"] not in tilladt})
    if forkerte:
        QMessageBox.warning(self, "Datafelter der ikke virker her",
            "Disse datafelter virker ikke på skærmen %s og bliver sprunget over:\n%s" % (ue, ", ".join(forkerte)))
    mappe = QFileDialog.getExistingDirectory(self, "Vælg mappe til eksport", os.path.join(MAPPE, "Eksport"))
    if not mappe:
        return
    base = os.path.join(mappe, "MoviaLayout_" + ue)
    with open(base + ".csv", "w", encoding="utf-8", newline="") as f:
        f.write(layout_til_csv(self.layout_))
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump({"skaerm": ue, "layout": self.layout_}, f, ensure_ascii=False, indent=2)
    self.render_png(base + "_preview.png")
    QMessageBox.information(self, "Eksporteret",
        "Gemt:\n%s.csv\n%s.json\n%s_preview.png\n\nNår MoviaMotor er bygget ind i modden,\n"
        "importerer movia_tools.importer_layout(...) CSV-filen,\nog skærmen opdaterer i spillet." % (base, base, base))


Editor.eksporter_spil = _eksporter_spil


def main():
    global SIG
    app = QApplication(sys.argv)
    SIG = Signaler()
    w = Editor()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
