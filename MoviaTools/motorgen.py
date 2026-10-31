# -*- coding: utf-8 -*-
"""Genererer hele WBP_MoviaMotor EventGraph som T3D."""
import sys
from bpgen import Graph, Chain, link

g = Graph()

# ---------- korte hjaelpere ----------
def M(f, ins, outs=(("ReturnValue", "real"),), **v):
    return g.call("Math", f, ins=ins, outs=outs, pure=True, **v)["ReturnValue"]

def S(f, ins, outs=(("ReturnValue", "string"),), **v):
    return g.call("Str", f, ins=ins, outs=outs, pure=True, **v)["ReturnValue"]

D2 = (("A", "real"), ("B", "real"))
I2 = (("A", "int"), ("B", "int"))
B2 = (("A", "bool"), ("B", "bool"))
def mul(a, b): return M("Multiply_DoubleDouble", D2, A=a, B=b)
def add(a, b): return M("Add_DoubleDouble", D2, A=a, B=b)
def sub(a, b): return M("Subtract_DoubleDouble", D2, A=a, B=b)
def div(a, b): return M("Divide_DoubleDouble", D2, A=a, B=b)
def ge(a, b): return M("GreaterEqual_DoubleDouble", D2, (("ReturnValue", "bool"),), A=a, B=b)
def le(a, b): return M("LessEqual_DoubleDouble", D2, (("ReturnValue", "bool"),), A=a, B=b)
def gt(a, b): return M("Greater_DoubleDouble", D2, (("ReturnValue", "bool"),), A=a, B=b)
def lt(a, b): return M("Less_DoubleDouble", D2, (("ReturnValue", "bool"),), A=a, B=b)
def AND(a, b): return M("BooleanAND", B2, (("ReturnValue", "bool"),), A=a, B=b)
def OR(a, b): return M("BooleanOR", B2, (("ReturnValue", "bool"),), A=a, B=b)
def ieq(a, b): return M("EqualEqual_IntInt", I2, (("ReturnValue", "bool"),), A=a, B=b)
def ige(a, b): return M("GreaterEqual_IntInt", I2, (("ReturnValue", "bool"),), A=a, B=b)
def ilt(a, b): return M("Less_IntInt", I2, (("ReturnValue", "bool"),), A=a, B=b)
def iadd(a, b): return M("Add_IntInt", I2, (("ReturnValue", "int"),), A=a, B=b)
def isub(a, b): return M("Subtract_IntInt", I2, (("ReturnValue", "int"),), A=a, B=b)
def idiv(a, b): return M("Divide_IntInt", I2, (("ReturnValue", "int"),), A=a, B=b)
def imod(a, b): return M("Percent_IntInt", I2, (("ReturnValue", "int"),), A=a, B=b)
def rnd(a): return M("Round", (("A", "real"),), (("ReturnValue", "int"),), A=a)
def iabs(a): return M("Abs_Int", (("A", "int"),), (("ReturnValue", "int"),), A=a)
def i2d(a): return M("Conv_IntToDouble", (("InInt", "int"),), InInt=a)
def b2d(a): return M("Conv_BoolToDouble", (("InBool", "bool"),), InBool=a)
def selF(a, b, pick): return M("SelectFloat", (("A", "real"), ("B", "real"), ("bPickA", "bool")), A=a, B=b, bPickA=pick)
def selS(a, b, pick): return M("SelectString", (("A", "string"), ("B", "string"), ("bPickA", "bool")), (("ReturnValue", "string"),), A=a, B=b, bPickA=pick)
def selB(a, b, pick): return OR(AND(a, pick), AND(b, M("Not_PreBool", (("A", "bool"),), (("ReturnValue", "bool"),), A=pick)))
def selC(a, b, pick): return M("SelectColor", (("A", "struct:LinearColor"), ("B", "struct:LinearColor"), ("bPickA", "bool")), (("ReturnValue", "struct:LinearColor"),), A=a, B=b, bPickA=pick)
def lerp(a, b, al): return M("Lerp", (("A", "real"), ("B", "real"), ("Alpha", "real")), A=a, B=b, Alpha=al)
def fmin(a, b): return M("FMin", D2, A=a, B=b)
def neqb(a, b): return M("NotEqual_BoolBool", B2, (("ReturnValue", "bool"),), A=a, B=b)
def floor64(a):
    f = g.call("Math", "FFloor64", ins=(("A", "real"),), outs=(("ReturnValue", "int64"),), pure=True, A=a)["ReturnValue"]
    return g.call("Math", "Conv_Int64ToDouble", ins=(("InInt", "int64"),), outs=(("ReturnValue", "real"),), pure=True, InInt=f)["ReturnValue"]
def cat(a, b): return S("Concat_StrStr", (("A", "string"), ("B", "string")), A=a, B=b)
def i2s(a): return S("Conv_IntToString", (("InInt", "int"),), InInt=a)
def d2s(a): return S("Conv_DoubleToString", (("InDouble", "real"),), InDouble=a)
def s2d(a): return S("Conv_StringToDouble", (("InString", "string"),), (("ReturnValue", "real"),), InString=a)
def s2i(a): return S("Conv_StringToInt", (("InString", "string"),), (("ReturnValue", "int"),), InString=a)
def trim(a): return S("Trim", (("SourceString", "string"),), SourceString=a)
def starts(a, p): return S("StartsWith", (("SourceString", "string"), ("InPrefix", "string")), (("ReturnValue", "bool"),), SourceString=a, InPrefix=p)
def repl(a, f, t): return S("Replace", (("SourceString", "string"), ("From", "string"), ("To", "string")), SourceString=a, From=f, To=t)
def parse(a, d): return S("ParseIntoArray", (("SourceString", "string"), ("Delimiter", "string"), ("CullEmptyStrings", "bool")), (("ReturnValue", "string[]"),), SourceString=a, Delimiter=d, CullEmptyStrings=True)
def streq(a, b): return S("EqualEqual_StriStri", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=a, B=b)
def contains(a, b): return S("Contains", (("SearchIn", "string"), ("Substring", "string")), (("ReturnValue", "bool"),), SearchIn=a, Substring=b)
def t2s(a): return g.call("Text", "Conv_TextToString", ins=(("InText", "text"),), outs=(("ReturnValue", "string"),), pure=True, InText=a)["ReturnValue"]
def s2t(a): return g.call("Text", "Conv_StringToText", ins=(("InString", "string"),), outs=(("ReturnValue", "text"),), pure=True, InString=a)["ReturnValue"]
def isvalid(o): return g.call("Sys", "IsValid", ins=(("Object", "obj:Object"),), outs=(("ReturnValue", "bool"),), pure=True, Object=o)["ReturnValue"]
def now(): return g.call("GS", "GetTimeSeconds", ins=(), outs=(("ReturnValue", "real"),), pure=True)["ReturnValue"]
def arrlen(var, elem):
    return g.arrfunc("Array_Length", elem, ins=[("TargetArray", "E[]")], outs=[("ReturnValue", "int")], pure=True,
                     TargetArray=g.get(var, elem + "[]"))["ReturnValue"]
def get(v, s): return g.get(v, s)
def it(v, e, i): return g.item(v, e, i)
def setv(ch, v, s, val): return ch.then(g.set(v, s, val))
def callev(ch, name):
    return ch.then(g.call(None, name, selfctx=True))
def pad2(x):
    s = i2s(x)
    return selS(cat("0", s), s, ilt(x, 10))
def selfp(): return g.self_ref()

INTERIOR = "/Script/UMG.WidgetBlueprintGeneratedClass'/Game/Gameplay/Vehicles/Common/Displays/PassengerDisplays/UMG_InteriorDisplayBase.UMG_InteriorDisplayBase_C'"
BUSLOGIC = "/Script/Engine.BlueprintGeneratedClass'/Game/Gameplay/Vehicles/BusBase/BusLogic/BP_BusLogic.BP_BusLogic_C'"
WORLDFN = "/Script/Engine.BlueprintGeneratedClass'/Game/Gameplay/World/BP_GlobalWorldFunctions.BP_GlobalWorldFunctions_C'"
WORLDMGR = "/Script/Engine.BlueprintGeneratedClass'/Game/Gameplay/World/BP_WorldManager_Base.BP_WorldManager_Base_C'"
TRIPFN = "/Script/CoreUObject.Class'/Script/Fernbus.BusTripInfo_Functions'"

def world_datetime():
    wm = g.call_path(WORLDFN, "Get World Manager", ins=(), outs=(("World Manager", "obj:Object"),), pure=True,
                     static_default="/Game/Gameplay/World/BP_GlobalWorldFunctions.Default__BP_GlobalWorldFunctions_C")["World Manager"]
    return g.call_path(WORLDMGR, "Get DateTime", ins=(), outs=(("DateTime", "struct:/Script/CoreUObject.DateTime"),), pure=True, target=wm)["DateTime"]


RSWT = "struct:/Script/Fernbus.RouteStopWithTime"
FELTER = (("ArrivalTime", "struct:/Script/CoreUObject.DateTime"), ("DepartureTime", "struct:/Script/CoreUObject.DateTime"),
          ("StopIdent", "struct:/Script/RoadmapSystem.BusStopIdentifier"), ("RouteStopInfo", "obj:Object"))

def stopnoegle(ident):
    """Entydig tekst for et stop: navn|index."""
    bi = g.break_struct("/Script/RoadmapSystem.BusStopIdentifier", "BusStopIdentifier", ident, (("StopName", "name"), ("StopIndex", "int")))
    nm = g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True, InName=bi["StopName"])["ReturnValue"]
    return cat(cat(nm, "|"), i2s(bi["StopIndex"]))

def naeste(trip, aktuel=False):
    """Samme logik som spillets passagerskaerm: mens bussen er ved et stop huskes spillets GetNextStop
    (i tNaesteStop, se MSidst). Ved et stop vises det aktuelle stop, ellers det huskede naeste stop."""
    cur = g.call_path(TRIPFN, "FBusTripInfo_GetCurrentStop", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                      outs=(("IsValid", "bool"), ("ReturnValue", RSWT)), pure=True, static_default="x", a=trip)
    bc = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", cur["ReturnValue"], FELTER)
    bo = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", get("tNaesteStop", RSWT), FELTER)
    # som passagerskaermen: vis altid det huskede naeste stop (ogsaa mens bussen holder ved et stop)
    return (cur["IsValid"] if aktuel else False), bc, bo, True

def stopnavn(ident):
    bi = g.break_struct("/Script/RoadmapSystem.BusStopIdentifier", "BusStopIdentifier", ident, (("StopName", "name"),))
    return g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True, InName=bi["StopName"])["ReturnValue"]

def tag_saet(start_pin, pre, val):
    """exec-kaede: MTagSet(pre, val). Returnerer sidste then-pin."""
    a = g.set("tTagPre", "string", pre); link(start_pin, a["execute"])
    b = g.set("tTagNy", "real", val); link(a["then"], b["execute"])
    c = g.call(None, "MTagSet", selfctx=True); link(b["then"], c["execute"])
    return c["then"]
def tag_plus1(start_pin, pre):
    a = g.set("tTagPre", "string", pre); link(start_pin, a["execute"])
    c0 = g.call(None, "MTagGet", selfctx=True); link(a["then"], c0["execute"])
    b = g.set("tTagNy", "real", add(get("tTagVal", "real"), "1")); link(c0["then"], b["execute"])
    c = g.call(None, "MTagSet", selfctx=True); link(b["then"], c["execute"])
    return c["then"]


def bus_actor0():
    """v38: bussen som skaermen sidder i (sat i tBus i starten af MoviaUpdate)."""
    return get("tBus", "obj:Object")

def bus_actor_spiller():
    pw = g.call("GS", "GetPlayerPawn", ins=(("PlayerIndex", "int"),), outs=(("ReturnValue", "obj:Actor"),), pure=True, PlayerIndex="0")["ReturnValue"]
    fa = g.call(None, "GetAttachParentActor", target_cls="Actor", target=pw, pure=True, outs=(("ReturnValue", "obj:Actor"),))["ReturnValue"]
    pw2 = g.call("GS", "GetPlayerPawn", ins=(("PlayerIndex", "int"),), outs=(("ReturnValue", "obj:Actor"),), pure=True, PlayerIndex="0")["ReturnValue"]
    fa2 = g.call(None, "GetAttachParentActor", target_cls="Actor", target=pw2, pure=True, outs=(("ReturnValue", "obj:Actor"),))["ReturnValue"]
    return g.call("Math", "SelectObject", ins=(("A", "obj:Object"), ("B", "obj:Object"), ("bSelectA", "bool")),
                  outs=(("ReturnValue", "obj:Object"),), pure=True, A=fa, B=pw2, bSelectA=isvalid(fa2))["ReturnValue"]

# =========================================================
# Construct
# =========================================================
g.next_col()
ev = g.event("/Script/UMG.UserWidget", "Construct")
ch = Chain(g, ev["then"])
o1 = g.call("Sys", "GetOuterObject", ins=(("Object", "obj:Object"),), outs=(("ReturnValue", "obj:Object"),), pure=True, Object=selfp())["ReturnValue"]
o2 = g.call("Sys", "GetOuterObject", ins=(("Object", "obj:Object"),), outs=(("ReturnValue", "obj:Object"),), pure=True, Object=o1)["ReturnValue"]
c = g.cast(o2, "UserWidget")
ch.then(c)
sh = setv(ch, "Host", "obj:UserWidget", c.out)
lt_ = g.set("LastTime", "real", now())
link(sh["then"], lt_["execute"])
link(c["CastFailed"], lt_["execute"])
ch.to(lt_["then"])
setv(ch, "tStart", "real", now())
setv(ch, "tPauseLoaded", "bool", False)
for _v, _e in (("tKnapVal", "real"), ("tKnapPrev", "bool"), ("tRegelPrev", "bool"), ("tTxt", "string")):
    ch.then(g.arrfunc("Array_Clear", _e, ins=[("TargetArray", "E[]")], TargetArray=g.get(_v, _e + "[]")))
ch.then(g.arrfunc("Array_Set", "string", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                  TargetArray=g.get("tTxt", "string[]"), Index="3", Item="", bSizeToFit=True))
_GEMCLS = "/Script/Engine.BlueprintGeneratedClass'/Game/MoviaSkaerme/BP_MoviaGem.BP_MoviaGem_C'"
dse = g.call("GS", "DoesSaveGameExist", ins=(("SlotName", "string"), ("UserIndex", "int")), outs=(("ReturnValue", "bool"),),
             SlotName="MoviaLogin", UserIndex="0")
ch.then(dse)
bld = g.branch(AND(ige(get("HuskGruppe", "int"), "0"), dse["ReturnValue"]))
ch.then(bld)
lch = Chain(g, bld["then"])
lgs = g.call("GS", "LoadGameFromSlot", ins=(("SlotName", "string"), ("UserIndex", "int")), outs=(("ReturnValue", "obj:Object"),),
             SlotName="MoviaLogin", UserIndex="0")
lch.then(lgs)
clg = g.cast(lgs["ReturnValue"], "", disp="BP Movia Gem", path=_GEMCLS)
lch.then(clg)
bh = g.branch(g.member_get(_GEMCLS, "Husk", "bool", clg.out))
lch.then(bh)
SETS = lambda arr, e, idx, val: g.arrfunc("Array_Set", e, ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                                         TargetArray=g.get(arr, e + "[]"), Index=idx, Item=val, bSizeToFit=True)
lch.then(SETS("tTxt", "string", "0", g.member_get(_GEMCLS, "Email", "string", clg.out)))
lch.then(SETS("tKnapVal", "real", get("HuskGruppe", "int"), "1"))
bfg = g.branch(ige(get("FeltGruppe", "int"), "0"))
lch.then(bfg)
lch.then(SETS("tKnapVal", "real", get("FeltGruppe", "int"), "1"))
jl = g.sequence(1)
for pp in (bld["else"], clg["CastFailed"], bh["else"], bfg["else"], lch.cur if hasattr(lch, "cur") else None):
    if pp is not None:
        link(pp, jl["execute"])
ch = Chain(g, jl["then_0"])
iv = get("Interval", "real")
tm = g.call("Sys", "K2_SetTimerDelegate", ins=(("Delegate", "delegate"), ("Time", "real"), ("bLooping", "bool")),
            outs=(("ReturnValue", "struct:/Script/Engine.TimerHandle"),),
            Time=selF(iv, "0.15", gt(iv, "0.01")), bLooping=True)
link(g.create_delegate("MoviaUpdate"), tm["Delegate"])
ch.then(tm)

# =========================================================
# MFind: tPath ("3/0/2") -> tW
# =========================================================
g.next_col()
ev = g.custom_event("MFind")
ch0 = Chain(g, ev["then"])
# "@Navn|sti": find widget paa navn (robust), ellers sti af barne-numre ("3/0/2")
bat = g.branch(starts(get("tPath", "string"), "@"))
ch0.then(bat)
nch = Chain(g, bat["then"])
setv(nch, "tParts", "string[]", parse(get("tPath", "string"), "|"))
wnavn = S("RightChop", (("SourceString", "string"), ("Count", "int")), SourceString=it("tParts", "string", "0"), Count="1")
fn = g.call(None, "GetWidgetFromName", target_cls="UserWidget", target=get("Host", "obj:UserWidget"),
            ins=(("Name", "name"),), outs=(("ReturnValue", "obj:Widget"),),
            Name=S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),), InString=wnavn))
nch.then(fn)
setv(nch, "tW", "obj:Widget", fn["ReturnValue"])
bok = g.branch(isvalid(get("tW", "obj:Widget")))
nch.then(bok)
nyp = g.set("tPath", "string", selS(it("tParts", "string", "1"), "", ige(arrlen("tParts", "string"), "2")))
link(bok["else"], nyp["execute"])
gp = g.call(None, "GetParent", selfctx=True, pure=True, outs=(("ReturnValue", "obj:PanelWidget"),))["ReturnValue"]
start = g.set("tW", "obj:Widget", gp)
link(bat["else"], start["execute"])
link(nyp["then"], start["execute"])
ch = Chain(g, start["then"])
setv(ch, "tParts", "string[]", parse(get("tPath", "string"), "/"))
fl = g.forloop("0", isub(arrlen("tParts", "string"), "1"))
ch.then(fl, outpin="LoopBody")
c = g.cast(get("tW", "obj:Widget"), "PanelWidget")
ch.then(c)
child = g.call(None, "GetChildAt", target_cls="PanelWidget", target=c.out, pure=True,
               ins=(("Index", "int"),), outs=(("ReturnValue", "obj:Widget"),), Index=s2i(it("tParts", "string", fl["Index"])))["ReturnValue"]
setv(ch, "tW", "obj:Widget", child)
fail = g.set("tW", "obj:Widget", None)
link(c["CastFailed"], fail["execute"])

# =========================================================
# MParse: tStr -> tNum   ("+0:02:30" -> 150, "12" -> 12)
# =========================================================
g.next_col()
ev = g.custom_event("MParse")
ch = Chain(g, ev["then"])
ts = trim(get("tStr", "string"))
setv(ch, "tNeg", "bool", starts(ts, "-"))
setv(ch, "tParts", "string[]", parse(repl(repl(trim(get("tStr", "string")), "+", ""), "-", ""), ":"))
setv(ch, "tAcc", "real", "0")
fl = g.forloop("0", isub(arrlen("tParts", "string"), "1"))
ch.then(fl, outpin="LoopBody")
setv(ch, "tAcc", "real", add(mul(get("tAcc", "real"), "60"), s2d(it("tParts", "string", fl["Index"]))))
ch2 = Chain(g, fl["Completed"])
acc = get("tAcc", "real")
setv(ch2, "tNum", "real", selF(mul(acc, "-1"), acc, get("tNeg", "bool")))

# =========================================================
# MRead: tVar -> tStr, tNum
# =========================================================
g.next_col()
ev = g.custom_event("MRead")
ch = Chain(g, ev["then"])
sw = g.switch_int(it("VarType", "int", get("tVar", "int")), 36)
ch.then(sw, outpin=None)
# 0 tekst
c0 = Chain(g, sw["0"])
setv(c0, "tPath", "string", it("VarPath", "string", get("tVar", "int")))
callev(c0, "MFind")
cst = g.cast(get("tW", "obj:Widget"), "TextBlock")
c0.then(cst)
txt = g.call(None, "GetText", target_cls="TextBlock", target=cst.out, pure=True, outs=(("ReturnValue", "text"),))["ReturnValue"]
setv(c0, "tStr", "string", t2s(txt))
callev(c0, "MParse")
f0 = g.set("tStr", "string", "")
link(cst["CastFailed"], f0["execute"])
f0b = g.set("tNum", "real", "0")
link(f0["then"], f0b["execute"])
# 1 synlig
c1 = Chain(g, sw["1"])
setv(c1, "tPath", "string", it("VarPath", "string", get("tVar", "int")))
callev(c1, "MFind")
vis = g.call(None, "IsVisible", target_cls="Widget", target=get("tW", "obj:Widget"), pure=True, outs=(("ReturnValue", "bool"),))["ReturnValue"]
setv(c1, "tNum", "real", b2d(vis))
setv(c1, "tStr", "string", selS("ja", "nej", vis))
# 2 tid
c2 = Chain(g, sw["2"])
setv(c2, "tNum", "real", now())
setv(c2, "tStr", "string", d2s(get("tNum", "real")))
# 3 klokken (minutter efter midnat i spillets ur)
c3 = Chain(g, sw["3"])
dt = world_datetime()
hr = g.call("Math", "GetHour", ins=(("A", "struct:/Script/CoreUObject.DateTime"),), outs=(("ReturnValue", "int"),), pure=True, A=dt)["ReturnValue"]
mi = g.call("Math", "GetMinute", ins=(("A", "struct:/Script/CoreUObject.DateTime"),), outs=(("ReturnValue", "int"),), pure=True, A=dt)["ReturnValue"]
setv(c3, "tNum", "real", i2d(iadd(M("Multiply_IntInt", I2, (("ReturnValue", "int"),), A=hr, B="60"), mi)))
setv(c3, "tStr", "string", d2s(get("tNum", "real")))
# 4 minutter til stop nr. VarIdx
c4 = Chain(g, sw["4"])
ci = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG Interior Display Base", path=INTERIOR)
c4.then(ci)
bl = g.member_get(INTERIOR, "Bus Logic", "obj:Object", ci.out)
info = g.member_get(BUSLOGIC, "Bus Trip Info", "struct:/Script/Fernbus.BusTripInfo", bl)
stop = g.call_path(TRIPFN, "FBusTripInfo_GetStopByIndexOffset", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"), ("Offset", "int")),
                   outs=(("IsValid", "bool"), ("ReturnValue", "struct:/Script/Fernbus.RouteStopWithTime")), pure=True,
                   static_default="/Script/Fernbus.Default__BusTripInfo_Functions",
                   a=info, Offset=it("VarIdx", "int", get("tVar", "int")))
br = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", stop["ReturnValue"],
                    (("ArrivalTime", "struct:/Script/CoreUObject.DateTime"),))
span = g.call("Math", "Subtract_DateTimeDateTime", ins=(("A", "struct:/Script/CoreUObject.DateTime"), ("B", "struct:/Script/CoreUObject.DateTime")),
              outs=(("ReturnValue", "struct:/Script/CoreUObject.Timespan"),), pure=True, A=br["ArrivalTime"], B=world_datetime())["ReturnValue"]
tot = g.call("Math", "GetTotalMinutes", ins=(("A", "struct:/Script/CoreUObject.Timespan"),), outs=(("ReturnValue", "real"),), pure=True, A=span)["ReturnValue"]
setv(c4, "tNum", "real", tot)
setv(c4, "tStr", "string", i2s(rnd(get("tNum", "real"))))
f4 = g.set("tNum", "real", "0")
link(ci["CastFailed"], f4["execute"])

# 5 afstand (meter til naeste stop) / 6 forventet minutter til stop nr. VarIdx
for case in ("5", "6"):
    cx = Chain(g, sw[case])
    cx.then(g.call(None, "MTrip", selfctx=True))
    if case == "5":
        setv(cx, "tNum", "real", get("tDist", "real"))
    else:
        setv(cx, "tNum", "real", add(sub(get("tMi", "real"), get("tM1", "real")), div(get("tDist", "real"), "400")))
    setv(cx, "tStr", "string", i2s(rnd(get("tNum", "real"))))

# 7 forsinkelse (bordcomputer): sekunder, positiv = forsinket  | 8 sidste stops planlagte ankomst (min efter midnat) | 9 linje
NATRON = "/Script/UMG.WidgetBlueprintGeneratedClass'/Game/UI/Berlin/Menu/Atron/NewAtron/UMG_TB_Natron_Base.UMG_TB_Natron_Base_C'"
for case in ("7", "8", "9"):
    cx = Chain(g, sw[case])
    cn = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
    cx.then(cn)
    trip = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn.out)["Result"]
    if case == "7":
        gyl, bc, bo, _ = naeste(trip)
        def secs(dt):
            span = g.call("Math", "Subtract_DateTimeDateTime", ins=(("A", "struct:/Script/CoreUObject.DateTime"), ("B", "struct:/Script/CoreUObject.DateTime")),
                          outs=(("ReturnValue", "struct:/Script/CoreUObject.Timespan"),), pure=True, A=world_datetime(), B=dt)["ReturnValue"]
            return g.call("Math", "GetTotalSeconds", ins=(("A", "struct:/Script/CoreUObject.Timespan"),), outs=(("ReturnValue", "real"),), pure=True, A=span)["ReturnValue"]
        setv(cx, "tNum", "real", selF(secs(bc["DepartureTime"]), secs(bo["DepartureTime"]), gyl))
        setv(cx, "tStr", "string", i2s(rnd(get("tNum", "real"))))
    elif case == "8":
        last = g.call_path(TRIPFN, "FBusTripInfo_GetLastStop", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                           outs=(("IsValid", "bool"), ("ReturnValue", "struct:/Script/Fernbus.RouteStopWithTime")), pure=True, static_default="x", a=trip)
        br = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", last["ReturnValue"],
                            (("ArrivalTime", "struct:/Script/CoreUObject.DateTime"),))
        hr = g.call("Math", "GetHour", ins=(("A", "struct:/Script/CoreUObject.DateTime"),), outs=(("ReturnValue", "int"),), pure=True, A=br["ArrivalTime"])["ReturnValue"]
        mi = g.call("Math", "GetMinute", ins=(("A", "struct:/Script/CoreUObject.DateTime"),), outs=(("ReturnValue", "int"),), pure=True, A=br["ArrivalTime"])["ReturnValue"]
        setv(cx, "tNum", "real", i2d(iadd(M("Multiply_IntInt", I2, (("ReturnValue", "int"),), A=hr, B="60"), mi)))
        setv(cx, "tStr", "string", d2s(get("tNum", "real")))
    else:
        bt = g.break_struct("/Script/Fernbus.BusTripInfo", "BusTripInfo", trip, (("Route", "obj:Object"),))
        line = g.member_get("/Script/CoreUObject.Class'/Script/Fernbus.LineRoute'", "Line", "name", bt["Route"])
        lstr = g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True, InName=line)["ReturnValue"]
        setv(cx, "tStr", "string", lstr)
        setv(cx, "tNum", "real", s2d(get("tStr", "string")))

# 10 klokken i sekunder | 11 naeste stops planlagte ankomst (sek efter midnat) | 12 sidste stops (sek efter midnat)
def secs_of_day(dt):
    h = g.call("Math", "GetHour", ins=(("A", "struct:/Script/CoreUObject.DateTime"),), outs=(("ReturnValue", "int"),), pure=True, A=dt)["ReturnValue"]
    m = g.call("Math", "GetMinute", ins=(("A", "struct:/Script/CoreUObject.DateTime"),), outs=(("ReturnValue", "int"),), pure=True, A=dt)["ReturnValue"]
    s_ = g.call("Math", "GetSecond", ins=(("A", "struct:/Script/CoreUObject.DateTime"),), outs=(("ReturnValue", "int"),), pure=True, A=dt)["ReturnValue"]
    hm = iadd(M("Multiply_IntInt", I2, (("ReturnValue", "int"),), A=h, B="3600"), M("Multiply_IntInt", I2, (("ReturnValue", "int"),), A=m, B="60"))
    return i2d(iadd(hm, s_))
c10 = Chain(g, sw["10"])
setv(c10, "tNum", "real", secs_of_day(world_datetime()))
setv(c10, "tStr", "string", d2s(get("tNum", "real")))
for case, fn in (("12", "FBusTripInfo_GetLastStop"),):
    cx = Chain(g, sw[case])
    cn = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
    cx.then(cn)
    trip = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn.out)["Result"]
    st = g.call_path(TRIPFN, fn, ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                     outs=(("IsValid", "bool"), ("ReturnValue", "struct:/Script/Fernbus.RouteStopWithTime")), pure=True, static_default="x", a=trip)
    br = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", st["ReturnValue"], (("ArrivalTime", "struct:/Script/CoreUObject.DateTime"),))
    setv(cx, "tNum", "real", secs_of_day(br["ArrivalTime"]))
    setv(cx, "tStr", "string", d2s(get("tNum", "real")))

# 11 naeste stops planlagte tid (afgang - samme tid som spillets navigator viser)
cx = Chain(g, sw["11"])
cn = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
cx.then(cn)
trip = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn.out)["Result"]
gyl, bc, bo, _ = naeste(trip)
setv(cx, "tNum", "real", selF(secs_of_day(bc["DepartureTime"]), secs_of_day(bo["DepartureTime"]), gyl))
setv(cx, "tStr", "string", d2s(get("tNum", "real")))

# 13 sidste stops navn
cx = Chain(g, sw["13"])
cn = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
cx.then(cn)
trip = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn.out)["Result"]
st = g.call_path(TRIPFN, "FBusTripInfo_GetLastStop", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                 outs=(("IsValid", "bool"), ("ReturnValue", "struct:/Script/Fernbus.RouteStopWithTime")), pure=True, static_default="x", a=trip)
br = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", st["ReturnValue"], (("StopIdent", "struct:/Script/RoadmapSystem.BusStopIdentifier"),))
bi = g.break_struct("/Script/RoadmapSystem.BusStopIdentifier", "BusStopIdentifier", br["StopIdent"], (("StopName", "name"),))
nm = g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True, InName=bi["StopName"])["ReturnValue"]
setv(cx, "tStr", "string", nm)
setv(cx, "tNum", "real", "0")

# 14 naeste stops navn (det aktuelle stop mens bussen holder der, ellers det naeste)
# 15 naeste stops planlagte afgang (sek efter midnat)
for case in ("14", "15"):
    cx = Chain(g, sw[case])
    cn = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
    cx.then(cn)
    trip = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn.out)["Result"]
    gyl, bc, bo, _ = naeste(trip)
    if case == "14":
        setv(cx, "tStr", "string", selS(stopnavn(bc["StopIdent"]), stopnavn(bo["StopIdent"]), gyl))
        setv(cx, "tNum", "real", "0")
    else:
        setv(cx, "tNum", "real", selF(secs_of_day(bc["DepartureTime"]), secs_of_day(bo["DepartureTime"]), gyl))
        setv(cx, "tStr", "string", d2s(get("tNum", "real")))

# 16 andre linjer ved stop: VarIdx = raekke*10 + maerke  -> StopLin[(raekke-1)*5 + maerke-1]
c16 = Chain(g, sw["16"])
vi = it("VarIdx", "int", get("tVar", "int"))
idx16 = iadd(M("Multiply_IntInt", I2, (("ReturnValue", "int"),), A=isub(idiv(vi, "10"), "1"), B="5"), isub(imod(it("VarIdx", "int", get("tVar", "int")), "10"), "1"))
setv(c16, "tT", "int", idx16)
setv(c16, "tNum", "real", "0")
b16 = g.branch(AND(ige(get("tT", "int"), "0"), ilt(get("tT", "int"), arrlen("StopLin", "string"))))
c16.then(b16)
s16 = g.set("tStr", "string", it("StopLin", "string", get("tT", "int")))
link(b16["then"], s16["execute"])
e16 = g.set("tStr", "string", "")
link(b16["else"], e16["execute"])
# 17 afgangstavle: VarIdx = raekke*10 + art (1 linje, 2 til, 3 minutter)
c17 = Chain(g, sw["17"])
setv(c17, "tT", "int", isub(idiv(it("VarIdx", "int", get("tVar", "int")), "10"), "1"))
setv(c17, "tStr", "string", "")
setv(c17, "tNum", "real", "-1")
b17 = g.branch(AND(ige(get("tT", "int"), "0"), AND(ilt(get("tT", "int"), arrlen("AfgLin", "string")),
               AND(ilt(get("tT", "int"), arrlen("AfgTil", "string")), ilt(get("tT", "int"), arrlen("AfgMin", "real"))))))
c17.then(b17)
sw17 = g.switch_int(imod(it("VarIdx", "int", get("tVar", "int")), "10"), 4)
link(b17["then"], sw17["execute"])
a1 = g.set("tStr", "string", it("AfgLin", "string", get("tT", "int"))); link(sw17["1"], a1["execute"])
a1b = g.set("tNum", "real", "0"); link(a1["then"], a1b["execute"])
a2 = g.set("tStr", "string", it("AfgTil", "string", get("tT", "int"))); link(sw17["2"], a2["execute"])
a3 = g.set("tNum", "real", it("AfgMin", "real", get("tT", "int"))); link(sw17["3"], a3["execute"])
a3b = g.set("tStr", "string", i2s(rnd(get("tNum", "real")))); link(a3["then"], a3b["execute"])
# 18 ved stoppet (1 = bussen holder ved stoppet eller er under 40 m fra det)
c18 = Chain(g, sw["18"])
ci18 = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG Interior Display Base", path=INTERIOR)
c18.then(ci18)
info18 = g.member_get(BUSLOGIC, "Bus Trip Info", "struct:/Script/Fernbus.BusTripInfo", g.member_get(INTERIOR, "Bus Logic", "obj:Object", ci18.out))
cs18 = g.call_path(TRIPFN, "FBusTripInfo_GetCurrentStop", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                   outs=(("IsValid", "bool"), ("ReturnValue", "struct:/Script/Fernbus.RouteStopWithTime")), pure=True, static_default="x", a=info18)
# v22: 1 naar bussen HOLDER ved stoppet: spillet siger den er ved et stop (GetCurrentStop gyldig,
# samme metode som koereskaermen) OG den holder stille (under 3 km/t)
bus18 = g.member_get(INTERIOR, "Bus", "obj:Object", ci18.out)
pawn18 = g.call("GS", "GetPlayerPawn", ins=(("PlayerIndex", "int"),), outs=(("ReturnValue", "obj:Actor"),), pure=True, PlayerIndex="0")["ReturnValue"]
vb18 = g.call(None, "GetVelocity", target_cls="Actor", target=bus18, pure=True, outs=(("ReturnValue", "struct:/Script/CoreUObject.Vector"),))["ReturnValue"]
vp18 = g.call(None, "GetVelocity", target_cls="Actor", target=pawn18, pure=True, outs=(("ReturnValue", "struct:/Script/CoreUObject.Vector"),))["ReturnValue"]
sb18 = g.call("Math", "VSize", ins=(("A", "struct:/Script/CoreUObject.Vector"),), outs=(("ReturnValue", "real"),), pure=True, A=vb18)["ReturnValue"]
spd18 = g.call("Math", "VSize", ins=(("A", "struct:/Script/CoreUObject.Vector"),), outs=(("ReturnValue", "real"),), pure=True, A=vp18)["ReturnValue"]
setv(c18, "tV", "real", div(selF(sb18, spd18, isvalid(bus18)), "27.7778"))   # cm/s -> km/t
# afstand fra bussen til selve stoppestedet (under 40 m)
V2a = "struct:/Script/CoreUObject.Vector2D"
RSIa = "/Script/CoreUObject.Class'/Script/Fernbus.RouteStopInfo'"
bcs18 = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", cs18["ReturnValue"], (("RouteStopInfo", "obj:Object"),))
spos18 = g.member_get(RSIa, "WorldPosition", V2a, bcs18["RouteStopInfo"])
bl18 = g.call(None, "K2_GetActorLocation", target_cls="Actor", target=bus18, pure=True, outs=(("ReturnValue", "struct:/Script/CoreUObject.Vector"),))["ReturnValue"]
pl18 = g.call(None, "K2_GetActorLocation", target_cls="Actor", target=pawn18, pure=True, outs=(("ReturnValue", "struct:/Script/CoreUObject.Vector"),))["ReturnValue"]
def v2(v): return g.call("Math", "Conv_VectorToVector2D", ins=(("InVector", "struct:/Script/CoreUObject.Vector"),), outs=(("ReturnValue", V2a),), pure=True, InVector=v)["ReturnValue"]
def dist2(a, b): return g.call("Math", "Distance2D", ins=(("V1", V2a), ("V2", V2a)), outs=(("ReturnValue", "real"),), pure=True, V1=a, V2=b)["ReturnValue"]
d18p = selF(dist2(v2(bl18), spos18), dist2(v2(pl18), spos18), isvalid(bus18))
setv(c18, "tNum", "real", b2d(AND(AND(cs18["IsValid"], lt(get("tV", "real"), "3")), le(d18p, "4000"))))
setv(c18, "tStr", "string", cat(cat(cat(cat(i2s(rnd(get("tV", "real"))), " km/t "), i2s(rnd(div(d18p, "100")))), " m"), selS(" *", "", cs18["IsValid"])))
# tekst (fejlsoegning): fart i km/t, * = ved stop ifoelge spillet


# 18 paa koereskaermen (Natron): samme regel - ved stop ifoelge spillet OG holder stille
def fart_kmt(pawn):
    """km/t for bussen spilleren sidder i (actoren spilleren er sat fast paa), ellers spillerens egen fart."""
    far = g.call(None, "GetAttachParentActor", target_cls="Actor", target=pawn, pure=True, outs=(("ReturnValue", "obj:Actor"),))["ReturnValue"]
    vf = g.call(None, "GetVelocity", target_cls="Actor", target=far, pure=True, outs=(("ReturnValue", "struct:/Script/CoreUObject.Vector"),))["ReturnValue"]
    vp = g.call(None, "GetVelocity", target_cls="Actor", target=pawn, pure=True, outs=(("ReturnValue", "struct:/Script/CoreUObject.Vector"),))["ReturnValue"]
    sf = g.call("Math", "VSize", ins=(("A", "struct:/Script/CoreUObject.Vector"),), outs=(("ReturnValue", "real"),), pure=True, A=vf)["ReturnValue"]
    sp = g.call("Math", "VSize", ins=(("A", "struct:/Script/CoreUObject.Vector"),), outs=(("ReturnValue", "real"),), pure=True, A=vp)["ReturnValue"]
    return div(selF(sf, sp, isvalid(far)), "27.7778")
c18n = Chain(g, ci18["CastFailed"])
cn18 = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
c18n.then(cn18)
trip18 = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn18.out)["Result"]
cur18n = g.call_path(TRIPFN, "FBusTripInfo_GetCurrentStop", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                     outs=(("IsValid", "bool"), ("ReturnValue", RSWT)), pure=True, static_default="x", a=trip18)
pawnn = g.call("GS", "GetPlayerPawn", ins=(("PlayerIndex", "int"),), outs=(("ReturnValue", "obj:Actor"),), pure=True, PlayerIndex="0")["ReturnValue"]
setv(c18n, "tV", "real", fart_kmt(pawnn))
bcn18 = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", cur18n["ReturnValue"], (("RouteStopInfo", "obj:Object"),))
sposn = g.member_get(RSIa, "WorldPosition", V2a, bcn18["RouteStopInfo"])
farn = g.call(None, "GetAttachParentActor", target_cls="Actor", target=pawnn, pure=True, outs=(("ReturnValue", "obj:Actor"),))["ReturnValue"]
lfn = g.call(None, "K2_GetActorLocation", target_cls="Actor", target=farn, pure=True, outs=(("ReturnValue", "struct:/Script/CoreUObject.Vector"),))["ReturnValue"]
lpn = g.call(None, "K2_GetActorLocation", target_cls="Actor", target=pawnn, pure=True, outs=(("ReturnValue", "struct:/Script/CoreUObject.Vector"),))["ReturnValue"]
dn18 = selF(dist2(v2(lfn), sposn), dist2(v2(lpn), sposn), isvalid(farn))
setv(c18n, "tNum", "real", b2d(AND(AND(cur18n["IsValid"], lt(get("tV", "real"), "3")), le(dn18, "4000"))))
setv(c18n, "tStr", "string", cat(cat(i2s(rnd(get("tV", "real"))), " km/t"), selS(" *", "", cur18n["IsValid"])))

# 21 afgangstid fra det stop bussen holder ved (sek efter midnat, 0 hvis ikke ved et stop) - koereskaermen
cx = Chain(g, sw["21"])
cn = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
cx.then(cn)
trip = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn.out)["Result"]
cur21 = g.call_path(TRIPFN, "FBusTripInfo_GetCurrentStop", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                    outs=(("IsValid", "bool"), ("ReturnValue", RSWT)), pure=True, static_default="x", a=trip)
b21 = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", cur21["ReturnValue"], (("DepartureTime", "struct:/Script/CoreUObject.DateTime"),))
setv(cx, "tNum", "real", selF(secs_of_day(b21["DepartureTime"]), "0", cur21["IsValid"]))
setv(cx, "tStr", "string", d2s(get("tNum", "real")))

# 22 afgangstekst ved stoppet: planlagt afgang, og hvis klokken er over: "planlagt (nu)"
def hms(secs_real):
    t = rnd(secs_real)
    return cat(cat(cat(cat(pad2(idiv(t, "3600")), ":"), pad2(imod(idiv(t, "60"), "60"))), ":"), pad2(imod(t, "60")))
cx = Chain(g, sw["22"])
cn = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
cx.then(cn)
trip = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn.out)["Result"]
cur22 = g.call_path(TRIPFN, "FBusTripInfo_GetCurrentStop", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                    outs=(("IsValid", "bool"), ("ReturnValue", RSWT)), pure=True, static_default="x", a=trip)
b22 = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", cur22["ReturnValue"], (("DepartureTime", "struct:/Script/CoreUObject.DateTime"),))
setv(cx, "tV", "real", secs_of_day(b22["DepartureTime"]))
setv(cx, "tNum", "real", secs_of_day(world_datetime()))
sen = gt(sub(get("tNum", "real"), get("tV", "real")), "30")
setv(cx, "tStr", "string", selS(cat(cat(cat(hms(get("tV", "real")), " ("), hms(get("tNum", "real"))), ")"), hms(get("tV", "real")), sen))
setv(cx, "tNum", "real", b2d(sen))

NOT_ = lambda x: g.call("Math", "Not_PreBool", ins=(("A", "bool"),), outs=(("ReturnValue", "bool"),), pure=True, A=x)["ReturnValue"]
# 23 knap-tilstand: tKnapVal[VarIdx]
cx = Chain(g, sw["23"])
vi23 = it("VarIdx", "int", get("tVar", "int"))
setv(cx, "tNum", "real", "0")
b23 = g.branch(AND(ige(vi23, "0"), ilt(it("VarIdx", "int", get("tVar", "int")), arrlen("tKnapVal", "real"))))
cx.then(b23)
s23 = g.set("tNum", "real", it("tKnapVal", "real", it("VarIdx", "int", get("tVar", "int"))))
link(b23["then"], s23["execute"])
cx.to(s23["then"])
setv(cx, "tStr", "string", i2s(rnd(get("tNum", "real"))))

