# -*- coding: utf-8 -*-
"""Lille generator for Unreal Blueprint-node tekst (T3D) der kan indsaettes med Ctrl+V."""
import uuid

SELF_CLASS = "/Script/UMG.WidgetBlueprintGeneratedClass'/Game/MoviaSkaerme/WBP_MoviaMotor.WBP_MoviaMotor_C'"
LIB = {
    "Math": "/Script/Engine.KismetMathLibrary",
    "Str": "/Script/Engine.KismetStringLibrary",
    "Text": "/Script/Engine.KismetTextLibrary",
    "Sys": "/Script/Engine.KismetSystemLibrary",
    "Arr": "/Script/Engine.KismetArrayLibrary",
    "GS": "/Script/Engine.GameplayStatics",
    "Tml": "/Script/TmlCore.CoreFunctionLibrary",
}
CLS = {
    "PanelWidget": "/Script/UMG.PanelWidget",
    "UserWidget": "/Script/UMG.UserWidget", "Widget": "/Script/UMG.Widget", "TextBlock": "/Script/UMG.TextBlock",
    "Border": "/Script/UMG.Border", "Image": "/Script/UMG.Image", "WidgetComponent": "/Script/UMG.WidgetComponent",
    "Object": "/Script/CoreUObject.Object", "Actor": "/Script/Engine.Actor", "Pawn": "/Script/Engine.Pawn",
}
STRUCT = {
    "LinearColor": "/Script/CoreUObject.LinearColor", "SlateColor": "/Script/SlateCore.SlateColor",
    "SlateBrush": "/Script/SlateCore.SlateBrush",
}
ENUM_VIS = "/Script/UMG.ESlateVisibility"


def gid():
    return uuid.uuid4().hex.upper()


def T(spec):
    """'exec' 'bool' 'int' 'real' 'string' 'text' 'name' 'obj:Widget' 'struct:LinearColor' 'enum:Vis'
       efterfulgt af [] for array."""
    arr = spec.endswith("[]")
    s = spec[:-2] if arr else spec
    cat, sub, subobj = s, "", "None"
    if s == "real":
        sub = "double"
    elif s.startswith("obj:"):
        cat = "object"
        k = s[4:]
        subobj = "\"/Script/CoreUObject.Class'%s'\"" % CLS.get(k, k)
    elif s.startswith("struct:"):
        cat = "struct"
        k = s[7:]
        subobj = "\"/Script/CoreUObject.ScriptStruct'%s'\"" % STRUCT.get(k, k)
    elif s.startswith("class:"):
        cat = "class"
        subobj = "\"/Script/CoreUObject.Class'%s'\"" % s[6:]
    elif s.startswith("enum:"):
        cat = "byte"
        subobj = "\"/Script/CoreUObject.Enum'%s'\"" % ENUM_VIS
    elif s == "wild":
        cat = "wildcard"
    return cat, sub, subobj, ("Array" if arr else "None")


class Pin:
    def __init__(self, node, name, direction, spec, default=None, hidden=False, defobj=None):
        self.node, self.name, self.dir, self.spec = node, name, direction, spec
        self.id = gid()
        self.default = default
        self.hidden = hidden
        self.defobj = defobj
        self.links = []

    def text(self):
        cat, sub, subobj, cont = T(self.spec)
        f = ['PinId=%s' % self.id, 'PinName="%s"' % self.name]
        if self.dir == "out":
            f.append('Direction="EGPD_Output"')
        f += ['PinType.PinCategory="%s"' % cat, 'PinType.PinSubCategory="%s"' % sub,
              'PinType.PinSubCategoryObject=%s' % subobj, 'PinType.PinSubCategoryMemberReference=()',
              'PinType.PinValueType=()', 'PinType.ContainerType=%s' % cont,
              'PinType.bIsReference=False', 'PinType.bIsConst=False', 'PinType.bIsWeakPointer=False',
              'PinType.bIsUObjectWrapper=False', 'PinType.bSerializeAsSinglePrecisionFloat=False']
        if self.default is not None:
            f.append('DefaultValue="%s"' % str(self.default).replace('"', '\\"'))
        if self.defobj:
            f.append('DefaultObject="%s"' % self.defobj)
        if self.links:
            f.append('LinkedTo=(%s,)' % ",".join("%s %s" % (p.node.name, p.id) for p in self.links))
        f += ['PersistentGuid=00000000000000000000000000000000', 'bHidden=%s' % ("True" if self.hidden else "False"),
              'bNotConnectable=False', 'bDefaultValueIsReadOnly=False', 'bDefaultValueIsIgnored=False',
              'bAdvancedView=False', 'bOrphanedPin=False', '']
        return "   CustomProperties Pin (%s)" % ",".join(f)


