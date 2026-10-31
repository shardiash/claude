# -*- coding: utf-8 -*-
"""
MOVIA REGLER - oversaetter regler/udtryk fra kommando.json til et lille
program, som regel-motoren (WBP_MoviaMotor) koerer inde i spillet.

Du kan skrive rigtige udtryk:
    "hvis": "Forsinkelse > 60 og Linje = '5C'"
    "hvis": "(Tid % 20) < 10"
    "til":  "{Forsinkelse / 60 :heltal} min"

Resultatet er tabeller (variabler, betingelser i "eller"-grupper, regler),
som movia_motor.py skriver ind i regel-motoren WBP_MoviaMotor.
Dette modul bruger IKKE unreal, saa det kan testes udenfor Unreal.
"""
import ast
import re

HANDLINGER = ("farve", "tekstfarve", "tekst", "vis", "skjul", "opacity", "billede", "blink", "flytx", "flyty", "klik", "tilfoejtag", "fjerntag")
FORMATER = ("raa", "heltal", "1dec", "fortegn", "mmss", "hhmm")
NEGER = {">": "<=", "<": ">=", ">=": "<", "<=": ">", "=": "!=", "!=": "=",
         "indeholder": "ikke_indeholder", "ikke_indeholder": "indeholder"}
VEND = {">": "<", "<": ">", ">=": "<=", "<=": ">=", "=": "=", "!=": "!="}
AST_OP = {ast.Gt: ">", ast.Lt: "<", ast.GtE: ">=", ast.LtE: "<=", ast.Eq: "=", ast.NotEq: "!="}


class RegelFejl(Exception):
    pass


# ---------------------------------------------------------------
# udtryk -> AST
# ---------------------------------------------------------------
def _forbered(tekst):
    t = " %s " % str(tekst)
    t = re.sub(r"(?i)\s+og\s+", " and ", t)
    t = re.sub(r"(?i)\s+eller\s+", " or ", t)
    t = re.sub(r"(?i)(^|[\s(])ikke\s+", r"\1not ", t)
    t = re.sub(r"(?i)\s+indeholder\s+", " __INDEHOLDER__ ", t)
    t = re.sub(r"(?<![<>!=])=(?!=)", "==", t)          # enkelt = -> ==
    t = t.replace("≥", ">=").replace("≤", "<=").replace("≠", "!=")
    # A indeholder "x"  ->  "x" in A
    t = re.sub(r"(\w+)\s+__INDEHOLDER__\s+('[^']*'|\"[^\"]*\")", r"\2 in \1", t)
    return t.strip()


def _parse(tekst):
    try:
        return ast.parse(_forbered(tekst), mode="eval").body
    except SyntaxError as e:
        raise RegelFejl("Kan ikke forstaa udtrykket '%s' (%s)" % (tekst, e.msg))