# 24 stopliste: VarIdx = raekke*10 + felt (1 navn, 2 ankomst sek, 3 findes 1/0, 4 afgang sek)
cx = Chain(g, sw["24"])
cn = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
cx.then(cn)
trip = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn.out)["Result"]
# rul: tKnapVal[RulGruppe] hvis den findes
rg = get("RulGruppe", "int")
setv(cx, "tT", "int", "0")
brg = g.branch(AND(ige(rg, "0"), ilt(get("RulGruppe", "int"), arrlen("tKnapVal", "real"))))
cx.then(brg)
srg = g.set("tT", "int", rnd(it("tKnapVal", "real", get("RulGruppe", "int"))))
link(brg["then"], srg["execute"])
j24 = g.set("tKi", "int", "0")
link(brg["else"], j24["execute"]); link(srg["then"], j24["execute"])
cx.to(j24["then"])
# base: 0 hvis spillets offset 0 er det stop vi viser som "naeste", ellers 1
o0_24 = g.call_path(TRIPFN, "FBusTripInfo_GetStopByIndexOffset", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"), ("Offset", "int")),
                    outs=(("IsValid", "bool"), ("ReturnValue", RSWT)), pure=True, static_default="x", a=trip, Offset="0")
bo0 = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", o0_24["ReturnValue"], (("StopIdent", "struct:/Script/RoadmapSystem.BusStopIdentifier"),))
bns = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", get("tNaesteStop", RSWT), (("StopIdent", "struct:/Script/RoadmapSystem.BusStopIdentifier"),))
base = M("SelectInt", (("A", "int"), ("B", "int"), ("bPickA", "bool")), (("ReturnValue", "int"),), A="0", B="1",
         bPickA=streq(stopnoegle(bo0["StopIdent"]), stopnoegle(bns["StopIdent"])))
# rul ikke laengere end listen: findes raekke 4 ikke ved denne rulning, saa ryk et trin tilbage (og gem det)
o4 = g.call_path(TRIPFN, "FBusTripInfo_GetStopByIndexOffset", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"), ("Offset", "int")),
                 outs=(("IsValid", "bool"), ("ReturnValue", RSWT)), pure=True, static_default="x", a=trip,
                 Offset=iadd(iadd(base, "4"), get("tT", "int")))
bclamp = g.branch(AND(NOT_(o4["IsValid"]), ige(get("tT", "int"), "1")))
cx.then(bclamp)
dec = g.set("tT", "int", isub(get("tT", "int"), "1"))
link(bclamp["then"], dec["execute"])
gem = g.arrfunc("Array_Set", "real", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                TargetArray=g.get("tKnapVal", "real[]"), Index=get("RulGruppe", "int"), Item=i2d(get("tT", "int")), bSizeToFit=True)
link(dec["then"], gem["execute"])
jc = g.set("tKi", "int", "0")
link(bclamp["else"], jc["execute"]); link(gem["then"], jc["execute"])
cx.to(jc["then"])
vi24 = imod(it("VarIdx", "int", get("tVar", "int")), "100")
raekke = idiv(vi24, "10")
raa24 = ige(it("VarIdx", "int", get("tVar", "int")), "100")
setv(cx, "tKi", "int", M("SelectInt", (("A", "int"), ("B", "int"), ("bPickA", "bool")), (("ReturnValue", "int"),),
                          A=iadd(isub(idiv(imod(it("VarIdx", "int", get("tVar", "int")), "100"), "10"), "1"),
                                 M("SelectInt", (("A", "int"), ("B", "int"), ("bPickA", "bool")), (("ReturnValue", "int"),),
                                   A="0", B=get("tT", "int"), bPickA=ige(it("VarIdx", "int", get("tVar", "int")), "200"))),
                          B=iadd(iadd(base, raekke), get("tT", "int")), bPickA=raa24))
st24 = g.call_path(TRIPFN, "FBusTripInfo_GetStopByIndexOffset", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"), ("Offset", "int")),
                   outs=(("IsValid", "bool"), ("ReturnValue", RSWT)), pure=True, static_default="x", a=trip, Offset=get("tKi", "int"))
b24 = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", st24["ReturnValue"],
                     (("ArrivalTime", "struct:/Script/CoreUObject.DateTime"), ("DepartureTime", "struct:/Script/CoreUObject.DateTime"),
                      ("StopIdent", "struct:/Script/RoadmapSystem.BusStopIdentifier")))
gyldig = AND(st24["IsValid"], ige(get("tKi", "int"), "0"))
sw24 = g.switch_int(imod(it("VarIdx", "int", get("tVar", "int")), "10"), 5)
cx.then(sw24, outpin=None)
f1 = g.set("tStr", "string", selS(stopnavn(b24["StopIdent"]), "", gyldig)); link(sw24["1"], f1["execute"])
f1b = g.set("tNum", "real", "0"); link(f1["then"], f1b["execute"])
f2 = g.set("tNum", "real", selF(secs_of_day(b24["ArrivalTime"]), "0", gyldig)); link(sw24["2"], f2["execute"])
f2b = g.set("tStr", "string", d2s(get("tNum", "real"))); link(f2["then"], f2b["execute"])
f3 = g.set("tNum", "real", b2d(gyldig)); link(sw24["3"], f3["execute"])
f3b = g.set("tStr", "string", i2s(rnd(get("tNum", "real")))); link(f3["then"], f3b["execute"])
f4 = g.set("tNum", "real", selF(secs_of_day(b24["DepartureTime"]), "0", gyldig)); link(sw24["4"], f4["execute"])
f4b = g.set("tStr", "string", d2s(get("tNum", "real"))); link(f4["then"], f4b["execute"])


# ---------- v27: login ----------
# Login-mailen ligger IKKE i git: skriv den i login_email.txt ved siden af dette script (den fil er i .gitignore)
import os as _os
_lf = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "login_email.txt")
LOGIN_EMAIL = open(_lf, encoding="utf-8").read().strip() if _os.path.exists(_lf) else "chauffoer@eksempel.dk"
LOGIN_KODE = "1234"
def txt_at(idx):
    return it("tTxt", "string", idx)
def loginok():
    return AND(streq(trim(txt_at("0")), LOGIN_EMAIL),
               S("EqualEqual_StrStr", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=txt_at("1"), B=LOGIN_KODE))
PRIKKER = "•" * 40
# 25 tekstfelt: VarIdx = feltgruppe*100 + plads*10 + maske(1 = prikker). Viser blinkende markoer i det aktive felt
cx = Chain(g, sw["25"])
v25 = lambda: it("VarIdx", "int", get("tVar", "int"))
setv(cx, "tT", "int", imod(idiv(v25(), "10"), "10"))
setv(cx, "tKi", "int", idiv(v25(), "100"))
raw25 = txt_at(get("tT", "int"))
n25 = S("Len", (("S", "string"),), (("ReturnValue", "int"),), S=txt_at(get("tT", "int")))
vist = selS(S("GetSubstring", (("SourceString", "string"), ("StartIndex", "int"), ("Length", "int")), SourceString=PRIKKER, StartIndex="0", Length=n25),
            raw25, ieq(imod(v25(), "10"), "1"))
aktiv = AND(ilt(get("tKi", "int"), arrlen("tKnapVal", "real")),
            ieq(rnd(it("tKnapVal", "real", get("tKi", "int"))), get("tT", "int")))
tnow = now()
blink = lt(sub(tnow, floor64(tnow)), "0.5")
setv(cx, "tStr", "string", cat(vist, selS("|", "", AND(AND(aktiv, blink), M("Not_PreBool", (("A", "bool"),), (("ReturnValue", "bool"),), A=ieq(imod(v25(), "10"), "2"))))))
setv(cx, "tNum", "real", i2d(S("Len", (("S", "string"),), (("ReturnValue", "int"),), S=txt_at(get("tT", "int")))))
# 26 login ok (1/0)
cx = Chain(g, sw["26"])
setv(cx, "tNum", "real", b2d(loginok()))
setv(cx, "tStr", "string", i2s(rnd(get("tNum", "real"))))
# 27 maerke (tag) paa bussen: VarPath = navnet
cx = Chain(g, sw["27"])
ca27 = g.cast(bus_actor0(), "Actor")
cx.then(ca27)
har27 = g.call(None, "ActorHasTag", target_cls="Actor", target=ca27.out, pure=True, ins=(("Tag", "name"),), outs=(("ReturnValue", "bool"),),
               Tag=S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),), InString=it("VarPath", "string", get("tVar", "int"))))["ReturnValue"]
s27 = g.set("tNum", "real", b2d(har27))
link(ca27["then"], s27["execute"])
f27 = g.set("tNum", "real", "0")
link(ca27["CastFailed"], f27["execute"])
s27b = g.set("tStr", "string", i2s(rnd(get("tNum", "real"))))
link(s27["then"], s27b["execute"]); link(f27["then"], s27b["execute"])
# 28 rute: 1 antal stop, 2 turnummer
cx = Chain(g, sw["28"])
cn28 = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
cx.then(cn28)
trip28 = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn28.out)["Result"]
sidste28 = g.call_path(TRIPFN, "FBusTripInfo_GetLastStopIndex", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                       outs=(("ReturnValue", "int"),), pure=True, static_default="x", a=trip28)["ReturnValue"]
bt28 = g.break_struct("/Script/Fernbus.BusTripInfo", "BusTripInfo", trip28, (("TourIdent", "struct:/Script/Fernbus.TourIdentifier"),))
bti28 = g.break_struct("/Script/Fernbus.TourIdentifier", "TourIdentifier", bt28["TourIdent"], (("Name", "name"),))
turnavn = g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True, InName=bti28["Name"])["ReturnValue"]
er2 = ieq(it("VarIdx", "int", get("tVar", "int")), "2")
setv(cx, "tStr", "string", selS(turnavn, i2s(iadd(sidste28, "1")), er2))
setv(cx, "tNum", "real", selF(s2d(get("tStr", "string")), i2d(iadd(sidste28, "1")), er2))
# 30 billet paa en af spillets billetknapper (Main): VarIdx 1 navn, 2 kort navn, 3 findes
TBTN = "/Script/UMG.WidgetBlueprintGeneratedClass'/Game/UI/Berlin/Menu/Atron/NewAtron/Widgets/UMG_TB_NAtron_Ticket_Button.UMG_TB_NAtron_Ticket_Button_C'"
PTK = "/Script/CoreUObject.Class'/Script/Fernbus.PassengerTicket'"
cx = Chain(g, sw["30"])
setv(cx, "tPath", "string", it("VarPath", "string", get("tVar", "int")))
callev(cx, "MFind")
ctb = g.cast(get("tW", "obj:Widget"), "", disp="UMG TB NAtron Ticket Button", path=TBTN)
cx.then(ctb)
tk = g.member_get(TBTN, "Ticket", "obj:Object", ctb.out)
lnavn = t2s(g.member_get(PTK, "LongDisplayName", "text", tk))
knavn = t2s(g.member_get(PTK, "ShortDisplayName", "text", g.member_get(TBTN, "Ticket", "obj:Object", ctb.out)))
fin30 = isvalid(g.member_get(TBTN, "Ticket", "obj:Object", ctb.out))
vi30 = it("VarIdx", "int", get("tVar", "int"))
grp30 = g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True,
              InName=g.member_get(TBTN, "TicketGroup", "name", ctb.out))["ReturnValue"]
katok = AND(S("NotEqual_StrStr", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=grp30, B="None"),
            S("NotEqual_StrStr", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=grp30, B=""))
erkat = ige(vi30, "4")
s30 = g.set("tStr", "string", selS(selS(grp30, "", katok), selS(selS(lnavn, knavn, ieq(vi30, "1")), "", fin30), erkat))
link(ctb["then"], s30["execute"])
s30b = g.set("tNum", "real", b2d(selB(katok, isvalid(g.member_get(TBTN, "Ticket", "obj:Object", ctb.out)), erkat)))
link(s30["then"], s30b["execute"])
f30 = g.set("tStr", "string", "")
link(ctb["CastFailed"], f30["execute"])
f30b = g.set("tNum", "real", "0")
link(f30["then"], f30b["execute"])
# 31 pause/vagt: 1 sek til afgang fra stoppet bussen holder ved, 2 er foerste stop (1/0), 3 pause holdt (min),
#                4 vagtens laengde (min, fra login-maerket ML_), 5 stop nr. (aktuelt stopindeks)
cx = Chain(g, sw["31"])
setv(cx, "tTagPre", "string", "ML_")
callev(cx, "MTagGet")
cn31 = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
cx.then(cn31)
trip31 = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn31.out)["Result"]
cur31 = g.call_path(TRIPFN, "FBusTripInfo_GetCurrentStop", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                    outs=(("IsValid", "bool"), ("ReturnValue", RSWT)), pure=True, static_default="x", a=trip31)
b31 = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", cur31["ReturnValue"], (("DepartureTime", "struct:/Script/CoreUObject.DateTime"),))
idx31 = g.call_path(TRIPFN, "FBusTripInfo_GetCurrentStopIndex", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                    outs=(("ReturnValue", "int"),), pure=True, static_default="x", a=trip31)["ReturnValue"]
nu31 = secs_of_day(world_datetime())
til31 = selF(M("FMax", D2, A=sub(secs_of_day(b31["DepartureTime"]), nu31), B="0"), "0", cur31["IsValid"])
vagt31 = selF(div(M("FMax", D2, A=sub(secs_of_day(world_datetime()), get("tTagVal", "real")), B="0"), "60"), "0", gt(get("tTagVal", "real"), "0"))
sw31 = g.switch_int(it("VarIdx", "int", get("tVar", "int")), 6)
cx.then(sw31, outpin=None)
for pin, val in (("1", til31), ("2", b2d(AND(cur31["IsValid"], ieq(idx31, "0")))), ("3", div(get("tPauseSum", "real"), "60")),
                 ("4", vagt31), ("5", i2d(M("Max", I2, (("ReturnValue", "int"),), A=idx31, B="0"))), ("Default", "0")):
    n_ = g.set("tNum", "real", val); link(sw31[pin], n_["execute"])
    n2 = g.set("tStr", "string", i2s(rnd(get("tNum", "real")))); link(n_["then"], n2["execute"])
f31 = g.set("tNum", "real", "0"); link(cn31["CastFailed"], f31["execute"])
# 32 tal gemt som maerke paa bussen: VarPath = prefix (fx "MB_" solgte billetter)
cx = Chain(g, sw["32"])
setv(cx, "tTagPre", "string", it("VarPath", "string", get("tVar", "int")))
callev(cx, "MTagGet")
setv(cx, "tNum", "real", get("tTagVal", "real"))
setv(cx, "tStr", "string", i2s(rnd(get("tNum", "real"))))
# 33 tekst gemt som maerke paa bussen: VarPath = prefix (fx "SKL:" skiltets linje)
cx = Chain(g, sw["33"])
setv(cx, "tTagPre", "string", it("VarPath", "string", get("tVar", "int")))
callev(cx, "MTagGet")
setv(cx, "tStr", "string", S("RightChop", (("SourceString", "string"), ("Count", "int")), SourceString=get("tTagFound", "string"),
                             Count=S("Len", (("S", "string"),), (("ReturnValue", "int"),), S=get("tTagPre", "string"))))
setv(cx, "tNum", "real", s2d(get("tStr", "string")))
# 34 FEJLSOEG skilt: 1 antal BoardComputere, 2 BC aktiv, 3 BC linje|dest, 4 BusLogic skiltdata, 5 BusLogic fundet
BCCLS0 = "/Script/Engine.BlueprintGeneratedClass'/Game/Gameplay/Vehicles/Common/BP_BoardComputer_TheBus_NAtron.BP_BoardComputer_TheBus_NAtron_C'"
cx = Chain(g, sw["34"])
ga34 = g.call("GS", "GetAllActorsOfClass", ins=(("ActorClass", "class:/Script/Engine.Actor"),), outs=(("OutActors", "obj:Actor[]"),))
ga34["ActorClass"].defobj = "/Game/Gameplay/Vehicles/Common/BP_BoardComputer_TheBus_NAtron.BP_BoardComputer_TheBus_NAtron_C"
cx.then(ga34)
n34 = g.arrfunc("Array_Length", "obj:Actor", ins=[("TargetArray", "E[]")], outs=[("ReturnValue", "int")], pure=True, TargetArray=ga34["OutActors"])["ReturnValue"]
setv(cx, "tStr", "string", cat("BC=", i2s(n34)))
setv(cx, "tNum", "real", "0")
vi34 = lambda: it("VarIdx", "int", get("tVar", "int"))
sw34 = g.switch_int(vi34(), 6)
cx.then(sw34, outpin=None)
c34 = g.cast(g.item_of(ga34["OutActors"], "obj:Actor", "0"), "", disp="BP Board Computer The Bus NAtron", path=BCCLS0)
link(sw34["2"], c34["execute"])
a34 = g.member_get(BCCLS0, "MoviaSkiltAktiv", "bool", c34.out)
l34 = g.member_get(BCCLS0, "MoviaSkiltL", "string", c34.out)
d34 = g.member_get(BCCLS0, "MoviaSkiltD", "string", c34.out)
s34 = g.set("tStr", "string", cat(cat(cat("A=", i2s(rnd(b2d(a34)))), cat(" L=", l34)), cat(" D=", d34)))
link(c34["then"], s34["execute"])
BLCLS = "/Script/Engine.BlueprintGeneratedClass'/Game/Gameplay/Vehicles/BusBase/BusLogic/BP_BusLogic.BP_BusLogic_C'"
cba = g.cast(bus_actor0(), "Actor")
link(sw34["4"], cba["execute"])
gc34 = g.call(None, "GetComponentByClass", target_cls="Actor", target=cba.out, ins=(("ComponentClass", "class:/Script/Engine.ActorComponent"),),
              outs=(("ReturnValue", "obj:/Script/Engine.ActorComponent"),))
gc34["ComponentClass"].defobj = "/Game/Gameplay/Vehicles/BusBase/BusLogic/BP_BusLogic.BP_BusLogic_C"
link(cba["then"], gc34["execute"])
cbl = g.cast(gc34["ReturnValue"], "", disp="BP Bus Logic", path=BLCLS)
link(gc34["then"], cbl["execute"])
dd = g.call_path(BLCLS, "Get Destination Display Data NEW", ins=(), outs=(("Line Number", "string"), ("Destination", "string[]")), pure=False, target=cbl.out)
link(cbl["then"], dd["execute"])
s34b = g.set("tStr", "string", cat(cat("BL: ", dd["Line Number"]), cat(" / ", g.item_of(dd["Destination"], "string", "0"))))
link(dd["then"], s34b["execute"])
f34 = g.set("tStr", "string", "BL: ikke fundet")
link(cbl["CastFailed"], f34["execute"])
# ---------- v40 skift rute: hjaelpere ----------
from bpgen import Node as _Node
BTIP = "/Script/Fernbus.BusTripInfo"
BTI = "struct:" + BTIP
DTS = "struct:/Script/CoreUObject.DateTime"
TSP = "struct:/Script/CoreUObject.Timespan"
TWT = "struct:/Script/Fernbus.TourWithTime"
TOURC = "/Script/CoreUObject.Class'/Script/Fernbus.Tour'"
LRC = "/Script/CoreUObject.Class'/Script/Fernbus.LineRoute'"
OPCLS = "/Script/CoreUObject.Class'/Script/Fernbus.OperatingPlan'"
OPT_ = "obj:/Script/Fernbus.OperatingPlan"
BSI_ = "struct:/Script/RoadmapSystem.BusStopIdentifier"
TMLGI = "/Script/CoreUObject.Class'/Script/Fernbus.TMLGameInstance'"
MAPB = "/Script/CoreUObject.Class'/Script/Fernbus.MapBase'"
MISSFN = "/Script/Engine.BlueprintGeneratedClass'/Game/Gameplay/Mission/BP_MissionFunctions.BP_MissionFunctions_C'"
MISSC = "/Script/Engine.BlueprintGeneratedClass'/Game/Gameplay/Mission/BP_TheBus_Mission.BP_TheBus_Mission_C'"
VSTOP = "/Script/CoreUObject.Class'/Script/RoadmapSystem.VehicleStopBase'"
NOTb = lambda x: g.call("Math", "Not_PreBool", ins=(("A", "bool"),), outs=(("ReturnValue", "bool"),), pure=True, A=x)["ReturnValue"]
def n2s(n): return g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True, InName=n)["ReturnValue"]
def s2n(s): return S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),), InString=s)
def ffloor(x): return M("FFloor", (("A", "real"),), (("ReturnValue", "int"),), A=x)
def imax(a, b): return M("Max", I2, (("ReturnValue", "int"),), A=a, B=b)
def RG(i): return it("RuteGrp", "int", str(i))
def kv(i):
    return selF(it("tKnapVal", "real", RG(i)), "0", AND(ige(RG(i), "0"), ilt(RG(i), arrlen("tKnapVal", "real"))))
def kvi(i): return rnd(kv(i))
def ARRSET(var, elem, idx, val):
    return g.arrfunc("Array_Set", elem, ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                     TargetArray=g.get(var, elem + "[]"), Index=idx, Item=val, bSizeToFit=True)
def ARRADD(var, elem, val):
    return g.arrfunc("Array_Add", elem, ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                     TargetArray=g.get(var, elem + "[]"), NewItem=val)
def ARRINS(var, elem, val, idx):
    return g.arrfunc("Array_Insert", elem, ins=[("TargetArray", "E[]"), ("NewItem", "E"), ("Index", "int")],
                     TargetArray=g.get(var, elem + "[]"), NewItem=val, Index=idx)
def ARRCLR(var, elem):
    return g.arrfunc("Array_Clear", elem, ins=[("TargetArray", "E[]")], TargetArray=g.get(var, elem + "[]"))
def setkv(ch, i, val):
    return ch.then(ARRSET("tKnapVal", "real", RG(i), val))
