# Movia-mod til The Bus – arbejdsnoter til Claude

Svar altid på dansk. Brugeren tester i spillet; du bygger i Unreal-editoren via computer use.

## Regler fra brugeren
- Rør ikke editoren/computeren mens brugeren spiller – vent på "klar".
- Byg modden når du er færdig, og kobl fra (release lock) bagefter.
- Brug aldrig Delete-tasten (Medal). Slet via højreklik → Delete.
- Vis et udkast (mock) og få ok før nye idéer bygges. Bevar det eksisterende design.
- Gæt ikke – undersøg/verificér ("VÆR SIKKER OG IKKE GÆT").

## Filer (MoviaTools/)
- `motorgen.py` – genererer motor-grafen (T3D) til `WBP_MoviaMotor`. `python3 motorgen.py _motor_vNN.t3d`
- `bpgen.py` – lille T3D-generator som motorgen bruger.
- `movia_motor.py` / `movia_regler.py` / `movia_tools.py` – bygger skærme + regler i editoren ud fra `kommando.json`.
- `movia_byg_motor.py` – tilføjer motorens variabler (kør før ny motor indsættes).
- `byg_skilt.py`, `byg_rute.py` – skriver Skilt- og Skift rute-lagene ind i `kommando.json`.
- `login_email.txt` (ikke i git) – login-mailen motoren tjekker. Uden filen bruges en eksempel-mail.

## Deploy i editoren (Windows: `C:\Users\tacci\Documents\The Bus\MoviaTools`)
Ny motor (genereret `_motor_vNN.t3d`, nyeste nummer vælges automatisk):
1. Commit ændrede filer til enheden.
2. Konsol: `exec(open(r"...\movia_ny_motor.py", encoding="utf-8").read())` – tilføjer variabler, sletter den gamle graf (remove_graph), kopierer motoren og åbner den.
3. I motor-vinduet: Graph → `+` ved GRAPHS → Enter → klik i grafen → Ctrl+V (1 min) → Confirm → **File → Refresh All Nodes** (obligatorisk; uden den kompilerer motoren med fejl).
4. Konsol: `movia_faerdig()` (eller `movia_faerdig(layout=True)` for også at køre kommando.json). Den kompilerer, tjekker loggen for fejl og at motoren ikke er tom, og gemmer kun hvis alt er ok.
   - Kun funktionerne uden at starte forfra: `import builtins; builtins.MOVIA_KUN_DEF = True; exec(...)`.
5. TML → Mod Creator → Build Mod → Build Client Only (~6 min). Tjek pak-filens tid i `Mods\MoviaSkaerme\Paks`.

## Status (31-10-2026)
- Motor v43 bygget. Skift rute: trin 1 (Nær dig / Søg linje), trin 2 (startstop), pause-kort, Tjeneste-skærm.
- START tildeler kursen til spilleren (AssignTour) og opdaterer passagerer (PassengerManager.UpdatePlayerTours).
- Mangler test: vælg rækker, START midt på ruten, passagerer, lag.