class Node:
    def __init__(self, g, cls, props):
        g.n += 1
        self.g = g
        self.cls = cls
        self.name = "%s_%d" % (cls, 900 + g.n)
        self.props = props
        self.pins = []
        self.x, self.y = g.pos()
        g.nodes.append(self)

    def pin(self, name, direction, spec, default=None, hidden=False, defobj=None):
        p = Pin(self, name, direction, spec, default, hidden, defobj)
        self.pins.append(p)
        return p

    def __getitem__(self, name):
        for p in self.pins:
            if p.name == name:
                return p
        raise KeyError("%s har ingen pin %s (har %s)" % (self.name, name, [p.name for p in self.pins]))

    def text(self):
        lines = ['Begin Object Class=/Script/BlueprintGraph.%s Name="%s"' % (self.cls, self.name)]
        for k, v in self.props:
            lines.append("   %s=%s" % (k, v))
        lines += ["   NodePosX=%d" % self.x, "   NodePosY=%d" % self.y, "   NodeGuid=%s" % gid()]
        lines += [p.text() for p in self.pins]
        lines.append("End Object")
        return "\r\n".join(lines)


def link(a, b):
    """a og b er Pins (ud -> ind)."""
    if a.dir == "in" and b.dir == "out":
        a, b = b, a
    a.links.append(b)
    b.links.append(a)