def hhmm(sek):
    si = ffloor(sek)
    return cat(cat(pad2(imod(idiv(si, "3600"), "24")), ":"), pad2(imod(idiv(si, "60"), "60")))
def dsek(sek):
    """sek (sek efter midnat) minus klokken nu, foldet ind i [-12t, 12t)"""
    raa = sub(sek, secs_of_day(world_datetime()))
    return selF(add(raa, "86400"), selF(sub(raa, "86400"), raa, ge(raa, "43200")), lt(raa, "-43200"))
def tb(trip, felter): return g.break_struct(BTIP, "BusTripInfo", trip, felter)
def trip_stops(trip): return tb(trip, (("Stops", RSWT + "[]"),))["Stops"]
def trip_linje(trip):
    return n2s(g.member_get(LRC, "Line", "name", tb(trip, (("Route", "obj:/Script/Fernbus.LineRoute"),))["Route"]))
def tw_tour(): return g.break_struct("/Script/Fernbus.TourWithTime", "TourWithTime", get("tRTourCur", TWT), (("Tour", "obj:/Script/Fernbus.Tour"),))["Tour"]
def tur_linje(): return n2s(g.member_get(TOURC, "Line", "name", tw_tour()))
def tur_kurs(): return n2s(g.member_get(TOURC, "Name", "name", tw_tour()))
def trip_kurs(trip):
    return n2s(g.member_get(TOURC, "Name", "name", tb(trip, (("Tour", "obj:/Script/Fernbus.Tour"),))["Tour"]))
def rs_felt(stopstruct, felt, spec):
    return g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", stopstruct, ((felt, spec),))[felt]
def rs_navn(stopstruct): return stopnavn(rs_felt(stopstruct, "StopIdent", BSI_))
def rs_afg(stopstruct): return secs_of_day(rs_felt(stopstruct, "DepartureTime", DTS))
def r_stop_at(trip, idx): return g.item_of(trip_stops(trip), RSWT, idx)
def nstops(trip):
    return g.arrfunc("Array_Length", RSWT, ins=[("TargetArray", "E[]")], outs=[("ReturnValue", "int")], pure=True, TargetArray=trip_stops(trip))["ReturnValue"]
def sidste_navn(trip):
    last = g.call_path(TRIPFN, "FBusTripInfo_GetLastStop", ins=(("a", BTI),), outs=(("IsValid", "bool"), ("ReturnValue", RSWT)),
                       pure=True, static_default="x", a=trip)
    return rs_navn(last["ReturnValue"])
def ts_sek(sek):
    return g.call("Math", "FromSeconds", ins=(("Seconds", "real"),), outs=(("ReturnValue", TSP),), pure=True, Seconds=sek)["ReturnValue"]
def dt_plus(dt, sek):
    return g.call("Math", "Add_DateTimeTimespan", ins=(("A", DTS), ("B", TSP)), outs=(("ReturnValue", DTS),), pure=True, A=dt, B=ts_sek(sek))["ReturnValue"]

# 35 skift rute: VarIdx  r*10+f (raekke 1-8: 1 tid, 2 linje+kurs, 3 til, 4 om X min, 5 findes, 6 valgt)
#                        100+r*10+f (stop 1-8: 1 navn, 2 tid, 3 findes, 4 valgt, 5 maerke)
#                        200 nedtaelling, 201 valgt tur, 202 starttid, 203 status, 204 antal, 205 titel, 206 undertitel, 207 antal stop
cx = Chain(g, sw["35"])
VI = lambda: it("VarIdx", "int", get("tVar", "int"))
setv(cx, "tStr", "string", "")
setv(cx, "tNum", "real", "0")
# hurtig udgang: raekker/stop laeses kun mens menuen er aaben (sparer meget arbejde hvert billede)
b200 = g.branch(ige(VI(), "200"))
cab35 = g.cast(bus_actor0(), "Actor")
cx.then(cab35)
aab35 = g.call(None, "ActorHasTag", target_cls="Actor", target=cab35.out, pure=True, ins=(("Tag", "name"),), outs=(("ReturnValue", "bool"),), Tag="MoviaRute")["ReturnValue"]
bopen = g.branch(OR(aab35, ige(VI(), "200")))
cx.then(bopen)
cx.then(b200)
# ---- raekker / stop
b100 = g.branch(ige(VI(), "100"))
link(b200["else"], b100["execute"])
# raekker
cr = Chain(g, b100["else"])
setv(cr, "tRQ", "int", iadd(isub(idiv(VI(), "10"), "1"), kvi(0)))
brf = g.branch(ilt(get("tRQ", "int"), arrlen("tRDep", "real")))
cr.then(brf)
swr = g.switch_int(imod(VI(), "10"), 7)
link(brf["then"], swr["execute"])
Q = lambda: get("tRQ", "int")
setv(Chain(g, swr["1"]), "tStr", "string", hhmm(it("tRDep", "real", Q())))
setv(Chain(g, swr["2"]), "tStr", "string", it("tRTxt", "string", Q()))
setv(Chain(g, swr["3"]), "tStr", "string", it("tRTil", "string", Q()))
c4 = Chain(g, swr["4"])
mins = rnd(div(dsek(it("tRDep", "real", Q())), "60"))
setv(c4, "tStr", "string", selS("nu", cat(cat("om ", i2s(mins)), " min"), M("LessEqual_IntInt", I2, (("ReturnValue", "bool"),), A=mins, B="0")))
setv(Chain(g, swr["5"]), "tNum", "real", "1")
setv(Chain(g, swr["6"]), "tNum", "real", b2d(ieq(Q(), kvi(1))))
# stop
cs = Chain(g, b100["then"])
VS = lambda: isub(VI(), "100")
setv(cs, "tRQ", "int", iadd(isub(idiv(VS(), "10"), "1"), kvi(2)))
bsf = g.branch(ilt(get("tRQ", "int"), arrlen("tRStDep", "real")))
cs.then(bsf)
sws = g.switch_int(imod(VS(), "10"), 6)
link(bsf["then"], sws["execute"])
Q2 = lambda: M("Multiply_IntInt", I2, (("ReturnValue", "int"),), A=Q(), B="2")
setv(Chain(g, sws["1"]), "tStr", "string", it("tRSt", "string", Q2()))
setv(Chain(g, sws["2"]), "tStr", "string", it("tRSt", "string", iadd(Q2(), "1")))
setv(Chain(g, sws["3"]), "tNum", "real", "1")
setv(Chain(g, sws["4"]), "tNum", "real", b2d(ieq(Q(), kvi(3))))
setv(Chain(g, sws["5"]), "tStr", "string", selS("start", selS("springes over", "", ilt(Q(), kvi(3))), ieq(Q(), "0")))
# ---- 200+
swx = g.switch_int(isub(VI(), "200"), 9)
link(b200["then"], swx["execute"])
# 200 nedtaelling til afgang fra startstoppet (maerket MR_), -1 hvis intet
c0 = Chain(g, swx["0"])
setv(c0, "tTagPre", "string", "MR_")
callev(c0, "MTagGet")
setv(c0, "tNum", "real", selF(dsek(get("tTagVal", "real")), "-1", S("NotEqual_StrStr", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=get("tTagFound", "string"), B="")))
DD = lambda: imax(ffloor(get("tNum", "real")), "0")
mmss = cat(i2s(idiv(DD(), "60")), cat(":", pad2(imod(DD(), "60"))))
hmmss = cat(i2s(idiv(DD(), "3600")), cat(":", cat(pad2(imod(idiv(DD(), "60"), "60")), cat(":", pad2(imod(DD(), "60"))))))
setv(c0, "tStr", "string", selS(hmmss, mmss, ige(DD(), "3600")))
# 201 valgt tur
c1 = Chain(g, swx["1"])
b1 = g.branch(ilt(kvi(1), arrlen("tRDep", "real")))
c1.then(b1)
setv(Chain(g, b1["then"]), "tStr", "string", cat(hhmm(it("tRDep", "real", kvi(1))), cat(" · ", it("tRTxt", "string", kvi(1)))))
# 202 starttid (valgt stop)
c2 = Chain(g, swx["2"])
b2 = g.branch(ilt(kvi(3), arrlen("tRStDep", "real")))
c2.then(b2)
setv(Chain(g, b2["then"]), "tStr", "string", it("tRSt", "string", iadd(M("Multiply_IntInt", I2, (("ReturnValue", "int"),), A=kvi(3), B="2"), "1")))
setv(Chain(g, swx["3"]), "tStr", "string", get("tRStat", "string"))
c4x = Chain(g, swx["4"])
setv(c4x, "tNum", "real", i2d(arrlen("tRDep", "real")))
setv(c4x, "tStr", "string", i2s(arrlen("tRDep", "real")))
setv(Chain(g, swx["5"]), "tStr", "string", get("tRTitel", "string"))
setv(Chain(g, swx["6"]), "tStr", "string", get("tRUnder", "string"))
c7x = Chain(g, swx["7"])
setv(c7x, "tNum", "real", i2d(arrlen("tRStDep", "real")))
c8x = Chain(g, swx["8"])
b8x = g.branch(ilt(kvi(3), arrlen("tRStDep", "real")))
c8x.then(b8x)
setv(Chain(g, b8x["then"]), "tStr", "string", it("tRSt", "string", M("Multiply_IntInt", I2, (("ReturnValue", "int"),), A=kvi(3), B="2")))

# 29 alder: sekunder siden skaermen blev vist
cx = Chain(g, sw["29"])
setv(cx, "tNum", "real", sub(now(), get("tStart", "real")))
setv(cx, "tStr", "string", d2s(get("tNum", "real")))

# =========================================================
# MTrip: tVar -> tDist (meter til naeste stop), tM1 (min til naeste stop), tMi (min til stop VarIdx)
# =========================================================
g.next_col()
ev = g.custom_event("MTrip")
ch = Chain(g, ev["then"])
setv(ch, "tDist", "real", "0")
setv(ch, "tM1", "real", "0")
setv(ch, "tMi", "real", "0")
ci = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG Interior Display Base", path=INTERIOR)
ch.then(ci)
bl = g.member_get(INTERIOR, "Bus Logic", "obj:Object", ci.out)
info = g.member_get(BUSLOGIC, "Bus Trip Info", "struct:/Script/Fernbus.BusTripInfo", bl)
def stop_at(off):
    st = g.call_path(TRIPFN, "FBusTripInfo_GetStopByIndexOffset", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"), ("Offset", "int")),
                     outs=(("IsValid", "bool"), ("ReturnValue", "struct:/Script/Fernbus.RouteStopWithTime")), pure=True,
                     static_default="x", a=info, Offset=off)
    return g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", st["ReturnValue"],
                          (("ArrivalTime", "struct:/Script/CoreUObject.DateTime"), ("RouteStopInfo", "obj:Object")))
def mins(br):
    span = g.call("Math", "Subtract_DateTimeDateTime", ins=(("A", "struct:/Script/CoreUObject.DateTime"), ("B", "struct:/Script/CoreUObject.DateTime")),
                  outs=(("ReturnValue", "struct:/Script/CoreUObject.Timespan"),), pure=True, A=br["ArrivalTime"], B=world_datetime())["ReturnValue"]
    return g.call("Math", "GetTotalMinutes", ins=(("A", "struct:/Script/CoreUObject.Timespan"),), outs=(("ReturnValue", "real"),), pure=True, A=span)["ReturnValue"]
b1 = stop_at("1")
setv(ch, "tM1", "real", mins(b1))
bi = stop_at(it("VarIdx", "int", get("tVar", "int")))
setv(ch, "tMi", "real", mins(bi))
pos = g.member_get("/Script/CoreUObject.Class'/Script/Fernbus.RouteStopInfo'", "WorldPosition", "struct:/Script/CoreUObject.Vector2D", b1["RouteStopInfo"])
bus = g.member_get(INTERIOR, "Bus", "obj:Object", ci.out)
loc = g.call_path("/Script/CoreUObject.Class'/Script/Engine.Actor'", "K2_GetActorLocation", ins=(), outs=(("ReturnValue", "struct:/Script/CoreUObject.Vector"),), pure=True, target=bus)["ReturnValue"]
loc2 = g.call("Math", "Conv_VectorToVector2D", ins=(("InVector", "struct:/Script/CoreUObject.Vector"),), outs=(("ReturnValue", "struct:/Script/CoreUObject.Vector2D"),), pure=True, InVector=loc)["ReturnValue"]
dist = g.call("Math", "Distance2D", ins=(("V1", "struct:/Script/CoreUObject.Vector2D"), ("V2", "struct:/Script/CoreUObject.Vector2D")), outs=(("ReturnValue", "real"),), pure=True, V1=loc2, V2=pos)["ReturnValue"]
setv(ch, "tDist", "real", div(dist, "100"))

# =========================================================
# MCond: tJ -> tCond
# =========================================================
g.next_col()
ev = g.custom_event("MCond")
ch = Chain(g, ev["then"])
J = lambda: get("tJ", "int")
setv(ch, "tVar", "int", it("CVar", "int", J()))
callev(ch, "MRead")
setv(ch, "tV", "real", add(mul(get("tNum", "real"), it("CA", "real", J())), it("CB", "real", J())))
bm = g.branch(gt(it("CM", "real", J()), "0"))
ch.then(bm)
cmv = it("CM", "real", J())
tv = get("tV", "real")
modset = g.set("tV", "real", sub(tv, mul(floor64(div(tv, cmv)), cmv)))
link(bm["then"], modset["execute"])
sw = g.switch_int(it("CKind", "int", J()), 3)
link(bm["else"], sw["execute"])
link(modset["then"], sw["execute"])
k0 = g.set("tCond", "bool", AND(ge(get("tV", "real"), it("CLo", "real", J())), le(get("tV", "real"), it("CHi", "real", J()))))
k1 = g.set("tCond", "bool", streq(get("tStr", "string"), it("CStr", "string", J())))
k2 = g.set("tCond", "bool", contains(get("tStr", "string"), it("CStr", "string", J())))
kd = g.set("tCond", "bool", False)
for pinname, node in (("0", k0), ("1", k1), ("2", k2), ("Default", kd)):
    link(sw[pinname], node["execute"])
neg = g.set("tCond", "bool", neqb(get("tCond", "bool"), it("CNeg", "bool", J())))
for node in (k0, k1, k2, kd):
    link(node["then"], neg["execute"])

# =========================================================
# MEval: tR -> tAny
# =========================================================
g.next_col()
ev = g.custom_event("MEval")
ch = Chain(g, ev["then"])
R = lambda: get("tR", "int")
setv(ch, "tAny", "bool", False)
setv(ch, "tOK", "bool", False)
b0 = g.branch(ieq(it("RCount", "int", R()), "0"))
ch.then(b0, outpin="then")
setv(ch, "tAny", "bool", True)
st = it("RStart", "int", R())
fl = g.forloop(st, isub(iadd(it("RStart", "int", R()), it("RCount", "int", R())), "1"))
link(b0["else"], fl["execute"])
body = Chain(g, fl["LoopBody"])
setv(body, "tJ", "int", fl["Index"])
bn = g.branch(it("CNew", "bool", J()))
body.then(bn, outpin="then")
setv(body, "tAny", "bool", OR(get("tAny", "bool"), get("tOK", "bool")))
okt = setv(body, "tOK", "bool", True)
mc = g.call(None, "MCond", selfctx=True)
link(okt["then"], mc["execute"])
link(bn["else"], mc["execute"])
body.to(mc["then"])
setv(body, "tOK", "bool", AND(get("tOK", "bool"), get("tCond", "bool")))
done = Chain(g, fl["Completed"])
setv(done, "tAny", "bool", OR(get("tAny", "bool"), get("tOK", "bool")))

# =========================================================
# MFmt: tVar, fA, fB, fM, fFmt -> tRes
# =========================================================
g.next_col()
ev = g.custom_event("MFmt")
ch = Chain(g, ev["then"])
callev(ch, "MRead")
setv(ch, "tV", "real", add(mul(get("tNum", "real"), get("fA", "real")), get("fB", "real")))
bm = g.branch(gt(get("fM", "real"), "0"))
ch.then(bm)
tv, fm = get("tV", "real"), get("fM", "real")
modset = g.set("tV", "real", sub(tv, mul(floor64(div(tv, fm)), fm)))
link(bm["then"], modset["execute"])
sw = g.switch_int(get("fFmt", "int"), 8)
link(bm["else"], sw["execute"])
link(modset["then"], sw["execute"])
V = lambda: get("tV", "real")
f0 = g.set("tRes", "string", get("tStr", "string"))
f1 = g.set("tRes", "string", i2s(rnd(V())))
f2 = g.set("tRes", "string", d2s(div(i2d(rnd(mul(V(), "10"))), "10")))
f3 = g.set("tRes", "string", cat(selS("+", "", ge(V(), "0.5")), i2s(rnd(V()))))
for pinname, node in (("0", f0), ("1", f1), ("2", f2), ("3", f3), ("Default", f1)):
    link(sw[pinname], node["execute"])
ft = g.set("tT", "int", iabs(rnd(V())))
link(sw["4"], ft["execute"])
link(sw["5"], ft["execute"])
T_ = lambda: get("tT", "int")
f45 = g.set("tRes", "string", cat(cat(cat(selS("-", "", lt(V(), "-0.5")), pad2(idiv(T_(), "60"))), ":"), pad2(imod(T_(), "60"))))
link(ft["then"], f45["execute"])
# 6 m:ss med fortegn (+0:16 / -2:48)
ft6 = g.set("tT", "int", iabs(rnd(V())))
link(sw["6"], ft6["execute"])
f6 = g.set("tRes", "string", cat(cat(cat(selS("+", selS("-", "", lt(V(), "-0.5")), gt(V(), "0.5")), i2s(idiv(T_(), "60"))), ":"), pad2(imod(T_(), "60"))))
link(ft6["then"], f6["execute"])
# 7 hh:mm:ss (fra sekunder)
ft7 = g.set("tT", "int", iabs(rnd(V())))
link(sw["7"], ft7["execute"])
f7 = g.set("tRes", "string", cat(cat(cat(cat(pad2(idiv(T_(), "3600")), ":"), pad2(imod(idiv(T_(), "60"), "60"))), ":"), pad2(imod(T_(), "60"))))
link(ft7["then"], f7["execute"])

# =========================================================
# MApply: tR, tAny
# =========================================================
g.next_col()
ev = g.custom_event("MApply")
ch = Chain(g, ev["then"])
ACT = lambda: it("RAction", "int", R())
DOIT = lambda: OR(get("tAny", "bool"), it("RHasEllers", "bool", R()))
# v27 klik: tryk paa en af spillets knapper (On Clicked) i det oejeblik betingelsen BLIVER sand
NBTN = "/Script/UMG.WidgetBlueprintGeneratedClass'/Game/UI/Berlin/Menu/Atron/NewAtron/Widgets/UMG_TB_NAtron_Button.UMG_TB_NAtron_Button_C'"
bklik = g.branch(ieq(ACT(), "9"))
ch.then(bklik)
kch = Chain(g, bklik["then"])
setv(kch, "tPath", "string", it("RTarget", "string", R()))
callev(kch, "MFind")
prev9 = AND(ilt(R(), g.arrfunc("Array_Length", "bool", ins=[("TargetArray", "E[]")], outs=[("ReturnValue", "int")], pure=True,
                               TargetArray=g.get("tRegelPrev", "bool[]"))["ReturnValue"]), it("tRegelPrev", "bool", R()))
NOT9 = lambda x: g.call("Math", "Not_PreBool", ins=(("A", "bool"),), outs=(("ReturnValue", "bool"),), pure=True, A=x)["ReturnValue"]
bk9 = g.branch(AND(AND(get("tAny", "bool"), NOT9(prev9)), gt(sub(now(), get("tStart", "real")), "0.8")))
kch.then(bk9)
cnb = g.cast(get("tW", "obj:Widget"), "", disp="UMG TB NAtron Button", path=NBTN)
link(bk9["then"], cnb["execute"])
cdl = g.call_delegate(NBTN, "On Clicked", cnb.out, params=(("Widget", "obj:Object", cnb.out),))
link(cnb["then"], cdl["execute"])
sp9 = g.arrfunc("Array_Set", "bool", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                TargetArray=g.get("tRegelPrev", "bool[]"), Index=R(), Item=AND(get("tAny", "bool"), gt(sub(now(), get("tStart", "real")), "0.8")), bSizeToFit=True)
TBK = "/Script/UMG.WidgetBlueprintGeneratedClass'/Game/UI/Berlin/Menu/Atron/NewAtron/Widgets/UMG_TB_NAtron_Ticket_Button.UMG_TB_NAtron_Ticket_Button_C'"
ctk = g.cast(get("tW", "obj:Widget"), "", disp="UMG TB NAtron Ticket Button", path=TBK)
link(cnb["CastFailed"], ctk["execute"])
cdt = g.call_delegate(TBK, "On Click", ctk.out, params=(("Widget", "obj:Object", ctk.out),))
link(ctk["then"], cdt["execute"])
for pp in (bk9["else"], ctk["CastFailed"], cdl["then"], cdt["then"]):
    link(pp, sp9["execute"])
jn = g.sequence(1)
link(bklik["else"], jn["execute"])
link(sp9["then"], jn["execute"])
ch = Chain(g, jn["then_0"])
# tekst forberedes foerst (MFmt bruger MFind)
bt = g.branch(AND(ieq(ACT(), "2"), get("tAny", "bool")))
ch.then(bt)
bs = g.branch(ige(it("RSlotVar", "int", R()), "0"))
link(bt["then"], bs["execute"])
cs = Chain(g, bs["then"])
setv(cs, "tVar", "int", it("RSlotVar", "int", R()))
setv(cs, "fA", "real", it("RSlotA", "real", R()))
setv(cs, "fB", "real", it("RSlotB", "real", R()))
setv(cs, "fM", "real", it("RSlotM", "real", R()))
setv(cs, "fFmt", "int", it("RSlotFmt", "int", R()))
callev(cs, "MFmt")
withslot = setv(cs, "tRes", "string", cat(cat(it("RTxtTil", "string", R()), get("tRes", "string")), it("RSuffix", "string", R())))
noslot = g.set("tRes", "string", cat(it("RTxtTil", "string", R()), it("RSuffix", "string", R())))
link(bs["else"], noslot["execute"])
# billede: find holder foerst
bb = g.branch(AND(ieq(ACT(), "6"), DOIT()))
for p in (bt["else"], withslot["then"], noslot["then"]):
    link(p, bb["execute"])
