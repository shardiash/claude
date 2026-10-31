# -*- coding: utf-8 -*-
"""Get Display Overrides(NEW) i BP_BoardComputer_TheBus_NAtron:
foerst tjek om bussen har maerket SKA (eget skilt fra Movia-menuen). Saa returneres
linje (SKL:...) og destination (SKD:...). Ellers koerer spillets egen logik som foer.
Brug: python3 skiltgen.py original.t3d ud.t3d"""
import re, sys, uuid
import bpgen
from bpgen import Graph, link

src, ud = sys.argv[1], sys.argv[2]
t = open(src, encoding="utf-8", errors="replace").read().replace("\r\n", "\n")
blokke = re.findall(r"(Begin Object .*?\nEnd Object)", t, re.S)
gid = lambda: uuid.uuid4().hex.upper()

entry = [b for b in blokke if "K2Node_FunctionEntry" in b.split("\n")[0]][0]
m = re.search(r'PinName="then".*?LinkedTo=\((\S+) (\w+),\)', entry)
foerste_node, foerste_pin = m.group(1), m.group(2)
entry_ref = re.search(r'Name="([^"]+)"', entry).group(1)
entry_then = re.search(r'PinId=(\w+),PinName="then"', entry).group(1)
res1 = [b for b in blokke if "K2Node_FunctionResult" in b.split("\n")[0]][0]


class Stub:
    def __init__(self, node, pid):
        self.node = type("N", (), {"name": node})()
        self.id = pid


g = Graph()
def S(f, ins, outs=(("ReturnValue", "string"),), **v): return g.call("Str", f, ins=ins, outs=outs, pure=True, **v)["ReturnValue"]
ACTOR = "/Script/CoreUObject.Class'/Script/Engine.Actor'"
par = g.call(None, "GetAttachParentActor", target_cls="Actor", pure=True, outs=(("ReturnValue", "obj:Actor"),))["ReturnValue"]
par2 = g.call(None, "GetAttachParentActor", target_cls="Actor", pure=True, outs=(("ReturnValue", "obj:Actor"),))["ReturnValue"]
ejer = g.call(None, "GetOwner", target_cls="Actor", pure=True, outs=(("ReturnValue", "obj:Actor"),))["ReturnValue"]
gyl = g.call("Sys", "IsValid", ins=(("Object", "obj:Object"),), outs=(("ReturnValue", "bool"),), pure=True, Object=par2)["ReturnValue"]
bus = g.call("Math", "SelectObject", ins=(("A", "obj:Object"), ("B", "obj:Object"), ("bSelectA", "bool")),
             outs=(("ReturnValue", "obj:Object"),), pure=True, A=par, B=ejer, bSelectA=gyl)["ReturnValue"]
cb = g.cast(bus, "Actor")
har = g.call(None, "ActorHasTag", target_cls="Actor", target=cb.out, pure=True, ins=(("Tag", "name"),), outs=(("ReturnValue", "bool"),), Tag="SKA")["ReturnValue"]
br = g.branch(har)
link(cb["then"], br["execute"])
sl = g.set("MoviaSkiltL", "string", ""); link(br["then"], sl["execute"])
sd = g.set("MoviaSkiltD", "string", ""); link(sl["then"], sd["execute"])
tags = lambda: g.member_get(ACTOR, "Tags", "name[]", cb.out)
n = g.arrfunc("Array_Length", "name", ins=[("TargetArray", "E[]")], outs=[("ReturnValue", "int")], pure=True, TargetArray=tags())["ReturnValue"]
fl = g.forloop("0", g.call("Math", "Subtract_IntInt", ins=(("A", "int"), ("B", "int")), outs=(("ReturnValue", "int"),), pure=True, A=n, B="1")["ReturnValue"])
link(sd["then"], fl["execute"])
tnavn = lambda: g.call("Str", "Conv_NameToString", ins=(("InName", "name"),), outs=(("ReturnValue", "string"),), pure=True,
                       InName=g.item_of(tags(), "name", fl["Index"]))["ReturnValue"]