class Graph:
    def __init__(self):
        self.nodes = []
        self.n = 0
        self.col = 0
        self.row = 0

    def pos(self):
        self.row += 1
        return self.col * 420, self.row * 140

    def next_col(self):
        self.col += 1
        self.row = 0

    def text(self):
        return "\r\n".join(n.text() for n in self.nodes) + "\r\n"

    # ---------- byggeklodser ----------
    def _val(self, pin, v):
        if isinstance(v, Pin):
            link(v, pin)
        elif v is not None:
            if isinstance(v, bool):
                pin.default = "true" if v else "false"
            else:
                pin.default = v

    def custom_event(self, navn):
        n = Node(self, "K2Node_CustomEvent", [("CustomFunctionName", '"%s"' % navn)])
        n.pin("OutputDelegate", "out", "delegate")
        n.pin("then", "out", "exec")
        return n

    def event(self, parent, navn, outs=()):
        n = Node(self, "K2Node_Event", [("EventReference", "(MemberParent=\"/Script/CoreUObject.Class'%s'\",MemberName=\"%s\")" % (parent, navn)),
                                        ("bOverrideFunction", "True")])
        n.pin("OutputDelegate", "out", "delegate")
        n.pin("then", "out", "exec")
        for o, s in outs:
            n.pin(o, "out", s)
        return n

    def call(self, lib, func, ins=(), outs=(), pure=False, target=None, target_cls=None, selfctx=False, **vals):
        """lib: noegle i LIB (statisk), eller None for medlemsfunktion (target_cls)."""
        if selfctx:
            ref = '(MemberName="%s",bSelfContext=True)' % func
        elif lib:
            ref = "(MemberParent=\"/Script/CoreUObject.Class'%s'\",MemberName=\"%s\")" % (LIB[lib], func)
        else:
            ref = "(MemberParent=\"/Script/CoreUObject.Class'%s'\",MemberName=\"%s\")" % (CLS[target_cls], func)
        props = [("FunctionReference", ref)]
        if pure:
            props.append(("bDefaultsToPureFunc", "True"))
        n = Node(self, "K2Node_CallFunction", props)
        if not pure:
            n.pin("execute", "in", "exec")
            n.pin("then", "out", "exec")
        if lib and not selfctx:
            pkg, kl = LIB[lib].rsplit(".", 1)
            n.pin("self", "in", "obj:" + LIB[lib], hidden=True, defobj="%s.Default__%s" % (pkg, kl))
        elif target_cls:
            sp = n.pin("self", "in", "obj:" + target_cls)
            self._val(sp, target)
        for nm, spec in ins:
            p = n.pin(nm, "in", spec)
            if nm in vals:
                self._val(p, vals[nm])
        for nm, spec in outs:
            n.pin(nm, "out", spec)
        return n

    def arrfunc(self, func, elemspec, ins=(), outs=(), pure=False, **vals):
        n = Node(self, "K2Node_CallArrayFunction",
                 [("FunctionReference", "(MemberParent=\"/Script/CoreUObject.Class'%s'\",MemberName=\"%s\")" % (LIB["Arr"], func))]
                 + ([("bDefaultsToPureFunc", "True")] if pure else []))
        if not pure:
            n.pin("execute", "in", "exec")
            n.pin("then", "out", "exec")
        n.pin("self", "in", "obj:" + LIB["Arr"], hidden=True, defobj="/Script/Engine.Default__KismetArrayLibrary")
        for nm, spec in ins:
            p = n.pin(nm, "in", spec.replace("E", elemspec) if spec in ("E", "E[]") else spec)
            if nm in vals:
                self._val(p, vals[nm])
        for nm, spec in outs:
            n.pin(nm, "out", spec.replace("E", elemspec) if spec in ("E", "E[]") else spec)
        return n

    def get(self, var, spec):
        n = Node(self, "K2Node_VariableGet", [("VariableReference", '(MemberName="%s",bSelfContext=True)' % var)])
        n.pin(var, "out", spec)
        return n[var]

    def set(self, var, spec, value):
        n = Node(self, "K2Node_VariableSet", [("VariableReference", '(MemberName="%s",bSelfContext=True)' % var)])
        n.pin("execute", "in", "exec")
        n.pin("then", "out", "exec")
        p = n.pin(var, "in", spec)
        self._val(p, value)
        n.pin("Output_Get", "out", spec)
        return n

    def item(self, var, elemspec, idx):
        """var[idx] (pure)"""
        arr = self.get(var, elemspec + "[]")
        n = Node(self, "K2Node_GetArrayItem", [])
        a = n.pin("Array", "in", elemspec + "[]")
        link(arr, a)
        i = n.pin("Dimension 1", "in", "int")
        self._val(i, idx)
        n.pin("Output", "out", elemspec)
        return n["Output"]

    def item_of(self, arrpin, elemspec, idx):
        """arrpin[idx] (pure) for en vilkaarlig array-pin"""
        n = Node(self, "K2Node_GetArrayItem", [])
        a = n.pin("Array", "in", elemspec + "[]")
        self._val(a, arrpin)
        i = n.pin("Dimension 1", "in", "int")
        self._val(i, idx)
        n.pin("Output", "out", elemspec)
        return n["Output"]

    def branch(self, cond):
        n = Node(self, "K2Node_IfThenElse", [])
        n.pin("execute", "in", "exec")
        c = n.pin("Condition", "in", "bool")
        self._val(c, cond)
        n.pin("then", "out", "exec")
        n.pin("else", "out", "exec")
        return n

    def switch_int(self, sel, count):
        n = Node(self, "K2Node_SwitchInteger", [])
        n.pin("execute", "in", "exec")
        s = n.pin("Selection", "in", "int")
        self._val(s, sel)
        n.pin("NotEqual_IntInt", "in", "obj:/Script/Engine.KismetMathLibrary", hidden=True, defobj="/Script/Engine.Default__KismetMathLibrary")
        for i in range(count):
            n.pin(str(i), "out", "exec")
        n.pin("Default", "out", "exec")
        return n

    def forloop(self, first, last):
        n = Node(self, "K2Node_MacroInstance", [("MacroGraphReference",
            "(MacroGraph=\"/Script/Engine.EdGraph'/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:ForLoop'\",GraphBlueprint=\"/Script/Engine.Blueprint'/Engine/EditorBlueprintResources/StandardMacros.StandardMacros'\",GraphGuid=55C904AF4B45FE1761FB55A8DB9FB801)")])
        n.pin("execute", "in", "exec")
        self._val(n.pin("FirstIndex", "in", "int"), first)
        self._val(n.pin("LastIndex", "in", "int"), last)
        n.pin("LoopBody", "out", "exec")
        n.pin("Index", "out", "int")
        n.pin("Completed", "out", "exec")
        return n

    def cast(self, obj, cls, disp=None, path=None):
        """impure cast: execute -> then (lykkedes) / CastFailed. Output: n.out"""
        disp = disp or {"TextBlock": "Text Block", "UserWidget": "User Widget", "Border": "Border", "Image": "Image",
                        "PanelWidget": "Panel Widget"}.get(cls, cls)
        tpath = path or "/Script/CoreUObject.Class'%s'" % CLS[cls]
        n = Node(self, "K2Node_DynamicCast", [("TargetType", '"%s"' % tpath)])
        n.pin("execute", "in", "exec")
        n.pin("then", "out", "exec")
        n.pin("CastFailed", "out", "exec")
        o = n.pin("Object", "in", "obj:Object")
        self._val(o, obj)
        n.out = n.pin("As" + disp, "out", "obj:" + (cls if not path else "Object"))
        return n

    def member_get(self, cls_path, var, spec, target):
        n = Node(self, "K2Node_VariableGet", [("VariableReference", '(MemberParent="%s",MemberName="%s")' % (cls_path, var)),
                                              ("SelfContextInfo", "NotSelfContext")])
        n.pin(var, "out", spec)
        sp = n.pin("self", "in", "obj:Object")
        self._val(sp, target)
        return n[var]

    def member_set(self, cls_path, var, spec, target, value):
        """Saetter en variabel paa et andet objekt (target)."""
        n = Node(self, "K2Node_VariableSet", [("VariableReference", '(MemberParent="%s",MemberName="%s")' % (cls_path, var)),
                                              ("SelfContextInfo", "NotSelfContext")])
        n.pin("execute", "in", "exec")
        n.pin("then", "out", "exec")
        p = n.pin(var, "in", spec)
        self._val(p, value)
        n.pin("Output_Get", "out", spec)
        sp = n.pin("self", "in", "obj:Object")
        self._val(sp, target)
        return n

    def make_struct(self, struct_path, outname, fields, **vals):
        n = Node(self, "K2Node_MakeStruct", [("StructType", "\"/Script/CoreUObject.ScriptStruct'%s'\"" % struct_path)])
        n.pin(outname, "out", "struct:" + struct_path)
        for nm, spec in fields:
            p = n.pin(nm, "in", spec)
            if nm in vals:
                self._val(p, vals[nm])
        return n[outname]

    def set_fields(self, struct_path, structref, fields, **vals):
        """K2Node_SetFieldsInStruct: aendrer udvalgte felter i en struct-variabel (structref = variabel-get pin)."""
        vis = ",".join('ShowPinForProperties(%d)=(PropertyName="%s",bShowPin=True,bCanToggleVisibility=True)' % (i, nm)
                       for i, (nm, _) in enumerate(fields))
        props = [("bMadeAfterOverridePinRemoval", "True")]
        for i, (nm, _) in enumerate(fields):
            props.append(("ShowPinForProperties(%d)" % i, '(PropertyName="%s",bShowPin=True,bCanToggleVisibility=True)' % nm))
        props.append(("StructType", "\"/Script/CoreUObject.ScriptStruct'%s'\"" % struct_path))
        n = Node(self, "K2Node_SetFieldsInStruct", props)
        n.pin("execute", "in", "exec")
        n.pin("then", "out", "exec")
        r = n.pin("StructRef", "in", "struct:" + struct_path)
        self._val(r, structref)
        n.pin("StructOut", "out", "struct:" + struct_path)
        for nm, spec in fields:
            p = n.pin(nm, "in", spec)
            if nm in vals:
                self._val(p, vals[nm])
        return n

    def call_path(self, cls_path, func, ins=(), outs=(), pure=True, static_default=None, target=None, **vals):
        props = [("FunctionReference", '(MemberParent="%s",MemberName="%s")' % (cls_path, func))]
        if pure:
            props.append(("bDefaultsToPureFunc", "True"))
        n = Node(self, "K2Node_CallFunction", props)
        if not pure:
            n.pin("execute", "in", "exec")
            n.pin("then", "out", "exec")
        if static_default:
            pass          # statisk funktion: self udfyldes automatisk
        else:
            sp = n.pin("self", "in", "obj:Object")
            self._val(sp, target)
        for nm, spec in ins:
            p = n.pin(nm, "in", spec)
            if nm in vals:
                self._val(p, vals[nm])
        for nm, spec in outs:
            n.pin(nm, "out", spec)
        return n

    def break_struct(self, struct_path, inname, value, outs):
        n = Node(self, "K2Node_BreakStruct", [("StructType", "\"/Script/CoreUObject.ScriptStruct'%s'\"" % struct_path)])
        p = n.pin(inname, "in", "struct:" + struct_path)
        self._val(p, value)
        for o, sp in outs:
            n.pin(o, "out", sp)
        return n

    def add_component(self, actor, comp_class_path, ret_spec):
        """K2Node_AddComponentByClass: actor (Pin) faar en ny komponent af klassen."""
        n = Node(self, "K2Node_AddComponentByClass", [])
        n.pin("execute", "in", "exec")
        n.pin("then", "out", "exec")
        sp = n.pin("self", "in", "obj:/Script/Engine.Actor")
        self._val(sp, actor)
        n.pin("bManualAttachment", "in", "bool", default="false")
        n.pin("RelativeTransform", "in", "struct:/Script/CoreUObject.Transform")
        n.pin("Class", "in", "class:/Script/Engine.ActorComponent", defobj=comp_class_path)
        n.pin("ReturnValue", "out", ret_spec)
        return n

    def sequence(self, count=2):
        n = Node(self, "K2Node_ExecutionSequence", [])
        n.pin("execute", "in", "exec")
        for i in range(count):
            n.pin("then_%d" % i, "out", "exec")
        return n

    def self_ref(self):
        n = Node(self, "K2Node_Self", [])
        n.pin("self", "out", "obj:" + SELF_CLASS.split("'")[1])
        return n["self"]

    def make_slatecolor(self, col):
        n = Node(self, "K2Node_MakeStruct", [("StructType", "\"/Script/CoreUObject.ScriptStruct'/Script/SlateCore.SlateColor'\"")])
        n.pin("SlateColor", "out", "struct:SlateColor")
        p = n.pin("SpecifiedColor", "in", "struct:LinearColor")
        self._val(p, col)
        return n["SlateColor"]

    def create_delegate(self, func):
        n = Node(self, "K2Node_CreateDelegate", [("SelectedFunctionName", '"%s"' % func)])
        n.pin("self", "in", "obj:Object")
        n.pin("OutputDelegate", "out", "delegate")
        return n["OutputDelegate"]


class Chain:
    """Holder styr paa exec-kaeden."""
    def __init__(self, g, start_pin):
        self.g = g
        self.cur = start_pin

    def then(self, node, inpin="execute", outpin="then"):
        link(self.cur, node[inpin])
        self.cur = node[outpin] if outpin else None
        return node

    def to(self, pin):
        self.cur = pin
        return self


def _call_delegate(self, cls_path, delegate, target, params=()):
    """K2Node_CallDelegate: kalder (broadcaster) en event dispatcher paa et andet objekt."""
    n = Node(self, "K2Node_CallDelegate", [("DelegateReference", '(MemberParent="%s",MemberName="%s")' % (cls_path, delegate)),
                                           ("SelfContextInfo", "NotSelfContext")])
    n.pin("execute", "in", "exec")
    n.pin("then", "out", "exec")
    sp = n.pin("self", "in", "obj:Object")
    self._val(sp, target)
    for pname, spec, val in params:
        p = n.pin(pname, "in", spec)
        self._val(p, val)
    return n


Graph.call_delegate = _call_delegate