cb = Chain(g, bb["then"])
setv(cb, "tPath", "string", selS(it("RTxtTil", "string", R()), it("RTxtEllers", "string", R()), get("tAny", "bool")))
callev(cb, "MFind")
w2 = setv(cb, "tW2", "obj:Widget", get("tW", "obj:Widget"))
# find maalet
tp = g.set("tPath", "string", it("RTarget", "string", R()))
link(bb["else"], tp["execute"])
link(w2["then"], tp["execute"])
ch = Chain(g, tp["then"])
callev(ch, "MFind")
bv = g.branch(AND(isvalid(get("tW", "obj:Widget")), DOIT()))
ch.then(bv)
sw = g.switch_int(ACT(), 12)
link(bv["then"], sw["execute"])
W = lambda: get("tW", "obj:Widget")
COL = lambda: selC(it("RColTil", "struct:LinearColor", R()), it("RColEllers", "struct:LinearColor", R()), get("tAny", "bool"))
# 0 farve (Border eller Image)
c = Chain(g, sw["0"])
cb_ = g.cast(W(), "Border")
c.then(cb_)
# v25: bloedt farveskift (glid) - toner fra nuvaerende farve mod maalfarven
glc = it("RGlid", "real", R())
curcol = g.member_get("/Script/CoreUObject.Class'/Script/UMG.Border'", "BrushColor", "struct:LinearColor", cb_.out)
alfa = selF("1", fmin("1", div(get("DT", "real"), selF(glc, "0.001", gt(it("RGlid", "real", R()), "0.001")))), le(it("RGlid", "real", R()), "0.001"))
nycol = M("LinearColorLerp", (("A", "struct:LinearColor"), ("B", "struct:LinearColor"), ("Alpha", "real")), (("ReturnValue", "struct:LinearColor"),),
          A=curcol, B=COL(), Alpha=alfa)
c.then(g.call(None, "SetBrushColor", target_cls="Border", target=cb_.out, ins=(("InBrushColor", "struct:LinearColor"),), InBrushColor=nycol))
ci_ = g.cast(W(), "Image")
link(cb_["CastFailed"], ci_["execute"])
sc = g.call(None, "SetColorAndOpacity", target_cls="Image", target=ci_.out, ins=(("InColorAndOpacity", "struct:LinearColor"),), InColorAndOpacity=COL())
link(ci_["then"], sc["execute"])
# 1 tekstfarve
c = Chain(g, sw["1"])
ct = g.cast(W(), "TextBlock")
c.then(ct)
c.then(g.call(None, "SetColorAndOpacity", target_cls="TextBlock", target=ct.out, ins=(("InColorAndOpacity", "struct:SlateColor"),),
              InColorAndOpacity=g.make_slatecolor(COL())))
# 2 tekst
c = Chain(g, sw["2"])
ct = g.cast(W(), "TextBlock")
c.then(ct)
c.then(g.call(None, "SetText", target_cls="TextBlock", target=ct.out, ins=(("InText", "text"),),
              InText=s2t(selS(get("tRes", "string"), it("RTxtEllers", "string", R()), get("tAny", "bool")))))
# 3 vis / 4 skjul
BTN = "/Script/CoreUObject.Class'/Script/UMG.Button'"
for case, on, off in (("3", "SelfHitTestInvisible", "Collapsed"), ("4", "Collapsed", "SelfHitTestInvisible")):
    bvis = g.branch(get("tAny", "bool"))
    link(sw[case], bvis["execute"])
    for pinname, val in (("then", on), ("else", off)):
        if val == "SelfHitTestInvisible":
            # knapper skal kunne trykkes -> Visible; alt andet lader klik gaa igennem
            cbt = g.cast(W(), "", disp="Button", path=BTN)
            link(bvis[pinname], cbt["execute"])
            sv1 = g.call(None, "SetVisibility", target_cls="Widget", target=W(), ins=(("InVisibility", "enum:Vis"),), InVisibility="Visible")
            sv2 = g.call(None, "SetVisibility", target_cls="Widget", target=W(), ins=(("InVisibility", "enum:Vis"),), InVisibility=val)
            link(cbt["then"], sv1["execute"]); link(cbt["CastFailed"], sv2["execute"])
        else:
            sv = g.call(None, "SetVisibility", target_cls="Widget", target=W(), ins=(("InVisibility", "enum:Vis"),), InVisibility=val)
            link(bvis[pinname], sv["execute"])
# 5 opacity (med glid)
c = Chain(g, sw["5"])
tgt = selF(it("RNumTil", "real", R()), it("RNumEllers", "real", R()), get("tAny", "bool"))
gl = it("RGlid", "real", R())
divisor = selF(gl, "0.001", gt(it("RGlid", "real", R()), "0.001"))
cur = g.call(None, "GetRenderOpacity", target_cls="Widget", target=W(), pure=True, outs=(("ReturnValue", "real"),))["ReturnValue"]
tgt2 = selF(it("RNumTil", "real", R()), it("RNumEllers", "real", R()), get("tAny", "bool"))
smooth = lerp(cur, tgt2, fmin("1", div(get("DT", "real"), divisor)))
newop = selF(tgt, smooth, le(it("RGlid", "real", R()), "0.001"))
c.then(g.call(None, "SetRenderOpacity", target_cls="Widget", target=W(), ins=(("InOpacity", "real"),), InOpacity=newop))
# 7/8 flyt (glid) i x / y: render-forskydning, toner mod maalet
WT = "/Script/UMG.WidgetTransform"
for case, akse in (("7", "X"), ("8", "Y")):
    c = Chain(g, sw[case])
    rt = g.member_get("/Script/CoreUObject.Class'/Script/UMG.Widget'", "RenderTransform", "struct:" + WT, W())
    tr = g.break_struct(WT, "WidgetTransform", rt, (("Translation", "struct:/Script/CoreUObject.Vector2D"),))
    bvt = g.call("Math", "BreakVector2D", ins=(("InVec", "struct:/Script/CoreUObject.Vector2D"),), outs=(("X", "real"), ("Y", "real")), pure=True, InVec=tr["Translation"])
    mal = selF(it("RNumTil", "real", R()), it("RNumEllers", "real", R()), get("tAny", "bool"))
    glx = it("RGlid", "real", R())
    a_ = selF("1", fmin("1", div(get("DT", "real"), selF(glx, "0.001", gt(it("RGlid", "real", R()), "0.001")))), le(it("RGlid", "real", R()), "0.001"))
    ny = lerp(bvt[akse], mal, a_)
    vec = g.call("Math", "MakeVector2D", ins=(("X", "real"), ("Y", "real")), outs=(("ReturnValue", "struct:/Script/CoreUObject.Vector2D"),), pure=True,
                 X=ny if akse == "X" else bvt["X"], Y=ny if akse == "Y" else bvt["Y"])["ReturnValue"]
    c.then(g.call(None, "SetRenderTranslation", target_cls="Widget", target=W(), ins=(("Translation", "struct:/Script/CoreUObject.Vector2D"),), Translation=vec))
# 6 billede
c = Chain(g, sw["6"])
ch2_ = g.cast(get("tW2", "obj:Widget"), "Image")
c.then(ch2_)
brush = g.member_get("/Script/CoreUObject.Class'/Script/UMG.Image'", "Brush", "struct:SlateBrush", ch2_.out)
ci2 = g.cast(W(), "Image")
c.then(ci2)
c.then(g.call(None, "SetBrush", target_cls="Image", target=ci2.out, ins=(("InBrush", "struct:SlateBrush"),), InBrush=brush))
# 10 tilfoej / 11 fjern maerke (tag) paa bussen spilleren sidder i (RTxtTil = navnet) - kun naar betingelsen er sand
def bus_actor():
    pw = g.call("GS", "GetPlayerPawn", ins=(("PlayerIndex", "int"),), outs=(("ReturnValue", "obj:Actor"),), pure=True, PlayerIndex="0")["ReturnValue"]
    fa = g.call(None, "GetAttachParentActor", target_cls="Actor", target=pw, pure=True, outs=(("ReturnValue", "obj:Actor"),))["ReturnValue"]
    pw2 = g.call("GS", "GetPlayerPawn", ins=(("PlayerIndex", "int"),), outs=(("ReturnValue", "obj:Actor"),), pure=True, PlayerIndex="0")["ReturnValue"]
    fa2 = g.call(None, "GetAttachParentActor", target_cls="Actor", target=pw2, pure=True, outs=(("ReturnValue", "obj:Actor"),))["ReturnValue"]
    return g.call("Math", "SelectObject", ins=(("A", "obj:Object"), ("B", "obj:Object"), ("bSelectA", "bool")),
                  outs=(("ReturnValue", "obj:Object"),), pure=True, A=fa, B=pw2, bSelectA=isvalid(fa2))["ReturnValue"]
def tagnavn(s_): return S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),), InString=s_)
ACTOR = "/Script/CoreUObject.Class'/Script/Engine.Actor'"
for case, fn in (("10", "Array_AddUnique"), ("11", "Array_RemoveItem")):
    bta = g.branch(get("tAny", "bool"))
    link(sw[case], bta["execute"])
    ca_ = g.cast(bus_actor(), "Actor")
    link(bta["then"], ca_["execute"])
    tags = g.member_get(ACTOR, "Tags", "name[]", ca_.out)
    if fn == "Array_AddUnique":
        an = g.arrfunc(fn, "name", ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                       TargetArray=tags, NewItem=tagnavn(it("RTxtTil", "string", R())))
    else:
        an = g.arrfunc(fn, "name", ins=[("TargetArray", "E[]"), ("Item", "E")], outs=[("ReturnValue", "bool")],
                       TargetArray=tags, Item=tagnavn(it("RTxtTil", "string", R())))
    link(ca_["then"], an["execute"])

# =========================================================
# MNavi: GPS-kort (spillets UMG_NaviMap) med Movia-farver + 3D-ring om naeste stop
# =========================================================
NAVIMAP = "/Script/UMG.WidgetBlueprintGeneratedClass'/Game/UI/HUD/UMG_NaviMap.UMG_NaviMap_C'"
ROADMAP = "/Script/UMG.WidgetBlueprintGeneratedClass'/Game/UI/Menu/MainMenu/Helper/UMG_RoadMap.UMG_RoadMap_C'"
MRW = "/Script/CoreUObject.Class'/Script/RoadmapSystem.MapRenderWidget'"
V2 = "struct:/Script/CoreUObject.Vector2D"
TEX = "obj:/Script/Engine.Texture2D"
RMS = "/Script/RoadmapSystem.RoadMapSettings"
RRS = "/Script/RoadmapSystem.RoadRenderSetting"
g.next_col()
ev = g.custom_event("MNavi")
ch = Chain(g, ev["then"])
harnavi = g.call("Str", "NotEqual_StrStr", ins=(("A", "string"), ("B", "string")), outs=(("ReturnValue", "bool"),), pure=True,
                 A=get("NaviPath", "string"), B="")["ReturnValue"]
ch.then(g.branch(harnavi))
setv(ch, "tPath", "string", get("NaviPath", "string"))
callev(ch, "MFind")
cnav = g.cast(get("tW", "obj:Widget"), "", disp="UMG Navi Map", path=NAVIMAP)
ch.then(cnav)
def mrw():
    rm = g.member_get(NAVIMAP, "UMG_RoadMap", "obj:Object", cnav.out)
    return g.member_get(ROADMAP, "MapRenderWidget", "obj:Object", rm)
# hver gang: zoom og 3D-haeldning (kortet saetter selv disse hvert billede ud fra sine egne variabler)
ch.then(g.member_set(NAVIMAP, "Zoom Factor Multiplier", "real", cnav.out, get("NaviZoom", "real")))
ch.then(g.member_set(NAVIMAP, "3DViewPitch", "real", cnav.out, get("NaviPitch", "real")))
ch.then(g.member_set(NAVIMAP, "3DView", "bool", cnav.out, True))
# --- opsaetning: 1. gang + igen efter 8 og 16 sek (kortet kan nulstille sig selv ved rutestart) ---
tid_ok = AND(ilt(get("tNaviN", "int"), "3"), gt(sub(now(), get("tNaviTid", "real")), "8"))
b_init = g.branch(OR(g.call("Math", "Not_PreBool", ins=(("A", "bool"),), outs=(("ReturnValue", "bool"),), pure=True, A=get("tNaviInit", "bool"))["ReturnValue"], tid_ok))
ch.then(b_init)
ich = Chain(g, b_init["then"])
setv(ich, "tNaviTid", "real", now())
setv(ich, "tNaviN", "int", iadd(get("tNaviN", "int"), "1"))
ich.then(g.call_path(NAVIMAP, "Set Enabled", ins=(("Enabled", "bool"),), pure=False, target=cnav.out, Enabled=True))
# vejfarver: hent indstillinger, farv alle vejtyper, saet tilbage
sq = g.sequence(2)
ich.then(sq, outpin="then_1")
grs = g.call_path(MRW, "GetRoadMapSettings", ins=(), outs=(("ReturnValue", "struct:" + RMS),), pure=False, target=mrw())
link(sq["then_0"], grs["execute"])
setv(ich, "tRMS", "struct:" + RMS, grs["ReturnValue"])
ich.then(g.arrfunc("Array_Clear", "struct:" + RRS, ins=[("TargetArray", "E[]")], TargetArray=g.get("tVeje", "struct:" + RRS + "[]")))
brs = g.break_struct(RMS, "RoadMapSettings", get("tRMS", "struct:" + RMS), (("RoadRenderSettings", "struct:" + RRS + "[]"),))
nlen = g.arrfunc("Array_Length", "struct:" + RRS, ins=[("TargetArray", "E[]")], outs=[("ReturnValue", "int")], pure=True,
                 TargetArray=brs["RoadRenderSettings"])["ReturnValue"]
fl = g.forloop("0", isub(nlen, "1"))
ich.then(fl, outpin="LoopBody")
brs2 = g.break_struct(RMS, "RoadMapSettings", get("tRMS", "struct:" + RMS), (("RoadRenderSettings", "struct:" + RRS + "[]"),))
el = g.item_of(brs2["RoadRenderSettings"], "struct:" + RRS, fl["Index"])
be = g.break_struct(RRS, "RoadRenderSetting", el, (("RoadTypeName", "string"), ("RenderAtZoom", "real")))
nstr = be["RoadTypeName"]
farve = selC(get("NaviVejStor", "struct:LinearColor"), get("NaviVej", "struct:LinearColor"),
             OR(contains(nstr, "Highway"), contains(nstr, "State")))
ny = g.make_struct(RRS, "RoadRenderSetting", (("RoadTypeName", "string"), ("RenderColor", "struct:LinearColor"), ("RenderAtZoom", "real")),
                   RoadTypeName=be["RoadTypeName"], RenderColor=farve, RenderAtZoom=be["RenderAtZoom"])
ich.then(g.arrfunc("Array_Add", "struct:" + RRS, ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                   TargetArray=g.get("tVeje", "struct:" + RRS + "[]"), NewItem=ny))
ich = Chain(g, fl["Completed"])
ich.then(g.set_fields(RMS, get("tRMS", "struct:" + RMS),
                      (("RoadRenderSettings", "struct:" + RRS + "[]"), ("PlayerExcludedRoadsColor", "struct:LinearColor")),
                      RoadRenderSettings=g.get("tVeje", "struct:" + RRS + "[]"), PlayerExcludedRoadsColor=get("NaviVej", "struct:LinearColor")))
ich.then(g.call_path(MRW, "SetRoadMapSettings", ins=(("Settings", "struct:" + RMS),), pure=False, target=mrw(),
                     Settings=get("tRMS", "struct:" + RMS)))
bbg = g.branch(isvalid(get("NaviBg", TEX)))
ich.then(bbg)
ich.then(g.call_path(MRW, "SetBackgroundImage", ins=(("Texture", TEX),), pure=False, target=mrw(), Texture=get("NaviBg", TEX)))
rb = g.call_path(MRW, "RebuildGeometry", ins=(), pure=False, target=mrw())
ich.then(rb)
link(bbg["else"], rb["execute"])
fin = g.set("tNaviInit", "bool", True)
ich.then(fin)
# --- ring om naeste stop ---
harring = g.call("Str", "NotEqual_StrStr", ins=(("A", "string"), ("B", "string")), outs=(("ReturnValue", "bool"),), pure=True,
                 A=get("RingPath", "string"), B="")["ReturnValue"]
b_ring = g.branch(harring)
link(fin["then"], b_ring["execute"])
link(b_init["else"], b_ring["execute"])
rch = Chain(g, b_ring["then"])
cn = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
rch.then(cn)
trip = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn.out)["Result"]
gyl, bc, bo, offok = naeste(trip)
pc = g.call("Math", "BreakVector2D", ins=(("InVec", V2),), outs=(("X", "real"), ("Y", "real")), pure=True,
            InVec=g.member_get("/Script/CoreUObject.Class'/Script/Fernbus.RouteStopInfo'", "WorldPosition", V2, bc["RouteStopInfo"]))
po = g.call("Math", "BreakVector2D", ins=(("InVec", V2),), outs=(("X", "real"), ("Y", "real")), pure=True,
            InVec=g.member_get("/Script/CoreUObject.Class'/Script/Fernbus.RouteStopInfo'", "WorldPosition", V2, bo["RouteStopInfo"]))
wpos = g.call("Math", "MakeVector2D", ins=(("X", "real"), ("Y", "real")), outs=(("ReturnValue", V2),), pure=True,
              X=selF(pc["X"], po["X"], gyl), Y=selF(pc["Y"], po["Y"], gyl))["ReturnValue"]
st = {"IsValid": OR(gyl, offok)}
proj = g.call_path(MRW, "ProjectPosition", ins=(("WorldPosition", V2),), outs=(("ReturnValue", V2),), pure=True, target=mrw(), WorldPosition=wpos)["ReturnValue"]
setv(rch, "tPos", V2, proj)
setv(rch, "tPath", "string", get("RingPath", "string"))
callev(rch, "MFind")
bv = g.call("Math", "BreakVector2D", ins=(("InVec", V2),), outs=(("X", "real"), ("Y", "real")), pure=True, InVec=get("tPos", V2))
px, py = bv["X"], bv["Y"]
slot = g.member_get("/Script/CoreUObject.Class'/Script/UMG.Widget'", "Slot", "obj:Object", get("tW", "obj:Widget"))
cs = g.cast(slot, "", disp="Canvas Panel Slot", path="/Script/CoreUObject.Class'/Script/UMG.CanvasPanelSlot'")
rch.then(cs)
nx = sub(add(get("NaviX", "real"), px), div(get("RingW", "real"), "2"))
ny2 = sub(add(get("NaviY", "real"), py), div(get("RingH", "real"), "2"))
mv = g.call("Math", "MakeVector2D", ins=(("X", "real"), ("Y", "real")), outs=(("ReturnValue", V2),), pure=True, X=nx, Y=ny2)["ReturnValue"]
rch.then(g.call_path("/Script/CoreUObject.Class'/Script/UMG.CanvasPanelSlot'", "SetPosition", ins=(("InPosition", V2),), pure=False,
                     target=cs.out, InPosition=mv))
bv2 = g.call("Math", "BreakVector2D", ins=(("InVec", V2),), outs=(("X", "real"), ("Y", "real")), pure=True, InVec=get("tPos", V2))
inde = AND(AND(ge(bv2["X"], "0"), le(bv2["X"], get("NaviW", "real"))), AND(ge(bv2["Y"], "0"), le(bv2["Y"], get("NaviH", "real"))))
synlig = AND(inde, st["IsValid"])
rch.then(g.call(None, "SetRenderOpacity", target_cls="Widget", target=get("tW", "obj:Widget"), ins=(("InOpacity", "real"),),
                InOpacity=selF("1", "0", synlig)))

# =========================================================
# MAfg: andre linjer ved de naeste 3 stop + afgangstavle (fra spillets koereplan / OperatingPlan)
# =========================================================
BSI = "struct:/Script/RoadmapSystem.BusStopIdentifier"
TIM = "struct:/Script/Fernbus.BusStopDisplayTimings"
TIMP = "/Script/Fernbus.BusStopDisplayTimings"
OPC = "/Script/CoreUObject.Class'/Script/Fernbus.OperatingPlan'"
OPT = "obj:/Script/Fernbus.OperatingPlan"
DT = "struct:/Script/CoreUObject.DateTime"
ANTAL_MAERKER = 5
g.next_col()
ev = g.custom_event("MAfg")
ch = Chain(g, ev["then"])
ch.then(g.branch(get("AfgBrug", "bool")))
ch.then(g.branch(gt(sub(now(), get("AfgTid", "real")), "2.5")))
setv(ch, "AfgTid", "real", now())
ci = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG Interior Display Base", path=INTERIOR)
ch.then(ci)
info = g.member_get(BUSLOGIC, "Bus Trip Info", "struct:/Script/Fernbus.BusTripInfo", g.member_get(INTERIOR, "Bus Logic", "obj:Object", ci.out))
bt = g.break_struct("/Script/Fernbus.BusTripInfo", "BusTripInfo", info, (("Route", "obj:Object"),))
egen = g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True,
              InName=g.member_get("/Script/CoreUObject.Class'/Script/Fernbus.LineRoute'", "Line", "name", bt["Route"]))["ReturnValue"]
