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
1. Commit ændrede filer til enheden.
2. Python-konsollen: `exec(open(r"...\movia_byg_motor.py", encoding="utf-8").read())` (kun ved nye variabler).
3. Åbn `/Game/MoviaSkaerme/WBP_MoviaMotor` → Graph → klik i grafen, Ctrl+A → højreklik node → Delete (tager 1-2 min).
4. Konsol: `import sys; sys.path.append(r"...\MoviaTools"); import movia_klip; movia_klip.kopier_fil(r"...\_motor_vNN.t3d")` – vent ~30 s.
5. Klik i grafen, Ctrl+V (1 min) → "Fix Self Context…" → Confirm.
6. File → Refresh All Nodes → Compile ("Good to go") → gem med disketten (ikke Ctrl+S) → luk vinduet.
7. Ved layout-/regelændringer: konsol `exec(open(r"...\movia_kommando.py", encoding="utf-8").read())`.
8. TML → Mod Creator → Build Mod → Build Client Only (~6 min). Tjek pak-filens tid i `Mods\MoviaSkaerme\Paks`.

## Status (31-10-2026)
- Motor v43 bygget. Skift rute: trin 1 (Nær dig / Søg linje), trin 2 (startstop), pause-kort, Tjeneste-skærm.
- START tildeler kursen til spilleren (AssignTour) og opdaterer passagerer (PassengerManager.UpdatePlayerTours).
- Mangler test: vælg rækker, START midt på ruten, passagerer, lag.
