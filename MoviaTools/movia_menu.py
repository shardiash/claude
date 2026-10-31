# -*- coding: utf-8 -*-
"""
MOVIA MENU - laver en "Movia"-menu i toppen af The Bus Modding.
Koer den EN gang hver gang du har startet editoren:
  Tools > Execute Python Script > movia_menu.py
"""
import unreal

MAPPE = r"C:\Users\tacci\Documents\The Bus\MoviaTools"


def _py(kode):
    return ("import sys; sys.path.append(r'%s'); " % MAPPE) + kode


KNAPPER = [
    ("Koer kommando.json",
     "Bygger skaermene fra kommando.json i MoviaTools",
     _py("exec(open(r'%s\\movia_kommando.py', encoding='utf-8').read())" % MAPPE)),
    ("Aabn Movia Editor",
     "Starter den visuelle editor",
     _py("import subprocess; subprocess.Popen(['cmd', '/c', 'start', '', r'%s\\start_editor.bat'], cwd=r'%s')" % (MAPPE, MAPPE))),
    ("Vis elementer i passagerskaermen",
     "Skriver alle elementnavne til Output Log",
     _py("import movia_tools, importlib; importlib.reload(movia_tools); movia_tools.vis_elementer('Passager')")),
    ("Ny mod ...",
     "Viser hvordan du opretter en ny mod",
     "import unreal; unreal.EditorDialog.show_message('Ny mod', "
     "'1. Klik TML i menuen > Mod Creator\\n"
     "2. Klik Create new Mod\\n"
     "3. Vaelg Empty og skriv et navn\\n"
     "4. Klik Create - editoren genstarter i din nye mod\\n"
     "5. Koer movia_menu.py igen og tryk Movia > Koer kommando.json\\n\\n"
     "Movias skrifttyper og billeder kopieres automatisk ind i den nye mod.', "
     "unreal.AppMsgType.OK)"),
    ("Byg mod (vejledning)",
     "Viser hvordan du bygger modden til spillet",
     "import unreal; unreal.EditorDialog.show_message('Byg mod', "
     "'1. Klik TML > Mod Creator\\n"
     "2. Klik Build Mod > Build Client Only\\n"
     "3. Vent til der ikke staar Cooking nederst til hoejre\\n"
     "4. Luk The Bus foer buildet er faerdigt, start spillet bagefter\\n"
     "5. Slaa modden til i spillets mod-menu', unreal.AppMsgType.OK)"),
]


def _fyld(menu, sektion, prefix):
    menu.add_section(sektion, "Movia")
    for i, (navn, tip, kode) in enumerate(KNAPPER):
        e = unreal.ToolMenuEntry(name="%s%d" % (prefix, i), type=unreal.MultiBlockType.MENU_ENTRY)
        e.set_label("Movia: " + navn if prefix == "MoviaTools" else navn)
        e.set_tool_tip(tip)
        e.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, "", kode)
        menu.add_menu_entry(sektion, e)


def lav_menu():
    menus = unreal.ToolMenus.get()
    lavet = []

    # 1) Sikreste sted: inde i den eksisterende Tools-menu (oeverst i Tools)
    try:
        tools = menus.find_menu("LevelEditor.MainMenu.Tools")
        if tools is None:
            tools = menus.extend_menu("LevelEditor.MainMenu.Tools")
        _fyld(tools, "MoviaToolsSektion", "MoviaTools")
        lavet.append("Tools-menuen (punkter der starter med 'Movia:')")
    except Exception as fejl:
        unreal.log_warning("[MOVIA] Tools-menu fejlede: %s" % fejl)

    # 2) Egen 'Movia'-menu i menulinjen
    try:
        hoved = menus.extend_menu("LevelEditor.MainMenu")
        menu = hoved.add_sub_menu("MoviaOwner", "", "Movia", "Movia", "Movia-vaerktoejer")
        menu = menus.find_menu("LevelEditor.MainMenu.Movia") or menu
        _fyld(menu, "MoviaSektion", "Movia")
        lavet.append("egen 'Movia'-menu i menulinjen")
    except Exception as fejl:
        unreal.log_warning("[MOVIA] Egen menu fejlede: %s" % fejl)

    menus.refresh_all_widgets()
    if lavet:
        unreal.log("[MOVIA] Menu v2 klar: " + " + ".join(lavet))
    else:
        unreal.log_error("[MOVIA] Kunne ikke lave nogen menu")


try:
    lav_menu()
except Exception as fejl:
    import traceback
    unreal.log_error("[MOVIA] Menuen fejlede: %s\n%s" % (fejl, traceback.format_exc()))
