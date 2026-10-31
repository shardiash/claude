# -*- coding: utf-8 -*-
"""MOVIA v34 - tilfoejer MoviaSkiltL / MoviaSkiltD (tekst) til BP_BoardComputer_TheBus_NAtron,
saa skiltet kan vise egen linje/destination. Koeres foer skilt-noderne indsaettes."""
import unreal
STI = "/Game/Gameplay/Vehicles/Common/BP_BoardComputer_TheBus_NAtron"
UD = r"C:\Users\tacci\Documents\The Bus\MoviaTools\_skilt_vars_ud.txt"
BEL = unreal.BlueprintEditorLibrary
log = []
try:
    bp = unreal.EditorAssetLibrary.load_asset(STI)
    for navn, typ in (("MoviaSkiltL", "string"), ("MoviaSkiltD", "string"), ("MoviaSkiltAktiv", "bool")):
        log.append("%s: %s" % (navn, BEL.add_member_variable(bp, navn, BEL.get_basic_type_by_name(typ))))
    BEL.compile_blueprint(bp)
    log.append("gemt: %s" % unreal.EditorAssetLibrary.save_asset(STI, only_if_is_dirty=False))
except Exception as e:
    import traceback
    log.append("FEJL: %s\n%s" % (e, traceback.format_exc()))
open(UD, "w", encoding="utf-8").write("\n".join(log))
print("\n".join(log))