starts = lambda p: S("StartsWith", (("SourceString", "string"), ("InPrefix", "string")), (("ReturnValue", "bool"),), SourceString=tnavn(), InPrefix=p)
chop = lambda: S("RightChop", (("SourceString", "string"), ("Count", "int")), SourceString=tnavn(), Count="4")
bL = g.branch(starts("SKL:")); link(fl["LoopBody"], bL["execute"])
setL = g.set("MoviaSkiltL", "string", chop()); link(bL["then"], setL["execute"])
bD = g.branch(starts("SKD:")); link(bL["else"], bD["execute"]); link(setL["then"], bD["execute"])
setD = g.set("MoviaSkiltD", "string", chop()); link(bD["then"], setD["execute"])
getL = g.get("MoviaSkiltL", "string")
getD = g.get("MoviaSkiltD", "string")

# min egen FunctionResult (klon af spillets)
RN = "K2Node_FunctionResult_950"
res = res1.split("\n")
res[0] = re.sub(r' ExportPath="[^"]*"', "", res[0]).replace(re.search(r'Name="([^"]+)"', res[0]).group(1), RN)
ny = []
pids = {}
for linje in res:
    if linje.strip().startswith("NodeGuid="):
        linje = "   NodeGuid=" + gid()
    elif linje.strip().startswith("NodePosX="):
        linje = "   NodePosX=2400"
    elif linje.strip().startswith("NodePosY="):
        linje = "   NodePosY=-700"
    elif "CustomProperties Pin" in linje:
        pn = re.search(r'PinName="([^"]*)"', linje).group(1)
        pid = gid(); pids[pn] = pid
        linje = re.sub(r"PinId=\w+", "PinId=" + pid, linje)
        linje = re.sub(r"LinkedTo=\([^)]*\),", "", linje)
        if pn == "Has Active Overrides":
            linje = re.sub(r'DefaultValue="[^"]*"', 'DefaultValue="true"', linje) if "DefaultValue=" in linje else linje.replace("PersistentGuid=", 'DefaultValue="true",PersistentGuid=')
    ny.append(linje)
def kobl(minpin, pn):
    minpin.links.append(Stub(RN, pids[pn]))
    i = [k for k, l in enumerate(ny) if 'PinName="%s"' % pn in l][0]
    ny[i] = ny[i].replace("PersistentGuid=", "LinkedTo=(%s %s,),PersistentGuid=" % (minpin.node.name, minpin.id))
kobl(fl["Completed"], "execute")
kobl(getL, "Override Line")
kobl(getD, "Override Destination")

# spillets foerste node: ellers/fejl gaar dertil
foer = Stub(foerste_node, foerste_pin)
for p in (cb["CastFailed"], br["else"]):
    p.links.append(foer)
ud_blokke = []
for b in blokke:
    if b is entry:
        continue
    navn = re.search(r'Name="([^"]+)"', b.split("\n")[0]).group(1)
    if navn == foerste_node:
        ref = "%s %s" % (entry_ref, entry_then)
        assert ref in b, "fandt ikke entry-link i foerste node"
        b = b.replace(ref, "%s %s,%s %s" % (cb.name, cb["CastFailed"].id, br.name, br["else"].id))
    ud_blokke.append(b)
for k, nd in enumerate([x for x in g.nodes if x is not cb]):
    nd.x = 450 + (k % 7) * 320
    nd.y = -1500 + (k // 7) * 170
cb.x, cb.y = 91, -300
txt = "\n".join(ud_blokke) + "\n" + g.text().replace("\r\n", "\n") + "\n".join(ny) + "\n"
open(ud, "w", newline="").write(txt.replace("\n", "\r\n"))
print("foerste node:", foerste_node, "| min foerste node:", cb.name, "| noder:", len(ud_blokke) + len(g.nodes) + 1)