# ---------------------------------------------------------------
# lineaer form  ((var*a)+b) mod m
# ---------------------------------------------------------------
def _lin(node):
    """Returnerer ('k', tal) for en konstant eller ('v', var, a, b, m)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return ("k", float(node.value))
    if isinstance(node, ast.Name):
        return ("v", node.id, 1.0, 0.0, 0.0)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        x = _lin(node.operand)
        if x[0] == "k":
            return ("k", -x[1])
        if x[4]:
            raise RegelFejl("minus foran %-udtryk er ikke understoettet")
        return ("v", x[1], -x[2], -x[3], 0.0)
    if isinstance(node, ast.BinOp):
        v, h = _lin(node.left), _lin(node.right)
        if v[0] == "k" and h[0] == "k":
            a, b = v[1], h[1]
            ops = {ast.Add: a + b, ast.Sub: a - b, ast.Mult: a * b}
            if isinstance(node.op, ast.Div):
                return ("k", a / b)
            if isinstance(node.op, ast.Mod):
                return ("k", a % b)
            if type(node.op) in ops:
                return ("k", ops[type(node.op)])
        if v[0] == "v" and h[0] == "v":
            raise RegelFejl("to datafelter kan ikke regnes sammen i samme udtryk (%s og %s)" % (v[1], h[1]))
        var, k, venstre = (v, h[1], True) if v[0] == "v" else (h, v[1], False)
        _, navn, a, b, m = var
        if m and not (isinstance(node.op, ast.Mod)):
            raise RegelFejl("efter % kan der ikke regnes mere - saet % til sidst")
        if isinstance(node.op, ast.Add):
            return ("v", navn, a, b + k, 0.0)
        if isinstance(node.op, ast.Sub):
            return ("v", navn, a, b - k, 0.0) if venstre else ("v", navn, -a, k - b, 0.0)
        if isinstance(node.op, ast.Mult):
            return ("v", navn, a * k, b * k, 0.0)
        if isinstance(node.op, ast.Div):
            if not venstre:
                raise RegelFejl("tal / datafelt er ikke understoettet")
            return ("v", navn, a / k, b / k, 0.0)
        if isinstance(node.op, ast.Mod):
            if not venstre or m:
                raise RegelFejl("% skal staa som  datafelt % tal")
            return ("v", navn, a, b, k)
    raise RegelFejl("ukendt udtryk: %s" % ast.dump(node)[:80])


def _tal(x):
    s = ("%.9f" % x).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ---------------------------------------------------------------
# betingelser -> DNF (liste af og-lister)
# ---------------------------------------------------------------
def _atom(var, op, vaerdi):
    return (var, op, vaerdi)       # var = (navn,a,b,m)


def _neg_dnf(dnf):
    # not (A1 or A2 ...) = (not A1) and (not A2)...   hvor not (x and y) = (not x) or (not y)
    res = [[]]
    for konj in dnf:
        ny = []
        for delres in res:
            for (var, op, v) in konj:
                ny.append(delres + [(var, NEGER[op], v)])
        res = ny
    return res


def _dnf(node):
    if isinstance(node, ast.BoolOp):
        dele = [_dnf(v) for v in node.values]
        if isinstance(node.op, ast.Or):
            return [k for d in dele for k in d]
        res = [[]]
        for d in dele:
            res = [a + b for a in res for b in d]
        return res
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return _neg_dnf(_dnf(node.operand))
    if isinstance(node, ast.Compare):
        konj = []
        venstre = node.left
        for op, hoejre in zip(node.ops, node.comparators):
            if isinstance(op, (ast.In, ast.NotIn)):
                if not (isinstance(venstre, ast.Constant) and isinstance(venstre.value, str) and isinstance(hoejre, ast.Name)):
                    raise RegelFejl("brug:  Felt indeholder 'tekst'")
                konj.append(_atom((hoejre.id, 1.0, 0.0, 0.0), "indeholder" if isinstance(op, ast.In) else "ikke_indeholder",
                                  venstre.value))
            else:
                o = AST_OP.get(type(op))
                if not o:
                    raise RegelFejl("ukendt sammenligning")
                konj.append(_sammenlign(venstre, o, hoejre))
            venstre = hoejre
        return [konj]
    if isinstance(node, ast.Name):           # bare  StopOenske  =  StopOenske = ja
        return [[_atom((node.id, 1.0, 0.0, 0.0), "=", "ja")]]
    raise RegelFejl("forstaar ikke betingelsen")


def _sammenlign(venstre, op, hoejre):
    def tekst(n):
        return isinstance(n, ast.Constant) and isinstance(n.value, str)
    if tekst(hoejre) or tekst(venstre):
        felt, t = (venstre, hoejre) if tekst(hoejre) else (hoejre, venstre)
        if not isinstance(felt, ast.Name):
            raise RegelFejl("tekst kan kun sammenlignes direkte med et datafelt")
        if op not in ("=", "!="):
            raise RegelFejl("tekst kan kun sammenlignes med = eller !=")
        return _atom((felt.id, 1.0, 0.0, 0.0), op, t.value)
    v, h = _lin(venstre), _lin(hoejre)
    if v[0] == "v" and h[0] == "k":
        return _atom(v[1:], op, _tal(h[1]))
    if v[0] == "k" and h[0] == "v":
        return _atom(h[1:], VEND[op], _tal(v[1]))
    raise RegelFejl("en sammenligning skal have et datafelt paa den ene side og et tal paa den anden")


# ---------------------------------------------------------------
# kompilering -> tabeller som regel-motoren (WBP_MoviaMotor) laeser
# ---------------------------------------------------------------
HANDLING_KODE = {"farve": 0, "tekstfarve": 1, "tekst": 2, "vis": 3, "skjul": 4, "opacity": 5, "billede": 6, "flytx": 7, "flyty": 8, "klik": 9, "tilfoejtag": 10, "fjerntag": 11}
FORMAT_KODE = {"raa": 0, "heltal": 1, "1dec": 2, "fortegn": 3, "mmss": 4, "hhmm": 5, "msek": 6, "hhmmss": 7}
VAR_KODE = {"tekst": 0, "synlig": 1, "tid": 2, "klokken": 3, "minutter": 4, "afstand": 5, "forventet": 6, "forsinkelse": 7, "sidstetid": 8, "linje": 9, "klokkesek": 10, "naestetid": 11, "sidstetidsek": 12, "sidstenavn": 13, "naestenavn": 14, "naesteafgang": 15, "stoplinje": 16, "afgang": 17, "vedstop": 18, "gpsx": 19, "gpsy": 20, "aktuelafgang": 21, "afgangtekst": 22, "knap": 23, "stopliste": 24, "tekstfelt": 25, "loginok": 26, "bustag": 27, "rute": 28, "alder": 29, "billet": 30, "pause": 31, "tagtal": 32, "tagtekst": 33, "skiltdbg": 34, "skiftrute": 35}
STOR = 1e15
EPS = 1e-6


class Kompiler:
    def __init__(self, kilde_for, maal_for, billede_for=None):
        """kilde_for(navn) -> (type, kilde[, idx]) eller None   (type: tekst synlig tid klokken minutter)
           maal_for(elementnavn) -> widgetnavn
           billede_for(billednavn) -> widgetnavn der holder billedet"""
        self.kilde_for = kilde_for
        self.maal_for = maal_for
        self.billede_for = billede_for or (lambda n: n)
        self.vars = []          # [(type, kilde, idx)]
        self.varnavne = {}
        self.conds = []
        self.rules = []
        self.linjer = []        # menneskelaesbar log

    def _var(self, navn):
        if navn not in self.varnavne:
            k = self.kilde_for(navn)
            if not k:
                raise RegelFejl("ukendt datafelt '%s'" % navn)
            t, kilde = k[0], k[1]
            idx = k[2] if len(k) > 2 else 0
            if t not in VAR_KODE:
                raise RegelFejl("datafeltet '%s' kan ikke bruges i regler endnu" % navn)
            self.varnavne[navn] = len(self.vars)
            self.vars.append((VAR_KODE[t], kilde, idx))
        return self.varnavne[navn]

    def _atom_cond(self, atom, ny):
        (navn, a, b, m), op, v = atom
        c = dict(var=self._var(navn), a=a, b=b, m=m, new=ny, kind=0, lo=-STOR, hi=STOR, str="", neg=False)
        if op in ("indeholder", "ikke_indeholder"):
            c.update(kind=2, str=str(v), neg=(op == "ikke_indeholder"))
            return c
        try:
            x = float(v)
            tal = True
        except (TypeError, ValueError):
            tal = False
        if not tal:
            if op not in ("=", "!="):
                raise RegelFejl("tekst kan kun sammenlignes med = eller !=")
            c.update(kind=1, str=str(v), neg=(op == "!="))
            return c
        if op == ">":
            c.update(lo=x + EPS)
        elif op == ">=":
            c.update(lo=x)
        elif op == "<":
            c.update(hi=x - EPS)
        elif op == "<=":
            c.update(hi=x)
        else:
            c.update(lo=x - 0.0001, hi=x + 0.0001, neg=(op == "!="))
        return c

    def _grupper(self, konjer):
        """konjer: liste af lister af atomer -> (start, antal) i conds"""
        start = len(self.conds)
        for konj in konjer:
            for i, atom in enumerate(konj):
                self.conds.append(self._atom_cond(atom, i == 0))
        return start, len(self.conds) - start

    def _hvis(self, hvis):
        if hvis in (None, "", True):
            return []
        if isinstance(hvis, dict):          # gammelt format {"hvis","er","vaerdi"}
            v = hvis.get("vaerdi")
            hvis = "%s %s %s" % (hvis["hvis"], {"=": "=="}.get(hvis.get("er", "="), hvis.get("er", "=")),
                                 repr(v) if isinstance(v, str) else v)
        return _dnf(_parse(hvis))

    def _skabelon(self, t):
        """'Om {Forsinkelse/60:heltal} min' -> (prefix, slot|None, suffix)"""
        t = str(t)
        pladser = re.findall(r"\{([^{}]*)\}", t)
        if not pladser:
            return t, None, ""
        if len(pladser) > 1:
            raise RegelFejl("en tekst kan kun have EN {plads} (fik %d)" % len(pladser))
        indhold = pladser[0]
        pre, suf = t.split("{%s}" % indhold, 1)
        saerlig = [f for f in ("hh:mm:ss", "mm:ss", "hh:mm", "m:ss") if indhold.replace(" ", "").endswith(":" + f)][:1]
        if saerlig:
            udtryk, fmt = indhold.replace(" ", "")[:-(len(saerlig[0]) + 1)], saerlig[0]
        elif ":" in indhold:
            udtryk, fmt = indhold.rsplit(":", 1)
        else:
            udtryk, fmt = indhold, ""
        fmt = {"": "", ".0f": "heltal", "d": "heltal", ".1f": "1dec", "+.0f": "fortegn", "+d": "fortegn",
               "mm:ss": "mmss", "hh:mm": "hhmm", "m:ss": "msek", "hh:mm:ss": "hhmmss"}.get(fmt.strip(), fmt.strip())
        x = _lin(_parse(udtryk))
        if x[0] == "k":
            return pre + _tal(x[1]) + suf, None, ""
        _, navn, a, b, m = x
        if not fmt:
            fmt = "raa" if (a, b, m) == (1.0, 0.0, 0.0) else "heltal"
        if fmt not in FORMAT_KODE:
            raise RegelFejl("ukendt format '%s' (brug %s)" % (fmt, ", ".join(FORMAT_KODE)))
        return pre, (self._var(navn), a, b, m, FORMAT_KODE[fmt]), suf

    def _regel(self, handling, maal, start_antal, til=None, ellers=None, har_ellers=False, glid=0.0, beskrivelse=""):
        start, antal = start_antal
        r = dict(start=start, count=antal, action=HANDLING_KODE[handling], target=maal, has_ellers=bool(har_ellers),
                 col_til="#FFFFFF", col_ellers="#FFFFFF", num_til=1.0, num_ellers=1.0, txt_til="", suffix="",
                 txt_ellers="", slot=(-1, 1.0, 0.0, 0.0, 0), glid=float(glid or 0))
        if handling in ("farve", "tekstfarve"):
            r["col_til"] = str(til or "#FFFFFF")
            r["col_ellers"] = str(ellers or "#FFFFFF")
        elif handling == "opacity":
            r["num_til"] = float(til if til is not None else 1)
            r["num_ellers"] = float(ellers if ellers is not None else 1)
        elif handling in ("flytx", "flyty"):   # forskyd elementet (pixels) - med glid bliver det en glidende animation
            r["num_til"] = float(til if til is not None else 0)
            r["num_ellers"] = float(ellers if ellers is not None else 0)
        elif handling == "tekst":
            pre, slot, suf = self._skabelon(til if til is not None else "")
            r.update(txt_til=pre, suffix=suf, txt_ellers=str(ellers) if ellers is not None else "")
            if slot:
                r["slot"] = slot
        elif handling in ("tilfoejtag", "fjerntag"):
            r["txt_til"] = str(til or "")
        elif handling == "billede":
            r["txt_til"] = self.billede_for(str(til)) if til else ""
            r["txt_ellers"] = self.billede_for(str(ellers)) if ellers else ""
        self.rules.append(r)
        self.linjer.append("%s %s: %s -> til=%s ellers=%s glid=%s" % (beskrivelse, handling, maal, til,
                                                                       ellers if har_ellers else "-", glid))

    def regel(self, r):
        handling = r.get("saet", "farve")
        if handling not in HANDLINGER:
            raise RegelFejl("ukendt 'saet': %s (brug %s)" % (handling, ", ".join(HANDLINGER)))
        if "element" not in r:
            raise RegelFejl("reglen mangler 'element'")
        maal = self.maal_for(r["element"])
        glid = float(r.get("glid", 0) or 0)
        hvis = r.get("hvis")
        if "er" in r and isinstance(hvis, str) and not any(c in hvis for c in "<>=!"):
            hvis = {"hvis": hvis, "er": r["er"], "vaerdi": r.get("vaerdi")}
        konjer = self._hvis(hvis)
        betinget = bool(konjer)
        txt = "hvis %s" % hvis if betinget else "altid"

        if handling == "blink":
            p = float(r.get("periode", 1.0))
            fase = (("Tid", 1.0, 0.0, p), ">=", _tal(p / 2))
            k2 = [k + [fase] for k in konjer] if betinget else [[fase]]
            self._regel("opacity", maal, self._grupper(k2), r.get("min", 0), 1, True, glid, txt + " (blink)")
            return
        if handling in ("vis", "skjul"):
            if glid > 0:
                til, ellers = (1, 0) if handling == "vis" else (0, 1)
                self._regel("opacity", maal, self._grupper(konjer), til, ellers, True, glid, txt)
            else:
                self._regel(handling, maal, self._grupper(konjer), None, None, betinget, 0, txt)
            return
        self._regel(handling, maal, self._grupper(konjer), r.get("til"), r.get("ellers"), "ellers" in r, glid, txt)

    def sider(self, s):
        """{"skift_hver": 10, "glid": 0.5, "sider": [["A","B"], ["Reklame"]]}"""
        T = float(s.get("skift_hver", 10))
        sider = s.get("sider", [])
        n = len(sider)
        if n < 2:
            raise RegelFejl("'sider' skal have mindst 2 sider")
        glid = float(s.get("glid", 0) or 0)
        for i, side in enumerate(sider):
            fra = (("Tid", 1.0, 0.0, T * n), ">=", _tal(T * i))
            til = (("Tid", 1.0, 0.0, T * n), "<", _tal(T * (i + 1)))
            for el in side:
                maal = self.maal_for(el)
                if glid > 0:
                    self._regel("opacity", maal, self._grupper([[fra, til]]), 1, 0, True, glid, "side %d" % (i + 1))
                else:
                    self._regel("vis", maal, self._grupper([[fra, til]]), None, None, True, 0, "side %d" % (i + 1))

    def program(self):
        return dict(vars=self.vars, conds=self.conds, rules=self.rules, log=self.linjer)


def kompiler(regler, kilde_for, maal_for, billede_for=None, sider=None, log=print):
    k = Kompiler(kilde_for, maal_for, billede_for)
    for nr, r in enumerate(regler or [], 1):
        try:
            k.regel(r)
        except (RegelFejl, KeyError, ValueError) as e:
            log("FEJL i regel %d (%s): %s" % (nr, r, e))
    if sider:
        try:
            k.sider(sider)
        except (RegelFejl, KeyError, ValueError) as e:
            log("FEJL i 'sider': %s" % e)
    return k.program()
