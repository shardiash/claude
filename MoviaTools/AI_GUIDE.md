# MOVIA KOMMANDO – guide til AI

Du (AI'en) skal skrive EN JSON-fil, der hedder `kommando.json`. Brugeren
lægger den i `C:\Users\tacci\Documents\The Bus\MoviaTools\` og kører
`movia_kommando.py` i The Bus Modding Editor (Tools > Execute Python Script).
Den bygger/ændrer en skærm i busspillet "The Bus". Svar KUN med gyldig JSON.

**Arbejdsgang (vigtigt):** kommando.json kan skrives af enhver (dig, Gemini, brugeren selv).
For at ændringen kommer i spillet skal brugeren altid:
1. køre `movia_kommando.py` i editorens Python-konsol (én linje), og
2. trykke TML > Mod Creator > Build Mod > Build Client Only.
Det er KUN nye *slags* funktioner (nye datafelter, nye knaptyper, nye handlinger) der kræver at
regel-motoren (WBP_MoviaMotor) selv ændres – det kan du ikke via kommando.json (det gøres med
`motorgen.py` + `movia_ny_motor.py`, se nederst). Brug derfor kun de
datafelter, knaptyper og handlinger der står i denne guide.
**Rediger den eksisterende kommando.json** (den indeholder alle skærme) – byg ikke forfra, ellers forsvinder
login, billetmenu, pause osv.

## Format

```json
{
  "skaerm": "Passager",
  "layout": { ... },          // valgfri: byg hele skærmen forfra
  "aendringer": [ ... ]       // valgfri: små ændringer i eksisterende elementer
}
```

Brug enten `layout`, `aendringer` eller begge.

Skal flere skærme laves på én gang (fx `Main` OG `Header`), så skriv en
liste: `[ {"skaerm": "Main", ...}, {"skaerm": "Header", ...} ]`.

## Skærme

| skaerm | Størrelse (px) | Hvad |
|---|---|---|
| `Passager` | 1600 × 430 | Passagerskærmen i loftet |
| `Main` | 1200 × 764 | Chaufførens bordcomputer, når bussen holder stille |
| `Driving` | 1200 × 764 | Chaufførens bordcomputer, når bussen kører |
| `Header` | 900 × 100 | Bordcomputerens topbjælke (ur, forsinkelse, linje). Den er FÆLLES for alle bordcomputer-skærme |
| `StopRaekke` | – | Én række i passagerskærmens stopliste (kun `aendringer`) |
| `Startup` | 1200 × 764 | Bordcomputerens opstartsskærm (kun `aendringer`) |
| `Start` | 1200 × 764 | Forskærmen før login (grøn log ind-knap, GPS) |
| `LogIn` | 1200 × 764 | Custom login (email/adgangskode, tastatur, Gem login) – logger ind i baggrunden |
| `Tur` | 1200 × 764 | Spillets linje/tur-valg – logger selv ind ("Logger ind…"), manuel skærm som reserve |
| `Tjeneste` | 1200 × 764 | Spillets "Service Journey" (kørsel hen til turens første stop). Er en kopi af Driving og skal holdes ens med den |

`Main`, `Driving` og `Tjeneste` har samme layout (Atron skifter selv: Main når bussen holder stille, Driving når den kører,
Tjeneste på vej hen til første stop). Ændrer du den ene, så ændr de andre på samme måde.

Alle skærme undtagen StopRaekke og Startup kan bygges med `layout`.

## layout

```json
"layout": {
  "w": 1600, "h": 430, "bg": "#FFFFFF",
  "items": [ element, element, ... ]
}
```

Elementer tegnes i rækkefølge: første = bagerst, sidste = forrest.
x/y er øverste venstre hjørne i pixels. Farver er hex: `"#RRGGBB"`.

### Element-typer

**Fast tekst**
```json
{"type": "text", "name": "Overskrift", "x": 806, "y": 22, "text": "Næste stop",
 "size": 18, "color": "#333333", "bold": false}
```

**Datafelt** (tekst som spillet selv opdaterer – brug ALTID dette til rigtige data)
```json
{"type": "text", "name": "Næste stop", "x": 942, "y": 18, "data": "NaesteStop",
 "size": 40, "color": "#1D1D1D", "bold": true}
```
Tilladte `data` afhænger af skærmen:

| skaerm | Tekst-datafelter (`"type": "text"`) | Område-datafelter (`"type": "box"`) |
|---|---|---|
| `Passager` | `NaesteStop`, `SidsteStop`, `Linje`, `Ur` | `StopListe` |
| `Header` | `Ur`, `Forsinkelse`, `Dato`, `LinjeDestination` | – |
| `Main` | – | `Header`, `StopListe` |
| `Driving` | – | `Header` |

- `Forsinkelse` = spillets forsinkelse/før tid, fx "-0:01:35" (spillet farver den selv)
- `LinjeDestination` = linje og endestation i én tekst, fx "498 - S OSTBAHNHOF"
- `Header` (på Main/Driving) = hele topbjælken som én blok. Dens indhold
  designes separat med `"skaerm": "Header"`.
- `StopListe` = spillets egen stopliste, som opdaterer sig selv.

**Boks**
```json
{"type": "box", "name": "Topfelt", "x": 790, "y": 0, "w": 810, "h": 92, "color": "#F3F4F5"}
```

**Boks der skifter farve ved en tilstand**
```json
{"type": "box", "name": "STOP-felt", "x": 790, "y": 93, "w": 152, "h": 136,
 "color": "#111111", "color_on": "#E2231A", "state": "StopOenske"}
```
Tilladte `state`: `StopOenske` (en passager har trykket stop). Brug højst én
boks med `StopOenske` pr. skærm.

**Dataområde** (et område spillet fylder ud)
```json
{"type": "box", "name": "Stopliste", "x": 960, "y": 100, "w": 620, "h": 320,
 "color": "#FFFFFF", "data": "StopListe"}
```
Tilladte `data` for bokse: `StopListe` – spillets liste over kommende stop.

**Billede**
```json
{"type": "box", "name": "Reklame", "x": 0, "y": 0, "w": 790, "h": 430,
 "color": "#FFFFFF", "image": "T_Reklame_Aeblefest"}
```
`image` kan være et billednavn der allerede er i modden
(`T_Reklame_Aeblefest`, `T_Reklame_Boennebaren`, `T_Movia_Kort`, `ikon_bus`,
`ikon_metro`, `ikon_stoppested`, `ikon_bus_position`) eller en fuld sti til en
PNG på brugerens computer, fx `"C:\\Users\\tacci\\Pictures\\logo.png"` –
den importeres automatisk.

**Spil-element** (et hvilket som helst eksisterende element fra spillet)
```json
{"type": "box", "name": "Knapper", "x": 0, "y": 680, "w": 1200, "h": 84, "spil": "ElementNavn"}
```
Flytter spillets eget element hen på pladsen (fx bordcomputerens knapper).
`ElementNavn` skal være det præcise navn fra Hierarchy – kør
`{"funktion": "vis_elementer"}` for at få listen. Brug kun navne du kender.

Valgfrit på alle elementer: `"hidden": true` (skjult i spillet).

### Hvad sker der med spillets gamle layout?
Alt, du ikke har koblet eller nævnt, bliver skjult. Skal noget af det gamle
blive stående (fx knapperne nederst på bordcomputeren), så skriv navnene i
`"behold": ["ElementNavn", ...]` inde i `layout`. VIGTIGT på `Main` og
`Driving`: bordcomputerens knapper skal flyttes med et spil-element eller
beholdes, ellers kan chaufføren ikke betjene den.

## aendringer

Små ændringer i spillets eksisterende elementer. `element` er navnet fra
Hierarchy i editoren (spørg brugeren, eller kør `vis_elementer` først).

```json
"aendringer": [
  {"funktion": "vis_elementer"},
  {"funktion": "tekst",          "element": "TextBlock_98", "vaerdi": "Næste stop"},
  {"funktion": "tekstfarve",     "element": "TextBlock_98", "vaerdi": "#333333"},
  {"funktion": "skrift",         "element": "TextBlock_98", "vaegt": "Bold", "stoerrelse": 30},
  {"funktion": "farve",          "element": "Image_0",      "vaerdi": "#F3F4F5"},
  {"funktion": "billede",        "element": "Image_Reklame", "vaerdi": "/Game/MoviaSkaerme/T_Reklame_Boennebaren"},
  {"funktion": "skjul",          "element": "Image_2"},
  {"funktion": "vis",            "element": "Image_2"},
  {"funktion": "gennemsigtighed","element": "Image_2", "vaerdi": 0.5}
]
```
`vaegt`: `Regular`, `Medium`, `SemiBold`, `Bold`, `ExtraBold`.
Hver ændring kan have sin egen `"skaerm"`, ellers bruges den øverste.

Kendte elementnavne på `Passager`: `Text_NextBusStop`, `Text_Busline`,
`Text_Destination`, `Text_Time`, `Image_Reklame`, `Image_0` (topfeltets baggrund),
`Image_3` (STOP-feltets farve), `Border_1` (STOP-feltets sorte baggrund),
`TextBlock_0` (teksten "STOP"), `Vertical_NextNextObjects` (stoplisten).

## regler (ting der ændrer sig mens man kører)

Læg `"regler"` (liste) inde i `"layout"`. Hver regel tjekkes hele tiden i spillet.
`element` = `name` på et element i samme layout (giv elementerne unikke navne!).

### hvis – rigtige udtryk
Skriv betingelsen som tekst:
```
"hvis": "Forsinkelse > 60"
"hvis": "Forsinkelse > 60 og Linje = '5C'"
"hvis": "Forsinkelse < -60 eller Forsinkelse > 120"
"hvis": "NaesteStop indeholder 'St.'"
"hvis": "Forsinkelse / 60 >= 2"
"hvis": "(Tid % 20) < 10"
```
- Sammenlign: `>  <  >=  <=  =  !=`, og tekst med `indeholder`
- Kombinér: `og`, `eller`, `ikke`, parenteser
- Regning: `+ - * /` og `%` (rest – sæt den til sidst). Kun ét datafelt pr. sammenligning.
- Tekst i 'enkelte anførselstegn'.
- Udelad `hvis` = gælder altid.

### Datafelter i regler
| navn | skærm | hvad |
|---|---|---|
| tekst-datafelterne (`NaesteStop`, `Linje`, `SidsteStop`, `Ur` …) | den skærm de hører til | spillets egen tekst (tal i teksten kan regnes med) |
| `Forsinkelse` | **Header**, **Driving** | sekunder, positiv = forsinket, negativ = for tidlig |
| `NaesteTid` | **Driving** | planlagt ankomst ved næste stop, sekunder efter midnat (format `hh:mm:ss`) |
| `SidsteTidSek` | **Driving** | planlagt ankomst ved sidste stop (endestation), sekunder efter midnat |
| `SidsteStopNavn` | **Driving** | navnet på sidste stop (tekst) |
| `NaesteStopNavn` | **Driving** | navnet på næste stop – bliver ved det stop bussen holder ved, indtil den kører igen (tekst) |
| `NaesteAfgang` | **Driving** | planlagt AFGANG fra næste stop, sekunder efter midnat (format `hh:mm:ss`) |
| `HolderVedStop` | **Driving** | 1 når bussen holder stille (under 3 km/t) ved et stop ifølge spillet, ellers 0 (bruges til at vise/skjule "Tag afgang"-boksen) |
| `AktuelAfgang` | **Driving** | planlagt afgang fra det stop bussen holder ved, sekunder efter midnat (format `hh:mm:ss`), 0 hvis ikke ved et stop |
| `LinjeNr` | **Driving** | linjenummer (tekst, fx 5C) |
| `Minutter1`, `Minutter2`, `Minutter3` | **Passager** | minutter til 1., 2. og 3. stop ifølge køreplanen |
| `Forventet1`, `Forventet2`, `Forventet3` | **Passager** | forventede minutter: køreplan rettet efter hvor langt bussen er fra næste stop (forsinkelse lægges til / trækkes fra) |
| `Afstand` | **Passager** | meter (i luftlinje) fra bussen til næste stop |
| `Linje1_1` … `Linje3_5` | **Passager** | andre buslinjer ved stop 1–3 (op til 5 pr. stop, din egen linje er fjernet). Tom tekst = ingen. Fx `Linje2_1` = første andre linje ved 2. stop |
| `AfgLinje1` … `AfgLinje8` | **Passager** | afgangstavle: linjenummer for de næste busser ved det stop bussen er ved/kommer til (tekst) |
| `AfgTil1` … `AfgTil8` | **Passager** | afgangstavle: destination (tekst) |
| `AfgMin1` … `AfgMin8` | **Passager** | afgangstavle: minutter til afgang |
| `VedStop` | **Passager** | 1 når bussen holder stille (under 3 km/t) ved et stop (spillet siger "ved stop"), ellers 0. Som tekst: fart + * ved stop (fejlsøgning) |
| `Klokken` | alle | spillets ur i minutter efter midnat (brug format `hh:mm`) |
| `KlokkeSek` | alle | spillets ur i sekunder efter midnat (brug format `hh:mm:ss`) |
| `Tid` | alle | sekunder siden spillet startede (til blink/sider) |

`Forsinkelse` findes IKKE på `Main` – lav forsinkelses-regler på skærmen `Header` eller `Driving`.
Kommer senere (virker IKKE i regler endnu): `Hastighed`, `Doere`, `Blinklys`, `Passagerer`, `StopOenske`.
(`StopOenske` virker allerede som `"state"` på en boks – se layout.)

### saet – hvad der sker
| saet | til / ellers |
|---|---|
| `farve` | #RRGGBB (boks) |
| `tekstfarve` | #RRGGBB |
| `tekst` | tekst, må have ÉN `{udtryk:format}` – se nedenfor |
| `vis` / `skjul` | (ingen) – gør det modsatte når hvis er falsk |
| `opacity` | 0 til 1 |
| `billede` | billednavn (fx `T_Reklame_Aeblefest`) |
| `blink` | blinker mens hvis er sand. `"periode": 1` (sek), `"min": 0` |
| `flytx` / `flyty` | forskyd elementet vandret/lodret i pixels (fx `"til": 0, "ellers": -120`). Med `glid` glider det |

`"ellers"`: værdi når hvis er falsk. `"glid": 0.5`: blød overgang i sekunder – på `vis`/`skjul`/`opacity` en fade, på `farve` (bokse) en blød farvetoning, på `flytx`/`flyty` en glidende bevægelse.

Eksempel – boks der glider ind fra venstre og toner frem, når bussen holder ved et stop:
```json
{"hvis": "HolderVedStop = 1", "saet": "vis", "element": "AfgangBoks", "glid": 0.25},
{"hvis": "HolderVedStop = 1", "saet": "flytx", "element": "AfgangBoks", "til": 0, "ellers": -120, "glid": 0.25}
```

### tekstformatering
```
"til": "{Forsinkelse / 60 : fortegn} min"   ->  "+2 min"
"til": "{Forsinkelse : mm:ss}"              ->  "01:30"
"til": "{Forsinkelse : m:ss}"               ->  "+0:16" / "-2:48" (med fortegn)
"til": "{KlokkeSek : hh:mm:ss}"            ->  "07:31:05"
"til": "Kl. {Ur}"                           ->  rå tekst
```
Formater: `raa`, `heltal`, `1dec`, `fortegn`, `mm:ss`, `hh:mm`, `m:ss` (med fortegn), `hh:mm:ss`.

### sider (skift mellem visninger)
```json
"sider": {"skift_hver": 10, "glid": 0.5, "sider": [["Stopliste", "Tidslinje"], ["Reklame2"]]}
```
Læg `"sider"` i `"layout"`. Hver side er en liste af elementnavne.

### z (lagdeling)
Alle elementer kan have `"z": 10`. Højere tal ligger øverst. Uden z = rækkefølgen i listen.

### Eksempel
```json
"regler": [
  {"hvis": "Forsinkelse > 60 eller Forsinkelse < -60", "saet": "farve",
   "element": "StatusBoks", "til": "#DE3B26", "ellers": "#3FA535", "glid": 0.3},
  {"saet": "tekst", "element": "ForsinkelseTekst", "til": "{Forsinkelse / 60 : fortegn} min"},
  {"hvis": "Forsinkelse > 120", "saet": "blink", "element": "Advarsel", "periode": 0.8}
]
```
(Eksemplet ovenfor hører til skærmen `Header`, fordi det bruger Forsinkelse.)

### Eksempel: rigtige minutter i passagerskærmens stopliste
Lav tre tekst-elementer ("Minutter 1-3") ud for stoplistens prikker og giv dem en regel:
```json
"regler": [
  {"saet": "tekst", "element": "Minutter 1", "til": "{Minutter1:heltal} min"},
  {"saet": "tekst", "element": "Minutter 2", "til": "{Minutter2:heltal} min"},
  {"saet": "tekst", "element": "Minutter 3", "til": "{Minutter3:heltal} min"}
]
```
Mere realistisk – forventet tid og "Nu" når bussen er tæt på (sidste regel vinder):
```json
"regler": [
  {"saet": "tekst", "element": "Minutter 1", "til": "{Forventet1:heltal} min"},
  {"saet": "tekst", "element": "Minutter 2", "til": "{Forventet2:heltal} min"},
  {"saet": "tekst", "element": "Minutter 3", "til": "{Forventet3:heltal} min"},
  {"hvis": "Afstand < 150 eller Forventet1 < 0.5", "saet": "tekst", "element": "Minutter 1", "til": "Nu"}
]
```

### Eksempel: ur og skift mellem stopliste og reklame
```json
"regler": [{"saet": "tekst", "element": "Ur", "til": "{Klokken:hh:mm}"}],
"sider": {"skift_hver": 10, "glid": 0.5, "sider": [["Stopliste", "Tidslinje"], ["Reklame2"]]}
```

Regel-motoren (WBP_MoviaMotor) sættes automatisk ind på skærmen, når kommandoen køres.
Programmet gemmes også i `program_<skaerm>.txt`, så man kan se hvad der blev lavet.

## aendringer – ekstra funktioner
Ud over dem ovenfor: `hoejde` (Spacer/SizeBox, vaerdi = tal), `klip` (klip indhold),
`juster` (vaerdi: top/midt/bund/fyld), `egenskab` (vaerdi: {"navn": ..., "vaerdi": ...}).

### Stoplistens rækker (skaerm `StopRaekke`)
En stoprække består af: `SizeBox_0` (prik + navn), `Image_2` (prikken), `TextBlock_4` (stopnavnet),
`HorizontalBox_5` + `Spacer_2` (skiftemuligheder – giver hul, hold dem skjult/0) og
`Spacer_4` (luft under rækken = afstanden mellem stop).
```json
{"skaerm": "StopRaekke", "aendringer": [
  {"funktion": "skjul",  "element": "HorizontalBox_5"},
  {"funktion": "hoejde", "element": "Spacer_2", "vaerdi": 0},
  {"funktion": "hoejde", "element": "SizeBox_0", "vaerdi": 56},
  {"funktion": "klip",   "element": "SizeBox_0"},
  {"funktion": "juster", "element": "TextBlock_4", "vaerdi": "top"},
  {"funktion": "hoejde", "element": "Spacer_4", "vaerdi": 147}
]}
```
Større `Spacer_4` = mere luft mellem stoppene. Spillet viser altid 3 stop.

## Movia-farver

Movia-gul `#FFC20E`, STOP-rød `#E2231A`, sort `#111111`, mørk tekst `#1D1D1D`,
grå tekst `#333333`, lysegrå tekst `#8A8F94`, lysegrå baggrund `#F3F4F5`,
grøn `#3FA535`, rød `#DE3B26`, mørkeblå `#233257`.
Skrifttype er altid Inter (vælges automatisk).

## Det kan IKKE lade sig gøre (lov det ikke)

- Andre datafelter end dem der står ovenfor (fx vejr, rigtigt GPS-kort, fart – fart kommer senere)
- Flere end 3 stop i passagerskærmens stopliste
- Live data fra internettet (vejr, nyheder) – spillet kan ikke hente web-data

## Eksempel: bordcomputer (Main) i Movia-stil

```json
{
  "skaerm": "Main",
  "layout": {
    "w": 1200, "h": 764, "bg": "#233257",
    "items": [
      {"type": "box", "name": "Kort", "x": 0, "y": 0, "w": 1200, "h": 764, "color": "#FFFFFF", "image": "T_Movia_Kort"},
      {"type": "box", "name": "Topbjælke", "x": 0, "y": 0, "w": 1200, "h": 100, "color": "#0A0A0A", "data": "Header"},
      {"type": "box", "name": "Stopliste", "x": 20, "y": 120, "w": 460, "h": 540, "color": "#DE3B26", "data": "StopListe"}
    ]
  }
}
```

## Eksempel: topbjælken (Header)

```json
{
  "skaerm": "Header",
  "layout": {
    "w": 900, "h": 100, "bg": "#0A0A0A",
    "items": [
      {"type": "box", "name": "Baggrund", "x": 0, "y": 0, "w": 900, "h": 100, "color": "#0A0A0A"},
      {"type": "text", "name": "Linje og destination", "x": 20, "y": 30, "data": "LinjeDestination", "size": 30, "color": "#FFFFFF", "bold": true},
      {"type": "text", "name": "Ur", "x": 660, "y": 8, "data": "Ur", "size": 44, "color": "#FFFFFF"},
      {"type": "text", "name": "Forsinkelse", "x": 700, "y": 62, "data": "Forsinkelse", "size": 24, "color": "#FFFFFF"}
    ]
  }
}
```

## Komplet eksempel (Movia-passagerskærm)

```json
{
  "skaerm": "Passager",
  "layout": {
    "w": 1600, "h": 430, "bg": "#FFFFFF",
    "items": [
      {"type": "box", "name": "Reklame", "x": 0, "y": 0, "w": 790, "h": 430, "color": "#FFFFFF", "image": "T_Reklame_Aeblefest"},
      {"type": "box", "name": "Topfelt", "x": 790, "y": 0, "w": 810, "h": 92, "color": "#F3F4F5"},
      {"type": "text", "name": "Label DK", "x": 806, "y": 22, "text": "Næste stop", "size": 18, "color": "#333333"},
      {"type": "text", "name": "Label EN", "x": 806, "y": 46, "text": "Next stop", "size": 18, "color": "#8A8F94"},
      {"type": "text", "name": "Næste stop", "x": 942, "y": 18, "data": "NaesteStop", "size": 40, "color": "#1D1D1D", "bold": true},
      {"type": "box", "name": "Venstre kolonne", "x": 790, "y": 92, "w": 152, "h": 338, "color": "#F3F4F5"},
      {"type": "box", "name": "STOP-felt", "x": 790, "y": 93, "w": 152, "h": 136, "color": "#111111", "color_on": "#E2231A", "state": "StopOenske"},
      {"type": "text", "name": "STOP", "x": 815, "y": 136, "text": "STOP", "size": 36, "color": "#FFFFFF", "bold": true},
      {"type": "text", "name": "Linje-label", "x": 806, "y": 250, "text": "Linje:", "size": 20, "color": "#333333"},
      {"type": "text", "name": "Linje", "x": 870, "y": 250, "data": "Linje", "size": 20, "color": "#8A8F94"},
      {"type": "text", "name": "Zone", "x": 806, "y": 285, "text": "Zone: 2", "size": 20, "color": "#333333"},
      {"type": "text", "name": "Tid", "x": 806, "y": 320, "data": "Ur", "size": 20, "color": "#333333"},
      {"type": "box", "name": "Stopliste", "x": 960, "y": 100, "w": 620, "h": 320, "color": "#FFFFFF", "data": "StopListe"}
    ]
  }
}
```

Layout-delen kan også åbnes og rettes i Movia Editor (Åbn… → vælg filen,
hvis den kun indeholder `layout`-delen).


## Den nyeste chaufførskærm (Driving) – brug den som udgangspunkt
Sådan ser bordcomputeren ud i modden lige nu: blå statuslinje, sort header med linje-boks, destination og stort ur,
sidebar (Billet, Opkald, Besked, Nat, Skilt, Rute), rød/grøn "Næste stop"-boks med planlagt tid og forsinkelse,
"Sidste stop"-boks (skifter til "Tag afgang" ved stop), GPS-kort med 3D-ring om næste stop, bundbjælke og navigation.
Spillets egne elementer skjules med `aendringer`, og `behold` holder spillets GridPanel_156 (bruges i baggrunden).
`Main` og `Tjeneste` er bygget på samme måde – ret dem ens.

Blokken herunder er **grundskærmen**. Menuerne ligger som ekstra lag oven på den i den rigtige kommando.json og må ikke slettes:
`Skilt …` (skilt-menu), `SR …` (skift rute + pause-kort), `Billet …` (billetmenu), `Liste …` (stopliste), `Pause …` (pausekort),
`Kasse …` (kasseopgørelse), `Nat …` (nattilstand), `Succes …` ("Login godkendt").
Hele skærmen med alle menuer (706 lag, 827 regler) ligger i `chauffoerskaerm_driving.json` ved siden af denne guide.
Ret derfor i den eksisterende kommando.json – tilføj/ret lag, men erstat ikke hele Driving med kun grundskærmen.

```json
{
  "skaerm": "Driving",
  "layout": {
    "w": 1200, "h": 764, "bg": "#233257", "behold": ["GridPanel_156"],
    "items": [
      {"type": "gps", "name": "Kort", "x": 80, "y": 98, "w": 1120, "h": 602, "pitch": -25, "afstand": 4000, "vinkel": 35, "baggrund": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\kort_bg.png", "z": -20, "color": "#3B4F7F", "zoom": 0.15, "vej": "#8E9CC4", "storvej": "#C3CCE6"},
      {"type": "box", "name": "Statusbjaelke", "x": 0, "y": 0, "w": 1200, "h": 26, "color": "#1F3FF0"},
      {"type": "text", "name": "Status ur", "x": 10, "y": 4, "text": "7:30", "size": 13, "bold": false, "color": "#FFFFFF"},
      {"type": "box", "name": "Status ikoner", "x": 1100, "y": 2, "w": 90, "h": 22, "color": "#FFFFFF", "image": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\status_ikoner.png"},
      {"type": "box", "name": "Header", "x": 0, "y": 26, "w": 1200, "h": 72, "color": "#0A0A0A"},
      {"type": "box", "name": "Log ud", "x": 0, "y": 26, "w": 80, "h": 72, "color": "#DE3B26", "image": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\knap_logud_rod.png"},
      {"type": "box", "name": "Linjeboks", "x": 84, "y": 30, "w": 66, "h": 64, "color": "#1E8FD8"},
      {"type": "text", "name": "Linje", "x": 84, "y": 39, "text": "5C", "size": 28, "bold": true, "color": "#FFFFFF", "w": 66, "h": 46, "align": "midt"},
      {"type": "text", "name": "Destination", "x": 162, "y": 38, "size": 30, "bold": true, "color": "#FFFFFF", "w": 714, "h": 46, "klip": true, "text": "Husum Torv"},
      {"type": "text", "name": "Ur", "x": 880, "y": 30, "text": "07:30:22", "size": 42, "bold": false, "color": "#FFFFFF", "w": 258, "h": 64, "align": "hoejre"},
      {"type": "box", "name": "Menu", "x": 1146, "y": 26, "w": 54, "h": 72, "color": "#5CBF2A", "image": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\knap_menu.png"},
      {"type": "box", "name": "Sidebjaelke", "x": 0, "y": 98, "w": 80, "h": 602, "color": "#15181D"},
      {"type": "box", "name": "Knap stop", "x": 4, "y": 102, "w": 72, "h": 84, "color": "#15181D", "image": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\knap_billet3.png"},
      {"type": "box", "name": "Knap telefon", "x": 4, "y": 190, "w": 72, "h": 84, "color": "#15181D", "image": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\knap_opkald3.png"},
      {"type": "box", "name": "Knap besked", "x": 4, "y": 278, "w": 72, "h": 84, "color": "#15181D", "image": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\knap_besked3.png"},
      {"type": "box", "name": "NaesteBoks", "x": 84, "y": 102, "w": 420, "h": 158, "color": "#3FA535"},
      {"type": "text", "name": "Naeste label", "x": 90, "y": 106, "text": "Næste stop:", "size": 11, "bold": false, "color": "#FFFFFF"},
      {"type": "text", "name": "Zone label", "x": 226, "y": 106, "text": "Zone 2", "size": 11, "bold": false, "color": "#FFFFFF"},
      {"type": "text", "name": "Planlagt label", "x": 346, "y": 106, "text": "Planlagt ankomst:", "size": 11, "bold": false, "color": "#FFFFFF", "w": 150, "h": 18, "align": "hoejre"},
      {"type": "text", "name": "Naeste stop", "x": 90, "y": 130, "size": 22, "bold": true, "color": "#FFFFFF", "w": 262, "h": 40, "klip": true, "text": "Nørrebro St."},
      {"type": "text", "name": "Naeste tid", "x": 336, "y": 122, "text": "07:31:00", "size": 22, "bold": false, "color": "#FFFFFF", "w": 160, "h": 36, "align": "hoejre"},
      {"type": "text", "name": "Forsinkelse label", "x": 346, "y": 168, "text": "Forsinkelse:", "size": 11, "bold": false, "color": "#FFFFFF", "w": 150, "h": 18, "align": "hoejre"},
      {"type": "text", "name": "Forsinkelse", "x": 336, "y": 184, "text": "+0:16", "size": 26, "bold": true, "color": "#FFFFFF", "w": 160, "h": 42, "align": "hoejre"},
      {"type": "box", "name": "Trekant", "x": 286, "y": 246, "w": 16, "h": 10, "color": "#FFFFFF", "image": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\trekant.png"},
      {"type": "box", "name": "SidsteBoks", "x": 84, "y": 264, "w": 420, "h": 82, "color": "#3FA535"},
      {"type": "text", "name": "Sidste label", "x": 90, "y": 268, "text": "Sidste stop:", "size": 11, "bold": false, "color": "#FFFFFF"},
      {"type": "text", "name": "Zone label 2", "x": 226, "y": 268, "text": "Zone 2", "size": 11, "bold": false, "color": "#FFFFFF"},
      {"type": "text", "name": "Planlagt label 2", "x": 346, "y": 268, "text": "Planlagt ankomst:", "size": 11, "bold": false, "color": "#FFFFFF", "w": 150, "h": 18, "align": "hoejre"},
      {"type": "text", "name": "Sidste stop", "x": 90, "y": 292, "text": "Husum Torv Sløjfen", "size": 18, "bold": true, "color": "#FFFFFF", "w": 262, "h": 32, "klip": true},
      {"type": "text", "name": "Sidste tid", "x": 336, "y": 286, "text": "07:47:00", "size": 22, "bold": false, "color": "#FFFFFF", "w": 160, "h": 36, "align": "hoejre"},
      {"type": "box", "name": "AfgangBoks", "x": 84, "y": 264, "w": 420, "h": 82, "color": "#1E5FD6", "opacity": 0},
      {"type": "text", "name": "Afgang label", "x": 90, "y": 268, "text": "Tag afgang:", "size": 11, "bold": false, "color": "#FFFFFF", "opacity": 0},
      {"type": "text", "name": "Afgang tid", "x": 90, "y": 286, "text": "08:19:00 (08:21:00)", "size": 26, "bold": true, "color": "#FFFFFF", "w": 400, "h": 46, "opacity": 0},
      {"type": "box", "name": "Bundbjaelke", "x": 0, "y": 700, "w": 1200, "h": 18, "color": "#1F3FF0"},
      {"type": "text", "name": "Koersel", "x": 8, "y": 702, "text": "Kørsel: 1504", "size": 9, "bold": false, "color": "#FFFFFF"},
      {"type": "text", "name": "Nummer", "x": 360, "y": 702, "text": "92590", "size": 9, "bold": false, "color": "#FFFFFF"},
      {"type": "text", "name": "Kunde", "x": 600, "y": 702, "text": "Kunde: GoCollective", "size": 9, "bold": false, "color": "#FFFFFF"},
      {"type": "text", "name": "Enhed", "x": 980, "y": 702, "text": "00c6c7b4b8d035   v 2.6.7", "size": 9, "bold": false, "color": "#FFFFFF"},
      {"type": "box", "name": "Navigation", "x": 0, "y": 718, "w": 1200, "h": 46, "color": "#F4F4F6"},
      {"type": "box", "name": "Nav menu", "x": 690, "y": 721, "w": 40, "h": 40, "color": "#FFFFFF", "image": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\nav_menu.png"},
      {"type": "box", "name": "Nav hjem", "x": 846, "y": 721, "w": 40, "h": 40, "color": "#FFFFFF", "image": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\nav_hjem.png"},
      {"type": "box", "name": "Nav tilbage", "x": 1010, "y": 721, "w": 40, "h": 40, "color": "#FFFFFF", "image": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\nav_tilbage.png"},
      {"type": "box", "name": "Stopring", "x": 600, "y": 400, "w": 260, "h": 104, "color": "#FFFFFF", "image": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\stop_ring2.png", "ring": true, "z": -12},
      {"type": "knap", "name": "Log ud tryk", "x": 0, "y": 26, "w": 80, "h": 72, "z": 210, "skiftertag": "MoviaLogud"}
    ],
    "regler": [
      {"hvis": "Forsinkelse > 0", "saet": "farve", "element": "NaesteBoks", "til": "#DE3B26", "ellers": "#3FA535", "glid": 0.6},
      {"hvis": "Forsinkelse > 0", "saet": "farve", "element": "SidsteBoks", "til": "#DE3B26", "ellers": "#3FA535", "glid": 0.6},
      {"hvis": "Forsinkelse < 0", "saet": "tekst", "element": "Forsinkelse label", "til": "Før tid:", "ellers": "Forsinkelse:"},
      {"saet": "tekst", "element": "Forsinkelse", "til": "{Forsinkelse:m:ss}"},
      {"saet": "tekst", "element": "Naeste stop", "til": "{NaesteStopNavn}"},
      {"saet": "tekst", "element": "Naeste tid", "til": "{NaesteTid:hh:mm:ss}"},
      {"saet": "tekst", "element": "Destination", "til": "{SidsteStopNavn}"},
      {"saet": "tekst", "element": "Sidste stop", "til": "{SidsteStopNavn}"},
      {"saet": "tekst", "element": "Sidste tid", "til": "{SidsteTidSek:hh:mm:ss}"},
      {"saet": "tekst", "element": "Ur", "til": "{KlokkeSek:hh:mm:ss}"},
      {"saet": "tekst", "element": "Status ur", "til": "{Klokken:hh:mm}"},
      {"saet": "tekst", "element": "Linje", "til": "{LinjeNr}"},
      {"saet": "tekst", "element": "Afgang tid", "til": "{AfgangTekst}"},
      {"hvis": "HolderVedStop = 1 og ListeAaben = 0", "saet": "vis", "element": "AfgangBoks", "glid": 0.25},
      {"hvis": "HolderVedStop = 1 og ListeAaben = 0", "saet": "flytx", "element": "AfgangBoks", "til": 0, "ellers": -120, "glid": 0.25},
      {"hvis": "HolderVedStop = 1 og ListeAaben = 0", "saet": "vis", "element": "Afgang label", "glid": 0.25},
      {"hvis": "HolderVedStop = 1 og ListeAaben = 0", "saet": "flytx", "element": "Afgang label", "til": 0, "ellers": -120, "glid": 0.25},
      {"hvis": "HolderVedStop = 1 og ListeAaben = 0", "saet": "vis", "element": "Afgang tid", "glid": 0.25},
      {"hvis": "HolderVedStop = 1 og ListeAaben = 0", "saet": "flytx", "element": "Afgang tid", "til": 0, "ellers": -120, "glid": 0.25},
      {"hvis": "HolderVedStop = 1 og ListeAaben = 0", "saet": "flyty", "element": "SidsteBoks", "til": 86, "ellers": 0, "glid": 0.25},
      {"hvis": "HolderVedStop = 1 og ListeAaben = 0", "saet": "flyty", "element": "Sidste label", "til": 86, "ellers": 0, "glid": 0.25},
      {"hvis": "HolderVedStop = 1 og ListeAaben = 0", "saet": "flyty", "element": "Zone label 2", "til": 86, "ellers": 0, "glid": 0.25},
      {"hvis": "HolderVedStop = 1 og ListeAaben = 0", "saet": "flyty", "element": "Planlagt label 2", "til": 86, "ellers": 0, "glid": 0.25},
      {"hvis": "HolderVedStop = 1 og ListeAaben = 0", "saet": "flyty", "element": "Sidste stop", "til": 86, "ellers": 0, "glid": 0.25},
      {"hvis": "HolderVedStop = 1 og ListeAaben = 0", "saet": "flyty", "element": "Sidste tid", "til": 86, "ellers": 0, "glid": 0.25},
      {"hvis": "ListeAaben = 0", "saet": "vis", "element": "SidsteBoks", "glid": 0.2},
      {"hvis": "ListeAaben = 0", "saet": "vis", "element": "Sidste label", "glid": 0.2},
      {"hvis": "ListeAaben = 0", "saet": "vis", "element": "Zone label 2", "glid": 0.2},
      {"hvis": "ListeAaben = 0", "saet": "vis", "element": "Planlagt label 2", "glid": 0.2},
      {"hvis": "ListeAaben = 0", "saet": "vis", "element": "Sidste stop", "glid": 0.2},
      {"hvis": "ListeAaben = 0", "saet": "vis", "element": "Sidste tid", "glid": 0.2},
      {"hvis": "Bekraeftet = 1 og BilletAaben = 0 og LogudAaben = 0", "saet": "vis", "element": "Log ud tryk"}
    ]
  },
  "aendringer": [
    {"funktion": "skjul", "element": "Border"},
    {"funktion": "skjul", "element": "Border_84"},
    {"funktion": "skjul", "element": "UMG_TB_NAtron_Time_Icons_C_Driving"},
    {"funktion": "skjul", "element": "UMG_TB_NAtron_Bottom_Row_Buttons_C_1"},
    {"funktion": "skjul", "element": "ButtonLSA"}
  ]
}
```

`AfgangTekst` (**Driving**): planlagt afgang fra stoppet bussen holder ved, fx `08:19:00`, og hvis man er for sent på den `08:19:00 (08:21:00)`.


## Tekst: justering og klip
Tekst-elementer kan have `"align": "midt"` eller `"align": "hoejre"` (kræver `w`), og `"klip": true`
(lang tekst afsluttes med "…" i stedet for at løbe ind i andre ting – kræver `w`).
```json
{"type": "text", "name": "Naeste tid", "x": 310, "y": 122, "w": 160, "text": "07:31:00", "size": 22, "align": "hoejre"}
{"type": "text", "name": "Naeste stop", "x": 64, "y": 130, "w": 262, "text": "-", "size": 22, "bold": true, "klip": true}
```
VIGTIGT: Brug IKKE `"data"` på Driving-skærmen til stopnavne – spillet farver de felter sort. Lav i stedet en
almindelig tekst og en regel: `{"saet": "tekst", "element": "Naeste stop", "til": "{NaesteStopNavn}"}`.

## GPS-kort (type "gps")
Et rigtigt, kørende GPS-kort (spillets eget navigationskort) i 3D. Kun ét pr. skærm.
```json
{"type": "gps", "name": "Kort", "x": 54, "y": 98, "w": 1146, "h": 602, "z": -20,
 "pitch": -35, "afstand": 4000, "vinkel": 35,
 "baggrund": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\kort_bg.png"}
```
- `pitch` = hvor skråt kortet ses (-20 fladt … -60 meget skråt), `afstand` = kamera-afstand, `vinkel` = kamera-drejning.
- `baggrund` = billede der farver kortets baggrund (spillet gør det mørkere, så vælg en lys farve).
- 3D-ring om næste busstop: et billede-element med `"ring": true` – motoren flytter det hen over næste stop på kortet
  og skjuler det, når stoppet er uden for kortet:
```json
{"type": "box", "name": "Stopring", "x": 0, "y": 0, "w": 140, "h": 70, "image": "...\\Ikoner\\stop_ring.png", "ring": true, "z": -12}
```


## Eksempel: linje-mærker og afgangstavle (Passager)
Mærke under 1. stop (gul, blå hvis S-bus), vises kun hvis der er en linje:
```json
{"hvis": "Linje1_1 != ''", "saet": "vis", "element": "Maerke1_1"},
{"hvis": "Linje1_1 indeholder 'S'", "saet": "farve", "element": "Maerke1_1", "til": "#1E5FD6", "ellers": "#F5B800"},
{"saet": "tekst", "element": "MaerkeTxt1_1", "til": "{Linje1_1}"}
```
Afgangstavle der kun vises ved stoppet (lag med højt `z`, så den dækker stoplisten):
```json
{"hvis": "VedStop = 1", "saet": "vis", "element": "Tavle bund"},
{"hvis": "VedStop = 1 og AfgLinje1 != ''", "saet": "vis", "element": "Tavle rk1 til"},
{"saet": "tekst", "element": "Tavle rk1 til", "til": "{AfgTil1}"},
{"saet": "tekst", "element": "Tavle rk1 min", "til": "{AfgMin1:heltal}"},
{"hvis": "AfgMin1 < 1", "saet": "tekst", "element": "Tavle rk1 min", "til": "Nu"}
```
Data hentes fra spillets egne afgangstavler ca. hvert 2,5 sekund.


## Reklamer: skift mellem flere + video
Flere reklamer på samme plads der skifter (med blød overgang) – læg dem oven i hinanden og brug `sider` i layoutet:
```json
"sider": {"skift_hver": 12, "glid": 0.8, "sider": [["Reklame"], ["Reklame 2"], ["Reklame 3"]]}
```
Video-reklamer: læg videoen (.mp4/.mov/.webm/.gif) i `MoviaTools\Reklamer` og dobbeltklik `video_til_flipbook.bat`
(kræver én gang: `pip install opencv-python pillow`). Det laver `Reklamer\<navn>_flipbook.png` + `.json`.
Brug den så som et billede-element med `"video"` i stedet for `"image"`:
```json
{"type": "box", "name": "Reklame 3", "x": 0, "y": 0, "w": 790, "h": 430, "color": "#000000",
 "video": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Reklamer\\pizza_flipbook.png"}
```
Videoer skal være korte (højst ca. 64 billeder = 8 sek ved 8 fps), uden lyd. Længere videoer bliver klippet.

## Trykknapper (type "knap") og stoplisten
Et lag af typen `"knap"` er en usynlig trykflade. Den tegner ikke noget selv – læg den oven på en boks/et ikon.
- `"skifter": "Liste"` – hvert tryk skifter variablen `Liste` mellem 0 og 1.
- `"trin": "Rul", "vaerdi": 1, "min": 0, "max": 30` – hvert tryk lægger `vaerdi` til variablen `Rul` (holdt mellem min og max).
Variablerne (fx `Liste`, `Rul`) kan bruges i regler som alle andre: `"hvis": "Liste = 1"`.
En knap kan kun trykkes, når den er synlig – skjul den med en `vis`-regel, når den ikke skal virke.

Stoplisten (**Driving/Main**): `Stop1Navn` … `Stop8Navn`, `Stop1Tid` (planlagt ankomst, sek – format `hh:mm:ss`),
`Stop1Afgang`, `Stop1Findes` (1/0). Stop1 er stoppet EFTER "Næste stop" (næste stop står ikke dobbelt); en knap-gruppe der hedder `Rul` ruller listen.

`AfgangTekst` (**Driving**): planlagt afgang fra stoppet bussen holder ved, fx `08:19:00`, og hvis man er for sent på den `08:19:00 (08:21:00)`.


---------------------------------------------------------------------
# DEL 2 – alt det nye (login, billetter, pause, kasse, nat)
---------------------------------------------------------------------

## Generelt for bordcomputer-skærmene (Main, Driving, Start, LogIn, Tur)
- Skærmen er 1200 × 764. Faste dele: statusbjælke 0–26, header 26–98, sidebar 0–80 (x), bundbjælke 700–718, navigation 718–764.
- **Skriftstørrelse er i punkter**: et design i pixels omregnes med ×0,75 (fx 24 px tekst → `"size": 18`).
- Ekstra felter på alle elementer: `"z"` (lag), `"opacity": 0` (start usynlig – bruges til ting der toner frem med en `vis`-regel med `glid`, så de ikke blinker når skærmen åbnes), `"align": "midt"|"hoejre"` + `"w"`/`"h"`, `"klip": true` (… ved for lang tekst).
- `"spil": "WidgetNavn"` på et element flytter et af spillets egne elementer hen til x/y/w/h (kun bordcomputeren).
- Billeder: `"image": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\fil.png"` på en box. Billedet strækkes til w/h og har sin egen baggrund (farven bruges ikke).
  Ikoner der findes: knap_billet3, knap_opkald3, knap_besked3, knap_nat3, knap_logud_rod, knap_logind, pil_op, pil_ned, pil_luk, ikon_check, ikon_fejl, ikon_slet, ikon_store, ikon_luk, status_ikoner, nav_menu, nav_hjem, nav_tilbage.
- En tekst må kun have ÉN `{plads}`. Skal der to tal i en linje, så lav to tekster ved siden af hinanden.
- Boksene lader klik gå igennem. Kun `knap`-lag kan trykkes.

## Husk-mærker på bussen (overlever skærmskift)
Atron skifter skærm (Main ↔ Driving) hele tiden, og så glemmer skærmen sine knap-variabler. Ting der skal huskes
gemmes derfor som et *mærke* på bussen:
| datafelt | mærke | betyder |
|---|---|---|
| `ListeAaben` | MoviaListe | stoplisten er åben (1/0) |
| `BilletAaben` | MoviaBillet | billetmenuen er åben |
| `NatAaben` | MoviaNat | nattilstand (skærmen dæmpes) |
| `LogudAaben` | MoviaLogud | kasseopgørelsen (log ud) er åben |
| `Bekraeftet` | MoviaOK | "Login godkendt" er bekræftet |
Tal der huskes: `LoginTid` (sek efter midnat ved login), `SolgteBilletter`, `Kvitteringer` (tælles af billetmenuen). De nulstilles ved login.

## Knaptyper (type "knap")
| nøgle | gør |
|---|---|
| `"skifter": "X"` | skifter variabel X mellem 0 og 1 (glemmes ved skærmskift) |
| `"trin": "X", "vaerdi": 1, "min": 0, "max": 30` | lægger vaerdi til X. Med min=max sættes X til den værdi |
| `"skiftertag": "MoviaListe"` | tænder/slukker et husk-mærke på bussen (se tabellen) |
| `"tilfoejtag": "MoviaOK"` | sætter et mærke (fx Bekræft). `"gruppe": "BekLokal"` sætter også variablen til 1 |
| `"logud": true` | afslutter vagten (spillets End Shift) |
| `"print": "UMG_TB_NAtron_Ticket_Button_8"` | printer billetten på den af spillets billetknapper (kun Main). `"taeller": "Printet"` tæller op |
| `"kategori": "UMG_TB_NAtron_Ticket_Button", "gruppe": "Kat", "vaerdi": 0` | åbner en af spillets billetkategorier (kun Main) |
| `"kvittering": true` | printer en kvittering (spillets Print Receipt) |
| Tastatur (kun LogIn): `"tegn": "a", "felt": "Felt", "nulstil": "Forsoeg", "store": "Store"` | skriver et tegn i det aktive felt. `"slet": true` / `"ryd": true` sletter |
| `"login": "Forsoeg"` | tjekker kontoen: Forsoeg = 2 hvis rigtig, 1 hvis forkert |

## Nye handlinger (saet)
| saet | gør |
|---|---|
| `klik` | trykker på et af spillets egne elementer (element = spillets widgetnavn), i det øjeblik betingelsen BLIVER sand |
| `tilfoejtag` / `fjerntag` | sætter/fjerner et mærke på bussen (`"til": "MoviaNat"`). element skal være et eksisterende lag |

## Nye datafelter
| navn | skærm | hvad |
|---|---|---|
| `Tekst0`, `Maske1` | LogIn | det der er skrevet i felt 0 (email) / felt 1 som prikker. Blinkende markør i det aktive felt |
| `Felt`, `Store`, `Forsoeg`, `Husk` | LogIn | knap-variabler: aktivt felt (0/1), store bogstaver, login-forsøg (0/1/2), gem login |
| `LoginOK` | LogIn | 1 hvis email og kode passer |
| `Alder` | alle | sekunder siden skærmen blev vist |
| `AntalStop`, `TurNr` | Driving/Main | antal stop på turen / turnummer |
| `Rute1Navn`…`Rute8Navn`, `Rute1Tid`, `Rute1Afgang`, `Rute1Findes` | Driving/Main | ruten fra start (ruller med `Rul`) |
| `FoersteNavn`, `FoersteAfgang` | Driving/Main | rutens første stop (ruller ikke) |
| `Billet1Navn`…`Billet6Navn`, `Billet1Kort`, `Billet1Findes` | Main | billetterne i den valgte kategori |
| `Kat1Navn`…`Kat3Navn`, `Kat1Findes` | Main | spillets billetkategorier |
| `PauseSek` | Driving/Main | sekunder til afgang fra stoppet bussen holder ved (format `mm:ss`) |
| `ErFoersteStop` | Driving/Main | 1 ved turens første stop (endestation) |
| `PauseHoldtMin` | Driving/Main | minutters pause holdt i dag |
| `VagtMin` | Driving/Main | minutter siden login (format `hh:mm`) |
| `StopNr` | Driving/Main | nummeret på det stop bussen er ved |

## Det der allerede er bygget (ændr det, men slet det ikke ved et uheld)
Lagnavne starter med: `Liste …` (stopliste), `Succes …` ("Login godkendt"), `Billet …` (billetmenu),
`Pause …` (pausekort), `Kasse …` (kasseopgørelse), `Nat …` (nat-knap og dæmpning), `Felt/Tast/Husk/OK/Logger …` (login).
Login-kontoen (email/kode) ligger i regel-motoren og kan ikke ændres i kommando.json.

## Typiske fejl
- To `{…}` i én tekst → reglen afvises.
- Et `knap`-lag uden en `vis`-regel kan altid trykkes – også når menuen er lukket.
- Glemt `"opacity": 0` på noget der toner frem → det blinker kort, når skærmen åbnes.
- Ændret Driving men ikke Main (eller omvendt) → skærmen skifter udseende når bussen stopper.

---------------------------------------------------------------------
# DEL 3 – skilt og skift rute (bordcomputeren)
---------------------------------------------------------------------

## Skilt-menuen (lag `Skilt …`, Driving og Main)
Sidebar-knappen "Skilt" (y 454) åbner en menu hvor chaufføren selv sætter linjenummer og destination på bussens skilt.
"Ikke i rute" vises også på passagerskærmen (lag `IkkeIRute …`, regel på `IkkeIRute = 1`).
| datafelt | hvad |
|---|---|
| `SkiltAaben` | menuen er åben (mærke MoviaSkilt) |
| `SkiltAktiv` | eget skilt er sat (1/0) |
| `IkkeIRute` | skiltet er sat til "Ikke i rute" (1/0) – virker også på passagerskærmen |
| `SkiltLinje`, `SkiltDestination` | teksten på det egne skilt |
| `Tekst0`/`Tekst1`, `Ren0`/`Ren1` | felterne linje (0) og destination (1) – `Ren` er uden blinkende markør |

| knap | gør |
|---|---|
| `"saetskilt": true` | sætter skiltet ud fra felt 0 og 1 |
| `"nulstilskilt": true` | skiltet følger ruten igen |
| `"rutetekst": true` | MIN RUTE: skriver turens linje og endestation i felterne |
| `"tekstsaet": "Skolebus", "vaerdi": 1` | skriver teksten i felt nr. vaerdi (hurtigvalg; `""` sletter) |

## Skift rute (lag `SR …`, Driving og Main)
Sidebar-knappen "Rute" (y 542) åbner menuen. Trin 1: vælg tur (fane NÆR DIG = ture forbi nærmeste stoppested de næste 2 timer,
fane SØG LINJE = alle dagens afgange for linjen). Trin 2: vælg startstop (fx som ekstrabus midt på ruten). START logger ind
på turen, tildeler kursen til chaufføren (så passagererne vil med) og viser pause-kortet (`SR pause …`) med nedtælling.
Knap-grupper: `RFane` (0/1), `RTrin` (1 = trin 1, 2 = trin 2), `RValg`/`SValg` (valgt række), `RRul`/`SRul` (rulning).
| datafelt | hvad |
|---|---|
| `SRAaben` | menuen er åben (mærke MoviaRute) |
| `SRTid1`…`SRTid8`, `SRLinje1`, `SRTil1`, `SROm1`, `SRFindes1`, `SRValgt1` | turlisten: tid, "17 · Kurs 3", "→ destination", "om X min", findes 1/0, valgt 1/0 |
| `SRStop1Navn`…`SRStop8Navn`, `SRStop1Tid`, `SRStop1Findes`, `SRStop1Valgt`, `SRStop1Maerke` | stoplisten i trin 2 (maerke: "start"/"springes over") |
| `SRStatus`, `SRAntal`, `SRStopAntal` | statuslinje og antal |
| `SRTitel`, `SRUnder`, `SRValgtTur`, `SRStartNavn`, `SRStartTid` | tekster om den valgte tur/startstop |
| `SRNed` | nedtælling til afgang fra startstoppet (tekst `m:ss`, tal = sekunder; >0 = vis pause-kortet) |
| `SRTekst`, `SRStopNavn` | pause-kortets linje/kurs og startstop |

| knap | gør |
|---|---|
| `"rutesoeg": 0` / `1` + `"gruppe": "RFane"` | søg nær dig (0) eller linjen i felt 8 (1) |
| `"rutetegn": "7"` | skriver i linjefeltet (felt 8). `"<"` sletter, `"C"` rydder |
| `"raekke": 0, "gruppe": "RValg", "rul": "RRul"` | vælger række 0-5 i listen (stoplisten: `SValg`/`SRul`) |
| `"rutevaelg": true` | går til trin 2 med den valgte tur |
| `"rutestart": true` | starter turen fra det valgte stop |

## Lagnavne der allerede er bygget (tilføjelse)
`Skilt …`, `SR …`, `IkkeIRute …`. Lag med samme forbogstaver bliver slettet og bygget forfra af `byg_skilt.py` / `byg_rute.py`.

---------------------------------------------------------------------
# AFSLUT ALTID DIT SVAR MED "SÅDAN BYGGER DU DET"
---------------------------------------------------------------------
Du (AI'en) skal ALTID slutte dit svar med en kort trin-for-trin vejledning til brugeren, der passer til det du har lavet:

**Når du kun har ændret kommando.json (design, tekster, regler):**
1. Gem filen som `kommando.json` i `C:\Users\tacci\Documents\The Bus\MoviaTools\` (erstat den gamle).
2. Åbn The Bus Modding Editor og skriv i Python-konsollen nederst:
   `exec(open(r"C:\Users\tacci\Documents\The Bus\MoviaTools\movia_kommando.py", encoding="utf-8").read())`
   – vent til loggen siger "ALT FAERDIGT".
3. TML → Mod Creator → Build Mod → Build Client Only. Vent ca. 6 minutter.
4. Start The Bus og test.

**Når motoren også er ændret (ny `_motor_vNN.t3d` fra motorgen.py):**
1. Læg `_motor_vNN.t3d` (og evt. ændrede .py-filer) i MoviaTools-mappen.
2. Python-konsollen: `exec(open(r"C:\Users\tacci\Documents\The Bus\MoviaTools\movia_ny_motor.py", encoding="utf-8").read())`
3. I motor-vinduet: Graph → `+` ved GRAPHS → Enter → klik i grafen → Ctrl+V → Confirm → File → Refresh All Nodes.
4. Python-konsollen: `movia_faerdig(layout=True)` – den gemmer kun hvis der ingen fejl er.
5. TML → Mod Creator → Build Mod → Build Client Only, og test i spillet.

Skriv vejledningen på dansk, kort og med de præcise linjer der skal indsættes.