# koereplanen: GameState -> Map -> GetCurrentOperatingPlan
gs = g.call("GS", "GetGameState", ins=(), outs=(("ReturnValue", "obj:/Script/Engine.GameStateBase"),), pure=True)["ReturnValue"]
cgs = g.cast(gs, "", disp="TMLGame State", path="/Script/CoreUObject.Class'/Script/Fernbus.TMLGameState'")
ch.then(cgs)
kort = g.member_get("/Script/CoreUObject.Class'/Script/Fernbus.TMLGameState'", "Map", "obj:Object", cgs.out)
sq = g.sequence(2)
ch.then(sq, outpin="then_1")
gop = g.call_path("/Script/CoreUObject.Class'/Script/Fernbus.MapBase'", "GetCurrentOperatingPlan", ins=(), outs=(("ReturnValue", OPT),), pure=False, target=kort)
link(sq["then_0"], gop["execute"])
setv(ch, "tOP", OPT, gop["ReturnValue"])
ch.then(g.branch(isvalid(get("tOP", OPT))))
for v, e in (("AfgLin", "string"), ("AfgTil", "string"), ("AfgMin", "real"), ("StopLin", "string")):
    ch.then(g.arrfunc("Array_Clear", e, ins=[("TargetArray", "E[]")], TargetArray=g.get(v, e + "[]")))

def arr_add(ch, var, elem, val):
    return ch.then(g.arrfunc("Array_Add", elem, ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                             TargetArray=g.get(var, elem + "[]"), NewItem=val))

def ident_of(stopstruct):
    return g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", stopstruct, (("StopIdent", BSI),))["StopIdent"]

# --- 1) afgangstavle: naeste 60 min fra det stop bussen er ved / kommer til ---
ch.then(g.arrfunc("Array_Clear", BSI, ins=[("TargetArray", "E[]")], TargetArray=g.get("tIdents", BSI + "[]")))
gyl, bc, bo, _ = naeste(info, aktuel=True)
bi_ = g.branch(gyl)
ch.then(bi_)
a1_ = g.arrfunc("Array_Add", BSI, ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                TargetArray=g.get("tIdents", BSI + "[]"), NewItem=bc["StopIdent"])
a2_ = g.arrfunc("Array_Add", BSI, ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                TargetArray=g.get("tIdents", BSI + "[]"), NewItem=bo["StopIdent"])
link(bi_["then"], a1_["execute"]); link(bi_["else"], a2_["execute"])
joinn = g.set("tT", "int", "0")
link(a1_["then"], joinn["execute"]); link(a2_["then"], joinn["execute"])
ch.to(joinn["then"])
nu = world_datetime()
slut = g.call("Math", "Add_DateTimeTimespan", ins=(("A", DT), ("B", "struct:/Script/CoreUObject.Timespan")), outs=(("ReturnValue", DT),), pure=True,
              A=world_datetime(), B=g.call("Math", "FromMinutes", ins=(("Minutes", "real"),), outs=(("ReturnValue", "struct:/Script/CoreUObject.Timespan"),), pure=True, Minutes="60")["ReturnValue"])["ReturnValue"]
sq2 = g.sequence(2)
ch.then(sq2, outpin="then_1")
gbt = g.call_path(OPC, "GetBusStopDisplayTimes", ins=(("StopIdents", BSI + "[]"), ("DateTimeStart", DT), ("DateTimeEnd", DT), ("bIsHoliday", "bool")),
                  outs=(("ReturnValue", TIM + "[]"),), pure=False, target=get("tOP", OPT),
                  StopIdents=g.get("tIdents", BSI + "[]"), DateTimeStart=nu, DateTimeEnd=slut, bIsHoliday=False)
link(sq2["then_0"], gbt["execute"])
setv(ch, "tTim", TIM + "[]", gbt["ReturnValue"])
fl = g.forloop("0", isub(arrlen("tTim", TIM), "1"))
ch.then(fl, outpin="LoopBody")
br = g.break_struct(TIMP, "BusStopDisplayTimings", it("tTim", TIM, fl["Index"]),
                    (("DateTime", DT), ("LineString", "string"), ("NextDestinationStrings", "string[]"), ("TourIdent", "struct:/Script/Fernbus.TourIdentifier")))
tidr = g.break_struct("/Script/Fernbus.TourIdentifier", "TourIdentifier", br["TourIdent"], (("Line", "name"),))
linje = g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True, InName=tidr["Line"])["ReturnValue"]
linje = selS(linje, br["LineString"], g.call("Str", "NotEqual_StrStr", ins=(("A", "string"), ("B", "string")), outs=(("ReturnValue", "bool"),), pure=True, A=linje, B="None")["ReturnValue"])
# minutter ud fra klokkeslaet (datoen i koereplanen kan vaere en anden end spillets dato)
raa = div(sub(secs_of_day(br["DateTime"]), secs_of_day(world_datetime())), "60")
setv(ch, "tV", "real", selF(add(raa, "1440"), raa, lt(raa, "-720")))
ch.then(g.branch(AND(AND(ge(get("tV", "real"), "-0.5"), le(get("tV", "real"), "90")), ilt(arrlen("AfgLin", "string"), "8"))))
setv(ch, "tStr", "string", linje)
arr_add(ch, "AfgLin", "string", get("tStr", "string"))
arr_add(ch, "AfgMin", "real", get("tV", "real"))
nlen = g.arrfunc("Array_Length", "string", ins=[("TargetArray", "E[]")], outs=[("ReturnValue", "int")], pure=True,
                 TargetArray=br["NextDestinationStrings"])["ReturnValue"]
bd = g.branch(ge(i2d(nlen), "1"))
ch.then(bd)
sidste = g.item_of(br["NextDestinationStrings"], "string", isub(nlen, "1"))
idx_til = selF(i2d(isub(nlen, "2")), i2d(isub(nlen, "1")), AND(streq(sidste, get("tStr", "string")), ge(i2d(nlen), "2")))
ad1 = g.arrfunc("Array_Add", "string", ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                TargetArray=g.get("AfgTil", "string[]"), NewItem=g.item_of(br["NextDestinationStrings"], "string", rnd(idx_til)))
link(bd["then"], ad1["execute"])
ad2 = g.arrfunc("Array_Add", "string", ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                TargetArray=g.get("AfgTil", "string[]"), NewItem="")
link(bd["else"], ad2["execute"])
ch = Chain(g, fl["Completed"])

# --- 2) andre linjer ved de naeste 3 stop (GetLinesThatContainStop) ---
for k in (1, 2, 3):
    st = g.call_path(TRIPFN, "FBusTripInfo_GetStopByIndexOffset", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"), ("Offset", "int")),
                     outs=(("IsValid", "bool"), ("ReturnValue", "struct:/Script/Fernbus.RouteStopWithTime")), pure=True,
                     static_default="x", a=info, Offset=str(k))
    sqk = g.sequence(2)
    ch.then(sqk, outpin="then_1")
    gl = g.call_path(OPC, "GetLinesThatContainStop", ins=(("StopIdent", BSI),), outs=(("ReturnValue", "name[]"),), pure=False,
                     target=get("tOP", OPT), StopIdent=ident_of(st["ReturnValue"]))
    link(sqk["then_0"], gl["execute"])
    setv(ch, "tLines", "name[]", gl["ReturnValue"])
    ch.then(g.arrfunc("Array_Clear", "string", ins=[("TargetArray", "E[]")], TargetArray=g.get("tSeen", "string[]")))
    fl = g.forloop("0", isub(arrlen("tLines", "name"), "1"))
    ch.then(fl, outpin="LoopBody")
    ln = g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True,
                InName=it("tLines", "name", fl["Index"]))["ReturnValue"]
    har = g.arrfunc("Array_Contains", "string", ins=[("TargetArray", "E[]"), ("ItemToFind", "E")], outs=[("ReturnValue", "bool")],
                    pure=True, TargetArray=g.get("tSeen", "string[]"), ItemToFind=ln)["ReturnValue"]
    NOT = lambda x: g.call("Math", "Not_PreBool", ins=(("A", "bool"),), outs=(("ReturnValue", "bool"),), pure=True, A=x)["ReturnValue"]
    ch.then(g.branch(AND(AND(NOT(har), NOT(streq(ln, egen))), NOT(streq(ln, "")))))
    arr_add(ch, "tSeen", "string", ln)
    ch = Chain(g, fl["Completed"])
    for _ in range(ANTAL_MAERKER):
        arr_add(ch, "tSeen", "string", "")
    for j in range(ANTAL_MAERKER):
        arr_add(ch, "StopLin", "string", g.item_of(g.get("tSeen", "string[]"), "string", str(j)))

# =========================================================
# MoviaUpdate (timer)
# =========================================================
# =========================================================
# MSidst: som spillets passagerskaerm - mens bussen er ved et stop gemmes GetNextStop i tNaesteStop
# (har vi endnu ikke vaeret ved et stop, bruges GetNextStop direkte)
# =========================================================
def sidst_logik(start_pin, trip):
    cur = g.call_path(TRIPFN, "FBusTripInfo_GetCurrentStop", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                      outs=(("IsValid", "bool"), ("ReturnValue", RSWT)), pure=True, static_default="x", a=trip)
    nxt = g.call_path(TRIPFN, "FBusTripInfo_GetNextStop", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                      outs=(("IsValid", "bool"), ("ReturnValue", RSWT)), pure=True, static_default="x", a=trip)
    b1 = g.branch(cur["IsValid"])
    link(start_pin, b1["execute"])
    # ved et stop: husk spillets naeste stop - men ved sidste stop (intet naeste) bliver vi paa det aktuelle stop
    bn = g.branch(nxt["IsValid"])
    link(b1["then"], bn["execute"])
    s1 = g.set("tNaesteStop", RSWT, nxt["ReturnValue"])
    s2 = g.set("tNaesteStop", RSWT, cur["ReturnValue"])
    link(bn["then"], s1["execute"]); link(bn["else"], s2["execute"])
    sh = g.set("tHarNaeste", "bool", True)
    link(s1["then"], sh["execute"]); link(s2["then"], sh["execute"])
    NOT = lambda x: g.call("Math", "Not_PreBool", ins=(("A", "bool"),), outs=(("ReturnValue", "bool"),), pure=True, A=x)["ReturnValue"]
    b2 = g.branch(NOT(get("tHarNaeste", "bool")))
    link(b1["else"], b2["execute"])
    c2 = Chain(g, b2["then"])
    setv(c2, "tNaesteStop", RSWT, nxt["ReturnValue"])

g.next_col()
ev = g.custom_event("MSidst")
ch = Chain(g, ev["then"])
cn = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
ch.then(cn)
trip = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn.out)["Result"]
sidst_logik(cn["then"], trip)
ci = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG Interior Display Base", path=INTERIOR)
link(cn["CastFailed"], ci["execute"])
info = g.member_get(BUSLOGIC, "Bus Trip Info", "struct:/Script/Fernbus.BusTripInfo", g.member_get(INTERIOR, "Bus Logic", "obj:Object", ci.out))
sidst_logik(ci["then"], info)

# =========================================================
# MKnap: trykknapper (lag af typen "knap") - tjekker om de er trykket og skifter/taeller deres tilstand
# =========================================================
g.next_col()
ev = g.custom_event("MKnap")
ch = Chain(g, ev["then"])
fl = g.forloop("0", isub(arrlen("KnapPath", "string"), "1"))
ch.then(fl, outpin="LoopBody")
setv(ch, "tKi", "int", fl["Index"])
setv(ch, "tPath", "string", it("KnapPath", "string", get("tKi", "int")))
callev(ch, "MFind")
cb = g.cast(get("tW", "obj:Widget"), "", disp="Button", path="/Script/CoreUObject.Class'/Script/UMG.Button'")
ch.then(cb)
trykket = g.call_path("/Script/CoreUObject.Class'/Script/UMG.Button'", "IsPressed", ins=(), outs=(("ReturnValue", "bool"),), pure=True, target=cb.out)["ReturnValue"]
setv(ch, "tB", "bool", trykket)
KI = lambda: get("tKi", "int")
foer = AND(ilt(KI(), g.arrfunc("Array_Length", "bool", ins=[("TargetArray", "E[]")], outs=[("ReturnValue", "int")], pure=True,
                               TargetArray=g.get("tKnapPrev", "bool[]"))["ReturnValue"]),
           it("tKnapPrev", "bool", KI()))
NOT = lambda x: g.call("Math", "Not_PreBool", ins=(("A", "bool"),), outs=(("ReturnValue", "bool"),), pure=True, A=x)["ReturnValue"]
bk = g.branch(AND(get("tB", "bool"), NOT(foer)))
ch.then(bk)
gi = lambda: it("KnapGruppe", "int", KI())
nu = selF(it("tKnapVal", "real", gi()), "0", ilt(gi(), arrlen("tKnapVal", "real")))
skift = sub("1", fmin("1", nu))
taelt = M("FClamp", (("Value", "real"), ("Min", "real"), ("Max", "real")), Value=add(nu, it("KnapVaerdi", "real", KI())),
          Min=it("KnapMin", "real", KI()), Max=it("KnapMax", "real", KI()))
nyv = selF(skift, taelt, ieq(it("KnapMode", "int", KI()), "0"))
setk = g.arrfunc("Array_Set", "real", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                 TargetArray=g.get("tKnapVal", "real[]"), Index=gi(), Item=nyv, bSizeToFit=True)
# v27: 2 tegn, 3 slet, 4 ryd (i tekstfeltet som gruppen peger paa), 6 log ind (gruppe = 2 hvis konto ok ellers 1)
swk = g.switch_int(it("KnapMode", "int", KI()), 23)
link(bk["then"], swk["execute"])
for pn in ("0", "1", "5", "Default"):
    link(swk[pn], setk["execute"])
plads = lambda: rnd(selF(it("tKnapVal", "real", gi()), "0", ilt(gi(), arrlen("tKnapVal", "real"))))
SETTXT = lambda val: g.arrfunc("Array_Set", "string", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                               TargetArray=g.get("tTxt", "string[]"), Index=plads(), Item=val, bSizeToFit=True)
cur_t = lambda: it("tTxt", "string", plads())
storeidx = lambda: rnd(it("KnapMax", "real", KI()))
store = AND(ige(rnd(it("KnapMax", "real", KI())), "0"),
            ge(selF(it("tKnapVal", "real", storeidx()), "0", ilt(storeidx(), arrlen("tKnapVal", "real"))), "1"))
tegn = selS(S("ToUpper", (("SourceString", "string"),), SourceString=it("KnapTegn", "string", KI())), it("KnapTegn", "string", KI()), store)
ny_t = selS(cat(cur_t(), tegn), cur_t(), ilt(S("Len", (("S", "string"),), (("ReturnValue", "int"),), S=cur_t()), "40"))
t2 = SETTXT(ny_t); link(swk["2"], t2["execute"])
t3 = SETTXT(S("LeftChop", (("SourceString", "string"), ("Count", "int")), SourceString=cur_t(), Count="1")); link(swk["3"], t3["execute"])
t4 = SETTXT(""); link(swk["4"], t4["execute"])
# nulstil gruppen KnapMin (fx fejlbeskeden) naar der skrives
bnul = g.branch(ige(rnd(it("KnapMin", "real", KI())), "0"))
for tn in (t2, t3, t4):
    link(tn["then"], bnul["execute"])
nul = g.arrfunc("Array_Set", "real", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                TargetArray=g.get("tKnapVal", "real[]"), Index=rnd(it("KnapMin", "real", KI())), Item="0", bSizeToFit=True)
link(bnul["then"], nul["execute"])
lg = g.arrfunc("Array_Set", "real", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
               TargetArray=g.get("tKnapVal", "real[]"), Index=gi(), Item=selF("2", "1", loginok()), bSizeToFit=True)
link(swk["6"], lg["execute"])
GEMCLS = "/Script/Engine.BlueprintGeneratedClass'/Game/MoviaSkaerme/BP_MoviaGem.BP_MoviaGem_C'"
GEMOBJ = "/Game/MoviaSkaerme/BP_MoviaGem.BP_MoviaGem_C"
SLOT = "MoviaLogin"
bok6 = g.branch(loginok())
link(lg["then"], bok6["execute"])
e6 = tag_saet(bok6["then"], "ML_", secs_of_day(world_datetime()))
e6 = tag_saet(e6, "MB_", "0")
e6 = tag_saet(e6, "MK_", "0")
e6 = tag_saet(e6, "MP_", "0")
ca6 = g.cast(bus_actor0(), "Actor")
link(e6, ca6["execute"])
e6 = ca6["then"]
for _t in ("MoviaOK", "MoviaLogud", "MoviaBillet"):
    _r = g.arrfunc("Array_RemoveItem", "name", ins=[("TargetArray", "E[]"), ("Item", "E")], outs=[("ReturnValue", "bool")],
                   TargetArray=g.member_get("/Script/CoreUObject.Class'/Script/Engine.Actor'", "Tags", "name[]", ca6.out),
                   Item=S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),), InString=_t))
    link(e6, _r["execute"]); e6 = _r["then"]
j6 = g.sequence(1)
link(e6, j6["execute"]); link(ca6["CastFailed"], j6["execute"])
e6 = j6["then_0"]
bsv = g.branch(AND(loginok(), ige(get("HuskGruppe", "int"), "0")))
link(e6, bsv["execute"]); link(bok6["else"], bsv["execute"])
husk = lambda: ge(selF(it("tKnapVal", "real", get("HuskGruppe", "int")), "0", ilt(get("HuskGruppe", "int"), arrlen("tKnapVal", "real"))), "1")
csg = g.call("GS", "CreateSaveGameObject", ins=(("SaveGameClass", "class:/Script/Engine.SaveGame"),), outs=(("ReturnValue", "obj:Object"),))
csg["SaveGameClass"].defobj = GEMOBJ
link(bsv["then"], csg["execute"])
cg = g.cast(csg["ReturnValue"], "", disp="BP Movia Gem", path=GEMCLS)
link(csg["then"], cg["execute"])
se = g.member_set(GEMCLS, "Email", "string", cg.out, selS(trim(txt_at("0")), "", husk()))
link(cg["then"], se["execute"])
sh = g.member_set(GEMCLS, "Husk", "bool", cg.out, husk())
link(se["then"], sh["execute"])
sv = g.call("GS", "SaveGameToSlot", ins=(("SaveGameObject", "obj:Object"), ("SlotName", "string"), ("UserIndex", "int")),
            outs=(("ReturnValue", "bool"),), SaveGameObject=cg.out, SlotName=SLOT, UserIndex="0")
link(sh["then"], sv["execute"])
# 7: saet maerket KnapTegn paa bussen (fx "MoviaOK" naar man trykker Bekraeft)
ca7 = g.cast(bus_actor0(), "Actor")
link(swk["7"], ca7["execute"])
tags7 = g.member_get("/Script/CoreUObject.Class'/Script/Engine.Actor'", "Tags", "name[]", ca7.out)
add7 = g.arrfunc("Array_AddUnique", "name", ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                 TargetArray=tags7, NewItem=S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),), InString=it("KnapTegn", "string", KI())))
link(ca7["then"], add7["execute"])
lok7 = g.arrfunc("Array_Set", "real", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                 TargetArray=g.get("tKnapVal", "real[]"), Index=gi(), Item="1", bSizeToFit=True)
link(add7["then"], lok7["execute"]); link(ca7["CastFailed"], lok7["execute"])
# 8: skift maerket KnapTegn paa bussen (taend/sluk) - husker fx at stoplisten er aaben, ogsaa naar Atron skifter skaerm
ca8 = g.cast(bus_actor0(), "Actor")
link(swk["8"], ca8["execute"])
navn8 = lambda: S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),), InString=it("KnapTegn", "string", KI()))
har8 = g.call(None, "ActorHasTag", target_cls="Actor", target=ca8.out, pure=True, ins=(("Tag", "name"),), outs=(("ReturnValue", "bool"),), Tag=navn8())["ReturnValue"]
b8 = g.branch(har8)
link(ca8["then"], b8["execute"])
rm8 = g.arrfunc("Array_RemoveItem", "name", ins=[("TargetArray", "E[]"), ("Item", "E")], outs=[("ReturnValue", "bool")],
                TargetArray=g.member_get("/Script/CoreUObject.Class'/Script/Engine.Actor'", "Tags", "name[]", ca8.out), Item=navn8())
ad8 = g.arrfunc("Array_AddUnique", "name", ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                TargetArray=g.member_get("/Script/CoreUObject.Class'/Script/Engine.Actor'", "Tags", "name[]", ca8.out), NewItem=navn8())
link(b8["then"], rm8["execute"]); link(b8["else"], ad8["execute"])
# 9: print billetten fra spillets billetknap (sti i KnapTegn): laeg i kurven, tag betaling, print
DISP = "/Script/UMG.WidgetBlueprintGeneratedClass'/Game/UI/Berlin/Menu/Atron/NewAtron/UMG_TB_NAtron_Display.UMG_TB_NAtron_Display_C'"
TBTN9 = "/Script/UMG.WidgetBlueprintGeneratedClass'/Game/UI/Berlin/Menu/Atron/NewAtron/Widgets/UMG_TB_NAtron_Ticket_Button.UMG_TB_NAtron_Ticket_Button_C'"
p9 = g.set("tPath", "string", it("KnapTegn", "string", KI()))
link(swk["9"], p9["execute"])
f9 = g.call(None, "MFind", selfctx=True)
link(p9["then"], f9["execute"])
c9 = g.cast(get("tW", "obj:Widget"), "", disp="UMG TB NAtron Ticket Button", path=TBTN9)
link(f9["then"], c9["execute"])
tk9 = g.member_get(TBTN9, "Ticket", "obj:Object", c9.out)
bv9 = g.branch(isvalid(g.member_get(TBTN9, "Ticket", "obj:Object", c9.out)))
link(c9["then"], bv9["execute"])
cn9 = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
link(bv9["then"], cn9["execute"])
disp9 = lambda: g.call_path(NATRON, "Get Display", ins=(), outs=(("AsUMG TB NAtron Display", "obj:Object"),), pure=True, target=cn9.out)["AsUMG TB NAtron Display"]
a9 = g.call_path(DISP, "Add Ticket Order", ins=(("NewParam", "obj:Object"),), pure=False, target=disp9(), NewParam=tk9)
link(cn9["then"], a9["execute"])
t9 = g.call_path(DISP, "Take Cash And Give Change", ins=(), pure=False, target=disp9())
link(a9["then"], t9["execute"])
pr9 = g.call_path(DISP, "Print Tickets and Finish Transaction", ins=(("Payed Cash", "bool"),), pure=False, target=disp9(), **{"Payed Cash": True})
link(t9["then"], pr9["execute"])
cnt9 = g.arrfunc("Array_Set", "real", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                 TargetArray=g.get("tKnapVal", "real[]"), Index=gi(),
                 Item=add(selF(it("tKnapVal", "real", gi()), "0", ilt(gi(), arrlen("tKnapVal", "real"))), "1"), bSizeToFit=True)
e9 = tag_plus1(pr9["then"], "MB_")
link(e9, cnt9["execute"])
# 10: tryk paa en af spillets kategoriknapper (On Click) og husk valget i gruppen
p10 = g.set("tPath", "string", it("KnapTegn", "string", KI()))
link(swk["10"], p10["execute"])
f10 = g.call(None, "MFind", selfctx=True)
link(p10["then"], f10["execute"])
c10 = g.cast(get("tW", "obj:Widget"), "", disp="UMG TB NAtron Ticket Button", path=TBTN9)
link(f10["then"], c10["execute"])
d10 = g.call_delegate(TBTN9, "On Click", c10.out, params=(("Widget", "obj:Object", c10.out),))
link(c10["then"], d10["execute"])
v10 = g.arrfunc("Array_Set", "real", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                TargetArray=g.get("tKnapVal", "real[]"), Index=gi(), Item=it("KnapVaerdi", "real", KI()), bSizeToFit=True)
link(d10["then"], v10["execute"]); link(c10["CastFailed"], v10["execute"])
# 11: print kvittering / 12: afslut vagt (log ud af ruten)
cn11 = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
link(swk["11"], cn11["execute"])
k11 = g.call_path(DISP, "Print Receipt", ins=(), pure=False,
                  target=g.call_path(NATRON, "Get Display", ins=(), outs=(("AsUMG TB NAtron Display", "obj:Object"),), pure=True, target=cn11.out)["AsUMG TB NAtron Display"])
link(cn11["then"], k11["execute"])
e11 = tag_plus1(k11["then"], "MK_")
cn12 = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
link(swk["12"], cn12["execute"])
k12 = g.call_path(DISP, "End Shift", ins=(), pure=False,
                  target=g.call_path(NATRON, "Get Display", ins=(), outs=(("AsUMG TB NAtron Display", "obj:Object"),), pure=True, target=cn12.out)["AsUMG TB NAtron Display"])
link(cn12["then"], k12["execute"])
# ---------- v34 skilt ----------
def tagstr_saet(start_pin, pre, val):
    a = g.set("tTagPre", "string", pre); link(start_pin, a["execute"])
    b = g.set("tTagS", "string", val); link(a["then"], b["execute"])
    c = g.call(None, "MTagSetS", selfctx=True); link(b["then"], c["execute"])
    return c["then"]
def tag_slet(start_pin, pre):
    a = g.set("tTagPre", "string", pre); link(start_pin, a["execute"])
    c = g.call(None, "MTagDel", selfctx=True); link(a["then"], c["execute"])
    return c["then"]
def navn_tag(start_pin, navn, tilfoej):
    ca = g.cast(bus_actor0(), "Actor"); link(start_pin, ca["execute"])
    tg = g.member_get("/Script/CoreUObject.Class'/Script/Engine.Actor'", "Tags", "name[]", ca.out)
    nm = S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),), InString=navn)
    if tilfoej:
        n = g.arrfunc("Array_AddUnique", "name", ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")], TargetArray=tg, NewItem=nm)
    else:
        n = g.arrfunc("Array_RemoveItem", "name", ins=[("TargetArray", "E[]"), ("Item", "E")], outs=[("ReturnValue", "bool")], TargetArray=tg, Item=nm)
    link(ca["then"], n["execute"])
    j = g.sequence(1); link(n["then"], j["execute"]); link(ca["CastFailed"], j["execute"])
    return j["then_0"]
txt_safe = lambda i: selS(it("tTxt", "string", i), "", ilt(i, arrlen("tTxt", "string")))
# 13: saet skiltet (linje = tekstfelt 0, destination = tekstfelt 1)
e13 = tagstr_saet(swk["13"], "SKL:", trim(txt_safe("0")))
e13 = tagstr_saet(e13, "SKD:", trim(txt_safe("1")))
e13 = navn_tag(e13, "SKA", True)
ikke13 = OR(streq(trim(txt_safe("1")), "Ikke i rute"), streq(trim(txt_safe("1")), "Ikke i route"))
b13 = g.branch(ikke13); link(e13, b13["execute"])
e13a = navn_tag(b13["then"], "SKI", True)
e13b = navn_tag(b13["else"], "SKI", False)
opd13 = g.call(None, "MSkiltOpd", selfctx=True)
link(e13a, opd13["execute"]); link(e13b, opd13["execute"])
# 14: skriv KnapTegn i tekstfelt nr. KnapVaerdi (hurtigvalg / fjern nummer)
t14 = g.arrfunc("Array_Set", "string", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                TargetArray=g.get("tTxt", "string[]"), Index=rnd(it("KnapVaerdi", "real", KI())), Item=it("KnapTegn", "string", KI()), bSizeToFit=True)
link(swk["14"], t14["execute"])
# 15: skiltet tilbage til ruten
e15 = tag_slet(swk["15"], "SKL:")
e15 = tag_slet(e15, "SKD:")
e15 = navn_tag(e15, "SKA", False)
e15 = navn_tag(e15, "SKI", False)
opd15 = g.call(None, "MSkiltOpd", selfctx=True); link(e15, opd15["execute"]); e15 = opd15["then"]
# 16: min rute -> linjenummer og endestation i felterne
cn16 = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
link(swk["16"], cn16["execute"])
trip16 = lambda: g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cn16.out)["Result"]
bt16 = g.break_struct("/Script/Fernbus.BusTripInfo", "BusTripInfo", trip16(), (("Route", "obj:Object"),))
lin16 = g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True,
               InName=g.member_get("/Script/CoreUObject.Class'/Script/Fernbus.LineRoute'", "Line", "name", bt16["Route"]))["ReturnValue"]
last16 = g.call_path(TRIPFN, "FBusTripInfo_GetLastStop", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                     outs=(("IsValid", "bool"), ("ReturnValue", "struct:/Script/Fernbus.RouteStopWithTime")), pure=True, static_default="x", a=trip16())
br16 = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", last16["ReturnValue"], (("StopIdent", "struct:/Script/RoadmapSystem.BusStopIdentifier"),))
end16 = stopnavn(br16["StopIdent"])
SETI = lambda i, val: g.arrfunc("Array_Set", "string", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                                TargetArray=g.get("tTxt", "string[]"), Index=i, Item=val, bSizeToFit=True)
s16a = SETI("0", lin16); link(cn16["then"], s16a["execute"])
s16b = SETI("1", end16); link(s16a["then"], s16b["execute"])
# ---------- v40 skift rute (knapper) ----------
# 18: vaelg raekke: gruppe = KnapVaerdi + rulning (gruppe KnapMin)
rg18 = rnd(it("KnapMin", "real", KI()))
v18 = add(it("KnapVaerdi", "real", KI()), selF(it("tKnapVal", "real", rnd(it("KnapMin", "real", KI()))), "0",
                                               AND(ige(rg18, "0"), ilt(rnd(it("KnapMin", "real", KI())), arrlen("tKnapVal", "real")))))
k18 = g.arrfunc("Array_Set", "real", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                TargetArray=g.get("tKnapVal", "real[]"), Index=gi(), Item=v18, bSizeToFit=True)
link(swk["18"], k18["execute"])
# 19: soeg (KnapVaerdi 0 = naer dig, 1 = linjen i tekstfelt 8). Gruppen (fanen) saettes til KnapVaerdi
k19 = g.arrfunc("Array_Set", "real", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                TargetArray=g.get("tKnapVal", "real[]"), Index=gi(), Item=it("KnapVaerdi", "real", KI()), bSizeToFit=True)
link(swk["19"], k19["execute"])
m19 = g.set("tRMode", "int", rnd(it("KnapVaerdi", "real", KI())))
link(k19["then"], m19["execute"])
e19 = g.call(None, "MRuteSoeg", selfctx=True)
link(m19["then"], e19["execute"])
# 20: vaelg tur -> trin 2 / 21: start
e20 = g.call(None, "MRuteVaelg", selfctx=True)
link(swk["20"], e20["execute"])
e21 = g.call(None, "MRuteStart", selfctx=True)
link(swk["21"], e21["execute"])
# 22: linjetastatur i tekstfelt 8 ("<" slet, "C" ryd, ellers tilfoej - max 4 tegn)
T8 = lambda: selS(it("tTxt", "string", "8"), "", ilt("8", arrlen("tTxt", "string")))
TG = lambda: it("KnapTegn", "string", KI())
ny22 = selS(S("LeftChop", (("SourceString", "string"), ("Count", "int")), SourceString=T8(), Count="1"),
            selS("", selS(cat(T8(), TG()), T8(), ilt(S("Len", (("S", "string"),), (("ReturnValue", "int"),), S=T8()), "4")),
                 S("EqualEqual_StrStr", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=TG(), B="C")),
            S("EqualEqual_StrStr", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=TG(), B="<"))
k22 = g.arrfunc("Array_Set", "string", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                TargetArray=g.get("tTxt", "string[]"), Index="8", Item=ny22, bSizeToFit=True)
link(swk["22"], k22["execute"])
RUTE_SLUT = [k18["then"], e19["then"], e20["then"], e21["then"], k22["then"]]

setp = g.arrfunc("Array_Set", "bool", ins=[("TargetArray", "E[]"), ("Index", "int"), ("Item", "E"), ("bSizeToFit", "bool")],
                 TargetArray=g.get("tKnapPrev", "bool[]"), Index=KI(), Item=get("tB", "bool"), bSizeToFit=True)
link(bk["else"], setp["execute"]); link(setk["then"], setp["execute"])
for pp in [bnul["else"], nul["then"], bsv["else"], cg["CastFailed"], sv["then"], lok7["then"], ca8["CastFailed"], rm8["then"], ad8["then"],
           c9["CastFailed"], bv9["else"], cn9["CastFailed"], cnt9["then"], v10["then"], cn11["CastFailed"], e11,
           cn12["CastFailed"], k12["then"], opd13["then"], t14["then"], e15, cn16["CastFailed"], s16b["then"]] + RUTE_SLUT:
    link(pp, setp["execute"])


# =========================================================
# v40 SKIFT RUTE
#  MRuteSoeg: fylder listen (tRTrips/tRTxt/tRDep/tRSi/tRKey) - tRMode 0 naer dig, 1 linje (tekstfelt 8)
#  MRuteTur:  vurderer tTrip2 og saetter den ind i listen sorteret efter afgang
#  MRuteVaelg: valgt raekke -> tRTrip + stopliste (trin 2)
#  MRuteStart: log ind paa turen fra det valgte stop, opdater missionen, pause-maerker
# =========================================================
g.next_col()
ev = g.custom_event("MRuteSoeg")
ch = Chain(g, ev["then"])
for v_, e_ in (("tRTrips", BTI), ("tRTwt", TWT), ("tRTxt", "string"), ("tRTil", "string"), ("tRDep", "real"), ("tRSi", "int"), ("tRKey", "real")):
    ch.then(ARRCLR(v_, e_))
setkv(ch, 0, "0")
setkv(ch, 1, "0")
setv(ch, "tRStat", "string", "Ingen afgange fundet")
gi_ = g.call("GS", "GetGameInstance", ins=(), outs=(("ReturnValue", "obj:Object"),), pure=True)["ReturnValue"]
cgi_ = g.cast(gi_, "", disp="TMLGame Instance", path=TMLGI)
ch.then(cgi_)
mapb_ = g.call_path(TMLGI, "GetSelectedMapInfo", ins=(), outs=(("ReturnValue", "obj:Object"),), pure=True, target=cgi_.out)["ReturnValue"]
setv(ch, "tOP", OPT_, g.call_path(MAPB, "GetCurrentOperatingPlan", ins=(), outs=(("ReturnValue", OPT_),), pure=True, target=mapb_)["ReturnValue"])
bop = g.branch(isvalid(get("tOP", OPT_)))
ch.then(bop)
f_op = g.set("tRStat", "string", "Fejl: fandt ikke koereplanen")
link(bop["else"], f_op["execute"]); link(cgi_["CastFailed"], f_op["execute"])
bmode = g.branch(ieq(get("tRMode", "int"), "1"))
link(bop["then"], bmode["execute"])
# ---- linje
cl = Chain(g, bmode["then"])
setv(cl, "tRLinje", "string", trim(selS(it("tTxt", "string", "8"), "", ilt("8", arrlen("tTxt", "string")))))
btom = g.branch(S("EqualEqual_StrStr", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=get("tRLinje", "string"), B=""))
cl.then(btom)
setv(Chain(g, btom["then"]), "tRStat", "string", "Skriv et linjenummer")
cl = Chain(g, btom["else"])
ma_ = _Node(g, "K2Node_MakeArray", [("NumInputs", "1")])
ma_.pin("Array", "out", "name[]")
link(s2n(get("tRLinje", "string")), ma_.pin("[0]", "in", "name"))
gtl = g.call_path(OPCLS, "GetToursByDateRange", ins=(("DateTimeStart", DTS), ("DateTimeEnd", DTS), ("LinesFilter", "name[]")),
                  outs=(("ReturnValue", TWT + "[]"),), pure=False, target=get("tOP", OPT_),
                  DateTimeStart=dt_plus(world_datetime(), "-14400"),
                  DateTimeEnd=dt_plus(world_datetime(), sub("90000", secs_of_day(world_datetime()))), LinesFilter=ma_["Array"])
cl.then(gtl)
setv(cl, "tRTours", TWT + "[]", gtl["ReturnValue"])
setv(cl, "tRStat", "string", cat(cat("AFGANGE I DAG · LINJE ", get("tRLinje", "string")), ""))
jl = g.sequence(1)
cl.then(jl, outpin="then_0")
# ---- naer dig: naermeste stoppested
cn_ = Chain(g, bmode["else"])
cab = g.cast(bus_actor0(), "Actor")
cn_.then(cab)
setv(cn_, "tRDiff", "real", "100000000")
setv(cn_, "tRI", "int", "-1")
gas = g.call("GS", "GetAllActorsOfClass", ins=(("ActorClass", "class:/Script/Engine.Actor"),), outs=(("OutActors", "obj:Actor[]"),))
gas["ActorClass"].defobj = "/Game/Gameplay/BP_BusStop.BP_BusStop_C"
cn_.then(gas)
setv(cn_, "tRStops", "obj:Actor[]", gas["OutActors"])
fls = g.forloop("0", isub(arrlen("tRStops", "obj:Actor"), "1"))
cn_.then(fls, outpin="LoopBody")
dist = g.call(None, "GetDistanceTo", target_cls="Actor", target=it("tRStops", "obj:Actor", fls["Index"]), pure=True,
              ins=(("OtherActor", "obj:Actor"),), outs=(("ReturnValue", "real"),), OtherActor=cab.out)["ReturnValue"]
bmin = g.branch(lt(dist, get("tRDiff", "real")))
cn_.then(bmin)
setv(cn_, "tRDiff", "real", g.call(None, "GetDistanceTo", target_cls="Actor", target=it("tRStops", "obj:Actor", fls["Index"]), pure=True,
                                     ins=(("OtherActor", "obj:Actor"),), outs=(("ReturnValue", "real"),), OtherActor=cab.out)["ReturnValue"])
setv(cn_, "tRI", "int", fls["Index"])
cn_ = Chain(g, fls["Completed"])
bfs = g.branch(ige(get("tRI", "int"), "0"))
cn_.then(bfs)
setv(Chain(g, bfs["else"]), "tRStat", "string", "Fandt intet stoppested")
cn_ = Chain(g, bfs["then"])
cvs = g.cast(it("tRStops", "obj:Actor", get("tRI", "int")), "", disp="Vehicle Stop Base", path=VSTOP)
cn_.then(cvs)
sid = g.call_path(VSTOP, "GetStopIdentifier", ins=(), outs=(("ReturnValue", BSI_),), pure=True, target=cvs.out)["ReturnValue"]
setv(cn_, "tRStop", BSI_, sid)
setv(cn_, "tRStopNavn", "string", stopnavn(get("tRStop", BSI_)))
cn_.then(ARRCLR("tLines", "name"))
fla = g.forloop("0", isub(arrlen("tRStops", "obj:Actor"), "1"))
cn_.then(fla, outpin="LoopBody")
cva = g.cast(it("tRStops", "obj:Actor", fla["Index"]), "", disp="Vehicle Stop Base", path=VSTOP)
cn_.then(cva)
sida = lambda: g.call_path(VSTOP, "GetStopIdentifier", ins=(), outs=(("ReturnValue", BSI_),), pure=True, target=cva.out)["ReturnValue"]
cn_.then(g.branch(S("EqualEqual_StriStri", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=stopnavn(sida()), B=get("tRStopNavn", "string"))))
gls = g.call_path(OPCLS, "GetLinesThatContainStop", ins=(("StopIdent", BSI_),), outs=(("ReturnValue", "name[]"),), pure=False,
                  target=get("tOP", OPT_), StopIdent=sida())
cn_.then(gls)
setv(cn_, "tLines2", "name[]", gls["ReturnValue"])
fll = g.forloop("0", isub(arrlen("tLines2", "name"), "1"))
cn_.then(fll, outpin="LoopBody")
cn_.then(g.arrfunc("Array_AddUnique", "name", ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                   TargetArray=g.get("tLines", "name[]"), NewItem=it("tLines2", "name", fll["Index"])))
cn_ = Chain(g, fla["Completed"])
gtn = g.call_path(OPCLS, "GetToursByDateRange", ins=(("DateTimeStart", DTS), ("DateTimeEnd", DTS), ("LinesFilter", "name[]")),
                  outs=(("ReturnValue", TWT + "[]"),), pure=False, target=get("tOP", OPT_),
                  DateTimeStart=dt_plus(world_datetime(), "-10800"), DateTimeEnd=dt_plus(world_datetime(), "7200"),
                  LinesFilter=g.get("tLines", "name[]"))
cn_.then(gtn)
setv(cn_, "tRTours", TWT + "[]", gtn["ReturnValue"])
setv(cn_, "tRStat", "string", cat(cat(cat("AFGANGE NÆR DIG · ", get("tRStopNavn", "string")), " ("),
                                  cat(i2s(rnd(div(get("tRDiff", "real"), "100"))), " m)")))
link(cn_.cur, jl["execute"])
# ---- faelles: alle ture -> ture (trips) fra nu af
cf = Chain(g, jl["then_0"])
flt_ = g.forloop("0", isub(arrlen("tRTours", TWT), "1"))
cf.then(flt_, outpin="LoopBody")
tr0 = g.call_path(TRIPFN, "FBusTripInfo_CreateFromTourAndDateTime",
                  ins=(("WorldTime", DTS), ("TimeTableDate", DTS), ("OperatingPlan", "obj:Object"), ("TourT", TWT)),
                  outs=(("ReturnValue", BTI),), pure=False, static_default="x",
                  WorldTime=world_datetime(), TimeTableDate=world_datetime(), OperatingPlan=get("tOP", OPT_),
                  TourT=it("tRTours", TWT, flt_["Index"]))
setv(cf, "tRTourCur", TWT, it("tRTours", TWT, flt_["Index"]))
cf.then(tr0)
setv(cf, "tTrip2", BTI, tr0["ReturnValue"])
setv(cf, "tROK", "bool", True)
flk = g.forloop("0", "30")
cf.then(flk, outpin="LoopBody")
cf.then(g.branch(get("tROK", "bool")))
callev(cf, "MRuteTur")
slut_ = g.call_path(TRIPFN, "FBusTripInfo_ReachedLastTrip", ins=(("a", BTI),), outs=(("ReturnValue", "bool"),), pure=True,
                    static_default="x", a=get("tTrip2", BTI))["ReturnValue"]
bsl = g.branch(OR(slut_, gt(dsek(rs_afg(r_stop_at(get("tTrip2", BTI), "0"))),
                              selF("43000", "7200", ieq(get("tRMode", "int"), "1")))))
cf.then(bsl)
setv(Chain(g, bsl["then"]), "tROK", "bool", False)
nxt = g.call_path(TRIPFN, "FBusTripInfo_GetNextTripInfo", ins=(("a", BTI), ("WorldTime", DTS), ("OperatingPlan", "obj:Object")),
                  outs=(("ReturnValue", BTI),), pure=False, static_default="x",
                  a=get("tTrip2", BTI), WorldTime=world_datetime(), OperatingPlan=get("tOP", OPT_))
cnx = Chain(g, bsl["else"])
cnx.then(nxt)
setv(cnx, "tTrip2", BTI, nxt["ReturnValue"])

# ---------------------------------------------------------
g.next_col()
ev = g.custom_event("MRuteTur")
ch = Chain(g, ev["then"])
ch.then(g.branch(AND(ige(nstops(get("tTrip2", BTI)), "2"), ilt(arrlen("tRDep", "real"), "80"))))
bm2 = g.branch(ieq(get("tRMode", "int"), "1"))
ch.then(bm2)
# linje: rigtig linje, start ved foerste stop
cA = Chain(g, bm2["then"])
cA.then(g.branch(S("EqualEqual_StriStri", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=tur_linje(), B=get("tRLinje", "string"))))
setv(cA, "tRF", "int", "0")
jA = g.sequence(1)
cA.then(jA, outpin="then_0")
# naer dig: find stoppet (paa navn) i turen - ikke endestationen
cB = Chain(g, bm2["else"])
setv(cB, "tRF", "int", "-1")
flj = g.forloop("0", isub(nstops(get("tTrip2", BTI)), "2"))
cB.then(flj, outpin="LoopBody")
cB.then(g.branch(AND(ilt(get("tRF", "int"), "0"),
                     S("EqualEqual_StriStri", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),),
                       A=rs_navn(r_stop_at(get("tTrip2", BTI), flj["Index"])), B=get("tRStopNavn", "string")))))
setv(cB, "tRF", "int", flj["Index"])
cB = Chain(g, flj["Completed"])
cB.then(g.branch(ige(get("tRF", "int"), "0")))
link(cB.cur, jA["execute"])
# faelles: afgangstid ved stoppet, kun fremtidige (op til 12 t / 2 t)
cC = Chain(g, jA["then_0"])
setv(cC, "tV", "real", rs_afg(r_stop_at(get("tTrip2", BTI), get("tRF", "int"))))
setv(cC, "tRNow", "real", dsek(get("tV", "real")))
cC.then(g.branch(AND(ge(get("tRNow", "real"), "-60"),
                     le(get("tRNow", "real"), selF("43000", "7200", ieq(get("tRMode", "int"), "1"))))))
# sorteret indsaettelse
setv(cC, "tRPos", "int", arrlen("tRKey", "real"))
flp = g.forloop("0", isub(arrlen("tRKey", "real"), "1"))
cC.then(flp, outpin="LoopBody")
cC.then(g.branch(AND(gt(it("tRKey", "real", flp["Index"]), get("tRNow", "real")), ilt(flp["Index"], get("tRPos", "int")))))
setv(cC, "tRPos", "int", flp["Index"])
cC = Chain(g, flp["Completed"])
P_ = lambda: get("tRPos", "int")
P3 = lambda: M("Multiply_IntInt", I2, (("ReturnValue", "int"),), A=get("tRPos", "int"), B="3")
cC.then(ARRINS("tRTrips", BTI, get("tTrip2", BTI), P_()))
cC.then(ARRINS("tRTwt", TWT, get("tRTourCur", TWT), P_()))
cC.then(ARRINS("tRDep", "real", get("tV", "real"), P_()))
cC.then(ARRINS("tRKey", "real", get("tRNow", "real"), P_()))
cC.then(ARRINS("tRSi", "int", get("tRF", "int"), P_()))
cC.then(ARRINS("tRTil", "string", cat("→ ", sidste_navn(get("tTrip2", BTI))), P_()))
cC.then(ARRINS("tRTxt", "string", cat(cat(tur_linje(), " · Kurs "), tur_kurs()), P_()))

# ---------------------------------------------------------
g.next_col()
ev = g.custom_event("MRuteVaelg")
ch = Chain(g, ev["then"])
bv_ = g.branch(ilt(kvi(1), arrlen("tRDep", "real")))
ch.then(bv_)
setv(Chain(g, bv_["else"]), "tRStat", "string", "Vælg en tur i listen først")
ch = Chain(g, bv_["then"])
setv(ch, "tRQ", "int", kvi(1))
setv(ch, "tRTrip", BTI, it("tRTrips", BTI, get("tRQ", "int")))
setv(ch, "tRTour", TWT, it("tRTwt", TWT, get("tRQ", "int")))
ch.then(ARRCLR("tRSt", "string"))
ch.then(ARRCLR("tRStDep", "real"))
flv = g.forloop("0", isub(nstops(get("tRTrip", BTI)), "1"))
ch.then(flv, outpin="LoopBody")
ch.then(ARRADD("tRSt", "string", rs_navn(r_stop_at(get("tRTrip", BTI), flv["Index"]))))
ch.then(ARRADD("tRSt", "string", hhmm(rs_afg(r_stop_at(get("tRTrip", BTI), flv["Index"])))))
ch.then(ARRADD("tRStDep", "real", rs_afg(r_stop_at(get("tRTrip", BTI), flv["Index"]))))
ch = Chain(g, flv["Completed"])
setv(ch, "tRTitel", "string", cat("Linje ", it("tRTxt", "string", get("tRQ", "int"))))
NS = lambda: arrlen("tRStDep", "real")
setv(ch, "tRUnder", "string", cat(cat(cat(it("tRSt", "string", "0"), " "), cat(it("tRSt", "string", "1"), " → ")),
                                  cat(cat(it("tRSt", "string", isub(M("Multiply_IntInt", I2, (("ReturnValue", "int"),), A=NS(), B="2"), "2")), " "),
                                      it("tRSt", "string", isub(M("Multiply_IntInt", I2, (("ReturnValue", "int"),), A=NS(), B="2"), "1")))))
setkv(ch, 3, i2d(it("tRSi", "int", get("tRQ", "int"))))
setkv(ch, 2, i2d(imax(isub(it("tRSi", "int", get("tRQ", "int")), "2"), "0")))
setkv(ch, 4, "2")

# ---------------------------------------------------------
g.next_col()
ev = g.custom_event("MRuteStart")
ch = Chain(g, ev["then"])
setv(ch, "tRQ", "int", kvi(3))
bst_ = g.branch(AND(ilt(get("tRQ", "int"), arrlen("tRStDep", "real")), ilt(get("tRQ", "int"), nstops(get("tRTrip", BTI)))))
ch.then(bst_)
ch = Chain(g, bst_["then"])
ch.then(g.set_fields(BTIP, get("tRTrip", BTI), (("CurrentStopIndex", "int"),), CurrentStopIndex=get("tRQ", "int")))
cnh = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
ch.then(cnh)
disp_ = g.call_path(NATRON, "Get Display", ins=(), outs=(("AsUMG TB NAtron Display", "obj:Object"),), pure=True, target=cnh.out)["AsUMG TB NAtron Display"]
ch.then(g.call_path(DISP, "Change Tour LogIn Status", ins=(("Tour Logged In", "bool"), ("Trip Info", BTI)), pure=False,
                    target=disp_, **{"Tour Logged In": True, "Trip Info": get("tRTrip", BTI)}))
# missionen (fri koersel) faar den nye tur
mis = g.call_path(MISSFN, "Get Mission", ins=(), outs=(("Mission", "obj:Object"),), pure=True,
                  static_default="/Game/Gameplay/Mission/BP_MissionFunctions.Default__BP_MissionFunctions_C")["Mission"]
cmi = g.cast(mis, "", disp="BP the Bus Mission", path=MISSC)
ch.then(cmi)
smi = g.member_set(MISSC, "Trip", BTI, cmi.out, get("tRTrip", BTI))
link(cmi["then"], smi["execute"])
TOURO = lambda: g.break_struct("/Script/Fernbus.TourWithTime", "TourWithTime", get("tRTour", TWT), (("Tour", "obj:/Script/Fernbus.Tour"),))["Tour"]
smt = g.member_set(MISSC, "Tour", "obj:/Script/Fernbus.Tour", cmi.out, TOURO())
link(smi["then"], smt["execute"])
smi = smt
jm = g.sequence(1)
link(smi["then"], jm["execute"]); link(cmi["CastFailed"], jm["execute"])
ch = Chain(g, jm["then_0"])
TMLPS = "/Script/CoreUObject.Class'/Script/Fernbus.TMLPlayerState'"
ps_ = g.call("GS", "GetPlayerState", ins=(("PlayerStateIndex", "int"),), outs=(("ReturnValue", "obj:/Script/Engine.PlayerState"),), pure=True, PlayerStateIndex="0")["ReturnValue"]
cps = g.cast(ps_, "", disp="TMLPlayer State", path=TMLPS)
ch.then(cps)
ident_ = g.call_path(TOURC, "GetIdent", ins=(), outs=(("ReturnValue", "struct:/Script/Fernbus.TourIdentifier"),), pure=True, target=TOURO())["ReturnValue"]
asg = g.call_path(TMLPS, "AssignTour", ins=(("Tour", "struct:/Script/Fernbus.TourIdentifier"),), pure=False, target=cps.out, Tour=ident_)
link(cps["then"], asg["execute"])
gpm = g.call("GS", "GetActorOfClass", ins=(("ActorClass", "class:/Script/Engine.Actor"),), outs=(("ReturnValue", "obj:Actor"),))
gpm["ActorClass"].defobj = "/Script/Fernbus.PassengerManager"
link(asg["then"], gpm["execute"]); link(cps["CastFailed"], gpm["execute"])
cpm = g.cast(gpm["ReturnValue"], "", disp="Passenger Manager", path="/Script/CoreUObject.Class'/Script/Fernbus.PassengerManager'")
link(gpm["then"], cpm["execute"])
upt = g.call_path("/Script/CoreUObject.Class'/Script/Fernbus.PassengerManager'", "UpdatePlayerTours", ins=(), pure=False, target=cpm.out)
link(cpm["then"], upt["execute"])
jp = g.sequence(1)
link(upt["then"], jp["execute"]); link(cpm["CastFailed"], jp["execute"])
ch = Chain(g, jp["then_0"])
e_ = tag_saet(ch.cur, "MR_", it("tRStDep", "real", get("tRQ", "int")))
e_ = tagstr_saet(e_, "MRS:", it("tRSt", "string", M("Multiply_IntInt", I2, (("ReturnValue", "int"),), A=get("tRQ", "int"), B="2")))
e_ = tagstr_saet(e_, "MRT:", get("tRTitel", "string"))
e_ = navn_tag(e_, "MoviaRute", False)
ch = Chain(g, e_)
setkv(ch, 4, "0")

# =========================================================
# MTagGet: tTagPre -> tTagVal (tal efter prefix, 0 hvis intet) + tTagFound (hele maerkenavnet)
# MTagSet: tTagPre + tTagNy -> erstatter maerket
# =========================================================
g.next_col()
ACTORC = "/Script/CoreUObject.Class'/Script/Engine.Actor'"
ev = g.custom_event("MTagGet")
ch = Chain(g, ev["then"])
setv(ch, "tTagVal", "real", "0")
setv(ch, "tTagFound", "string", "")
cat_ = g.cast(bus_actor0(), "Actor")
ch.then(cat_)
tagsg = lambda: g.member_get(ACTORC, "Tags", "name[]", cat_.out)
ntag = g.arrfunc("Array_Length", "name", ins=[("TargetArray", "E[]")], outs=[("ReturnValue", "int")], pure=True, TargetArray=tagsg())["ReturnValue"]
flt = g.forloop("0", isub(ntag, "1"))
ch.then(flt, outpin="LoopBody")
tnavn = lambda: g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True,
                       InName=g.item_of(tagsg(), "name", flt["Index"]))["ReturnValue"]
bst = g.branch(starts(tnavn(), get("tTagPre", "string")))
ch.then(bst)
setv(ch, "tTagFound", "string", tnavn())
setv(ch, "tTagVal", "real", s2d(S("RightChop", (("SourceString", "string"), ("Count", "int")), SourceString=tnavn(),
                                   Count=S("Len", (("S", "string"),), (("ReturnValue", "int"),), S=get("tTagPre", "string")))))

g.next_col()
ev = g.custom_event("MTagSet")
ch = Chain(g, ev["then"])
callev(ch, "MTagGet")
cas = g.cast(bus_actor0(), "Actor")
ch.then(cas)
tagss = lambda: g.member_get(ACTORC, "Tags", "name[]", cas.out)
bfd = g.branch(S("NotEqual_StrStr", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=get("tTagFound", "string"), B=""))
ch.then(bfd)
rmt = g.arrfunc("Array_RemoveItem", "name", ins=[("TargetArray", "E[]"), ("Item", "E")], outs=[("ReturnValue", "bool")],
                TargetArray=tagss(), Item=S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),), InString=get("tTagFound", "string")))
link(bfd["then"], rmt["execute"])
adt = g.arrfunc("Array_AddUnique", "name", ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                TargetArray=tagss(), NewItem=S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),),
                                               InString=cat(get("tTagPre", "string"), i2s(rnd(get("tTagNy", "real"))))))
link(rmt["then"], adt["execute"]); link(bfd["else"], adt["execute"])

g.next_col()
ev = g.custom_event("MTagSetS")
ch = Chain(g, ev["then"])
callev(ch, "MTagGet")
cas2 = g.cast(bus_actor0(), "Actor")
ch.then(cas2)
tagss2 = lambda: g.member_get(ACTORC, "Tags", "name[]", cas2.out)
bfd2 = g.branch(S("NotEqual_StrStr", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=get("tTagFound", "string"), B=""))
ch.then(bfd2)
rmt2 = g.arrfunc("Array_RemoveItem", "name", ins=[("TargetArray", "E[]"), ("Item", "E")], outs=[("ReturnValue", "bool")],
                 TargetArray=tagss2(), Item=S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),), InString=get("tTagFound", "string")))
link(bfd2["then"], rmt2["execute"])
adt2 = g.arrfunc("Array_AddUnique", "name", ins=[("TargetArray", "E[]"), ("NewItem", "E")], outs=[("ReturnValue", "int")],
                 TargetArray=tagss2(), NewItem=S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),),
                                                 InString=cat(get("tTagPre", "string"), get("tTagS", "string"))))
link(rmt2["then"], adt2["execute"]); link(bfd2["else"], adt2["execute"])

# MSkiltOpd: faa bussens skilt til at hente teksten igen (spillets "Display Overrides Changed")
BCCLS = "/Script/Engine.BlueprintGeneratedClass'/Game/Gameplay/Vehicles/Common/BP_BoardComputer_TheBus_NAtron.BP_BoardComputer_TheBus_NAtron_C'"
g.next_col()
ev = g.custom_event("MSkiltOpd")
ch = Chain(g, ev["then"])
chop4 = lambda: S("RightChop", (("SourceString", "string"), ("Count", "int")), SourceString=get("tTagFound", "string"), Count="4")
setv(ch, "tTagPre", "string", "SKL:")
callev(ch, "MTagGet")
setv(ch, "tStr", "string", chop4())
setv(ch, "tTagPre", "string", "SKD:")
callev(ch, "MTagGet")
setv(ch, "tRes", "string", chop4())
setv(ch, "tTagPre", "string", "SKA")
callev(ch, "MTagGet")
setv(ch, "tOK", "bool", S("NotEqual_StrStr", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=get("tTagFound", "string"), B=""))
ga = g.call("GS", "GetAllActorsOfClass", ins=(("ActorClass", "class:/Script/Engine.Actor"),), outs=(("OutActors", "obj:Actor[]"),))
ga["ActorClass"].defobj = "/Game/Gameplay/Vehicles/Common/BP_BoardComputer_TheBus_NAtron.BP_BoardComputer_TheBus_NAtron_C"
ch.then(ga)
nga = g.arrfunc("Array_Length", "obj:Actor", ins=[("TargetArray", "E[]")], outs=[("ReturnValue", "int")], pure=True, TargetArray=ga["OutActors"])["ReturnValue"]
flb = g.forloop("0", isub(nga, "1"))
ch.then(flb, outpin="LoopBody")
cbc = g.cast(g.item_of(ga["OutActors"], "obj:Actor", flb["Index"]), "", disp="BP Board Computer The Bus NAtron", path=BCCLS)
ch.then(cbc)
ch.then(g.member_set(BCCLS, "MoviaSkiltAktiv", "bool", cbc.out, get("tOK", "bool")))
ch.then(g.member_set(BCCLS, "MoviaSkiltL", "string", cbc.out, get("tStr", "string")))
ch.then(g.member_set(BCCLS, "MoviaSkiltD", "string", cbc.out, get("tRes", "string")))
dcl = g.call_delegate(BCCLS, "Display Overrides Changed", cbc.out)
dcl.props[0] = ("DelegateReference", '(MemberParent="%s",MemberName="Display Overrides Changed",MemberGuid=7574126249EBB6B4EB6BB4AE160EDBCA)' % BCCLS)
ch.then(dcl)

g.next_col()
ev = g.custom_event("MTagDel")
ch = Chain(g, ev["then"])
callev(ch, "MTagGet")
cas3 = g.cast(bus_actor0(), "Actor")
ch.then(cas3)
bfd3 = g.branch(S("NotEqual_StrStr", (("A", "string"), ("B", "string")), (("ReturnValue", "bool"),), A=get("tTagFound", "string"), B=""))
ch.then(bfd3)
rmt3 = g.arrfunc("Array_RemoveItem", "name", ins=[("TargetArray", "E[]"), ("Item", "E")], outs=[("ReturnValue", "bool")],
                 TargetArray=g.member_get(ACTORC, "Tags", "name[]", cas3.out),
                 Item=S("Conv_StringToName", (("InString", "string"),), (("ReturnValue", "name"),), InString=get("tTagFound", "string")))
link(bfd3["then"], rmt3["execute"])

# =========================================================
# MPause: taeller pause (holder ved stop, afgang om mere end 2 min) og gemmer den paa bussen hvert 5. sek
# =========================================================
g.next_col()
ev = g.custom_event("MPause")
ch = Chain(g, ev["then"])
bld_ = g.branch(get("tPauseLoaded", "bool"))
ch.then(bld_)
lp = Chain(g, bld_["else"])
setv(lp, "tTagPre", "string", "MP_")
callev(lp, "MTagGet")
setv(lp, "tPauseSum", "real", get("tTagVal", "real"))
setv(lp, "tPauseGemt", "real", now())
ldn = setv(lp, "tPauseLoaded", "bool", True)
cnp = g.cast(get("Host", "obj:UserWidget"), "", disp="UMG TB Natron Base", path=NATRON)
link(bld_["then"], cnp["execute"])
pch = Chain(g, cnp["then"])
tripP = g.call_path(NATRON, "Get Trip Info", ins=(), outs=(("Result", "struct:/Script/Fernbus.BusTripInfo"),), pure=True, target=cnp.out)["Result"]
curP = g.call_path(TRIPFN, "FBusTripInfo_GetCurrentStop", ins=(("a", "struct:/Script/Fernbus.BusTripInfo"),),
                   outs=(("IsValid", "bool"), ("ReturnValue", RSWT)), pure=True, static_default="x", a=tripP)
bcP = g.break_struct("/Script/Fernbus.RouteStopWithTime", "RouteStopWithTime", curP["ReturnValue"], (("DepartureTime", "struct:/Script/CoreUObject.DateTime"),))
pawnP = g.call("GS", "GetPlayerPawn", ins=(("PlayerIndex", "int"),), outs=(("ReturnValue", "obj:Actor"),), pure=True, PlayerIndex="0")["ReturnValue"]
holder = AND(AND(curP["IsValid"], gt(sub(secs_of_day(bcP["DepartureTime"]), secs_of_day(world_datetime())), "120")), lt(fart_kmt(pawnP), "3"))
bph = g.branch(holder)
pch.then(bph)
pch.then(g.set("tPauseSum", "real", add(get("tPauseSum", "real"), get("DT", "real"))))
bgem = g.branch(gt(sub(now(), get("tPauseGemt", "real")), "5"))
pch.then(bgem)
pg = g.set("tPauseGemt", "real", now())
link(bgem["then"], pg["execute"])
tag_saet(pg["then"], "MP_", get("tPauseSum", "real"))

g.next_col()
ev = g.custom_event("MoviaUpdate")
ch = Chain(g, ev["then"])
# v38: find bussen ud fra skaermens egen widget-komponent (ejer -> oeverste forælder), ellers spillerens bus
wcb = g.call("Tml", "GetWidgetComponentByWidget", ins=(("Widget", "obj:UserWidget"),), outs=(("ReturnValue", "obj:WidgetComponent"),),
             Widget=get("Host", "obj:UserWidget"))
ch.then(wcb)
ejer = lambda: g.call_path("/Script/CoreUObject.Class'/Script/Engine.ActorComponent'", "GetOwner", ins=(), outs=(("ReturnValue", "obj:Actor"),),
                           pure=True, target=wcb["ReturnValue"])["ReturnValue"]
par = lambda a: g.call(None, "GetAttachParentActor", target_cls="Actor", target=a, pure=True, outs=(("ReturnValue", "obj:Actor"),))["ReturnValue"]
selO = lambda a, b, pick: g.call("Math", "SelectObject", ins=(("A", "obj:Object"), ("B", "obj:Object"), ("bSelectA", "bool")),
                                 outs=(("ReturnValue", "obj:Object"),), pure=True, A=a, B=b, bSelectA=pick)["ReturnValue"]
top = selO(par(par(ejer())), selO(par(ejer()), ejer(), isvalid(par(ejer()))), isvalid(par(par(ejer()))))
setv(ch, "tBus", "obj:Object", selO(top, bus_actor_spiller(), isvalid(ejer())))
setv(ch, "DT", "real", sub(now(), get("LastTime", "real")))
setv(ch, "LastTime", "real", now())
callev(ch, "MSidst")
callev(ch, "MKnap")
callev(ch, "MNavi")
callev(ch, "MAfg")
callev(ch, "MPause")
fl = g.forloop("0", isub(arrlen("RAction", "int"), "1"))
ch.then(fl, outpin="LoopBody")
setv(ch, "tR", "int", fl["Index"])
callev(ch, "MEval")
callev(ch, "MApply")
ch = Chain(g, fl["Completed"])
wc = g.call("Tml", "GetWidgetComponentByWidget", ins=(("Widget", "obj:UserWidget"),), outs=(("ReturnValue", "obj:WidgetComponent"),),
            Widget=get("Host", "obj:UserWidget"))
ch.then(wc)
bw = g.branch(isvalid(wc["ReturnValue"]))
ch.then(bw)
ch.then(g.call(None, "RequestRenderUpdate", target_cls="WidgetComponent", target=wc["ReturnValue"]))

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "motor.t3d"
    open(out, "w", newline="").write(g.text())
    print(len(g.nodes), "noder,", len(g.text()), "tegn")
